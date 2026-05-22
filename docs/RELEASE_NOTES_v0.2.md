# v0.2.0 — Inviting release + research snapshot

## Highlights

- **README visuals:** aerial hero, GUI previews, density sweep and city preset figures under `docs/images/`
- **City presets:** Boston, San Francisco, RTP configs + `scripts/demo_city_presets.py`
- **Channel:** Dual-band 28/39 GHz, geometric 3D LOS, `codebook` vs `ideal` beam modes
- **IEEE paper:** Updated `paper/main.tex` with extra figures; build via `bash scripts/build_paper.sh` or [Paper workflow](https://github.com/linux-ram/mmwave-v2i-sim/actions/workflows/paper.yml)

## Quick start

```bash
pip install -r requirements-lock.txt && pip install -e ".[dev,gui]"
python -m mmwave_v2i_sim.cli --gui
```

## Study the paper

```bash
bash scripts/build_paper.sh
open paper/main.pdf
```

Or download `paper-pdf` artifact from the latest Paper PDF workflow run.
