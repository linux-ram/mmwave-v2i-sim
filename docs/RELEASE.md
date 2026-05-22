# Release Guide

## Pre-release checklist

1. `pytest` passes
2. `python scripts/generate_validation_report.py`
3. `bash scripts/demo.sh` (builds vendor `2drbp_parity` on Linux/macOS)
4. Review [docs/assumptions_limitations.md](assumptions_limitations.md)

## Tag a release (v0.2+)

```bash
# bump version in pyproject.toml and src/mmwave_v2i_sim/__init__.py
pytest
git tag -a v0.2.0 -m "v0.2.0: short description"
git push origin v0.2.0
gh release create v0.2.0 --title "v0.2.0" --notes-file docs/RELEASE_NOTES_v0.2.md --latest
```

Historical notes: [RELEASE_NOTES_v0.1.md](RELEASE_NOTES_v0.1.md), [RELEASE_NOTES_v0.2.md](RELEASE_NOTES_v0.2.md).

## Desktop bundle (optional)

```bash
pip install pyinstaller
pyinstaller packaging/mmwave_gui.spec
```

On macOS, extend the spec with a `BUNDLE` target for a double-click `.app`.

## MathWorks File Exchange (optional)

- Upload release zip with README, LICENSE, USER_GUIDE
- Link File Exchange [84948](https://www.mathworks.com/matlabcentral/fileexchange/84948)
- Python 3.11+, PySide6/matplotlib for GUI
