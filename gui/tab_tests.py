#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests Tab — Print tests, nozzle check, color patterns."""

import customtkinter as ctk
from i18n import i18n


class TestsTab:
    """Tab for print tests and nozzle checks."""

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
        i18n.on_language_change(lambda _: self.update_language())

    def setup_ui(self):
        self.scroll = ctk.CTkScrollableFrame(self.parent)
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.scroll.columnconfigure(0, weight=1)

        row = 0

        # ── Nozzle Check ──
        self.nozzle_frame = ctk.CTkFrame(self.scroll)
        self.nozzle_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=(5, 2))
        self.nozzle_frame.columnconfigure(0, weight=1)

        self.nozzle_label = ctk.CTkLabel(self.nozzle_frame, text=i18n.t("nozzle_check"), font=ctk.CTkFont(size=14, weight="bold"))
        self.nozzle_label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))

        desc = ctk.CTkLabel(self.nozzle_frame, text="Prints a nozzle check pattern to verify print head condition.",
                           wraplength=400, justify="left")
        desc.grid(row=1, column=0, sticky="w", padx=10, pady=2)

        self.nozzle_btn = ctk.CTkButton(self.nozzle_frame, text=i18n.t("start_test"), command=self.nozzle_check)
        self.nozzle_btn.grid(row=2, column=0, sticky="w", padx=10, pady=(2, 8))

        row += 1

        # ── Print Test ──
        self.test_frame = ctk.CTkFrame(self.scroll)
        self.test_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        self.test_frame.columnconfigure(1, weight=1)

        self.test_label = ctk.CTkLabel(self.test_frame, text=i18n.t("print_test"), font=ctk.CTkFont(size=14, weight="bold"))
        self.test_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(8, 4))

        # Test type selector
        ctk.CTkLabel(self.test_frame, text="Test type:").grid(row=1, column=0, sticky="w", padx=10, pady=2)
        self.test_type_var = ctk.StringVar(value="nozzle_check")
        self.test_type_menu = ctk.CTkOptionMenu(
            self.test_frame,
            values=["Nozzle Check", "Color Pattern", "Color + Mono"],
            variable=self.test_type_var,
        )
        self.test_type_menu.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Number of tests
        self.num_label = ctk.CTkLabel(self.test_frame, text=i18n.t("number_of_tests"))
        self.num_label.grid(row=2, column=0, sticky="w", padx=10, pady=2)
        self.num_entry = ctk.CTkEntry(self.test_frame, placeholder_text="1", width=60)
        self.num_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.num_entry.insert(0, "1")

        self.test_btn = ctk.CTkButton(self.test_frame, text=i18n.t("start_test"), command=self.run_test)
        self.test_btn.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(4, 8))

        row += 1

        # ── Results ──
        self.result_frame = ctk.CTkFrame(self.scroll)
        self.result_frame.grid(row=row, column=0, sticky="nsew", padx=5, pady=2)
        self.result_frame.columnconfigure(0, weight=1)
        self.result_frame.rowconfigure(1, weight=1)

        ctk.CTkLabel(self.result_frame, text="Results", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 4))

        self.result_text = ctk.CTkTextbox(self.result_frame, height=200, font=ctk.CTkFont(family="Courier", size=12))
        self.result_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(2, 8))

    def nozzle_check(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        def _run():
            try:
                self.app.printer.print_check_nozzles(type=0)
                self._append_result("Nozzle check pattern sent to printer.")
                self.app.log("Nozzle check sent", "info")
            except Exception as e:
                self._append_result(f"Error: {e}")
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_run)

    def run_test(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        try:
            num_tests = int(self.num_entry.get() or "1")
        except ValueError:
            num_tests = 1

        test_type = self.test_type_var.get()

        def _run():
            try:
                for i in range(num_tests):
                    self._append_result(f"Running test {i + 1}/{num_tests}: {test_type}")

                    if test_type == "Nozzle Check":
                        self.app.printer.print_check_nozzles(type=0)
                    elif test_type == "Color Pattern":
                        self.app.printer.print_test_color_pattern(type=0)
                    elif test_type == "Color + Mono":
                        self.app.printer.print_test_color_pattern(type=1)

                self._append_result(f"All {num_tests} test(s) completed.")
                self.app.log(f"{num_tests} test(s) completed", "info")
            except Exception as e:
                self._append_result(f"Error: {e}")
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_run)

    def _append_result(self, text):
        def _update():
            self.result_text.insert("end", text + "\n")
            self.result_text.see("end")

        self.parent.after(0, _update)

    def update_language(self):
        try:
            self.nozzle_label.configure(text=i18n.t("nozzle_check"))
            self.test_label.configure(text=i18n.t("print_test"))
            self.num_label.configure(text=i18n.t("number_of_tests"))
            self.nozzle_btn.configure(text=i18n.t("start_test"))
            self.test_btn.configure(text=i18n.t("start_test"))
        except Exception:
            pass
