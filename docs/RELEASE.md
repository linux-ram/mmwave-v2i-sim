# Release Guide

## Pre-release checklist

1. `pytest` passes
2. `python scripts/generate_validation_report.py`
3. `python scripts/bench_scale.py` within expected budgets
4. `bash scripts/demo.sh`
5. Review `docs/assumptions_limitations.md`
6. Review `docs/open_data_sources.md` (no unlicensed assets bundled)

## GitHub publish

```bash
git init
git add .
git commit -m "Initial Python mmWave V2I simulator release"
git remote add origin <your-repo-url>
git push -u origin main
```

## Desktop bundle (optional)

```bash
pip install pyinstaller
pyinstaller --name mmwave-v2i-sim \
  --collect-all matplotlib \
  --collect-all PySide6 \
  --windowed \
  -c "from mmwave_v2i_sim.cli import main; main()" 2>/dev/null || \
pyinstaller packaging/mmwave_gui.spec
```

See `packaging/mmwave_gui.spec` for GUI entrypoint.

## MathWorks File Exchange

- Upload repository or release zip
- Include README, LICENSE, USER_GUIDE
- Link to original MATLAB entry: File Exchange 84948
- Note Python 3.11+ requirement and PySide6/matplotlib for GUI
