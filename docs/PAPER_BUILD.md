# IEEE paper build

## Prerequisites

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**PDF engine (pick one):**

- **Tectonic** (recommended on macOS): `brew install tectonic`
- **pdfLaTeX**: TeX Live / MacTeX (`pdflatex` on `PATH`)

## One-command build

From the repository root:

```bash
bash scripts/build_paper.sh
```

This regenerates GUI preview figures for the paper, then compiles `paper/main.tex` with **Tectonic** if available, otherwise **pdfLaTeX**.

## Figures only

```bash
python scripts/generate_readme_assets.py
python scripts/generate_paper_figures.py
```

## Output artifacts

| Path | Description |
|------|-------------|
| `paper/figures/fig_gui_map.png` | Figure 1 style map preview |
| `paper/figures/fig_gui_packing.png` | Figure 2 style packing preview |
| `paper/main.pdf` | IEEE-style technical report (committed for citation) |

## CI

The [Paper PDF workflow](https://github.com/linux-ram/mmwave-v2i-sim/actions/workflows/paper.yml) also builds `main.pdf` on Ubuntu with TeX Live and uploads an artifact.

## Citing the paper

See [CITATION.md](CITATION.md) for BibTeX entries using the exact title in `paper/main.tex`.
