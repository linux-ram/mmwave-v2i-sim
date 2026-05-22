#!/usr/bin/env python3
"""Generate PNG previews for README and GitHub (no GUI required)."""

from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mmwave_v2i_sim.sim_engine.engine import SimSession
from mmwave_v2i_sim.sim_engine.visualize import draw_figure1_map, draw_figure2_packing

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"
ASSETS = ROOT / "assets"
PAPER_FIG = ROOT / "paper" / "figures" / "fig_density_sweep.png"


def _save_sim_previews() -> None:
    session = SimSession(n_vehicle=10, seed=42)
    snap = session.reset()
    for _ in range(8):
        nxt = session.step()
        if nxt is not None:
            snap = nxt

    fig_map, ax_map = plt.subplots(figsize=(8, 4.5))
    draw_figure1_map(ax_map, snap, route_display="full", run_progress="Preview | 10 vehicles")
    fig_map.subplots_adjust(left=0.06, right=0.98, top=0.94, bottom=0.08)
    fig_map.savefig(OUT / "preview_map.png", dpi=150, bbox_inches="tight")
    plt.close(fig_map)

    fig_pack, axes = plt.subplots(2, 1, figsize=(5, 5), gridspec_kw={"height_ratios": [3, 1]})
    draw_figure2_packing(axes[0], axes[1], snap)
    fig_pack.subplots_adjust(left=0.14, right=0.96, top=0.90, bottom=0.08, hspace=0.35)
    fig_pack.savefig(OUT / "preview_packing.png", dpi=150, bbox_inches="tight")
    plt.close(fig_pack)


def _save_city_preset_figure() -> None:
    from mmwave_v2i_sim.mobility.city_presets import CITY_PRESETS

    fig, ax = plt.subplots(figsize=(7, 3.5))
    colors = ["#4D96FF", "#FF6B6B", "#6BCB77"]
    for (key, preset), color in zip(CITY_PRESETS.items(), colors):
        rect = plt.Rectangle(
            (0, 0),
            preset.length_m / 100.0,
            preset.width_m / 100.0,
            fill=False,
            edgecolor=color,
            linewidth=2,
            label=f"{preset.city_name} ({preset.length_m:.0f}×{preset.width_m:.0f} m)",
        )
        ax.add_patch(rect)
        ax.text(
            preset.length_m / 200.0,
            preset.width_m / 100.0 + 0.3,
            preset.city_name,
            ha="center",
            fontsize=9,
            color=color,
        )
    ax.set_xlim(-0.5, 20)
    ax.set_ylim(-0.5, 14)
    ax.set_aspect("equal")
    ax.set_xlabel("Relative extent (×100 m)")
    ax.set_title("Open-license city presets (research path)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "city_presets.png", dpi=150)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    aerial = ASSETS / "CitySectionAerialView.png"
    if aerial.is_file():
        shutil.copy2(aerial, OUT / "hero_aerial.png")
        print(f"Copied {OUT / 'hero_aerial.png'}")
    _save_sim_previews()
    print(f"Wrote {OUT / 'preview_map.png'} and preview_packing.png")
    _save_city_preset_figure()
    print(f"Wrote {OUT / 'city_presets.png'}")
    if PAPER_FIG.is_file():
        shutil.copy2(PAPER_FIG, OUT / "density_sweep.png")
        print(f"Copied density_sweep.png")
    else:
        print("Run: python scripts/generate_paper_figures.py first for density_sweep.png")


if __name__ == "__main__":
    main()
