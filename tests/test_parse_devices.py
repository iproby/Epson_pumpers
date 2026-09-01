"""Unit tests for parse_devices helpers (no devices.xml, no pysnmp)."""
import sys
import unittest
from unittest.mock import MagicMock

sys.modules.setdefault("epson_print_conf", MagicMock())
sys.modules.setdefault("tomli", MagicMock())

from parse_devices import equal_dicts, ordinal, text_to_bytes, text_to_dict  # noqa: E402


class ParseDevicesHelpersTests(unittest.TestCase):
    def test_text_to_bytes_list(self):
        self.assertEqual(text_to_bytes("0a 0b 0c"), [10, 11, 12])

    def test_text_to_bytes_contiguous_range(self):
        # more than 6 contiguous values collapse to a range object
        result = text_to_bytes("01 02 03 04 05 06 07 08")
        self.assertEqual(list(result), list(range(1, 9)))

    def test_text_to_dict(self):
        self.assertEqual(text_to_dict("0a 01 0b 02"), {10: 1, 11: 2})

    def test_equal_dicts_ignores_keys(self):
        a = {"x": 1, "alias": ["A"]}
        b = {"x": 1, "alias": ["B"]}
        self.assertTrue(equal_dicts(a, b, ["alias"]))
        self.assertFalse(equal_dicts(a, b, []))

    def test_ordinal(self):
        self.assertEqual(ordinal(1), "1st")
        self.assertEqual(ordinal(2), "2nd")
        self.assertEqual(ordinal(3), "3rd")
        self.assertEqual(ordinal(4), "4th")
        self.assertEqual(ordinal(11), "11th")
        self.assertEqual(ordinal(21), "21st")


if __name__ == "__main__":
    unittest.main()
