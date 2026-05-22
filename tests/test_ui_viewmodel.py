from __future__ import annotations

from pathlib import Path

from mmwave_v2i_sim.config.schema import load_scenario_config
from mmwave_v2i_sim.core.engine import SimulationEngine
from mmwave_v2i_sim.ui.viewmodel import build_kpi_rows, build_step_kpi_rows


def test_build_kpi_rows_contains_expected_keys() -> None:
    cfg = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    artifact = SimulationEngine(cfg).run().to_dict()
    rows = build_kpi_rows(artifact)
    keys = [k for k, _ in rows]
    assert "mean_utilization" in keys
    assert "mean_los_ratio" in keys
    assert "scheduler_strategy" in keys


def test_build_step_kpi_rows_has_step_fields() -> None:
    rows = build_step_kpi_rows({"step": 3, "trim_loss": 0.1, "utilization": 0.9})
    keys = [k for k, _ in rows]
    assert "step" in keys
    assert "trim_loss" in keys
