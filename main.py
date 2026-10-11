#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main launcher for Epson Printer Configuration tool.
Runs modern CustomTkinter GUI by default, with option to use classic Tkinter UI.
"""

import argparse
import os
import sys


def _ensure_tk_env():
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


_ensure_tk_env()


def main():
    parser = argparse.ArgumentParser(description="Epson Printer Configuration")
    parser.add_argument(
        "--classic",
        action="store_true",
        help="Launch legacy Tkinter user interface",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Launch interactive command-line reset tool (easy_reset.py)",
    )
    args, unknown = parser.parse_known_args()

    if args.cli:
        from easy_reset import main as cli_main
        sys.exit(cli_main())
    elif args.classic:
        import ui
        ui.main() if hasattr(ui, "main") else None
    else:
        try:
            from gui.app import EpsonPrinterApp
            app = EpsonPrinterApp()
            app.run()
        except ImportError as e:
            print(f"Warning: Modern GUI could not be loaded ({e}). Falling back to classic UI...")
            import ui
            ui.main() if hasattr(ui, "main") else None


if __name__ == "__main__":
    main()
