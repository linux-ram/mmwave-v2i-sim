#!/usr/bin/env python3
"""Generate PNG previews for README and GitHub (no GUI required)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mmwave_v2i_sim.sim_engine.engine import SimSession
from mmwave_v2i_sim.sim_engine.visualize import draw_figure1_map, draw_figure2_packing

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"


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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _save_sim_previews()
    print(f"Wrote {OUT / 'preview_map.png'} and preview_packing.png")


if __name__ == "__main__":
    main()
