"""Unit tests for easy_reset helpers (no printer, no GUI)."""
import unittest

from easy_reset import is_valid_printer_host


class EasyResetHelpersTests(unittest.TestCase):
    def test_valid_ipv4(self):
        self.assertEqual(is_valid_printer_host("192.168.1.50"), "192.168.1.50")
        self.assertEqual(is_valid_printer_host(" 10.0.0.1 "), "10.0.0.1")

    def test_invalid_ipv4(self):
        self.assertIsNone(is_valid_printer_host(""))
        self.assertIsNone(is_valid_printer_host("999.1.1.1"))
        self.assertIsNone(is_valid_printer_host("not an ip; rm -rf /"))
        self.assertIsNone(is_valid_printer_host("http://example.com"))

    def test_hostname(self):
        self.assertEqual(is_valid_printer_host("printer.local"), "printer.local")


if __name__ == "__main__":
    unittest.main()
