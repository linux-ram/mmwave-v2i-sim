# v0.2.0 — Inviting release + research snapshot

## Highlights

- **README:** stacked GUI previews (map + packing), tagline *mmWave V2I link-layer simulator in Python*
- **Session export:** completed runs save as **ZIP** (`manifest.json`, CSV trim-loss, JSONL, embedded `session.npz`)
- **City presets:** Boston, San Francisco, RTP configs + `scripts/demo_city_presets.py` (research path)
- **Channel:** Dual-band 28/39 GHz, geometric LOS, `codebook` vs `ideal` beam modes (research path)
- **Paper:** Two-page IEEE-style [`paper/main.pdf`](../paper/main.pdf) with GUI figures; author Ramanathan Subramanian
- **Citation:** [`docs/CITATION.md`](../docs/CITATION.md), [`CITATION.cff`](../CITATION.cff), Tectonic build via `bash scripts/build_paper.sh`
- **CI:** Linux 2DRBP parity build; validation report artifacts

## Quick start

```bash
git clone https://github.com/linux-ram/mmwave-v2i-sim.git
cd mmwave-v2i-sim
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-lock.txt
pip install -e ".[dev,gui]"
python -m mmwave_v2i_sim.cli --gui
```

After a run completes, use **Save** to download `mmwave_sim_session.zip`.

## Study the paper

```bash
bash scripts/build_paper.sh
open paper/main.pdf
```

Or download the `paper-pdf` artifact from the latest [Paper PDF workflow](https://github.com/linux-ram/mmwave-v2i-sim/actions/workflows/paper.yml) run.

## Since v0.1.0

- ZIP session export (replaces standalone `.npz` as the default download)
- README and technical report refresh (no separate hero aerial / density-sweep README section)
- Citation pack and committed PDF
- City presets and dual-band research path (YAML; not wired into default desktop `sim_engine` GUI)

## Known limits (post-v0.2 issues)

Tracked on GitHub: [#1](https://github.com/linux-ram/mmwave-v2i-sim/issues/1) 3D/KPI panel, [#2](https://github.com/linux-ram/mmwave-v2i-sim/issues/2) scale, [#3](https://github.com/linux-ram/mmwave-v2i-sim/issues/3) paper-in-CI polish.
