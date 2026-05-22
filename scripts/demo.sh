#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true
echo "== Build 2DRBP parity binary (optional, improves packing parity) =="
if command -v c++ >/dev/null 2>&1; then
  c++ -std=c++17 -O2 vendor/RectangleBinPack/2drbp_parity.cpp \
    vendor/RectangleBinPack/GuillotineBinPack.cpp vendor/RectangleBinPack/Rect.cpp \
    -o vendor/RectangleBinPack/2drbp_parity || true
  c++ -std=c++17 -O2 vendor/RectangleBinPack/2drbp_maxrects.cpp \
    vendor/RectangleBinPack/GuillotineBinPack.cpp vendor/RectangleBinPack/Rect.cpp \
    -o vendor/RectangleBinPack/2drbp_maxrects || true
fi
echo "== Tests =="
python -m pytest -q
echo "== MATLAB parity headless run =="
python -m mmwave_v2i_sim.cli --config configs/scenario_default.yaml --output artifacts/demo_run.json
echo "== Batch density sweep =="
python -m mmwave_v2i_sim.cli --batch --config configs/scenario_default.yaml --output artifacts/batch_trim.json
echo "Demo complete. Launch GUI with:"
echo "  python -m mmwave_v2i_sim.cli --gui --config configs/scenario_default.yaml"
