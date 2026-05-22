from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np

from mmwave_v2i_sim.sim_engine.engine import SimSession
from mmwave_v2i_sim.sim_engine.session_export import (
    build_workspace,
    load_workspace_npz,
    save_workspace_npz,
    save_workspace_zip,
    snapshot_to_dict,
)
from mmwave_v2i_sim.sim_engine.trim_plot import TrimPlotSeries


def test_snapshot_to_dict_has_trim_loss(tmp_path: Path) -> None:
    session = SimSession(n_vehicle=5, seed=1)
    snap = session.reset()
    d = snapshot_to_dict(snap)
    assert "trim_loss" in d
    assert "vehicles" in d
    assert d["n_vehicle"] == 5


def test_save_workspace_npz_roundtrip(tmp_path: Path) -> None:
    session = SimSession(n_vehicle=5, seed=1)
    snap = session.reset()
    logs = [[snapshot_to_dict(snap)]]
    ws = build_workspace(
        n_vehicle=5,
        packing_algorithm="guillotine",
        p_los_thresh=0.5,
        route_display="full",
        n_runs_target=1,
        base_seed=1,
        trim_series=[TrimPlotSeries(n_vehicle=5, algorithm="guillotine", runs=[[0.1, 0.2]])],
        completed_run_logs=logs,
    )
    out = tmp_path / "session.npz"
    save_workspace_npz(out, ws)
    data = load_workspace_npz(out)
    assert data["n_vehicle"] == 5
    assert data["n_completed_runs"] == 1


def test_save_workspace_zip_structure(tmp_path: Path) -> None:
    session = SimSession(n_vehicle=5, seed=1)
    snap = session.reset()
    logs = [[snapshot_to_dict(snap)]]
    ws = build_workspace(
        n_vehicle=5,
        packing_algorithm="guillotine",
        p_los_thresh=0.5,
        route_display="full",
        n_runs_target=1,
        base_seed=1,
        trim_series=[TrimPlotSeries(n_vehicle=5, algorithm="guillotine", runs=[[0.1, 0.2]])],
        completed_run_logs=logs,
    )
    out = tmp_path / "session.zip"
    save_workspace_zip(out, ws)

    with zipfile.ZipFile(out, "r") as zf:
        names = set(zf.namelist())
        assert "README.txt" in names
        assert "manifest.json" in names
        assert "trim_series.json" in names
        assert "trim_loss_steps.csv" in names
        assert "runs/run_001/steps.jsonl" in names
        assert "session.npz" in names
        manifest = json.loads(zf.read("manifest.json"))
        assert manifest["n_vehicle"] == 5
        assert manifest["format_version"] == 1
        lines = zf.read("runs/run_001/steps.jsonl").decode().strip().splitlines()
        assert len(lines) == 1
        step = json.loads(lines[0])
        assert "trim_loss" in step
        assert isinstance(step["vehicles"], list)

    data = load_workspace_npz(out)
    assert data["n_completed_runs"] == 1
