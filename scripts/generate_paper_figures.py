"""Generate figures for IEEE paper from validation artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main() -> None:
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

    out_dir = Path("paper/figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y_py, "r-o", label="Python simulator (sim_engine)")
    if y_ref is not None:
        ax.plot(x, y_ref, "k--s", label="MATLAB-adjacent reference (legacy proxy)")
    ax.set_xscale("log")
    ax.set_xlabel("Vehicle count")
    ax.set_ylabel("Trim loss")
    ax.set_title("Density sweep comparison")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "fig_density_sweep.pdf")
    fig.savefig(out_dir / "fig_density_sweep.png", dpi=150)
    print(f"Wrote {out_dir / 'fig_density_sweep.pdf'}")


if __name__ == "__main__":
    main()
