"""Generate validation report from CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from mmwave_v2i_sim.analysis.validation import write_report


def main() -> None:
    p = argparse.ArgumentParser(description="Generate MATLAB-adjacent validation report.")
    p.add_argument("--config", type=Path, default=Path("configs/scenario_minimal.yaml"))
    p.add_argument("--output", type=Path, default=Path("artifacts/validation"))
    args = p.parse_args()
    out = write_report(args.config, args.output)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
