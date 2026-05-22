"""Generate validation report from CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from mmwave_v2i_sim.analysis.validation import write_report


def main() -> None:
    p = argparse.ArgumentParser(description="Generate validation report (sim_engine + optional legacy).")
    p.add_argument(
        "--config",
        type=Path,
        default=Path("configs/scenario_legacy_research.yaml"),
        help="Legacy research config (optional second block in report)",
    )
    p.add_argument("--output", type=Path, default=Path("artifacts/validation"))
    p.add_argument(
        "--sim-engine-only",
        action="store_true",
        help="Skip legacy research-engine sweep",
    )
    args = p.parse_args()
    legacy_path = None if args.sim_engine_only else args.config
    out = write_report(legacy_path, args.output, include_legacy=legacy_path is not None)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
