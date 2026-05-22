"""MATLAB Figure 1/2 visualization (plotArc, visualizePacking, aerial map)."""

from __future__ import annotations

import colorsys
from pathlib import Path
from typing import Optional

import matplotlib.image as mpimg
import numpy as np
from matplotlib.patches import Polygon, Rectangle

from mmwave_v2i_sim.sim_engine.constants import (
    BEAM_ARC_DEG,
    B_TOT,
    MAP_XLIM,
    MAP_YLIM,
    PACK_PAD,
    ROUTE_SEGMENT_WINDOW,
    T_TOT,
)
from mmwave_v2i_sim.sim_engine.engine import StepSnapshot
from mmwave_v2i_sim.sim_engine.packing import ALGORITHM_LABELS

ASSETS = Path(__file__).resolve().parents[3] / "assets"
_AERIAL: Optional[np.ndarray] = None

# Base candy tones; extended to one unique color per vehicle (up to 50, no reuse).
_CANDY_BASE = [
    "#FF6B6B", "#FF8C42", "#FFD93D", "#6BCB77", "#4D96FF",
    "#9B59B6", "#E84393", "#00CEC9", "#E17055", "#74B9FF",
    "#FD79A8", "#FDCB6E", "#55EFC4", "#A29BFE", "#FF7675",
    "#00B894", "#D63031", "#0984E3", "#6C5CE7", "#F39C12",
]
_MAX_RSB_VEHICLE_COLORS = 50


def _build_unique_vehicle_colors(n: int) -> list[str]:
    """Build n distinct saturated hex colors (no modulo reuse across vehicles)."""
    colors = list(_CANDY_BASE[: min(len(_CANDY_BASE), n)])
    used = set(colors)
    i = 0
    while len(colors) < n:
        h = (i * 0.618033988749895) % 1.0
        s = 0.78 + 0.12 * ((i % 4) / 4.0)
        v = 0.88 + 0.08 * ((i % 3) / 3.0)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
        if hex_color not in used:
            colors.append(hex_color)
            used.add(hex_color)
        i += 1
    return colors


_VEHICLE_RSB_COLORS = _build_unique_vehicle_colors(_MAX_RSB_VEHICLE_COLORS)


def _rsb_color_for_vehicle(vehicle_id: int) -> str:
    if not 0 <= vehicle_id < len(_VEHICLE_RSB_COLORS):
        raise IndexError(f"vehicle_id {vehicle_id} out of palette range")
    return _VEHICLE_RSB_COLORS[vehicle_id]

# Map vehicle status colours
COLOR_LOS_PACKED = "#00E676"     # bright green
COLOR_LOS_UNPACKED = "#FFEB3B"   # bright yellow
COLOR_NO_LOS = "#AAAAAA"         # grey

# Break route polylines when consecutive samples exceed this gap (metres).
_MAX_ROUTE_SEGMENT_M = 60.0


def _route_xy_plot_segments(xy: np.ndarray) -> np.ndarray:
    """Insert NaN rows so matplotlib does not draw chords across route gaps."""
    if len(xy) < 2:
        return xy
    chunks: list[np.ndarray] = [xy[0:1]]
    for i in range(1, len(xy)):
        if float(np.linalg.norm(xy[i] - xy[i - 1])) > _MAX_ROUTE_SEGMENT_M:
            chunks.append(np.array([[np.nan, np.nan]]))
        chunks.append(xy[i : i + 1])
    return np.vstack(chunks)


def _unpacked_vehicle_numbers(snap: StepSnapshot) -> list[int]:
    """Map 1-based RSB indices from the packer to 1-based vehicle numbers."""
    los_vehicle_ids = [v.vehicle_id for v in snap.vehicles if v.link_state]
    nums: list[int] = []
    for idx in snap.packing.ind_rsb_left_unpacked:
        rsb_0 = idx - 1 if idx >= 1 else idx
        if 0 <= rsb_0 < len(los_vehicle_ids):
            nums.append(los_vehicle_ids[rsb_0] + 1)
    return sorted(nums)


