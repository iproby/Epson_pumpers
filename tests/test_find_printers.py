"""Unit tests that do not talk to a real printer."""
import sys
import unittest
from unittest.mock import MagicMock, patch

# epson_print_conf pulls in pysnmp; mock it so tests run without deps.
sys.modules.setdefault("epson_print_conf", MagicMock())

from find_printers import PrinterScanner  # noqa: E402


class PrinterScannerTests(unittest.TestCase):
    def setUp(self):
        self.scanner = PrinterScanner()

    def test_check_printer_open(self):
        with patch("find_printers.socket.create_connection") as conn:
            conn.return_value.__enter__.return_value = MagicMock()
            self.assertTrue(self.scanner.check_printer("192.168.1.50", 9100))
            conn.assert_called_once()

    def test_check_printer_closed(self):
        with patch(
            "find_printers.socket.create_connection",
            side_effect=OSError("refused"),
        ):
            self.assertFalse(self.scanner.check_printer("192.168.1.50", 9100))

    def test_full_ipv4_miss_does_not_scan_subnet(self):
        with patch.object(self.scanner, "scan_ip", return_value=None) as scan:
            with patch("find_printers.socket.gethostbyname_ex") as hostex:
                result = self.scanner.get_all_printers("192.168.1.50")
        self.assertEqual(result, [])
        scan.assert_called_once_with("192.168.1.50")
        hostex.assert_not_called()

    def test_named_printer_returned(self):
        with patch.object(
            self.scanner,
            "scan_ip",
            return_value={"ip": "10.0.0.8", "hostname": "epson"},
        ):
            with patch.object(
                self.scanner, "get_printer_name", return_value="XP-205"
            ):
                result = self.scanner.get_all_printers("10.0.0.8")
        self.assertEqual(
            result,
            [{"ip": "10.0.0.8", "hostname": "epson", "name": "XP-205"}],
        )


if __name__ == "__main__":
    unittest.main()
