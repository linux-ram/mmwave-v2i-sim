"""Copy GUI preview figures into paper/figures for main.tex and IEEE PDF."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEWS = ROOT / "docs" / "images"
OUT = ROOT / "paper" / "figures"

FIGURES = [
    ("preview_map.png", "fig_gui_map.png"),
    ("preview_packing.png", "fig_gui_packing.png"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in FIGURES:
        src = PREVIEWS / src_name
        if not src.is_file():
            raise SystemExit(
                f"Missing {src}. Run: python scripts/generate_readme_assets.py"
            )
        shutil.copy2(src, OUT / dst_name)
        print(f"Wrote {OUT / dst_name}")


if __name__ == "__main__":
    main()