def _format_unpacked_vehicle_numbers(vehicle_nums: list[int], per_line: int = 10) -> str:
    """Wrap long unpacked vehicle lists so they stay inside the stats panel."""
    if not vehicle_nums:
        return "Indices unpacked = none"
    labels = [str(n) for n in vehicle_nums]
    lines = ["Indices unpacked = " + ", ".join(labels[:per_line])]
    for start in range(per_line, len(labels), per_line):
        lines.append("  " + ", ".join(labels[start : start + per_line]))
    return "\n".join(lines)


def _style_axes_bold(ax: object) -> None:
    ax.tick_params(labelsize=9, width=1.0)  # type: ignore[union-attr]
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():  # type: ignore[union-attr]
        lbl.set_fontweight("bold")


def _aerial_image() -> np.ndarray:
    global _AERIAL
    if _AERIAL is None:
        _AERIAL = np.flipud(mpimg.imread(ASSETS / "CitySectionAerialView.png"))
    return _AERIAL


def plot_arc(
    ax: object,
    a_rad: float,
    center_x: float,
    center_y: float,
    radius: float = 40.0,
    arc_deg: float = BEAM_ARC_DEG,
) -> Polygon:
    t = np.linspace(a_rad, a_rad + np.radians(arc_deg), 64)
    x = radius * np.cos(t) + center_x
    y = radius * np.sin(t) + center_y
    x = np.concatenate([x, [center_x, x[0]]])
    y = np.concatenate([y, [center_y, y[0]]])
    patch = Polygon(
        np.column_stack([x, y]),
        closed=True,
        facecolor="m",
        edgecolor="k",
        linewidth=2,
        alpha=0.85,
    )
    ax.add_patch(patch)  # type: ignore[union-attr]
    return patch


def _classify_vehicles(snap: StepSnapshot) -> dict[int, str]:
    """Return {vehicle_id: 'packed' | 'unpacked' | 'no_los'}."""
    status: dict[int, str] = {}
    los_ordered = [v.vehicle_id for v in snap.vehicles if v.link_state]
    unpacked_vids = {
        los_ordered[idx - 1]
        for idx in snap.packing.ind_rsb_left_unpacked
        if idx >= 1 and idx - 1 < len(los_ordered)
    }
    for v in snap.vehicles:
        if not v.link_state:
            status[v.vehicle_id] = "no_los"
        elif v.vehicle_id in unpacked_vids:
            status[v.vehicle_id] = "unpacked"
        else:
            status[v.vehicle_id] = "packed"
    return status


