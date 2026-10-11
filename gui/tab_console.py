#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Console Tab — Interactive Python API Playground for EpsonPrinter."""

import io
import pprint
import sys
import traceback
import customtkinter as ctk
from i18n import i18n


class ConsoleTab:
    """Tab providing an interactive Python sandbox to inspect and command the printer."""

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.history = []
        self.history_index = -1
        self.setup_ui()
        i18n.on_language_change(lambda _: self.update_language())

    def setup_ui(self):
        self.container = ctk.CTkFrame(self.parent)
        self.container.pack(fill="both", expand=True, padx=5, pady=5)
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(2, weight=1)

        # ── Help / Banner ──
        self.help_lbl = ctk.CTkLabel(
            self.container,
            text=i18n.t("console_help"),
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
            wraplength=650,
            justify="left",
        )
        self.help_lbl.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 2))

        # ── Quick Snippets Bar ──
        snippet_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        snippet_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=2)

        snippets = [
            ("Status", "pprint(printer.get_printer_status())"),
            ("Waste", "pprint(printer.get_waste_ink_levels())"),
            ("Inks", "pprint(printer.get_cartridges())"),
            ("Serial", "print(printer.get_serial_number())"),
            ("Stats", "pprint(printer.stats())"),
        ]
        for name, code in snippets:
            btn = ctk.CTkButton(
                snippet_bar,
                text=name,
                width=65,
                height=26,
                font=ctk.CTkFont(size=11),
                command=lambda c=code: self._insert_snippet(c),
            )
            btn.pack(side="left", padx=2)

        # ── Output Display ──
        self.output_text = ctk.CTkTextbox(
            self.container,
            font=ctk.CTkFont(family="Courier", size=12),
            wrap="word",
        )
        self.output_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=4)
        self.output_text.insert("0.0", ">>> EpsonPrinter Interactive Console\n>>> Type Python code below and press 'Execute' (or Ctrl+Enter)\n")

        # ── Input Area ──
        input_frame = ctk.CTkFrame(self.container)
        input_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(2, 8))
        input_frame.columnconfigure(0, weight=1)

        self.input_text = ctk.CTkTextbox(
            input_frame,
            height=70,
            font=ctk.CTkFont(family="Courier", size=12),
        )
        self.input_text.grid(row=0, column=0, sticky="ew", padx=(6, 4), pady=6)
        self.input_text.bind("<Control-Return>", lambda e: self.execute_code())

        # Action Buttons
        btn_box = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_box.grid(row=0, column=1, sticky="ns", padx=(2, 6), pady=6)

        self.exec_btn = ctk.CTkButton(
            btn_box,
            text=f"▶ {i18n.t('execute')}",
            width=80,
            command=self.execute_code,
        )
        self.exec_btn.pack(side="top", pady=2)

        self.clear_btn = ctk.CTkButton(
            btn_box,
            text=i18n.t("clear"),
            width=80,
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
            command=self.clear_output,
        )
        self.clear_btn.pack(side="top", pady=2)

    def _insert_snippet(self, code: str):
        self.input_text.delete("0.0", "end")
        self.input_text.insert("0.0", code)
        self.input_text.focus()

    def clear_output(self):
        self.output_text.delete("0.0", "end")

    def execute_code(self):
        code = self.input_text.get("0.0", "end").strip()
        if not code:
            return

        self.input_text.delete("0.0", "end")
        self._append_output(f">>> {code}\n")

        # Environment setup
        local_scope = {
            "printer": self.app.printer,
            "app": self.app,
            "i18n": i18n,
            "pprint": pprint.pprint,
            "sys": sys,
        }

        def _run():
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            redirected_output = io.StringIO()
            sys.stdout = redirected_output
            sys.stderr = redirected_output
            try:
                # Try eval first (for expressions)
                try:
                    compiled = compile(code, "<console>", "eval")
                    res = eval(compiled, globals(), local_scope)
                    if res is not None:
                        pprint.pprint(res, stream=redirected_output)
                except SyntaxError:
                    # Fall back to exec for multi-line statements
                    compiled = compile(code, "<console>", "exec")
                    exec(compiled, globals(), local_scope)
            except Exception:
                traceback.print_exc(file=redirected_output)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

            output_str = redirected_output.getvalue()
            if output_str:
                self.parent.after(0, lambda: self._append_output(output_str))

        self.app.run_threaded(_run)

    def _append_output(self, text: str):
        self.output_text.insert("end", text)
        self.output_text.see("end")

    def update_language(self):
        try:
            self.help_lbl.configure(text=i18n.t("console_help"))
            self.exec_btn.configure(text=f"▶ {i18n.t('execute')}")
            self.clear_btn.configure(text=i18n.t("clear"))
        except Exception:
            pass
