"""Incremental simulation session for interactive GUI stepping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from mmwave_v2i_sim.channel.model import ChannelSnapshot
from mmwave_v2i_sim.config.schema import ScenarioConfig
from mmwave_v2i_sim.core.engine import SimulationEngine
from mmwave_v2i_sim.mobility.base import VehicleState
from mmwave_v2i_sim.plugins.base import AllocationInput


@dataclass
class StepSnapshot:
    step: int
    phase: str
    time_elapsed_s: float
    los_ratio: float
    utilization: float
    trim_loss: float
    vehicles: list[VehicleState]
    channel: list[ChannelSnapshot]
    requests: list[tuple[int, int]]
    accepted: int
    rejected: int
    packing_placed: list[tuple[int, int, int, int]]  # x, y, w, h in grid units


@dataclass
class SimulationSession:
    config: ScenarioConfig
    engine: SimulationEngine = field(init=False)
    current_step: int = field(default=-1, init=False)
    trim_history: list[float] = field(default_factory=list, init=False)
    util_history: list[float] = field(default_factory=list, init=False)
    route_history: dict[int, list[tuple[float, float]]] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.engine = SimulationEngine(self.config)

    def reset(self) -> StepSnapshot:
        self.current_step = -1
        self.trim_history.clear()
        self.util_history.clear()
        self.route_history.clear()
        return self.step()

    def step(self) -> StepSnapshot | None:
        max_steps = self.config.run.steps
        if self.current_step + 1 >= max_steps:
            return None
        self.current_step += 1
        return self._advance(self.current_step)

    def _advance(self, step: int) -> StepSnapshot:
        cfg = self.config
        phases = cfg.run.frame_phases
        mobility = self.engine._mobility
        channel_model = self.engine._channel
        scheduler = self.engine._scheduler

        states = mobility.states_at_step(step)
        snapshots = channel_model.evaluate_step(states)
        for v in states:
            hist = self.route_history.setdefault(v.vehicle_id, [])
            hist.append((v.x_m, v.y_m))
            cap = cfg.render.max_route_points
            if len(hist) > cap:
                del hist[:-cap]

        los_ratio = (
            float(np.mean([1.0 if s.is_los else 0.0 for s in snapshots])) if snapshots else 0.0
        )

        requests: list[tuple[int, int]] = []
        for snap in snapshots:
            sinr_best = max(snap.sinr_db_by_band.values())
            t_req = int(np.clip(6 - (sinr_best / 8.0), 1, 6))
            f_req = int(np.clip(5 - (sinr_best / 10.0), 1, 5))
            requests.append((t_req, f_req))

        alloc = scheduler.allocate(
            AllocationInput(
                available_time_blocks=10,
                available_freq_blocks=10,
                requests=requests,
                objective=cfg.run.scheduler_objective,
            )
        )
        utilization = float(np.clip(alloc.utilization, 0.0, 1.0))
        trim_loss = 1.0 - utilization
        self.trim_history.append(trim_loss)
        self.util_history.append(utilization)

        packing = _greedy_pack_rects(10, 10, requests[: alloc.accepted_requests])

        return StepSnapshot(
            step=step,
            phase=phases[-1],
            time_elapsed_s=float(step),
            los_ratio=los_ratio,
            utilization=utilization,
            trim_loss=trim_loss,
            vehicles=states,
            channel=snapshots,
            requests=requests,
            accepted=alloc.accepted_requests,
            rejected=alloc.rejected_requests,
            packing_placed=packing,
        )

    def snapshot_kpis(self, snap: StepSnapshot) -> dict[str, Any]:
        return {
            "step": snap.step,
            "phase": snap.phase,
            "time_elapsed_s": snap.time_elapsed_s,
            "scheduler_strategy": self.config.run.scheduler_strategy,
            "scheduler_objective": self.config.run.scheduler_objective,
            "utilization": snap.utilization,
            "trim_loss": snap.trim_loss,
            "los_ratio": snap.los_ratio,
            "accepted_requests": snap.accepted,
            "rejected_requests": snap.rejected,
            "active_vehicles": len(snap.vehicles),
        }


def _greedy_pack_rects(
    t_blocks: int, f_blocks: int, rects: list[tuple[int, int]]
) -> list[tuple[int, int, int, int]]:
    """Simple shelf packing for MATLAB-style visualizePacking panel."""
    placed: list[tuple[int, int, int, int]] = []
    cursor_x, cursor_y, row_h = 0, 0, 0
    for w, h in rects:
        if cursor_x + w > t_blocks:
            cursor_x = 0
            cursor_y += row_h
            row_h = 0
        if cursor_y + h > f_blocks:
            break
        placed.append((cursor_x, cursor_y, w, h))
        cursor_x += w
        row_h = max(row_h, h)
    return placed
