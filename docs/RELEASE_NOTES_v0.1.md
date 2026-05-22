# v0.1.0 — Initial public release

## Highlights

- **MATLAB-parity desktop simulator** (`sim_engine`): aerial map, LoS beams, 2DRBP packing (Guillotine / Shelf / MaxRects).
- **PySide6 GUI**: Figure 1 + Figure 2 layout, playback controls, batch runs (1/5/20/50), session `.zip` export (JSON/CSV + embedded `session.npz`).
- **Trim-loss trend plot** with multi-run statistics.
- Optional OSM road-snapped routes (Boston Seaport).
- Legacy research engine (`core/`) for protocol-phase experiments.

## Install

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-lock.txt
pip install -e ".[dev,gui]"
pytest
python -m mmwave_v2i_sim.cli --gui
```

## Related work

- Original MATLAB simulator: [linux-ram/mmWave-V2I-2DRBP](https://github.com/linux-ram/mmWave-V2I-2DRBP)
- MathWorks File Exchange: [84948](https://www.mathworks.com/matlabcentral/fileexchange/84948)

## Known limits (v0.2 roadmap)

- GUI vehicle count capped at 50 (not interactive 200-vehicle scale).
- 2D matplotlib viewport (no 3D city mesh).
- IEEE PDF build not automated in CI.