def draw_figure1_map(
    ax: object,
    snap: StepSnapshot,
    route_display: str = "full",
    run_progress: str | None = None,
) -> None:
    from matplotlib.lines import Line2D  # type: ignore[import]

    ax.clear()  # type: ignore[union-attr]
    img = _aerial_image()
    ax.imshow(  # type: ignore[union-attr]
        img,
        extent=[MAP_XLIM[0], MAP_XLIM[1], MAP_YLIM[0], MAP_YLIM[1]],
        origin="upper",
        zorder=0,
    )

    bs = snap.base_station_position
    current_step = snap.i_num - 1
    status_by_vid = _classify_vehicles(snap)
    has_los = any(v.link_state for v in snap.vehicles)

    for veh in snap.vehicles:
        x_ms, y_ms = float(veh.position[0]), float(veh.position[1])
        label = str(veh.vehicle_id + 1)
        status = status_by_vid[veh.vehicle_id]

        if status == "no_los":
            ax.add_patch(  # type: ignore[union-attr]
                Rectangle(
                    (x_ms - 4, y_ms - 4), 8, 8,
                    facecolor=COLOR_NO_LOS, edgecolor="#666666",
                    linewidth=1.0, alpha=0.7, zorder=3,
                )
            )
            ax.text(  # type: ignore[union-attr]
                x_ms + 8, y_ms + 8, label, fontsize=8, fontweight="bold",
                color="#555555", zorder=6,
            )
            continue

        theta = veh.theta
        if route_display == "full":
            seg = _route_xy_plot_segments(veh.route_xy)
            alpha_route = 0.7
        elif route_display == "active_segment":
            start = max(0, current_step - ROUTE_SEGMENT_WINDOW)
            end = min(len(veh.route_xy), current_step + ROUTE_SEGMENT_WINDOW + 1)
            seg = _route_xy_plot_segments(veh.route_xy[start:end])
            alpha_route = 0.9
        else:
            seg = np.empty((0, 2))
            alpha_route = 0.9

        if len(seg) > 1:
            ax.plot(  # type: ignore[union-attr]
                seg[:, 0], seg[:, 1], "-r", linewidth=2.5, alpha=alpha_route, zorder=3,
            )

        plot_arc(ax, np.radians(180.0 + theta), float(bs[0]), float(bs[1]))
        plot_arc(ax, np.radians(theta), x_ms, y_ms)

        face = COLOR_LOS_PACKED if status == "packed" else COLOR_LOS_UNPACKED
        ax.add_patch(  # type: ignore[union-attr]
            Rectangle(
                (x_ms - 5, y_ms - 5), 10, 10,
                facecolor=face, edgecolor="k", linewidth=2.0, zorder=4,
            )
        )
        ax.plot(  # type: ignore[union-attr]
            [x_ms, bs[0]], [y_ms, bs[1]], "-b", linewidth=1, zorder=2,
        )
        ax.text(  # type: ignore[union-attr]
            x_ms + 8, y_ms + 8, label, fontsize=8, fontweight="bold", color="k", zorder=6,
        )

    ax.plot(  # type: ignore[union-attr]
        float(bs[0]), float(bs[1]), "b^", markersize=10,
        markeredgecolor="k", linewidth=1, zorder=5,
    )

    ax.set_xlim(MAP_XLIM)  # type: ignore[union-attr]
    ax.set_ylim(MAP_YLIM)  # type: ignore[union-attr]
    ax.set_xlabel("X Coordinate (in m)", fontsize=12, fontweight="bold")  # type: ignore[union-attr]
    ax.set_ylabel("Y Coordinate (in m)", fontsize=12, fontweight="bold")  # type: ignore[union-attr]
    title = f"Time Elapsed = {snap.i_num} s   |   Vehicles: {snap.n_vehicle}"
    if run_progress:
        title = f"{title}   |   {run_progress}"
    ax.set_title(title, fontsize=14, fontweight="bold")  # type: ignore[union-attr]

    legend_handles = [
        Line2D([0], [0], color="m", linewidth=6, label="MS/BS Beam"),
        Line2D([0], [0], color="r", linewidth=3, label="Vehicle Route"),
        Line2D([0], [0], marker="^", color="b", linestyle="None",
               markersize=8, label="Base Station"),
        Line2D([0], [0], marker="s", color=COLOR_LOS_PACKED, markeredgecolor="k",
               linestyle="None", markersize=8, label="LoS + RSB packed"),
        Line2D([0], [0], marker="s", color=COLOR_LOS_UNPACKED, markeredgecolor="k",
               linestyle="None", markersize=8, label="LoS + RSB dropped"),
        Line2D([0], [0], marker="s", color=COLOR_NO_LOS, markeredgecolor="#666666",
               linestyle="None", markersize=7, label="No line-of-sight"),
    ]
    if not has_los:
        legend_handles = legend_handles[2:]  # drop beam/route lines when nothing active
    ax.legend(handles=legend_handles, fontsize=8, loc="upper right")  # type: ignore[union-attr]


