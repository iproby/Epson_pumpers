#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Application Window for Epson Printer Configuration GUI.
Modern cross-platform interface powered by CustomTkinter.
"""

import os
import sys
import threading


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

from tkinter import messagebox
from typing import Callable, Optional
import customtkinter as ctk

from epson_print_conf import EpsonPrinter
from find_printers import PrinterScanner
from i18n import i18n

from gui.tab_about import AboutTab
from gui.tab_configuration import ConfigurationTab
from gui.tab_console import ConsoleTab
from gui.tab_eeprom import EEPROMTab
from gui.tab_maintenance import MaintenanceTab
from gui.tab_status import StatusTab
from gui.tab_tests import TestsTab

# Set default appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class EpsonPrinterApp(ctk.CTk):
    """Modern CustomTkinter GUI for Epson Printer Configuration."""

    def __init__(self):
        super().__init__()

        self.printer: Optional[EpsonPrinter] = None
        self.scanner = PrinterScanner()
        self._valid_models = []
        self._init_printer_models()

        # Window setup
        self.title("🖨️ " + i18n.t("app_title") + " v8.0")
        self.geometry("1060x740")
        self.minsize(880, 600)

        # Set window icon
        self._init_window_icon()

        # Tabs registry
        self.tab_buttons = {}
        self.tab_frames = {}
        self.tab_instances = {}
        self.active_tab_name = "status"

        self._build_top_bar()
        self._build_body()
        self._build_status_bar()

        # Initialize tabs
        self._init_tabs()
        self.select_tab("status")

        # Listen to language changes
        i18n.on_language_change(lambda _: self._update_language())

    def _init_printer_models(self):
        """Preload supported printer model names."""
        try:
            temp = EpsonPrinter()
            self._valid_models = sorted(temp.valid_printers)
        except Exception:
            self._valid_models = []

    def _init_window_icon(self):
        """Configure application window icon."""
        try:
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
            ico_file = os.path.join(assets_dir, "app_icon.ico")
            png_file = os.path.join(assets_dir, "icon_1024.png")

            if sys.platform.startswith("win") and os.path.exists(ico_file):
                self.iconbitmap(ico_file)
            elif os.path.exists(png_file):
                from PIL import ImageTk, Image
                # Scale for window icon (64x64)
                pil_img = Image.open(png_file).resize((64, 64), Image.Resampling.LANCZOS)
                self._app_icon_tk = ImageTk.PhotoImage(pil_img)
                self.iconphoto(False, self._app_icon_tk)
        except Exception:
            pass

    def _build_top_bar(self):
        """Top bar: Model selection, IP address, Detect, Connect, Language & Theme."""
        self.top_bar = ctk.CTkFrame(self, corner_radius=0, height=52)
        self.top_bar.pack(side="top", fill="x", padx=0, pady=0)
        self.top_bar.columnconfigure(3, weight=1)

        # Model Label & Combobox
        self.model_lbl = ctk.CTkLabel(self.top_bar, text=i18n.t("printer_model"), font=ctk.CTkFont(size=12, weight="bold"))
        self.model_lbl.grid(row=0, column=0, padx=(12, 4), pady=10, sticky="w")

        default_model = self._valid_models[0] if self._valid_models else ""
        self.model_combo = ctk.CTkComboBox(
            self.top_bar,
            values=self._valid_models,
            width=180,
            font=ctk.CTkFont(size=12),
        )
        if default_model:
            self.model_combo.set(default_model)
        self.model_combo.grid(row=0, column=1, padx=4, pady=10, sticky="w")

        # IP Label & Entry
        self.ip_lbl = ctk.CTkLabel(self.top_bar, text=i18n.t("ip_address"), font=ctk.CTkFont(size=12, weight="bold"))
        self.ip_lbl.grid(row=0, column=2, padx=(12, 4), pady=10, sticky="w")

        self.ip_entry = ctk.CTkEntry(
            self.top_bar,
            placeholder_text="192.168.1.50",
            width=150,
            font=ctk.CTkFont(size=12),
        )
        self.ip_entry.grid(row=0, column=3, padx=4, pady=10, sticky="w")

        # Detect Button
        self.detect_btn = ctk.CTkButton(
            self.top_bar,
            text=i18n.t("detect_printers"),
            width=90,
            command=self.detect_printers,
        )
        self.detect_btn.grid(row=0, column=4, padx=4, pady=10)

        # Connect Button
        self.connect_btn = ctk.CTkButton(
            self.top_bar,
            text=i18n.t("connect"),
            width=90,
            fg_color="#27ae60",
            hover_color="#2ecc71",
            command=self.toggle_connection,
        )
        self.connect_btn.grid(row=0, column=5, padx=4, pady=10)

        # Language Menu
        self.lang_menu = ctk.CTkOptionMenu(
            self.top_bar,
            values=["English", "Русский"],
            width=95,
            command=self._on_language_select,
        )
        self.lang_menu.set("English" if i18n.lang == "en" else "Русский")
        self.lang_menu.grid(row=0, column=6, padx=4, pady=10)

        # Theme Menu
        self.theme_menu = ctk.CTkOptionMenu(
            self.top_bar,
            values=["Dark", "Light", "System"],
            width=85,
            command=self._on_theme_select,
        )
        self.theme_menu.set("Dark")
        self.theme_menu.grid(row=0, column=7, padx=(4, 12), pady=10)

    def _build_body(self):
        """Split window into left navigation bar and main view."""
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(side="top", fill="both", expand=True, padx=0, pady=0)
        self.body.columnconfigure(1, weight=1)
        self.body.rowconfigure(0, weight=1)

        # Left Sidebar
        self.sidebar = ctk.CTkFrame(self.body, width=170, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)

        # Main Content Frame
        self.content_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

    def _build_status_bar(self):
        """Bottom status bar with status indicator dot and log text."""
        self.status_bar = ctk.CTkFrame(self, height=28, corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x", padx=0, pady=0)
        self.status_bar.columnconfigure(1, weight=1)

        self.status_dot = ctk.CTkLabel(
            self.status_bar,
            text="●",
            text_color="#95a5a6",
            font=ctk.CTkFont(size=14),
            width=20,
        )
        self.status_dot.grid(row=0, column=0, padx=(10, 2), pady=3, sticky="w")

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text=i18n.t("status_bar_disconnected"),
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self.status_label.grid(row=0, column=1, padx=4, pady=3, sticky="w")

        self.busy_label = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="e",
        )
        self.busy_label.grid(row=0, column=2, padx=12, pady=3, sticky="e")

    def _init_tabs(self):
        """Initialize all tab classes and sidebar buttons."""
        tabs_spec = [
            ("status", "tab_status", StatusTab),
            ("maintenance", "tab_maintenance", MaintenanceTab),
            ("configuration", "tab_configuration", ConfigurationTab),
            ("eeprom", "tab_eeprom", EEPROMTab),
            ("tests", "tab_tests", TestsTab),
            ("console", "tab_console", ConsoleTab),
            ("about", "tab_about", AboutTab),
        ]

        for i, (tab_id, i18n_key, tab_class) in enumerate(tabs_spec):
            # Sidebar button
            btn = ctk.CTkButton(
                self.sidebar,
                text=i18n.t(i18n_key),
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
                fg_color="transparent",
                hover_color="#34495e",
                height=38,
                corner_radius=6,
                command=lambda tid=tab_id: self.select_tab(tid),
            )
            btn.pack(side="top", fill="x", padx=6, pady=3)
            self.tab_buttons[tab_id] = (btn, i18n_key)

            # Container frame
            frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            self.tab_frames[tab_id] = frame

            # Instantiate tab
            instance = tab_class(parent=frame, app=self)
            self.tab_instances[tab_id] = instance

    def select_tab(self, tab_id: str):
        """Display the chosen tab and update sidebar highlight."""
        if tab_id not in self.tab_frames:
            return

        self.active_tab_name = tab_id

        # Hide all tab frames
        for tid, frame in self.tab_frames.items():
            frame.grid_forget()

        # Show selected tab
        self.tab_frames[tab_id].grid(row=0, column=0, sticky="nsew")

        # Update button styles
        for tid, (btn, _) in self.tab_buttons.items():
            if tid == tab_id:
                btn.configure(fg_color=["#3b8ed0", "#1f538d"])
            else:
                btn.configure(fg_color="transparent")

    # ── Connection Management ──

    def toggle_connection(self):
        """Connect or disconnect from the chosen printer."""
        if self.printer is not None:
            self.disconnect_printer()
        else:
            self.connect_printer()

    def connect_printer(self):
        """Establish printer session."""
        model = self.model_combo.get().strip()
        ip = self.ip_entry.get().strip()

        if not ip:
            messagebox.showwarning(i18n.t("warning"), i18n.t("not_connected"))
            return

        self.log(i18n.t("please_wait"), "busy")
        self.status_dot.configure(text_color="#f39c12")  # Orange

        def _connect():
            try:
                p = EpsonPrinter(model=model, hostname=ip)
                # Verify link by checking serial number or model
                sn = p.get_serial_number()
                self.printer = p

                def _on_success():
                    self.connect_btn.configure(
                        text=i18n.t("disconnect"),
                        fg_color="#c0392b",
                        hover_color="#e74c3c",
                    )
                    self.status_dot.configure(text_color="#2ecc71")  # Green
                    status_msg = i18n.t("status_bar_connected", model=model or "Printer", ip=ip)
                    self.status_label.configure(text=status_msg)
                    self.log(status_msg, "info")

                    # Auto refresh status tab
                    if "status" in self.tab_instances:
                        self.tab_instances["status"].refresh_status()

                self.after(0, _on_success)
            except Exception as e:
                self.after(0, lambda: self._on_connect_failed(str(e)))

        self.run_threaded(_connect)

    def _on_connect_failed(self, error_msg: str):
        self.printer = None
        self.status_dot.configure(text_color="#e74c3c")
        self.status_label.configure(text=f"{i18n.t('error')}: {error_msg}")
        self.log(f"Connection failed: {error_msg}", "error")
        messagebox.showerror(i18n.t("error"), f"Failed to connect to printer:\n{error_msg}")

    def disconnect_printer(self):
        """Disconnect and reset state."""
        self.printer = None
        self.connect_btn.configure(
            text=i18n.t("connect"),
            fg_color="#27ae60",
            hover_color="#2ecc71",
        )
        self.status_dot.configure(text_color="#95a5a6")
        self.status_label.configure(text=i18n.t("status_bar_disconnected"))
        self.log(i18n.t("disconnected"), "info")

    def detect_printers(self):
        """Scan network for printers."""
        self.log(i18n.t("scanning_network"), "busy")
        self.detect_btn.configure(state="disabled")

        def _scan():
            try:
                ip_hint = self.ip_entry.get().strip()
                printers = self.scanner.get_all_printers(ip_hint)

                def _done():
                    self.detect_btn.configure(state="normal")
                    if printers:
                        found_count = len(printers)
                        self.log(f"{found_count} {i18n.t('printers_found')}", "info")
                        # Pick first printer
                        first = printers[0]
                        if first.get("ip"):
                            self.ip_entry.delete(0, "end")
                            self.ip_entry.insert(0, first["ip"])
                        if first.get("name") and first["name"] in self._valid_models:
                            self.model_combo.set(first["name"])

                        msg = "\n".join([f"• {p.get('name', 'Printer')} @ {p.get('ip')}" for p in printers])
                        messagebox.showinfo(f"{found_count} {i18n.t('printers_found')}", msg)
                    else:
                        self.log(i18n.t("no_printers_found"), "warning")
                        messagebox.showinfo(i18n.t("info"), i18n.t("no_printers_found"))

                self.after(0, _done)
            except Exception as e:
                self.after(0, lambda: self.detect_btn.configure(state="normal"))
                self.log(f"Scan error: {e}", "error")

        self.run_threaded(_scan)

    # ── Thread Worker & Logging ──

    def run_threaded(self, target: Callable, on_done: Optional[Callable] = None, on_error: Optional[Callable] = None):
        """Run a task in a daemon background thread."""
        self.busy_label.configure(text=i18n.t("status_bar_busy"))

        def _wrapper():
            err = None
            res = None
            try:
                res = target()
            except Exception as e:
                err = e
            finally:
                def _callback():
                    self.busy_label.configure(text="")
                    if err and on_error:
                        on_error(err)
                    elif not err and on_done:
                        on_done(res)

                self.after(0, _callback)

        thread = threading.Thread(target=_wrapper, daemon=True)
        thread.start()

    def log(self, message: str, level: str = "info"):
        """Output a message to status bar."""
        self.status_label.configure(text=message)

    def get_current_ip(self) -> str:
        """Return currently entered IP."""
        return self.ip_entry.get().strip()

    # ── Language & Theme Handlers ──

    def _on_language_select(self, choice: str):
        i18n.lang = "ru" if choice == "Русский" else "en"

    def _on_theme_select(self, choice: str):
        ctk.set_appearance_mode(choice)

    def _update_language(self):
        """Refresh UI texts on language switch."""
        self.title("🖨️ " + i18n.t("app_title") + " v8.0")
        self.model_lbl.configure(text=i18n.t("printer_model"))
        self.ip_lbl.configure(text=i18n.t("ip_address"))
        self.detect_btn.configure(text=i18n.t("detect_printers"))

        if self.printer is None:
            self.connect_btn.configure(text=i18n.t("connect"))
            self.status_label.configure(text=i18n.t("status_bar_disconnected"))
        else:
            self.connect_btn.configure(text=i18n.t("disconnect"))
            self.status_label.configure(
                text=i18n.t("status_bar_connected", model=self.printer.model or "Printer", ip=self.get_current_ip())
            )

        for tid, (btn, i18n_key) in self.tab_buttons.items():
            btn.configure(text=i18n.t(i18n_key))

    def run(self):
        """Launch mainloop."""
        self.mainloop()


if __name__ == "__main__":
    app = EpsonPrinterApp()
    app.run()
