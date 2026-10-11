"""Unit tests for i18n module."""
import unittest

from i18n import I18n


class I18nTests(unittest.TestCase):
    def setUp(self):
        self.i18n = I18n("en")

    def test_default_language(self):
        self.assertEqual(self.i18n.lang, "en")
        self.assertEqual(self.i18n.t("connect"), "Connect")

    def test_switch_language(self):
        self.i18n.lang = "ru"
        self.assertEqual(self.i18n.lang, "ru")
        self.assertEqual(self.i18n.t("connect"), "Подключить")

    def test_unknown_key_returns_bracketed(self):
        self.assertEqual(self.i18n.t("some_unknown_key_xyz"), "[some_unknown_key_xyz]")

    def test_format_parameters(self):
        msg = self.i18n.t("status_bar_connected", model="XP-3150", ip="192.168.1.10")
        self.assertIn("XP-3150", msg)
        self.assertIn("192.168.1.10", msg)

    def test_language_callback(self):
        notified = []
        cb = lambda lang: notified.append(lang)
        self.i18n.on_language_change(cb)
        self.i18n.lang = "ru"
        self.assertEqual(notified, ["ru"])
        self.i18n.remove_callback(cb)
        self.i18n.lang = "en"
        self.assertEqual(notified, ["ru"])  # removed, not called again


if __name__ == "__main__":
    unittest.main()
