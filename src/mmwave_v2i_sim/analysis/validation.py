"""Validation and MATLAB-adjacent comparison reporting."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from mmwave_v2i_sim.config.schema import ScenarioConfig, load_scenario_config
from mmwave_v2i_sim.core.session import SimulationSession


@dataclass(frozen=True)
class DensitySweepResult:
    vehicle_count: int
    mean_trim_loss: float
    mean_utilization: float
    mean_los_ratio: float
    steps: int


def run_density_sweep(
    base_config: ScenarioConfig,
    vehicle_counts: list[int],
    steps: int = 20,
    trials: int = 3,
) -> list[DensitySweepResult]:
    rows: list[DensitySweepResult] = []
    for n in vehicle_counts:
        trial_trim: list[float] = []
        trial_util: list[float] = []
        trial_los: list[float] = []
        for t in range(trials):
            cfg = base_config.model_copy(deep=True)
            cfg.scale.max_vehicles = n
            cfg.run.steps = steps
            cfg.run.seed = base_config.run.seed + t
            session = SimulationSession(cfg)
            snap = session.reset()
            los_vals = [snap.los_ratio]
            for _ in range(steps - 1):
                nxt = session.step()
                if nxt:
                    snap = nxt
                    los_vals.append(snap.los_ratio)
            trial_trim.append(float(np.mean(session.trim_history)))
            trial_util.append(float(np.mean(session.util_history)))
            trial_los.append(float(np.mean(los_vals)))
        rows.append(
            DensitySweepResult(
                vehicle_count=n,
                mean_trim_loss=float(np.mean(trial_trim)),
                mean_utilization=float(np.mean(trial_util)),
                mean_los_ratio=float(np.mean(trial_los)),
                steps=steps,
            )
        )
    return rows


def matlab_reference_trim_loss(vehicle_counts: list[int]) -> dict[int, float]:
    """Qualitative MATLAB-adjacent reference trend (original paper-style sweep)."""
    # Original MATLAB increased trim loss with vehicle density; use monotonic proxy.
    ref = {}
    for i, n in enumerate(sorted(vehicle_counts)):
        ref[n] = 0.15 + 0.012 * i + 0.002 * n
    return ref


def build_report(base_config: ScenarioConfig) -> dict[str, Any]:
    counts = [1, 2, 5, 10, 50]
    sweep = run_density_sweep(base_config, counts, steps=15, trials=3)
    ref = matlab_reference_trim_loss(counts)
    comparison = []
    for row in sweep:
        ref_val = ref[row.vehicle_count]
        comparison.append(
            {
                "vehicles": row.vehicle_count,
                "trim_loss_python": row.mean_trim_loss,
                "trim_loss_matlab_ref": ref_val,
                "delta": row.mean_trim_loss - ref_val,
                "utilization": row.mean_utilization,
                "los_ratio": row.mean_los_ratio,
            }
        )
    monotonic = all(
        comparison[i]["trim_loss_python"] <= comparison[i + 1]["trim_loss_python"] + 0.05
        for i in range(len(comparison) - 1)
    )
    return {
        "config_fingerprint_fields": {
            "seed": base_config.run.seed,
            "scheduler": base_config.run.scheduler_strategy,
        },
        "comparison": comparison,
        "checks": {
            "trim_loss_in_valid_range": all(0.0 <= c["trim_loss_python"] <= 1.0 for c in comparison),
            "trim_loss_trend_monotonic_soft": monotonic,
        },
        "caveats": [
            "Legacy validation path uses research engine unless configs/scenario_default.yaml is selected.",
            "MATLAB reference values are qualitative trend proxies for legacy mode.",
            "Use `python -m mmwave_v2i_sim.cli --batch` for strict MATLAB parity density sweep.",
        ],
    }


def write_report(base_config_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg = load_scenario_config(base_config_path)
    report = build_report(cfg)
    out = output_dir / "validation_report.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    md = output_dir / "validation_report.md"
    lines = ["# Validation Report", "", "## Density Sweep (MATLAB-adjacent)", ""]
    lines.append("| Vehicles | Trim (Python) | Trim (MATLAB ref) | Delta |")
    lines.append("|---:|---:|---:|---:|")
    for row in report["comparison"]:
        lines.append(
            f"| {row['vehicles']} | {row['trim_loss_python']:.4f} | "
            f"{row['trim_loss_matlab_ref']:.4f} | {row['delta']:.4f} |"
        )
    lines.extend(["", "## Checks", ""])
    for k, v in report["checks"].items():
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Caveats", ""])
    for c in report["caveats"]:
        lines.append(f"- {c}")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
