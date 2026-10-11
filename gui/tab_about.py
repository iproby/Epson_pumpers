#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""About Tab — Application details, licenses, links, and system environment info."""

import platform
import sys
import webbrowser
import customtkinter as ctk
from i18n import i18n

APP_VERSION = "8.0"
GITHUB_URL = "https://github.com/Ircama/epson_print_conf"


class AboutTab:
    """Tab presenting application metadata, links, and environment diagnostics."""

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
        i18n.on_language_change(lambda _: self.update_language())

    def setup_ui(self):
        self.container = ctk.CTkFrame(self.parent)
        self.container.pack(fill="both", expand=True, padx=5, pady=5)
        self.container.columnconfigure(0, weight=1)

        row = 0

        # ── App Title & Badge ──
        title_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        title_frame.grid(row=row, column=0, pady=(15, 6))

        self.title_lbl = ctk.CTkLabel(
            title_frame,
            text=f"🖨️ {i18n.t('app_title')}",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.title_lbl.pack()

        self.ver_lbl = ctk.CTkLabel(
            title_frame,
            text=f"Version {APP_VERSION} (Modern Edition)",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.ver_lbl.pack(pady=2)

        row += 1

        # ── Description ──
        desc_box = ctk.CTkFrame(self.container)
        desc_box.grid(row=row, column=0, sticky="ew", padx=20, pady=8)

        self.desc_lbl = ctk.CTkLabel(
            desc_box,
            text=i18n.t("description"),
            font=ctk.CTkFont(size=13),
            justify="center",
        )
        self.desc_lbl.pack(padx=15, pady=12)

        row += 1

        # ── Links & Buttons ──
        btn_box = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_box.grid(row=row, column=0, pady=8)

        self.repo_btn = ctk.CTkButton(
            btn_box,
            text=f"🌐 {i18n.t('github_repo')}",
            command=lambda: webbrowser.open(GITHUB_URL),
        )
        self.repo_btn.pack(side="left", padx=6)

        self.web_btn = ctk.CTkButton(
            btn_box,
            text=f"🖨️ {i18n.t('web_interface')}",
            fg_color="#27ae60",
            hover_color="#2ecc71",
            command=self.open_printer_web,
        )
        self.web_btn.pack(side="left", padx=6)

        row += 1

        # ── Diagnostic / System Information ──
        diag_box = ctk.CTkFrame(self.container)
        diag_box.grid(row=row, column=0, sticky="ew", padx=20, pady=10)
        diag_box.columnconfigure(1, weight=1)

        ctk.CTkLabel(diag_box, text="System Information", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(8, 4)
        )

        sys_info = [
            ("Python", f"{sys.version_split()[0] if hasattr(sys, 'version_split') else sys.version.split()[0]} ({platform.python_implementation()})"),
            ("Platform", f"{platform.system()} {platform.release()} ({platform.machine()})"),
            ("CustomTkinter", ctk.__version__),
        ]

        for i, (k, v) in enumerate(sys_info, start=1):
            ctk.CTkLabel(diag_box, text=f"{k}:", text_color="gray").grid(row=i, column=0, sticky="w", padx=12, pady=1)
            ctk.CTkLabel(diag_box, text=v, font=ctk.CTkFont(family="Courier", size=11)).grid(row=i, column=1, sticky="w", padx=4, pady=1)

        diag_box.rowconfigure(len(sys_info) + 1, weight=1)

    def open_printer_web(self):
        ip = self.app.get_current_ip()
        if ip:
            webbrowser.open(f"http://{ip}")
        else:
            self.app.log(i18n.t("not_connected"), "warning")

    def update_language(self):
        try:
            self.title_lbl.configure(text=f"🖨️ {i18n.t('app_title')}")
            self.desc_lbl.configure(text=i18n.t("description"))
            self.repo_btn.configure(text=f"🌐 {i18n.t('github_repo')}")
            self.web_btn.configure(text=f"🖨️ {i18n.t('web_interface')}")
        except Exception:
            pass
