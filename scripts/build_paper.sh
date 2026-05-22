#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true
export MPLCONFIGDIR="${MPLCONFIGDIR:-$(pwd)/.matplotlib_cache}"
mkdir -p "$MPLCONFIGDIR"
python scripts/generate_validation_report.py
python scripts/generate_paper_figures.py
cd paper
if command -v tectonic >/dev/null 2>&1; then
  tectonic -X compile main.tex
  echo "Built paper/main.pdf (tectonic)"
elif command -v pdflatex >/dev/null 2>&1; then
  pdflatex -interaction=nonstopmode main.tex
  pdflatex -interaction=nonstopmode main.tex
  echo "Built paper/main.pdf (pdflatex)"
else
  echo "Neither tectonic nor pdflatex found; figures and main.tex are ready."
  echo "Install: brew install tectonic"
  exit 1
fi
