"""Deterministic simulation engine with protocol phase event logging."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

import numpy as np

from mmwave_v2i_sim.channel import SimpleChannelModel
from mmwave_v2i_sim.config.schema import ScenarioConfig
from mmwave_v2i_sim.mobility import build_mobility_provider
from mmwave_v2i_sim.plugins.base import AllocationInput
from mmwave_v2i_sim.plugins.registry import PluginRegistry
from mmwave_v2i_sim.scheduling import register_builtin_strategies


@dataclass(frozen=True)
class RunArtifacts:
    seed: int
    steps: int
    timestep_s: float
    phases: list[str]
    config_fingerprint: str
    phase_order_valid: bool
    mean_utilization: float
    mean_trim_loss: float
    mean_blockage_ratio: float
    mean_latency_ms: float
    fairness_jain: float
    mean_vehicle_speed_mps: float
    mean_vehicle_count_per_step: float
    mean_los_ratio: float
    mean_pathloss_db_by_band: dict[float, float]
    mean_sinr_db_by_band: dict[float, float]
    scheduler_strategy: str
    scheduler_objective: str
    mean_accepted_requests: float
    mean_rejected_requests: float
    events: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "steps": self.steps,
            "timestep_s": self.timestep_s,
            "phases": self.phases,
            "config_fingerprint": self.config_fingerprint,
            "phase_order_valid": self.phase_order_valid,
            "mean_utilization": self.mean_utilization,
            "mean_trim_loss": self.mean_trim_loss,
            "mean_blockage_ratio": self.mean_blockage_ratio,
            "mean_latency_ms": self.mean_latency_ms,
            "fairness_jain": self.fairness_jain,
            "mean_vehicle_speed_mps": self.mean_vehicle_speed_mps,
            "mean_vehicle_count_per_step": self.mean_vehicle_count_per_step,
            "mean_los_ratio": self.mean_los_ratio,
            "mean_pathloss_db_by_band": self.mean_pathloss_db_by_band,
            "mean_sinr_db_by_band": self.mean_sinr_db_by_band,
            "scheduler_strategy": self.scheduler_strategy,
            "scheduler_objective": self.scheduler_objective,
            "mean_accepted_requests": self.mean_accepted_requests,
            "mean_rejected_requests": self.mean_rejected_requests,
            "events": self.events,
        }


class SimulationEngine:
    """Small deterministic baseline engine.

    This deliberately keeps logic minimal for Milestone 0 while
    enforcing deterministic seeded behavior for reproducibility tests.
    """

    def __init__(self, config: ScenarioConfig) -> None:
        self._config = config
        self._rng = np.random.default_rng(config.run.seed)
        self._mobility = build_mobility_provider(config)
        self._channel = SimpleChannelModel(config)
        self._registry = PluginRegistry()
        register_builtin_strategies(self._registry)
        self._scheduler = self._registry.resolve(config.run.scheduler_strategy)

    def _config_fingerprint(self) -> str:
        payload = self._config.model_dump(mode="json")
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return sha256(serialized.encode("utf-8")).hexdigest()

    def run(self) -> RunArtifacts:
        steps = self._config.run.steps
        phases = list(self._config.run.frame_phases)
        phase_events: list[dict[str, Any]] = []
        n_vehicle = self._config.scale.max_vehicles

        utilization_samples = []
        trim_loss_samples = []
        blockage_samples = []
        latency_samples_ms = []
        throughput_samples = []
        per_step_vehicle_counts = []
        per_step_mean_speeds = []
        per_step_los_ratio = []
        band_pathloss: dict[float, list[float]] = {b: [] for b in self._config.radio.enabled_bands_ghz}
        band_sinr: dict[float, list[float]] = {b: [] for b in self._config.radio.enabled_bands_ghz}
        accepted_requests_samples: list[int] = []
        rejected_requests_samples: list[int] = []

        for step in range(steps):
            step_states = self._mobility.states_at_step(step)
            channel_snapshots = self._channel.evaluate_step(step_states)
            per_step_vehicle_counts.append(len(step_states))
            if step_states:
                per_step_mean_speeds.append(float(np.mean([s.speed_mps for s in step_states])))
            else:
                per_step_mean_speeds.append(0.0)

            if channel_snapshots:
                los_ratio = float(np.mean([1.0 if s.is_los else 0.0 for s in channel_snapshots]))
                per_step_los_ratio.append(los_ratio)
                for snapshot in channel_snapshots:
                    for band, pl in snapshot.pathloss_db_by_band.items():
                        band_pathloss[band].append(float(pl))
                    for band, sinr in snapshot.sinr_db_by_band.items():
                        band_sinr[band].append(float(sinr))
            else:
                per_step_los_ratio.append(0.0)

            for phase_idx, phase in enumerate(phases):
                timestamp_s = (step * len(phases) + phase_idx) * self._config.run.timestep_s
                phase_events.append(
                    {
                        "step": step,
                        "phase": phase,
                        "timestamp_s": float(timestamp_s),
                        "active_vehicles": len(step_states),
                        "los_ratio": per_step_los_ratio[-1],
                    }
                )
                if phase == "beacon":
                    blockage = float(1.0 - per_step_los_ratio[-1]) if channel_snapshots else 0.0
                    blockage_samples.append(blockage)
                elif phase == "beam_training":
                    _ = float(self._rng.uniform(0.03, 0.12))
                elif phase == "access_grant":
                    _ = float(self._rng.uniform(0.65, 0.98))
                else:
                    requests = []
                    for snapshot in channel_snapshots:
                        sinr_best = max(snapshot.sinr_db_by_band.values())
                        t_req = int(np.clip(6 - (sinr_best / 8.0), 1, 6))
                        f_req = int(np.clip(5 - (sinr_best / 10.0), 1, 5))
                        requests.append((t_req, f_req))
                    alloc = self._scheduler.allocate(
                        AllocationInput(
                            available_time_blocks=10,
                            available_freq_blocks=10,
                            requests=requests,
                            objective=self._config.run.scheduler_objective,
                        )
                    )
                    utilization = float(np.clip(alloc.utilization, 0.0, 1.0))
                    throughput = utilization * n_vehicle * 8.0
                    accepted_requests_samples.append(alloc.accepted_requests)
                    rejected_requests_samples.append(alloc.rejected_requests)
                    latency_ms = float(
                        1000.0
                        * (1.0 - utilization)
                        * self._config.run.timestep_s
                        * (1.0 + blockage_samples[-1])
                    )
                    utilization_samples.append(utilization)
                    trim_loss_samples.append(1.0 - utilization)
                    throughput_samples.append(throughput)
                    latency_samples_ms.append(latency_ms)

        utilization = np.array(utilization_samples, dtype=float)
        trim_loss = 1.0 - utilization
        throughput = np.array(throughput_samples, dtype=float)
        if throughput.size == 0:
            fairness_jain = 0.0
        else:
            fairness_jain = float((throughput.sum() ** 2) / (throughput.size * (throughput**2).sum()))

        phase_order_valid = True
        for step in range(steps):
            at_step = [e["phase"] for e in phase_events if e["step"] == step]
            if at_step != phases:
                phase_order_valid = False
                break

        return RunArtifacts(
            seed=self._config.run.seed,
            steps=steps,
            timestep_s=self._config.run.timestep_s,
            phases=phases,
            config_fingerprint=self._config_fingerprint(),
            phase_order_valid=phase_order_valid,
            mean_utilization=float(utilization.mean()),
            mean_trim_loss=float(trim_loss.mean()),
            mean_blockage_ratio=float(np.mean(blockage_samples) if blockage_samples else 0.0),
            mean_latency_ms=float(np.mean(latency_samples_ms) if latency_samples_ms else 0.0),
            fairness_jain=fairness_jain,
            mean_vehicle_speed_mps=float(np.mean(per_step_mean_speeds) if per_step_mean_speeds else 0.0),
            mean_vehicle_count_per_step=float(
                np.mean(per_step_vehicle_counts) if per_step_vehicle_counts else 0.0
            ),
            mean_los_ratio=float(np.mean(per_step_los_ratio) if per_step_los_ratio else 0.0),
            mean_pathloss_db_by_band={
                band: float(np.mean(values)) if values else 0.0 for band, values in band_pathloss.items()
            },
            mean_sinr_db_by_band={
                band: float(np.mean(values)) if values else 0.0 for band, values in band_sinr.items()
            },
            scheduler_strategy=self._config.run.scheduler_strategy,
            scheduler_objective=self._config.run.scheduler_objective,
            mean_accepted_requests=float(
                np.mean(accepted_requests_samples) if accepted_requests_samples else 0.0
            ),
            mean_rejected_requests=float(
                np.mean(rejected_requests_samples) if rejected_requests_samples else 0.0
            ),
            events=phase_events,
        )
