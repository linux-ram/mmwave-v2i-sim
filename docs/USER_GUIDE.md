# User Guide

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,gui]"
# Optional: build native packing binaries
c++ -std=c++17 -O2 vendor/RectangleBinPack/2drbp_parity.cpp \
  vendor/RectangleBinPack/GuillotineBinPack.cpp vendor/RectangleBinPack/Rect.cpp \
  -o vendor/RectangleBinPack/2drbp_parity
c++ -std=c++17 -O2 vendor/RectangleBinPack/2drbp_maxrects.cpp \
  -o vendor/RectangleBinPack/2drbp_maxrects
# Optional: install OSM road-snapped routes support
pip install -e ".[osm]"
pytest
```

## GUI (primary mode)

```bash
python -m mmwave_v2i_sim.cli --gui
```

The GUI layout:

- **Left column:** Aerial city map (Figure 1), **PLAYBACK** controls, then **SIMULATION PARAMETERS**.
- **Right column:** Bin packing view (Figure 2) and **trim loss vs step** trend plot (session-persistent, B&W).

### Playback controls

Two-row centered panel:

- **Row 1 — buttons:** Play/Pause · Step · Fwd/Back direction toggle · Terminate
- **Row 2 — knobs:** Playback interval slider (ms/step) · Vehicles button group (1 / 2 / 5 / 10 / 50)

| Control | Description |
|---------|-------------|
| **Play / Pause** | Auto-advance; locks simulation parameters until Restart or Reset |
| **Step** | One timestep in the current direction |
| **Fwd/Back toggle** | Sets step direction: unchecked = forward, checked = backward |
| **Terminate** | Stop playback and wipe all session run data (trim plot, step logs) |
| **Step** | One timestep; arrow shows direction (▶ forward, ◀ backward) |
| **Run progress** | `| Vehicles: N | x/Y runs` next to vehicle buttons |
| **Playback interval** | 50–500 ms/step — animation speed only |
| **Vehicles** | Resets the session; selects number of vehicles |

Vehicles advance **one route sample per simulation second**. When `osmnx` is installed
the sim uses OSM road-snapped routes cached under `assets/`; otherwise the bundled 50-path
`vehicularRoutes.mat` dataset is used (n≥50 vehicles cycle routes with a deterministic start stagger).

### Simulation parameters

| Parameter | Effect |
|-----------|--------|
| **Packing** | Guillotine (simplest), Shelf (fastest), or Max Rects (tightest) |
| **Runs** | How many times to run the simulation with the current parameters (1, 5, 20, or 50) |
| **LoS threshold** | P(LoS) cutoff in steps of 0.1 (default 0.5); vehicles with P(LoS) ≥ threshold join the packing |
| **Route display** | On (full path visible) or Off (hide routes) |

**SESSION DATA** panel (sibling to SIMULATION PARAMETERS): **Download simulation data** saves a `.zip` bundle (disabled until at least one run completes) containing:

- `manifest.json` — session parameters
- `trim_loss_steps.csv` — per-step trim loss (Excel/MATLAB friendly)
- `trim_series.json` — aggregated trim histories
- `runs/run_NNN/steps.jsonl` — one JSON line per timestep
- `session.npz` — full Python workspace inside the zip

Quick load in Python:

```python
from pathlib import Path
from mmwave_v2i_sim.sim_engine.session_export import load_workspace_npz
data = load_workspace_npz(Path("mmwave_sim_session.zip"))
```

Open `trim_loss_steps.csv` in Excel or MATLAB `readtable`.

Beam wedges use a **fixed 15°** span; orientation follows per-vehicle geometry.

**Parameter lock:** While playing, parameter controls are disabled until all scheduled runs finish or you press **Terminate**.

### Map vehicle colours

| Square | Meaning |
|--------|---------|
| **Bright green** | Line-of-sight + Resource Service Block packed into this step's Resource Block |
| **Bright yellow** | Line-of-sight + Resource Service Block dropped (no free space) |
| **Grey** | No line-of-sight to base station |

### Packing panel

Title shows the algorithm name; subtitle shows the **Resource Block** dimensions:
**6,250,000 time-slots × 40,000 frequency-bins** (1.00 s × 1.00 GHz).

Each packed **Resource Service Block** is drawn in normalized [0, 1]² coordinates with its 1-based
vehicle ID at the rectangle center. Trim loss statistics appear below the grid.

Glossary:
- **Resource Block:** the full time-frequency canvas to be filled each step.
- **Resource Service Block:** per-vehicle time/bandwidth demand to be packed.
- Each faint grid cell = 0.1 s × 100 MHz.

### Trim loss trend plot

- Plots **% of Resource Block area unused per step** vs simulation step.
- A run is saved **only when the simulation reaches its natural end**. **Terminate** discards in-progress data and clears the session.

| # runs (same params) | Rendering |
|----------------------|-----------|
| 1 run | Dashed line with dot markers |
| 2–4 runs | Individual faint runs + bold mean line (no error bars) |
| 5+ runs | Individual faint runs + bold mean line + thin error bars (±1 std) |

Different parameter combinations (vehicles, algorithm, LoS threshold) use distinct line styles and markers.
The legend label shows all three: e.g. `(10 vehicles, LoS threshold = 0.5, guillotine packing)`.

Data persists across runs until the window closes or **Terminate** is pressed.

## Headless run

```bash
python -m mmwave_v2i_sim.cli --config configs/scenario_default.yaml
```

## Batch density sweep (Figure 3)

```bash
python -m mmwave_v2i_sim.cli --batch
```

Sweeps `nVehicle ∈ {1, 2, 5, 10, 50}` across 5 trials and reports mean/std trim loss.

## Scale limits (v0.1)

| Mode | Max vehicles | Config / entry |
|------|--------------|----------------|
| GUI (interactive) | 50 | Vehicle buttons in playback panel |
| Headless `sim_engine` | 50 (bundled routes; cycles with stagger) | `configs/scenario_default.yaml` |
| Headless legacy research | 200 | `configs/scenario_scale_200.yaml` |

Benchmark headless throughput:

```bash
python scripts/bench_scale.py
```

Regression gate: `tests/test_scale.py` (200-vehicle profile, 30 steps under 30 s).

## Scenarios

| File | Description |
|------|-------------|
| `configs/scenario_default.yaml` | Default sim engine (10 vehicles, Guillotine) |
| `configs/scenario_boston_osm.yaml` | Same as default; prefers OSM Boston routes when `osmnx` installed |
| `configs/scenario_legacy_research.yaml` | Research engine (200 vehicles, multi-BS, synthetic routes) |
| `configs/scenario_scale_200.yaml` | Legacy 200-vehicle / 20-BS headless profile |

## Package structure

All simulation logic lives in `src/mmwave_v2i_sim/sim_engine/`. The old `matlab_port` package
is a deprecated compatibility shim that re-exports from `sim_engine`.

## How to cite this work

See **[docs/CITATION.md](CITATION.md)** for the recommended paper title, BibTeX (`@misc` and `@software`), and APA-style examples. The technical report PDF is **[paper/main.pdf](../paper/main.pdf)**. You may also cite the original MATLAB File Exchange entry [84948](https://www.mathworks.com/matlabcentral/fileexchange/84948).
