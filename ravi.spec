# -*- mode: python ; coding: utf-8 -*-
# Derleme:  pyinstaller --noconfirm ravi.spec
# Çıktı  :  dist/RAVI.exe (Windows)  veya  dist/RAVI (Linux)
import os
import sys

# Logo dosyaları varsa pakete eklenir (yoksa uygulama simgesiz çalışır)
datas = [(f, ".") for f in ("ravi_logo.ico", "ravi_logo.png") if os.path.exists(f)]
ikon = "ravi_logo.ico" if sys.platform.startswith("win") and os.path.exists("ravi_logo.ico") else None

a = Analysis(
    ["ravi.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="RAVI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,   # siyah komut penceresi açılmasın
    icon=ikon,
)
