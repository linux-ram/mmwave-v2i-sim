"""MATLAB vehicleBinPackSimulation-style 2D rendering helpers."""

from __future__ import annotations

import math

import numpy as np
from matplotlib.patches import Rectangle
from matplotlib import cm

from mmwave_v2i_sim.core.session import StepSnapshot


def _arc_xy(cx: float, cy: float, r: float, a0: float, a1: float, n: int = 24) -> tuple[np.ndarray, np.ndarray]:
    angles = np.linspace(a0, a1, n)
    xs = cx + r * np.cos(angles)
    ys = cy + r * np.sin(angles)
    return xs, ys


def draw_matlab_scene(
    ax,
    snap: StepSnapshot,
    route_history: dict[int, list[tuple[float, float]]],
    bs_positions: list[tuple[float, float, float]],
    city_length: float,
    city_width: float,
    max_draw_vehicles: int = 80,
    max_route_points: int = 120,
) -> None:
    """Figure 1 style: city map, routes, beams, LoS links, vehicles."""
    ax.clear()
    ax.set_facecolor("#d8dce3")
    _draw_city_grid(ax, city_length, city_width)

    for bs in bs_positions:
        ax.plot(bs[0], bs[1], "ks", markersize=10)

    draw_ids: set[int]
    if len(snap.vehicles) <= max_draw_vehicles:
        draw_ids = {v.vehicle_id for v in snap.vehicles}
    else:
        stride = max(1, len(snap.vehicles) // max_draw_vehicles)
        draw_ids = {v.vehicle_id for i, v in enumerate(snap.vehicles) if i % stride == 0}
    for vid, route in route_history.items():
        if vid not in draw_ids or len(route) < 2:
            continue
        tail = route[-max_route_points:]
        xs, ys = zip(*tail)
        ax.plot(xs, ys, "-r", linewidth=1.5, alpha=0.7)

    pairs = [(v, ch) for v, ch in zip(snap.vehicles, snap.channel) if v.vehicle_id in draw_ids]
    for v, ch in pairs:
        if not ch.is_los:
            continue
        bs = bs_positions[ch.base_station_id]
        theta = math.atan2(v.y_m - bs[1], v.x_m - bs[0])
        beam_span = math.radians(15.0)
        bx, by = _arc_xy(bs[0], bs[1], 20.0, theta + math.pi - beam_span, theta + math.pi + beam_span)
        ax.plot(bx, by, "k-", linewidth=1)
        vx, vy = _arc_xy(v.x_m, v.y_m, 20.0, theta - beam_span, theta + beam_span)
        ax.plot(vx, vy, "k-", linewidth=1)
        ax.plot([v.x_m, bs[0]], [v.y_m, bs[1]], "-b", linewidth=1)
        ax.add_patch(Rectangle((v.x_m - 5, v.y_m - 5), 10, 10, facecolor="y", edgecolor="c", linewidth=1))

    shown = len(pairs)
    total = len(snap.vehicles)
    suffix = f" | Showing {shown}/{total} vehicles" if shown < total else ""
    ax.set_title(
        f"Time Elapsed = {snap.time_elapsed_s:.0f} seconds | Phase: {snap.phase}{suffix}",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("X Coordinate (in m)", fontweight="bold")
    ax.set_ylabel("Y Coordinate (in m)", fontweight="bold")
    ax.set_xlim(0, city_length)
    ax.set_ylim(0, city_width)
    ax.set_aspect("equal", adjustable="box")


def draw_packing_panel(ax, snap: StepSnapshot, t_blocks: int = 10, f_blocks: int = 10) -> None:
    """Figure 2 style: time-frequency resource bin packing."""
    ax.clear()
    ax.set_facecolor("#f7f7f7")
    ax.add_patch(Rectangle((0, 0), t_blocks, f_blocks, fill=False, edgecolor="k", linewidth=2))
    tab20 = cm.get_cmap("tab20")
    for i, (x, y, w, h) in enumerate(snap.packing_placed):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=tab20(i % 20), edgecolor="k", alpha=0.85))
    ax.set_title(f"Resource Packing | Trim Loss = {snap.trim_loss:.3f}", fontweight="bold")
    ax.set_xlabel("Time blocks")
    ax.set_ylabel("Frequency blocks")
    ax.set_xlim(0, t_blocks)
    ax.set_ylim(0, f_blocks)
    ax.set_aspect("equal", adjustable="box")


def draw_trim_trend(ax, trim_history: list[float]) -> None:
    """Figure 3 style: trim-loss trend with error-bar-like band."""
    ax.clear()
    if not trim_history:
        ax.set_title("Trim Loss Trend")
        return
    x = np.arange(1, len(trim_history) + 1)
    y = np.array(trim_history)
    sigma = float(np.std(y)) if len(y) > 1 else 0.0
    ax.errorbar(x, y, yerr=sigma, fmt="r-", linewidth=2, capsize=3)
    ax.plot(x, y, "ks", markersize=6)
    ax.set_title("Mean Time-Frequency Resource Utilization", fontweight="bold")
    ax.set_xlabel("Simulation Step")
    ax.set_ylabel("Trim Loss", fontweight="bold")
    ax.grid(True, alpha=0.3)


def _draw_city_grid(ax, length: float, width: float) -> None:
    """Synthetic aerial city section reminiscent of MATLAB CitySectionAerialView."""
    block_w, block_h = length / 8, width / 6
    for i in range(8):
        for j in range(6):
            if (i + j) % 2 == 0:
                ax.add_patch(
                    Rectangle(
                        (i * block_w, j * block_h),
                        block_w * 0.85,
                        block_h * 0.85,
                        facecolor="#b0b8c4",
                        edgecolor="#8891a0",
                        alpha=0.55,
                    )
                )
