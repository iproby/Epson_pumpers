"""Unit tests for GUI components and helpers."""

import os
import sys
import unittest
from unittest.mock import MagicMock

# Ensure Tk environment for macOS headless testing
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

from gui.tab_status import _get_ink_color
from gui.tab_eeprom import EEPROMTab
from gui.app import EpsonPrinterApp
from i18n import i18n


class GuiHelpersTests(unittest.TestCase):
    def test_ink_color_mapping(self):
        self.assertEqual(_get_ink_color("Black"), "#2c3e50")
        self.assertEqual(_get_ink_color("Cyan"), "#00a8ff")
        self.assertEqual(_get_ink_color("Magenta"), "#e84393")
        self.assertEqual(_get_ink_color("Yellow"), "#fbc531")
        self.assertEqual(_get_ink_color("Matte Black"), "#1e272e")
        self.assertEqual(_get_ink_color("Light Cyan"), "#4cd137")
        self.assertTrue(_get_ink_color("Unknown Color").startswith("#"))

    def test_eeprom_address_parsing(self):
        tab = EEPROMTab.__new__(EEPROMTab)
        parsed = tab._parse_addresses("0x10, 0x20, 48, 0x0A")
        self.assertEqual(parsed, [16, 32, 48, 10])

    def test_eeprom_address_parsing_with_whitespace(self):
        tab = EEPROMTab.__new__(EEPROMTab)
        parsed = tab._parse_addresses("  0x01 ,  0x02,  ")
        self.assertEqual(parsed, [1, 2])


class AppIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = EpsonPrinterApp()

    def tearDown(self):
        self.app.destroy()

    def test_app_lifecycle_and_title(self):
        self.assertIn("Epson Printer", self.app.title())
        self.assertEqual(self.app.active_tab_name, "status")

    def test_tab_switching(self):
        expected_tabs = ["status", "maintenance", "configuration", "eeprom", "tests", "console", "about"]
        for tab_name in expected_tabs:
            self.app.select_tab(tab_name)
            self.assertEqual(self.app.active_tab_name, tab_name)

    def test_language_switching(self):
        self.app._on_language_select("Русский")
        self.assertIn("Настройка", self.app.title())
        self.app._on_language_select("English")
        self.assertIn("Epson Printer", self.app.title())

    def test_theme_switching(self):
        self.app._on_theme_select("Light")
        self.app._on_theme_select("Dark")
        self.app._on_theme_select("System")


if __name__ == "__main__":
    unittest.main()
