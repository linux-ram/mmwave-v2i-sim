"""Generate figures for IEEE paper from validation and research demos."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mmwave_v2i_sim.config.schema import load_scenario_config
from mmwave_v2i_sim.core.engine import SimulationEngine
from mmwave_v2i_sim.mobility.city_presets import CITY_PRESETS


def _fig_density_sweep(out_dir: Path) -> None:
    report_path = Path("artifacts/validation/validation_report.json")
    if not report_path.exists():
        raise SystemExit("Run: python scripts/generate_validation_report.py")
    data = json.loads(report_path.read_text(encoding="utf-8"))
    primary = data.get("sim_engine") or data
    rows = primary["comparison"]
    x = [r["vehicles"] for r in rows]
    y_py = [r.get("trim_loss_mean", r.get("trim_loss_python")) for r in rows]
    legacy = data.get("legacy", {})
    legacy_rows = legacy.get("comparison", [])
    y_ref = (
        [r["trim_loss_matlab_proxy"] for r in legacy_rows]
        if legacy_rows
        else None
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y_py, "r-o", label="Python simulator (sim_engine)")
    if y_ref is not None:
        ax.plot(x, y_ref, "k--s", label="MATLAB-adjacent reference (legacy proxy)")
    ax.set_xscale("log")
    ax.set_xlabel("Vehicle count")
    ax.set_ylabel("Trim loss")
    ax.set_title("Density sweep comparison")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_density_sweep.pdf")
    fig.savefig(out_dir / "fig_density_sweep.png", dpi=150)
    plt.close(fig)
    print(f"Wrote {out_dir / 'fig_density_sweep.pdf'}")


def _fig_dual_band(out_dir: Path) -> None:
    summary = Path("artifacts/city_preset_summary.json")
    rows = json.loads(summary.read_text(encoding="utf-8"))
    labels = [r["label"] for r in rows]
    s28 = [r["mean_sinr_28ghz"] for r in rows]
    s39 = [r["mean_sinr_39ghz"] for r in rows]

    x = range(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar([i - w / 2 for i in x], s28, width=w, label="28 GHz", color="#4D96FF")
    ax.bar([i + w / 2 for i in x], s39, width=w, label="39 GHz", color="#FF6B6B")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=15, ha="right", fontsize=8)
    ax.set_ylabel("Mean SINR (dB)")
    ax.set_title("Dual-band channel snapshot (3GPP-inspired abstraction)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_dual_band.pdf")
    fig.savefig(out_dir / "fig_dual_band.png", dpi=150)
    plt.close(fig)
    print(f"Wrote {out_dir / 'fig_dual_band.pdf'}")


def _fig_city_presets(out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 3))
    for preset, color in zip(
        CITY_PRESETS.values(),
        ["#4D96FF", "#FF6B6B", "#6BCB77"],
    ):
        ax.bar(
            preset.city_name,
            preset.length_m * preset.width_m / 1e6,
            color=color,
            alpha=0.85,
        )
    ax.set_ylabel("Scene area (km² proxy)")
    ax.set_title("City preset coverage")
    ax.tick_params(axis="x", rotation=12)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_city_presets.pdf")
    fig.savefig(out_dir / "fig_city_presets.png", dpi=150)
    plt.close(fig)
    print(f"Wrote {out_dir / 'fig_city_presets.pdf'}")


def main() -> None:
    out_dir = Path("paper/figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    _fig_density_sweep(out_dir)
    # Ensure city summary exists for dual-band figure
    if not Path("artifacts/city_preset_summary.json").is_file():
        import subprocess
        import sys

        subprocess.run([sys.executable, "scripts/demo_city_presets.py"], check=True)
    _fig_dual_band(out_dir)
    _fig_city_presets(out_dir)


if __name__ == "__main__":
    main()
