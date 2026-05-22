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

This runs validation, regenerates figures, then compiles `paper/main.tex` with **Tectonic** if available, otherwise **pdfLaTeX**.

## Figures only

```bash
python scripts/generate_validation_report.py
python scripts/generate_paper_figures.py
```

## Output artifacts

| Path | Description |
|------|-------------|
| `paper/figures/fig_density_sweep.pdf` | Trim-loss density sweep |
| `paper/figures/fig_city_presets.pdf` | City preset extents |
| `paper/figures/fig_dual_band.pdf` | Dual-band SINR comparison |
| `paper/main.pdf` | IEEE-style technical report (committed for citation) |

## CI

The [Paper PDF workflow](https://github.com/linux-ram/mmwave-v2i-sim/actions/workflows/paper.yml) also builds `main.pdf` on Ubuntu with TeX Live and uploads an artifact.

## Citing the paper

See [CITATION.md](CITATION.md) for BibTeX entries using the exact title in `paper/main.tex`.
