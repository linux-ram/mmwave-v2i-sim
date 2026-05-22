"""UI view-model helpers kept independent from GUI toolkit imports."""

from __future__ import annotations

from typing import Any


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def build_step_kpi_rows(kpis: dict[str, Any]) -> list[tuple[str, str]]:
    keys = [
        "step",
        "phase",
        "time_elapsed_s",
        "scheduler_strategy",
        "scheduler_objective",
        "utilization",
        "trim_loss",
        "los_ratio",
        "accepted_requests",
        "rejected_requests",
        "active_vehicles",
    ]
    return [(k, _fmt(kpis.get(k, "n/a"))) for k in keys]


def build_kpi_rows(artifact: dict[str, Any]) -> list[tuple[str, str]]:
    keys = [
        "scheduler_strategy",
        "scheduler_objective",
        "mean_utilization",
        "mean_trim_loss",
        "mean_latency_ms",
        "mean_los_ratio",
        "mean_accepted_requests",
        "mean_rejected_requests",
        "fairness_jain",
        "mean_vehicle_count_per_step",
        "mean_vehicle_speed_mps",
    ]
    return [(k, _fmt(artifact.get(k, "n/a"))) for k in keys]
