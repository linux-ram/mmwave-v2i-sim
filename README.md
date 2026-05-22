# mmwave-v2i-sim

[![CI](https://github.com/linux-ram/mmwave-v2i-sim/actions/workflows/ci.yml/badge.svg)](https://github.com/linux-ram/mmwave-v2i-sim/actions/workflows/ci.yml)

Open-source **Python port** of the MATLAB [mmWave-V2I-2DRBP](https://github.com/linux-ram/mmWave-V2I-2DRBP) link-layer simulator: aerial city map, vehicular routes, LoS beams, and 2DRBP resource-block packing.

| | |
|---|---|
| **MATLAB original** | [linux-ram/mmWave-V2I-2DRBP](https://github.com/linux-ram/mmWave-V2I-2DRBP) |
| **This repo** | Cross-platform GUI, Guillotine / Shelf / MaxRects packing, session export |
| **Milestones** | [docs/MILESTONE_STATUS.md](docs/MILESTONE_STATUS.md) |

## Quick Start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-lock.txt
pip install -e ".[dev,gui]"
# Optional: native Guillotine parity binary
c++ -std=c++17 -O2 vendor/RectangleBinPack/2drbp_parity.cpp \
  vendor/RectangleBinPack/GuillotineBinPack.cpp vendor/RectangleBinPack/Rect.cpp \
  -o vendor/RectangleBinPack/2drbp_parity
pytest
bash scripts/demo.sh
```

## Run Modes

- **GUI** (Figure 1 + Figure 2): `python -m mmwave_v2i_sim.cli --gui`
- **Headless step replay**: `python -m mmwave_v2i_sim.cli --config configs/scenario_default.yaml`
- **Batch density sweep** (Figure 3): `python -m mmwave_v2i_sim.cli --batch`

## Architecture

**Default path** — MATLAB parity (`sim_engine`):

- [`sim_engine/loader.py`](src/mmwave_v2i_sim/sim_engine/loader.py) — `loadVehRouteData.m`
- [`sim_engine/engine.py`](src/mmwave_v2i_sim/sim_engine/engine.py) — `vehicleBinPackSimulation.m` stepping
- [`sim_engine/packing.py`](src/mmwave_v2i_sim/sim_engine/packing.py) — Guillotine / Shelf / MaxRects
- [`sim_engine/visualize.py`](src/mmwave_v2i_sim/sim_engine/visualize.py) — aerial map, beams, packing panel
- [`ui/app.py`](src/mmwave_v2i_sim/ui/app.py) — PySide6 desktop GUI

**Legacy research path** — protocol phases, synthetic mobility, plugin schedulers:

- [`core/`](src/mmwave_v2i_sim/core/) + [`configs/scenario_legacy_research.yaml`](configs/scenario_legacy_research.yaml)

Deprecation shim: `matlab_port/` re-exports `sim_engine` with a warning.

Bundled MIT-licensed assets: [`assets/`](assets/). OSM routes are optional (`pip install -e ".[osm]"`); without network, bundled `vehicularRoutes.mat` is used.

## Cross-platform smoke

| Platform | Status |
|----------|--------|
| macOS | Verified (primary dev) |
| Linux | CI (`pytest` + validation report) |
| Windows | Manual: same Quick Start; GUI requires PySide6 |

## Validation

```bash
python scripts/generate_validation_report.py
# Reports: artifacts/validation/validation_report.json
```

## Documentation

- [User guide](docs/USER_GUIDE.md)
- [Assumptions & limitations](docs/assumptions_limitations.md)
- [Open data sources](docs/open_data_sources.md)
- [Release guide](docs/RELEASE.md)

## Citation

See [CITATION.cff](CITATION.cff). Original MATLAB entry: MathWorks File Exchange [84948](https://www.mathworks.com/matlabcentral/fileexchange/84948).

## License

MIT — see [LICENSE](LICENSE).

## Suggested GitHub topics

`mmwave` `v2i` `2drbp` `simulator` `python` `matlab-port` `5g` `resource-allocation`
