# mmWave V2I Simulator (Python)

Strict open-source Python port of the MATLAB [mmWave-V2I-2DRBP](https://github.com/linux-ram/mmWave-V2I-2DRBP) link-layer simulator: aerial city map, vehicular routes, LoS beams, and Guillotine 2DRBP packing.

## Quick Start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,gui]"
# Optional: native Guillotine parity binary
c++ -std=c++17 -O2 vendor/RectangleBinPack/2drbp_parity.cpp \
  vendor/RectangleBinPack/GuillotineBinPack.cpp vendor/RectangleBinPack/Rect.cpp \
  -o vendor/RectangleBinPack/2drbp_parity
pytest
bash scripts/demo.sh
```

## Run Modes

- GUI (Figure 1 + Figure 2): `python -m mmwave_v2i_sim.cli --gui`
- Headless step replay: `python -m mmwave_v2i_sim.cli --config configs/scenario_default.yaml`
- Batch density sweep (Figure 3): `python -m mmwave_v2i_sim.cli --batch`

## MATLAB Parity Module

- `src/mmwave_v2i_sim/matlab_port/loader.py` — `loadVehRouteData.m`
- `src/mmwave_v2i_sim/matlab_port/engine.py` — `vehicleBinPackSimulation.m` stepping
- `src/mmwave_v2i_sim/matlab_port/guillotine_packer.py` — `determinePacking.m` / 2DRBP
- `src/mmwave_v2i_sim/matlab_port/visualize.py` — `plotArc.m`, `visualizePacking.m`, aerial map
- `assets/` — bundled MIT-licensed map and routes

Legacy research-oriented engine modules remain under `src/mmwave_v2i_sim/core/` for optional use via `configs/scenario_legacy_research.yaml`.

See [docs/USER_GUIDE.md](docs/USER_GUIDE.md) and [docs/open_data_sources.md](docs/open_data_sources.md).

## License

MIT — see [LICENSE](LICENSE).
