from __future__ import annotations

import json
from pathlib import Path

from mmwave_v2i_sim.analysis.validation import (
    build_legacy_report,
    build_report,
    build_sim_engine_report,
    write_report,
)
from mmwave_v2i_sim.config.schema import load_scenario_config


def test_sim_engine_report_passes_checks() -> None:
    report = build_sim_engine_report(num_trials=2, seed=42)
    assert report["checks"]["trim_loss_in_valid_range"] is True
    assert len(report["comparison"]) == 5
    assert report["checks"]["nonzero_trim_at_n50"] is True


def test_build_report_primary_passes() -> None:
    cfg = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    report = build_report(cfg, sim_trials=2, sim_seed=42)
    assert report["summary"]["all_checks_pass"] is True
    assert report["sim_engine"]["engine"] == "sim_engine"


def test_legacy_report_sanity() -> None:
    cfg = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    report = build_legacy_report(cfg)
    assert report["checks"]["trim_loss_in_valid_range"] is True
    assert len(report["comparison"]) == 5


def test_write_report_is_reproducible() -> None:
    cfg_path = Path("configs/scenario_legacy_research.yaml")
    out = Path("artifacts/validation_test")
    p1 = write_report(cfg_path, out)
    with p1.open(encoding="utf-8") as f:
        first = json.load(f)
    p2 = write_report(cfg_path, out)
    with p2.open(encoding="utf-8") as f:
        second = json.load(f)
    assert first == second
