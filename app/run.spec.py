# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_submodules

# File utama Python
main_script = 'run.py'

# Include semua modul di dalam folder app
hidden_imports = collect_submodules('app')

# Data files yang mau disertakan (source, target folder di dalam exe)
datas = [
    ('log.db', '.'),               # database di root exe
    ('requirements.txt', '.'),     # file requirements
    ('app', 'app'),                 # folder app
]

block_cipher = None

a = Analysis(
    [main_script],
    pathex=[os.path.abspath('.')],  # lokasi project
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='network_monitoring_project',  # nama exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True  # ubah ke False kalau mau tanpa console
)