def draw_figure2_packing(
    ax_pack: object,
    ax_text: object,
    snap: StepSnapshot,
) -> None:
    rb_w, rb_h = snap.rb
    data = snap.packing.data
    algo_label = ALGORITHM_LABELS.get(snap.packing_algorithm, "Packing")

    ax_pack.clear()  # type: ignore[union-attr]

    ax_pack.add_patch(  # type: ignore[union-attr]
        Rectangle(
            (0, 0), 1.0, 1.0,
            facecolor="white", edgecolor="black", linewidth=2.0,
        )
    )

    for i in range(1, 10):
        ax_pack.axvline(i / 10, color="grey", lw=0.4, ls=":", alpha=0.4)  # type: ignore[union-attr]
        ax_pack.axhline(i / 10, color="grey", lw=0.4, ls=":", alpha=0.4)  # type: ignore[union-attr]

    los_vehicle_ids = [v.vehicle_id for v in snap.vehicles if v.link_state]
    unpacked_0 = {
        idx - 1 for idx in snap.packing.ind_rsb_left_unpacked if idx >= 1
    }
    packed_rsb_indices = [i for i in range(len(snap.rsb_items)) if i not in unpacked_0]

    for j, row in enumerate(data):
        x, y, w, h = row
        if w <= 0 or h <= 0:
            continue
        nx, ny, nw, nh = x / rb_w, y / rb_h, w / rb_w, h / rb_h
        if j < len(packed_rsb_indices):
            rsb_idx = packed_rsb_indices[j]
            vid = los_vehicle_ids[rsb_idx] if rsb_idx < len(los_vehicle_ids) else j
        else:
            vid = j
        color = _rsb_color_for_vehicle(vid)
        ax_pack.add_patch(  # type: ignore[union-attr]
            Rectangle((nx, ny), nw, nh, facecolor=color, edgecolor="k", linewidth=1.0)
        )
        ax_pack.text(  # type: ignore[union-attr]
            nx + nw / 2, ny + nh / 2, str(vid + 1),
            ha="center", va="center", fontsize=7, fontweight="bold", color="k",
        )

    ax_pack.set_xlim(-PACK_PAD, 1.0 + PACK_PAD)  # type: ignore[union-attr]
    ax_pack.set_ylim(-PACK_PAD, 1.0 + PACK_PAD)  # type: ignore[union-attr]
    ax_pack.set_xlabel("Time (normalized)", fontsize=9, fontweight="bold")  # type: ignore[union-attr]
    ax_pack.set_ylabel("Bandwidth (normalized)", fontsize=9, fontweight="bold")  # type: ignore[union-attr]
    _style_axes_bold(ax_pack)

    rb_text = (
        f"Resource Block = {rb_w:,} time-slots x {rb_h:,} freq-bins"
        f"  ({T_TOT:.2f} s x {B_TOT/1e9:.2f} GHz)"
    )
    ax_pack.set_title(algo_label, fontsize=11, fontweight="bold", pad=22)  # type: ignore[union-attr]
    ax_pack.text(  # type: ignore[union-attr]
        0.5, 1.01, rb_text,
        transform=ax_pack.transAxes,  # type: ignore[union-attr]
        fontsize=8, fontweight="bold", ha="center", va="bottom", color="#333333",
    )

    ax_pack.text(  # type: ignore[union-attr]
        0.98, 0.98, "Each grid cell = 0.1 s x 100 MHz",
        fontsize=7, color="grey", ha="right", va="top",
    )

    n_rsb_total = len(snap.rsb_items)
    unpacked = snap.packing.n_rsb_left_unpacked
    trim_pct = snap.packing.trim_loss * 100.0
    lines = (
        f"Trim Loss = {trim_pct:.2f}%\n"
        f"Total Resource Service Blocks: {n_rsb_total}\n"
        f"Unpacked: {unpacked}\n"
        f"{_format_unpacked_vehicle_numbers(_unpacked_vehicle_numbers(snap))}"
    )
    ax_text.clear()  # type: ignore[union-attr]
    ax_text.axis("off")  # type: ignore[union-attr]
    ax_text.text(  # type: ignore[union-attr]
        0.02, 0.75, lines, color="red", fontsize=9, ha="left", va="top",
        linespacing=1.3, wrap=True,
        transform=ax_text.transAxes,  # type: ignore[union-attr]
    )
