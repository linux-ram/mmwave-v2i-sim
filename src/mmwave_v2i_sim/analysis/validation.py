"""Validation and MATLAB-adjacent comparison reporting."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from mmwave_v2i_sim.config.schema import ScenarioConfig, load_scenario_config
from mmwave_v2i_sim.core.session import SimulationSession
from mmwave_v2i_sim.sim_engine.batch import run_density_sweep as sim_engine_density_sweep


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
    """Illustrative monotonic trend proxy — NOT measured MATLAB output.

    Use for qualitative comparison in legacy-engine reports only.
    For strict parity, run ``python -m mmwave_v2i_sim.cli --batch``.
    """
    ref = {}
    for i, n in enumerate(sorted(vehicle_counts)):
        ref[n] = 0.15 + 0.012 * i + 0.002 * n
    return ref


def _soft_monotonic_trim(comparison: list[dict[str, Any]], key: str, slack: float = 0.05) -> bool:
    if len(comparison) < 2:
        return True
    vals = [row[key] for row in comparison]
    return all(vals[i] <= vals[i + 1] + slack for i in range(len(vals) - 1))


def build_sim_engine_report(num_trials: int = 3, seed: int = 12345) -> dict[str, Any]:
    """Validation on primary MATLAB-parity engine (default GUI/CLI path)."""
    result = sim_engine_density_sweep(num_trials=num_trials, seed=seed)
    comparison = [
        {
            "vehicles": n,
            "trim_loss_mean": float(result.mean_trim_loss[i]),
            "trim_loss_std": float(result.std_trim_loss[i]),
        }
        for i, n in enumerate(result.n_vehicle)
    ]
    trim_vals = [c["trim_loss_mean"] for c in comparison]
    spread = (max(trim_vals) - min(trim_vals)) if trim_vals else 0.0
    checks = {
        "trim_loss_in_valid_range": all(0.0 <= v <= 1.0 for v in trim_vals),
        "trim_loss_varies_with_density": spread > 0.05,
        "nonzero_trim_at_n50": trim_vals[-1] > 0.0 if trim_vals else False,
    }
    return {
        "engine": "sim_engine",
        "num_trials": num_trials,
        "seed": seed,
        "comparison": comparison,
        "checks": checks,
        "metrics": {"trim_loss_spread": spread},
        "caveats": [
            "Primary validation path for v0.1 release.",
            "Matches GUI density options and `cli --batch`.",
            "Trim loss may decrease with vehicle count (differs from illustrative MATLAB proxy).",
            "MATLAB numeric parity requires side-by-side runs of the original repo.",
        ],
    }


def build_legacy_report(base_config: ScenarioConfig) -> dict[str, Any]:
    """Legacy research-engine sweep with illustrative MATLAB proxy."""
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
                "trim_loss_matlab_proxy": ref_val,
                "delta_vs_proxy": row.mean_trim_loss - ref_val,
                "utilization": row.mean_utilization,
                "los_ratio": row.mean_los_ratio,
            }
        )
    checks = {
        "trim_loss_in_valid_range": all(0.0 <= c["trim_loss_python"] <= 1.0 for c in comparison),
        "trim_loss_trend_monotonic_soft": _soft_monotonic_trim(
            comparison, "trim_loss_python"
        ),
    }
    return {
        "engine": "legacy_core",
        "config_fingerprint_fields": {
            "seed": base_config.run.seed,
            "scheduler": base_config.run.scheduler_strategy,
        },
        "comparison": comparison,
        "checks": checks,
        "caveats": [
            "Uses configs/scenario_legacy_research.yaml research engine.",
            "trim_loss_matlab_proxy is an illustrative trend, not File Exchange output.",
        ],
    }


def build_report(
    base_config: ScenarioConfig | None = None,
    *,
    include_legacy: bool = True,
    sim_trials: int = 3,
    sim_seed: int = 12345,
) -> dict[str, Any]:
    sim_report = build_sim_engine_report(num_trials=sim_trials, seed=sim_seed)
    legacy_report = None
    if include_legacy and base_config is not None:
        legacy_report = build_legacy_report(base_config)

    sim_checks_pass = all(sim_report["checks"].values())
    legacy_checks_pass = None
    if legacy_report is not None:
        legacy_checks_pass = all(legacy_report["checks"].values())

    return {
        "sim_engine": sim_report,
        "legacy": legacy_report,
        "summary": {
            "sim_engine_checks_pass": sim_checks_pass,
            "legacy_checks_pass": legacy_checks_pass,
            "all_checks_pass": sim_checks_pass,
            "primary_engine": "sim_engine",
        },
        "caveats": [
            "v0.1 release gates on sim_engine checks; legacy block is informational.",
            "Original MATLAB repo: https://github.com/linux-ram/mmWave-V2I-2DRBP",
        ],
    }


def write_report(
    base_config_path: Path | None,
    output_dir: Path,
    *,
    include_legacy: bool = True,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg = None
    if include_legacy and base_config_path is not None:
        cfg = load_scenario_config(base_config_path)
    report = build_report(cfg, include_legacy=include_legacy and cfg is not None)
    out = output_dir / "validation_report.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    md = output_dir / "validation_report.md"
    lines = ["# Validation Report", ""]
    lines.append("## sim_engine (primary, MATLAB parity)")
    lines.append("")
    lines.append("| Vehicles | Trim mean | Trim std |")
    lines.append("|---:|---:|---:|")
    for row in report["sim_engine"]["comparison"]:
        lines.append(
            f"| {row['vehicles']} | {row['trim_loss_mean']:.4f} | {row['trim_loss_std']:.4f} |"
        )
    lines.extend(["", "### Checks", ""])
    for k, v in report["sim_engine"]["checks"].items():
        lines.append(f"- {k}: {v}")

    if report.get("legacy"):
        lines.extend(["", "## legacy core (research engine)", ""])
        lines.append("| Vehicles | Trim (Python) | Trim (proxy) | Delta |")
        lines.append("|---:|---:|---:|---:|")
        for row in report["legacy"]["comparison"]:
            lines.append(
                f"| {row['vehicles']} | {row['trim_loss_python']:.4f} | "
                f"{row['trim_loss_matlab_proxy']:.4f} | {row['delta_vs_proxy']:.4f} |"
            )
        lines.extend(["", "### Checks", ""])
        for k, v in report["legacy"]["checks"].items():
            lines.append(f"- {k}: {v}")

    lines.extend(["", "## Summary", ""])
    lines.append(f"- sim_engine_checks_pass: {report['summary']['sim_engine_checks_pass']}")
    if report["summary"].get("legacy_checks_pass") is not None:
        lines.append(f"- legacy_checks_pass: {report['summary']['legacy_checks_pass']}")
    lines.append(f"- all_checks_pass (v0.1 gate): {report['summary']['all_checks_pass']}")
    lines.extend(["", "## Caveats", ""])
    for c in report["caveats"]:
        lines.append(f"- {c}")
    if report.get("legacy"):
        for c in report["legacy"]["caveats"]:
            lines.append(f"- {c}")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
