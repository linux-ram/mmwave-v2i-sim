"""Session-persistent trim-loss trend plots (Figure 3 style, B&W)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

_LINE_STYLES = ["-", "--", "-.", ":"]
# Distinct filled markers per series (triangle, circle, diamond, square, …).
_MARKERS = ["^", "o", "D", "s", "v", "p", "h", "8"]
_LINE_GRAY = ["#333333", "#555555", "#777777", "#999999"]
_FAINT_RUN_GRAY = "#bbbbbb"
_ERRORBAR_MIN_RUNS = 5


@dataclass
class TrimPlotSeries:
    n_vehicle: int
    algorithm: str
    los_thresh: float = 0.5
    runs: list[list[float]] = field(default_factory=list)


def style_for_series_index(idx: int) -> tuple[str, str]:
    """Stable (line_style, marker) for a series index."""
    ls = _LINE_STYLES[idx % len(_LINE_STYLES)]
    mk = _MARKERS[idx % len(_MARKERS)]
    return ls, mk


def draw_trim_trend_panel(
    ax: object,
    series_list: list[TrimPlotSeries],
    series_styles: dict[tuple[int, str, float], tuple[str, str]] | None = None,
) -> None:
    """Draw trim loss (%) vs simulation step for all completed runs.

    Rendering rules per series:
      - 1 run      -> dashed line + dot markers per step.
      - 2-4 runs   -> faint gray runs + thin gray mean (no error bars).
      - 5+ runs    -> faint gray runs + thin gray mean + thin error bars.
    """
    ax.clear()  # type: ignore[union-attr]
    ax.set_title(  # type: ignore[union-attr]
        "Trim Loss vs Step  (% of resource block area unused per step)",
        fontsize=10, fontweight="bold",
    )
    ax.set_xlabel("Simulation Step", fontsize=9, fontweight="bold")  # type: ignore[union-attr]
    ax.set_ylabel("Trim Loss (%)", fontsize=9, fontweight="bold")  # type: ignore[union-attr]
    ax.tick_params(labelsize=9)  # type: ignore[union-attr]
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():  # type: ignore[union-attr]
        lbl.set_fontweight("bold")
    ax.grid(True, alpha=0.25, color="grey")  # type: ignore[union-attr]

    has_data = any(s.runs for s in series_list)
    if not has_data:
        ax.text(  # type: ignore[union-attr]
            0.5, 0.5, "Complete a run to plot trim loss",
            ha="center", va="center", transform=ax.transAxes,  # type: ignore[union-attr]
            color="grey", fontsize=9,
        )
        return

    legend_handles: list = []
    legend_labels: list[str] = []

    for si, series in enumerate(series_list):
        if not series.runs:
            continue

        key: tuple[int, str, float] = (series.n_vehicle, series.algorithm, series.los_thresh)
        if series_styles is not None and key in series_styles:
            ls, mk = series_styles[key]
        else:
            ls, mk = style_for_series_index(si)

        label = (
            f"({series.n_vehicle} vehicles, "
            f"LoS threshold = {series.los_thresh:.1f}, "
            f"{series.algorithm} packing)"
        )

        n_runs = len(series.runs)

        color = _LINE_GRAY[si % len(_LINE_GRAY)]

        if n_runs == 1:
            y = np.array(series.runs[0]) * 100.0
            x = np.arange(1, len(y) + 1)
            line, = ax.plot(  # type: ignore[union-attr]
                x, y, linestyle=ls, marker=mk, color=color,
                markersize=5, markerfacecolor=color, markeredgecolor=color,
                linewidth=0.6, label=label,
            )
            legend_handles.append(line)
            legend_labels.append(label)
        else:
            min_len = min(len(r) for r in series.runs)
            arr = np.array([r[:min_len] for r in series.runs]) * 100.0
            x = np.arange(1, min_len + 1)

            for run in arr:
                ax.plot(  # type: ignore[union-attr]
                    x, run, linestyle="--", color=_FAINT_RUN_GRAY,
                    linewidth=0.5, alpha=0.45,
                )

            mean = arr.mean(axis=0)
            std = arr.std(axis=0)

            if n_runs >= _ERRORBAR_MIN_RUNS:
                container = ax.errorbar(  # type: ignore[union-attr]
                    x, mean, yerr=std, fmt="", linestyle=ls, marker=mk, color=color,
                    markersize=5, markerfacecolor=color, markeredgecolor=color,
                    linewidth=0.6, elinewidth=0.6, ecolor=color,
                    capsize=1, capthick=0.6,
                    label=label,
                )
                legend_handles.append(container)
            else:
                line, = ax.plot(  # type: ignore[union-attr]
                    x, mean, linestyle=ls, marker=mk, color=color,
                    markersize=5, markerfacecolor=color, markeredgecolor=color,
                    linewidth=0.6, label=label,
                )
                legend_handles.append(line)
            legend_labels.append(label)

    if legend_handles:
        ax.legend(legend_handles, legend_labels, fontsize=7, loc="upper right")  # type: ignore[union-attr]
