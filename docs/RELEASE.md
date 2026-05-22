# Release Guide

## Pre-release checklist

1. `pytest` passes
2. `python scripts/generate_validation_report.py`
3. `python scripts/bench_scale.py` within expected budgets (optional)
4. `bash scripts/demo.sh`
5. Review `docs/assumptions_limitations.md`
6. Review `docs/open_data_sources.md` (no unlicensed assets bundled)
7. Review [docs/FILE_EXCHANGE_CHECKLIST.md](FILE_EXCHANGE_CHECKLIST.md)

## GitHub publish (linux-ram/mmwave-v2i-sim)

Prerequisites: [GitHub CLI](https://cli.github.com/) (`gh auth login`) and write access to the `linux-ram` org.

```bash
cd /path/to/mmwave-v2i-sim
gh repo create linux-ram/mmwave-v2i-sim \
  --public \
  --source=. \
  --remote=origin \
  --description "Python desktop port of the mmWave V2I 2DRBP link-layer simulator" \
  --push
```

If the repo already exists:

```bash
git remote add origin git@github.com:linux-ram/mmwave-v2i-sim.git
git push -u origin main
```

## Tag v0.1.0

```bash
git tag -a v0.1.0 -m "Initial public release: MATLAB-parity GUI and sim_engine"
git push origin v0.1.0
gh release create v0.1.0 --title "v0.1.0" --notes-file docs/RELEASE_NOTES_v0.1.md
```

## Cross-link MATLAB repo

On [linux-ram/mmWave-V2I-2DRBP](https://github.com/linux-ram/mmWave-V2I-2DRBP), add to README:

> **Python port:** [mmwave-v2i-sim](https://github.com/linux-ram/mmwave-v2i-sim) — cross-platform GUI, Guillotine/Shelf/MaxRects packing, session export.

## Desktop bundle (optional)

```bash
pip install pyinstaller
pyinstaller packaging/mmwave_gui.spec
```

## MathWorks File Exchange

- Upload repository or release zip
- Include README, LICENSE, USER_GUIDE
- Link to original MATLAB entry: File Exchange 84948
- Note Python 3.11+ requirement and PySide6/matplotlib for GUI
