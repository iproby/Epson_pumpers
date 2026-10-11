#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Desktop Build Automation Script.
Builds standalone release packages for Windows (.exe), macOS (.app & .dmg), and Linux.
"""

import argparse
import os
import shutil
import subprocess
import sys
import zipfile

# Ensure utf-8 stdout encoding on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def ensure_icons(project_root: str):
    """Ensure assets/app_icon.ico and app_icon.icns exist before building."""
    assets_dir = os.path.join(project_root, "assets")
    ico_path = os.path.join(assets_dir, "app_icon.ico")
    icns_path = os.path.join(assets_dir, "app_icon.icns")

    if not os.path.exists(ico_path) or not os.path.exists(icns_path):
        print("Generating application icons...")
        icon_gen = os.path.join(project_root, "generate_icons.py")
        subprocess.check_call([sys.executable, icon_gen])


def _setup_environment():
    """Setup necessary environment variables for PyInstaller."""
    if sys.platform == "darwin":
        for tcl_candidate in [
            "/usr/local/munki/Python.framework/Versions/3.12/lib/tcl8.6",
            "/opt/homebrew/lib/tcl8.6",
            "/Library/Frameworks/Python.framework/Versions/3.12/lib/tcl8.6",
        ]:
            if "TCL_LIBRARY" not in os.environ and os.path.exists(tcl_candidate):
                os.environ["TCL_LIBRARY"] = tcl_candidate
                break
        for tk_candidate in [
            "/usr/local/munki/Python.framework/Versions/3.12/lib/tk8.6",
            "/opt/homebrew/lib/tk8.6",
            "/Library/Frameworks/Python.framework/Versions/3.12/lib/tk8.6",
        ]:
            if "TK_LIBRARY" not in os.environ and os.path.exists(tk_candidate):
                os.environ["TK_LIBRARY"] = tk_candidate
                break


def build():
    parser = argparse.ArgumentParser(description="Build Epson Printer Configuration standalone package")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before packaging")
    parser.add_argument("--spec", default=None, help="PyInstaller spec file to use (default: platform-specific)")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_root, "dist")
    build_dir = os.path.join(project_root, "build")

    _setup_environment()
    ensure_icons(project_root)

    if args.spec:
        spec_file = args.spec
    elif sys.platform.startswith("win"):
        spec_file = "app_windows.spec"
    else:
        spec_file = "app.spec"

    if args.clean:
        print("Cleaning previous build artifacts...")
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

    print(f"Building on platform: {sys.platform} using {spec_file}...")
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", spec_file]
    ret = subprocess.call(cmd, cwd=project_root)
    if ret != 0:
        print(f"Build failed with exit code {ret}", file=sys.stderr)
        sys.exit(ret)

    print("\n[OK] PyInstaller build succeeded!")

    # Post-packaging steps
    if sys.platform == "darwin":
        app_path = os.path.join(dist_dir, "EpsonPrinterConfig.app")
        if os.path.exists(app_path):
            # 1. Create ZIP archive
            zip_dest = os.path.join(dist_dir, "EpsonPrinterConfig-macos.zip")
            print(f"Archiving macOS app bundle to {zip_dest}...")
            cmd_zip = ["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", app_path, zip_dest]
            subprocess.call(cmd_zip)
            print(f"[OK] Created {zip_dest}")

            # 2. Create DMG Disk Image if hdiutil is present
            if shutil.which("hdiutil"):
                dmg_dest = os.path.join(dist_dir, "EpsonPrinterConfig-v8.0.dmg")
                staging_dir = os.path.join(dist_dir, "dmg_staging")
                if os.path.exists(staging_dir):
                    shutil.rmtree(staging_dir)
                os.makedirs(staging_dir)

                print("Creating macOS DMG disk image...")
                # Copy app into staging
                subprocess.check_call(["ditto", app_path, os.path.join(staging_dir, "EpsonPrinterConfig.app")])
                # Add Applications symlink
                os.symlink("/Applications", os.path.join(staging_dir, "Applications"))

                if os.path.exists(dmg_dest):
                    os.remove(dmg_dest)

                cmd_dmg = [
                    "hdiutil", "create",
                    "-volname", "Epson Printer Config",
                    "-srcfolder", staging_dir,
                    "-ov",
                    "-format", "UDZO",
                    dmg_dest,
                ]
                subprocess.check_call(cmd_dmg)
                shutil.rmtree(staging_dir)
                print(f"[OK] Created DMG: {dmg_dest}")

    elif sys.platform.startswith("win"):
        exe_path = os.path.join(dist_dir, "epson_print_conf.exe")
        if os.path.exists(exe_path):
            zip_dest = os.path.join(dist_dir, "epson_print_conf-windows.zip")
            print(f"Archiving Windows executable to {zip_dest}...")
            with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(exe_path, arcname="epson_print_conf.exe")
            print(f"[OK] Created {zip_dest}")

    elif sys.platform.startswith("linux"):
        bin_path = os.path.join(dist_dir, "epson_print_conf")
        if os.path.exists(bin_path):
            tar_dest = os.path.join(dist_dir, "epson_print_conf-linux.tar.gz")
            print(f"Archiving Linux binary to {tar_dest}...")
            import tarfile
            with tarfile.open(tar_dest, "w:gz") as tar:
                tar.add(bin_path, arcname="epson_print_conf")
            print(f"[OK] Created {tar_dest}")

    print("\nPackage generation complete! Output files are located in 'dist/'.")


if __name__ == "__main__":
    build()
