from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_cli(*extra: str, output: Path) -> dict[str, object]:
    cmd = [
        sys.executable,
        "-m",
        "mmwave_v2i_sim.cli",
        "--config",
        "configs/scenario_default.yaml",
        "--output",
        str(output),
        *extra,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(output.read_text(encoding="utf-8"))


def test_headless_sim_engine_export(tmp_path: Path) -> None:
    out = tmp_path / "run_summary.json"
    artifact = _run_cli(output=out)
    assert artifact["engine"] == "sim_engine"
    assert artifact["n_vehicle"] == 10
    assert artifact["steps_run"] >= 1
    assert "trim_history" in artifact
    assert isinstance(artifact["trim_history"], list)


def test_headless_sim_engine_is_deterministic(tmp_path: Path) -> None:
    a = _run_cli(output=tmp_path / "a.json")
    b = _run_cli(output=tmp_path / "b.json")
    assert a == b


def test_batch_density_sweep_export(tmp_path: Path) -> None:
    out = tmp_path / "batch.json"
    artifact = _run_cli("--batch", output=out)
    assert artifact["engine"] == "sim_engine"
    assert artifact["n_vehicle"] == [1, 2, 5, 10, 50]
    assert len(artifact["mean_trim_loss"]) == 5
    assert len(artifact["std_trim_loss"]) == 5
