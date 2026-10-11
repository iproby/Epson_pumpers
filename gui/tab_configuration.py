#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration Tab — MAC address, Serial Number, Printer Config viewer."""

import customtkinter as ctk
from tkinter import messagebox
from i18n import i18n


class ConfigurationTab:
    """Tab for reading/writing MAC address, serial number, and viewing printer config."""

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
        i18n.on_language_change(lambda _: self.update_language())

    def setup_ui(self):
        # Scrollable container
        self.scroll = ctk.CTkScrollableFrame(self.parent)
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.scroll.columnconfigure(0, weight=1)

        row = 0

        # ── MAC Address Section ──
        self.mac_frame = ctk.CTkFrame(self.scroll)
        self.mac_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=(5, 2))
        self.mac_frame.columnconfigure(1, weight=1)

        self.mac_label = ctk.CTkLabel(self.mac_frame, text=i18n.t("mac_address"), font=ctk.CTkFont(size=14, weight="bold"))
        self.mac_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(8, 4))

        self.mac_current_label = ctk.CTkLabel(self.mac_frame, text=i18n.t("current_mac"))
        self.mac_current_label.grid(row=1, column=0, sticky="w", padx=10, pady=2)
        self.mac_current_value = ctk.CTkLabel(self.mac_frame, text="—", font=ctk.CTkFont(family="Courier"))
        self.mac_current_value.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.mac_read_btn = ctk.CTkButton(self.mac_frame, text=i18n.t("read_value"), width=80, command=self.read_mac)
        self.mac_read_btn.grid(row=1, column=2, padx=10, pady=2)

        self.mac_new_label = ctk.CTkLabel(self.mac_frame, text=i18n.t("new_mac"))
        self.mac_new_label.grid(row=2, column=0, sticky="w", padx=10, pady=2)
        self.mac_entry = ctk.CTkEntry(self.mac_frame, placeholder_text="AA:BB:CC:DD:EE:FF")
        self.mac_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.mac_write_btn = ctk.CTkButton(self.mac_frame, text=i18n.t("write_value"), width=80, command=self.write_mac,
                                           fg_color="#d35400", hover_color="#e67e22")
        self.mac_write_btn.grid(row=2, column=2, padx=10, pady=(2, 8))

        row += 1

        # ── Serial Number Section ──
        self.serial_frame = ctk.CTkFrame(self.scroll)
        self.serial_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        self.serial_frame.columnconfigure(1, weight=1)

        self.serial_label = ctk.CTkLabel(self.serial_frame, text=i18n.t("serial_number"), font=ctk.CTkFont(size=14, weight="bold"))
        self.serial_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(8, 4))

        self.serial_current_label = ctk.CTkLabel(self.serial_frame, text=i18n.t("current_serial"))
        self.serial_current_label.grid(row=1, column=0, sticky="w", padx=10, pady=2)
        self.serial_current_value = ctk.CTkLabel(self.serial_frame, text="—", font=ctk.CTkFont(family="Courier"))
        self.serial_current_value.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.serial_read_btn = ctk.CTkButton(self.serial_frame, text=i18n.t("read_value"), width=80, command=self.read_serial)
        self.serial_read_btn.grid(row=1, column=2, padx=10, pady=2)

        self.serial_new_label = ctk.CTkLabel(self.serial_frame, text=i18n.t("new_serial"))
        self.serial_new_label.grid(row=2, column=0, sticky="w", padx=10, pady=2)
        self.serial_entry = ctk.CTkEntry(self.serial_frame, placeholder_text="W1BK012345")
        self.serial_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.serial_write_btn = ctk.CTkButton(self.serial_frame, text=i18n.t("write_value"), width=80, command=self.write_serial,
                                              fg_color="#d35400", hover_color="#e67e22")
        self.serial_write_btn.grid(row=2, column=2, padx=10, pady=(2, 8))

        row += 1

        # ── Printer Config Viewer ──
        self.config_frame = ctk.CTkFrame(self.scroll)
        self.config_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        self.config_frame.columnconfigure(0, weight=1)

        self.config_label = ctk.CTkLabel(self.config_frame, text=i18n.t("printer_config"), font=ctk.CTkFont(size=14, weight="bold"))
        self.config_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 4))

        btn_row = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        btn_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=2)
        self.show_config_btn = ctk.CTkButton(btn_row, text=i18n.t("show_config"), command=self.show_config)
        self.show_config_btn.pack(side="left", padx=(0, 5))
        self.show_keys_btn = ctk.CTkButton(btn_row, text=i18n.t("show_keys"), command=self.show_keys)
        self.show_keys_btn.pack(side="left", padx=5)

        self.config_text = ctk.CTkTextbox(self.config_frame, height=250, font=ctk.CTkFont(family="Courier", size=12))
        self.config_text.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(2, 8))

    def read_mac(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        def _read():
            try:
                mac = self.app.printer.get_wifi_mac_address()
                self.parent.after(0, lambda: self.mac_current_value.configure(text=mac or "—"))
                self.app.log(f"MAC: {mac}", "info")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_read)

    def write_mac(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        mac_str = self.mac_entry.get().strip()
        if not mac_str:
            return

        if not messagebox.askyesno(i18n.t("confirm_action"), i18n.t("eeprom_confirm")):
            return

        def _write():
            try:
                # Convert MAC string to int list
                mac_parts = mac_str.replace("-", ":").split(":")
                mac_ints = [int(p, 16) for p in mac_parts]
                if len(mac_ints) != 6:
                    raise ValueError("MAC address must have 6 octets")

                conf = self.app.printer.expand_printer_conf(
                    self.app.printer.PRINTER_CONFIG.get(self.app.printer.model, {})
                )
                if "wifi_mac_address" not in conf:
                    raise ValueError("This printer model does not support MAC address writing")

                mac_addrs = list(conf["wifi_mac_address"])
                for i, addr in enumerate(mac_addrs):
                    self.app.printer.write_eeprom(addr, mac_ints[i])

                self.app.log(i18n.t("success"), "info")
                self.read_mac()
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_write)

    def read_serial(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        def _read():
            try:
                serial = self.app.printer.get_serial_number()
                self.parent.after(0, lambda: self.serial_current_value.configure(text=serial or "—"))
                self.app.log(f"Serial: {serial}", "info")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_read)

    def write_serial(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        serial_str = self.serial_entry.get().strip()
        if not serial_str:
            return

        if not messagebox.askyesno(i18n.t("confirm_action"), i18n.t("eeprom_confirm")):
            return

        def _write():
            try:
                conf = self.app.printer.expand_printer_conf(
                    self.app.printer.PRINTER_CONFIG.get(self.app.printer.model, {})
                )
                if "serial_number" not in conf:
                    raise ValueError("This printer model does not support serial number writing")

                serial_addrs = list(conf["serial_number"])
                serial_bytes = serial_str.encode("ascii")
                if len(serial_bytes) > len(serial_addrs):
                    raise ValueError(f"Serial number too long (max {len(serial_addrs)} chars)")

                serial_bytes = serial_bytes.ljust(len(serial_addrs), b'\x00')
                for i, addr in enumerate(serial_addrs):
                    self.app.printer.write_eeprom(addr, serial_bytes[i])

                self.app.log(i18n.t("success"), "info")
                self.read_serial()
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_write)

    def show_config(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        def _show():
            try:
                conf = self.app.printer.expand_printer_conf(
                    self.app.printer.PRINTER_CONFIG.get(self.app.printer.model, {})
                )
                import pprint
                text = pprint.pformat(conf, width=100)

                def _update():
                    self.config_text.delete("0.0", "end")
                    self.config_text.insert("0.0", text)

                self.parent.after(0, _update)
                self.app.log(i18n.t("success"), "info")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_show)

    def show_keys(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        def _show():
            try:
                keys = self.app.printer.list_known_keys()
                text = str(keys) if keys else "No keys found for this model."

                def _update():
                    self.config_text.delete("0.0", "end")
                    self.config_text.insert("0.0", text)

                self.parent.after(0, _update)
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_show)

    def update_language(self):
        try:
            self.mac_label.configure(text=i18n.t("mac_address"))
            self.mac_current_label.configure(text=i18n.t("current_mac"))
            self.mac_read_btn.configure(text=i18n.t("read_value"))
            self.mac_new_label.configure(text=i18n.t("new_mac"))
            self.mac_write_btn.configure(text=i18n.t("write_value"))
            self.serial_label.configure(text=i18n.t("serial_number"))
            self.serial_current_label.configure(text=i18n.t("current_serial"))
            self.serial_read_btn.configure(text=i18n.t("read_value"))
            self.serial_new_label.configure(text=i18n.t("new_serial"))
            self.serial_write_btn.configure(text=i18n.t("write_value"))
            self.config_label.configure(text=i18n.t("printer_config"))
            self.show_config_btn.configure(text=i18n.t("show_config"))
            self.show_keys_btn.configure(text=i18n.t("show_keys"))
        except Exception:
            pass
