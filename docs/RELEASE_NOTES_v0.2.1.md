# v0.2.1 — Repository cleanup

Maintenance release after v0.2.0. No change to default GUI simulation behavior.

## Changes

- Removed deprecated `matlab_port` shim and unused UI modules (`matlab_scene`, `viewmodel`)
- Removed orphan README images and stale v0.1 publish docs/scripts
- Vendor packing binaries no longer committed; build via `bash scripts/demo.sh` or CI
- Aligned `pyproject.toml` author with citation pack (Ramanathan Subramanian)
- Simplified `docs/RELEASE.md` and `generate_readme_assets.py` (map + packing previews only)

## Quick start

```bash
git clone https://github.com/linux-ram/mmwave-v2i-sim.git
cd mmwave-v2i-sim
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-lock.txt
pip install -e ".[dev,gui]"
bash scripts/demo.sh   # builds local 2drbp binaries (recommended)
python -m mmwave_v2i_sim.cli --gui
```

## Full feature set

See [RELEASE_NOTES_v0.2.0.md](RELEASE_NOTES_v0.2.0.md) for ZIP export, paper PDF, city presets, and citation helpers.
