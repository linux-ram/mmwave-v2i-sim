#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true
export MPLCONFIGDIR="${MPLCONFIGDIR:-$(pwd)/.matplotlib_cache}"
mkdir -p "$MPLCONFIGDIR"
python scripts/generate_validation_report.py
python scripts/generate_paper_figures.py
cd paper
if command -v pdflatex >/dev/null; then
  pdflatex -interaction=nonstopmode main.tex
  pdflatex -interaction=nonstopmode main.tex
  echo "Built paper/main.pdf"
else
  echo "pdflatex not found; figures and main.tex are ready."
fi
