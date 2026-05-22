# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all("matplotlib")
pyside_datas, pyside_binaries, pyside_hidden = collect_all("PySide6")
datas += pyside_datas
binaries += pyside_binaries
hiddenimports += pyside_hidden

a = Analysis(
    ["../src/mmwave_v2i_sim/cli.py"],
    pathex=["../src"],
    binaries=binaries,
    datas=datas + [("../configs", "configs")],
    hiddenimports=hiddenimports + ["mmwave_v2i_sim"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="mmwave-v2i-sim",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="mmwave-v2i-sim",
)
