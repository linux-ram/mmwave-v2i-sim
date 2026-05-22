"""Export GUI session state to a NumPy .npz workspace archive."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from mmwave_v2i_sim.sim_engine.engine import StepSnapshot
from mmwave_v2i_sim.sim_engine.trim_plot import TrimPlotSeries


def snapshot_to_dict(snap: StepSnapshot) -> dict[str, Any]:
    """Serialize one simulation step for workspace export."""
    return {
        "i_num": snap.i_num,
        "n_vehicle": snap.n_vehicle,
        "base_station_position": snap.base_station_position.copy(),
        "rb": np.array(snap.rb),
        "packing_algorithm": snap.packing_algorithm,
        "trim_loss": snap.packing.trim_loss,
        "trim_loss_pct": snap.packing.trim_loss * 100.0,
        "n_rsb_left_unpacked": snap.packing.n_rsb_left_unpacked,
        "ind_rsb_left_unpacked": list(snap.packing.ind_rsb_left_unpacked),
        "packing_data": snap.packing.data.copy() if snap.packing.data.size else snap.packing.data,
        "rsb_items": np.array(snap.rsb_items) if snap.rsb_items else np.empty((0, 2)),
        "vehicles": [
            {
                "vehicle_id": v.vehicle_id,
                "position": v.position.copy(),
                "link_state": v.link_state,
                "theta": v.theta,
                "phi": v.phi,
                "rsb": np.array(v.rsb),
            }
            for v in snap.vehicles
        ],
    }


def trim_series_to_dict(series_list: list[TrimPlotSeries]) -> dict[str, Any]:
    return {
        "series": [
            {
                "n_vehicle": s.n_vehicle,
                "algorithm": s.algorithm,
                "los_thresh": s.los_thresh,
                "runs": [list(r) for r in s.runs],
            }
            for s in series_list
        ],
    }


def build_workspace(
    *,
    n_vehicle: int,
    packing_algorithm: str,
    p_los_thresh: float,
    route_display: str,
    n_runs_target: int,
    base_seed: int,
    trim_series: list[TrimPlotSeries],
    completed_run_logs: list[list[dict[str, Any]]],
    current_session_trim: list[float] | None = None,
) -> dict[str, Any]:
    """Build a dict mirroring key MATLAB workspace variables for this session."""
    all_trim: list[list[float]] = []
    for s in trim_series:
        all_trim.extend(s.runs)
    if current_session_trim:
        all_trim.append(list(current_session_trim))

    return {
        "n_vehicle": n_vehicle,
        "packing_algorithm": packing_algorithm,
        "p_los_thresh": p_los_thresh,
        "route_display": route_display,
        "n_runs_target": n_runs_target,
        "base_seed": base_seed,
        "trim_series": trim_series_to_dict(trim_series),
        "all_trim_loss_runs": all_trim,
        "completed_run_step_logs": completed_run_logs,
        "n_completed_runs": len(completed_run_logs),
    }


def save_workspace_npz(path: Path, workspace: dict[str, Any]) -> None:
    """Save workspace dict as compressed .npz (allow_pickle for nested structures)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, workspace=np.array(workspace, dtype=object))
