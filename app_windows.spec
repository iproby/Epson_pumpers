# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification for building standalone Windows executable."""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

datas = []
if os.path.exists("epson_print_conf.pickle"):
    datas.append(("epson_print_conf.pickle", "."))
if os.path.exists("devices.xml"):
    datas.append(("devices.xml", "."))
if os.path.exists("assets"):
    datas.append(("assets", "assets"))

datas += collect_data_files("customtkinter")

hiddenimports = [
    "customtkinter",
    "darkdetect",
    "PIL",
    "PIL._tkinter_finder",
    "pysnmp",
    "pysnmp_sync_adapter",
    "yaml",
    "tomli",
    "hexdump2",
    "pyprintlpr",
    "epson_escp2",
    "tkinter",
    "i18n",
    "gui",
    "gui.app",
    "gui.tab_status",
    "gui.tab_maintenance",
    "gui.tab_configuration",
    "gui.tab_eeprom",
    "gui.tab_tests",
    "gui.tab_console",
    "gui.tab_about",
]
hiddenimports += collect_submodules("customtkinter")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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

exe_icon = "assets/app_icon.ico" if os.path.exists("assets/app_icon.ico") else None
version_file = "version_info.txt" if os.path.exists("version_info.txt") else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="epson_print_conf",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=exe_icon,
    version=version_file,
)
