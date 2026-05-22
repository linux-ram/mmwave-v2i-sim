from __future__ import annotations

import pytest
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mmwave_v2i_sim.sim_engine.constants import PACK_PAD
from mmwave_v2i_sim.sim_engine.engine import SimSession
from mmwave_v2i_sim.sim_engine.trim_plot import TrimPlotSeries, draw_trim_trend_panel
from mmwave_v2i_sim.sim_engine.visualize import draw_figure1_map, draw_figure2_packing


def _session(n_vehicle: int = 5, seed: int = 99, algo: str = "guillotine") -> tuple:
    session = SimSession(n_vehicle=n_vehicle, seed=seed, packing_algorithm=algo)
    snap = session.reset()
    return session, snap


def test_visual_smoke_renders_without_error() -> None:
    _, snap = _session()
    fig1, ax1 = plt.subplots()
    fig2 = plt.figure()
    ax_pack = fig2.add_subplot(4, 1, (1, 3))
    ax_text = fig2.add_subplot(4, 1, 4)
    draw_figure1_map(ax1, snap)
    draw_figure2_packing(ax_pack, ax_text, snap)
    plt.close(fig1)
    plt.close(fig2)


def test_packing_axes_use_symmetric_padding() -> None:
    _, snap = _session()
    fig, ax = plt.subplots()
    ax_text_fig, ax_text = plt.subplots()
    draw_figure2_packing(ax, ax_text, snap)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    assert xlim[0] == pytest.approx(-PACK_PAD)
    assert xlim[1] == pytest.approx(1.0 + PACK_PAD)
    assert ylim[0] == pytest.approx(-PACK_PAD)
    assert ylim[1] == pytest.approx(1.0 + PACK_PAD)
    plt.close(fig)
    plt.close(ax_text_fig)


def test_map_has_single_aerial_layer() -> None:
    _, snap = _session(n_vehicle=10)
    fig, ax = plt.subplots()
    draw_figure1_map(ax, snap)
    images = ax.images
    assert len(images) == 1, "Expected aerial image only (no heatmap overlay)"
    plt.close(fig)


def test_trim_trend_panel_renders() -> None:
    session = SimSession(n_vehicle=5, seed=42)
    session.reset()
    for _ in range(3):
        session.step()
    fig, ax = plt.subplots()
    series = [TrimPlotSeries(n_vehicle=5, algorithm="guillotine", runs=[list(session.trim_history)])]
    draw_trim_trend_panel(ax, series)
    plt.close(fig)


def test_trim_plot_uses_verbose_legend() -> None:
    fig, ax = plt.subplots()
    series = [
        TrimPlotSeries(n_vehicle=10, algorithm="guillotine", los_thresh=0.5,
                       runs=[[0.1, 0.2, 0.3], [0.15, 0.25, 0.35]]),
    ]
    draw_trim_trend_panel(ax, series)
    legend = ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert any("vehicles" in t and "packing" in t for t in texts), texts
    assert any("LoS threshold" in t for t in texts), texts
    plt.close(fig)


def test_trim_plot_los_thresh_in_legend_label() -> None:
    fig, ax = plt.subplots()
    series = [
        TrimPlotSeries(n_vehicle=5, algorithm="shelf", los_thresh=0.7,
                       runs=[[0.2, 0.3]]),
    ]
    draw_trim_trend_panel(ax, series)
    legend = ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert any("0.7" in t for t in texts), texts
    plt.close(fig)


def test_trim_plot_error_bars_only_at_5_runs() -> None:
    from mmwave_v2i_sim.sim_engine.trim_plot import _ERRORBAR_MIN_RUNS

    assert _ERRORBAR_MIN_RUNS == 5
    run_data = [[0.1 * (i + 1) * j / 10 for j in range(1, 6)] for i in range(4)]

    fig, ax = plt.subplots()
    series = [TrimPlotSeries(n_vehicle=5, algorithm="guillotine", runs=run_data)]
    draw_trim_trend_panel(ax, series)
    containers = ax.containers
    assert len(containers) == 0, "No error bars expected for 4 runs"
    plt.close(fig)

    fig2, ax2 = plt.subplots()
    run_data_5 = run_data + [[0.05, 0.1, 0.15, 0.2, 0.25]]
    series5 = [TrimPlotSeries(n_vehicle=5, algorithm="guillotine", runs=run_data_5)]
    draw_trim_trend_panel(ax2, series5)
    containers5 = ax2.containers
    assert len(containers5) >= 1, "Error bars expected for 5 runs"
    plt.close(fig2)


def test_trim_plot_individual_runs_plus_mean() -> None:
    fig, ax = plt.subplots()
    runs = [[0.1, 0.2, 0.3], [0.12, 0.22, 0.32], [0.08, 0.18, 0.28]]
    series = [TrimPlotSeries(n_vehicle=10, algorithm="guillotine", runs=runs)]
    draw_trim_trend_panel(ax, series)
    # 3 faint individual run lines should be present (plus optional mean line)
    plain_lines = [ln for ln in ax.get_lines() if ln.get_alpha() is not None and ln.get_alpha() < 0.6]
    assert len(plain_lines) >= 3
    plt.close(fig)


def test_vehicle_color_categories_in_legend() -> None:
    _, snap = _session(n_vehicle=10)
    fig, ax = plt.subplots()
    draw_figure1_map(ax, snap)
    legend = ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert any("RSB packed" in t for t in texts)
    assert any("RSB dropped" in t for t in texts)
    assert any("line-of-sight" in t.lower() for t in texts)
    plt.close(fig)


def test_active_segment_route_draw() -> None:
    _, snap = _session()
    fig, ax = plt.subplots()
    draw_figure1_map(ax, snap, route_display="active_segment")
    plt.close(fig)


def test_full_route_draw() -> None:
    _, snap = _session()
    fig, ax = plt.subplots()
    draw_figure1_map(ax, snap, route_display="full")
    plt.close(fig)


def test_route_off_draw() -> None:
    _, snap = _session()
    fig, ax = plt.subplots()
    draw_figure1_map(ax, snap, route_display="off")
    plt.close(fig)


def test_shelf_algo_renders() -> None:
    _, snap = _session(algo="shelf")
    fig = plt.figure()
    ax_pack = fig.add_subplot(2, 1, 1)
    ax_text = fig.add_subplot(2, 1, 2)
    draw_figure2_packing(ax_pack, ax_text, snap)
    plt.close(fig)


def test_max_rects_algo_renders() -> None:
    _, snap = _session(algo="max_rects")
    fig = plt.figure()
    ax_pack = fig.add_subplot(2, 1, 1)
    ax_text = fig.add_subplot(2, 1, 2)
    draw_figure2_packing(ax_pack, ax_text, snap)
    plt.close(fig)
