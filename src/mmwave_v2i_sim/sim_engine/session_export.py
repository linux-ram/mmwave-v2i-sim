"""Export GUI session state to a portable ZIP bundle (JSON/CSV + optional .npz)."""

from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path
from typing import Any

import numpy as np

from mmwave_v2i_sim.sim_engine.engine import StepSnapshot
from mmwave_v2i_sim.sim_engine.trim_plot import TrimPlotSeries

README_TXT = """mmWave V2I Simulator — session export
=====================================

This ZIP archive contains simulation session data in open, tool-friendly formats.

Files
-----
manifest.json       Session parameters and export metadata
trim_series.json    Trim-loss histories grouped by (n_vehicle, algorithm, LoS)
trim_loss_steps.csv Per-step trim loss for each completed run
runs/run_NNN/       One folder per completed simulation run
  steps.jsonl       One JSON object per line (timestep snapshot)
session.npz         Full Python workspace (NumPy); optional reload path

Python quick load (human-readable files)
----------------------------------------
import json, zipfile
with zipfile.ZipFile("mmwave_sim_session.zip") as zf:
    manifest = json.loads(zf.read("manifest.json"))

Python full workspace (same as legacy .npz export)
--------------------------------------------------
import numpy as np
data = np.load("session.npz", allow_pickle=True)["workspace"].item()

MATLAB / Excel
--------------
Open trim_loss_steps.csv in Excel or read with readtable() in MATLAB.
Read steps.jsonl line-by-line for per-step vehicle and packing fields.
"""


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


def to_jsonable(obj: Any) -> Any:
    """Convert numpy scalars/arrays to JSON-serializable Python types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    return obj


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


def _trim_steps_csv_rows(
    completed_run_logs: list[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_idx, run_steps in enumerate(completed_run_logs):
        for step_idx, step in enumerate(run_steps):
            rows.append(
                {
                    "run_index": run_idx,
                    "step_index": step_idx,
                    "i_num": step.get("i_num", step_idx),
                    "trim_loss": float(step.get("trim_loss", 0.0)),
                    "trim_loss_pct": float(step.get("trim_loss_pct", 0.0)),
                    "n_rsb_left_unpacked": int(step.get("n_rsb_left_unpacked", 0)),
                }
            )
    return rows


def _write_trim_steps_csv(rows: list[dict[str, Any]]) -> str:
    buf = io.StringIO()
    if not rows:
        writer = csv.writer(buf)
        writer.writerow(
            ["run_index", "step_index", "i_num", "trim_loss", "trim_loss_pct", "n_rsb_left_unpacked"]
        )
        return buf.getvalue()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def save_workspace_zip(path: Path, workspace: dict[str, Any]) -> None:
    """Save session as a ZIP bundle: README, JSON, CSV, per-run JSONL, and session.npz."""
    path.parent.mkdir(parents=True, exist_ok=True)
    completed = workspace.get("completed_run_step_logs") or []

    manifest = {
        "format_version": 1,
        "export_type": "mmwave_v2i_sim_session",
        "n_vehicle": workspace["n_vehicle"],
        "packing_algorithm": workspace["packing_algorithm"],
        "p_los_thresh": workspace["p_los_thresh"],
        "route_display": workspace["route_display"],
        "n_runs_target": workspace["n_runs_target"],
        "base_seed": workspace["base_seed"],
        "n_completed_runs": workspace["n_completed_runs"],
        "contents": [
            "README.txt",
            "manifest.json",
            "trim_series.json",
            "trim_loss_steps.csv",
            "runs/run_NNN/steps.jsonl",
            "session.npz",
        ],
    }

    trim_rows = _trim_steps_csv_rows(completed)

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", README_TXT)
        zf.writestr("manifest.json", json.dumps(to_jsonable(manifest), indent=2) + "\n")
        zf.writestr(
            "trim_series.json",
            json.dumps(to_jsonable(workspace.get("trim_series", {})), indent=2) + "\n",
        )
        zf.writestr("trim_loss_steps.csv", _write_trim_steps_csv(trim_rows))

        for run_idx, run_steps in enumerate(completed):
            run_dir = f"runs/run_{run_idx + 1:03d}"
            lines = [json.dumps(to_jsonable(step)) for step in run_steps]
            zf.writestr(f"{run_dir}/steps.jsonl", "\n".join(lines) + ("\n" if lines else ""))
            zf.writestr(
                f"{run_dir}/manifest.json",
                json.dumps(
                    to_jsonable(
                        {
                            "run_index": run_idx,
                            "n_steps": len(run_steps),
                        }
                    ),
                    indent=2,
                )
                + "\n",
            )

        npz_buf = io.BytesIO()
        np.savez_compressed(npz_buf, workspace=np.array(workspace, dtype=object))
        zf.writestr("session.npz", npz_buf.getvalue())


def load_workspace_npz(path: Path) -> dict[str, Any]:
    """Load workspace from a standalone .npz or from ``session.npz`` inside a ZIP."""
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path, "r") as zf:
            if "session.npz" not in zf.namelist():
                raise ValueError("ZIP archive missing session.npz")
            data = zf.read("session.npz")
        loaded = np.load(io.BytesIO(data), allow_pickle=True)
    else:
        loaded = np.load(path, allow_pickle=True)
    return loaded["workspace"].item()
