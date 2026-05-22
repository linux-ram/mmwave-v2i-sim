from __future__ import annotations

import json
from pathlib import Path

from mmwave_v2i_sim.analysis.validation import build_report, write_report
from mmwave_v2i_sim.config.schema import load_scenario_config


def test_build_report_passes_sanity_checks() -> None:
    cfg = load_scenario_config(Path("configs/scenario_legacy_research.yaml"))
    report = build_report(cfg)
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
