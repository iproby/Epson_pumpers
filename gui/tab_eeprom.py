#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EEPROM Tab — Direct EEPROM read/write, hex dump, detect configuration."""

import customtkinter as ctk
from tkinter import messagebox
from i18n import i18n


class EEPROMTab:
    """Tab for direct EEPROM operations and configuration detection."""

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

        # ── Read EEPROM ──
        self.read_frame = ctk.CTkFrame(self.scroll)
        self.read_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=(5, 2))
        self.read_frame.columnconfigure(1, weight=1)

        self.read_label = ctk.CTkLabel(self.read_frame, text=i18n.t("read_eeprom"), font=ctk.CTkFont(size=14, weight="bold"))
        self.read_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(8, 4))

        self.addr_label = ctk.CTkLabel(self.read_frame, text=i18n.t("address"))
        self.addr_label.grid(row=1, column=0, sticky="w", padx=10, pady=2)
        self.addr_entry = ctk.CTkEntry(self.read_frame, placeholder_text=i18n.t("eeprom_address_hint"))
        self.addr_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.read_btn = ctk.CTkButton(self.read_frame, text=i18n.t("read_value"), width=80, command=self.read_eeprom)
        self.read_btn.grid(row=1, column=2, padx=10, pady=2)

        self.read_result = ctk.CTkTextbox(self.read_frame, height=80, font=ctk.CTkFont(family="Courier", size=12))
        self.read_result.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(2, 8))

        row += 1

        # ── Write EEPROM ──
        self.write_frame = ctk.CTkFrame(self.scroll)
        self.write_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        self.write_frame.columnconfigure(1, weight=1)

        self.write_label = ctk.CTkLabel(self.write_frame, text=i18n.t("write_eeprom"), font=ctk.CTkFont(size=14, weight="bold"))
        self.write_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(8, 4))

        self.write_addr_label = ctk.CTkLabel(self.write_frame, text=i18n.t("value"))
        self.write_addr_label.grid(row=1, column=0, sticky="w", padx=10, pady=2)
        self.write_entry = ctk.CTkEntry(self.write_frame, placeholder_text=i18n.t("eeprom_write_hint"))
        self.write_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.write_btn = ctk.CTkButton(self.write_frame, text=i18n.t("write_value"), width=80, command=self.write_eeprom,
                                       fg_color="#d35400", hover_color="#e67e22")
        self.write_btn.grid(row=1, column=2, padx=10, pady=2)

        self.write_result = ctk.CTkTextbox(self.write_frame, height=60, font=ctk.CTkFont(family="Courier", size=12))
        self.write_result.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(2, 8))

        row += 1

        # ── Dump & Detect ──
        self.tools_frame = ctk.CTkFrame(self.scroll)
        self.tools_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        self.tools_frame.columnconfigure(0, weight=1)

        tools_label = ctk.CTkLabel(self.tools_frame, text="Tools", font=ctk.CTkFont(size=14, weight="bold"))
        tools_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(8, 4))

        btn_row = ctk.CTkFrame(self.tools_frame, fg_color="transparent")
        btn_row.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=2)

        self.dump_btn = ctk.CTkButton(btn_row, text=i18n.t("dump_eeprom"), command=self.dump_eeprom)
        self.dump_btn.pack(side="left", padx=(0, 5))
        self.detect_config_btn = ctk.CTkButton(btn_row, text=i18n.t("detect_config"), command=self.detect_config)
        self.detect_config_btn.pack(side="left", padx=5)
        self.detect_keys_btn = ctk.CTkButton(btn_row, text=i18n.t("detect_keys"), command=self.detect_keys)
        self.detect_keys_btn.pack(side="left", padx=5)

        self.dump_text = ctk.CTkTextbox(self.tools_frame, height=250, font=ctk.CTkFont(family="Courier", size=11))
        self.dump_text.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=(2, 8))
        self.tools_frame.rowconfigure(2, weight=1)

    def _parse_addresses(self, input_str):
        """Parse comma-separated addresses (hex or decimal)."""
        addresses = []
        for part in input_str.split(","):
            part = part.strip()
            if not part:
                continue
            if part.startswith("0x") or part.startswith("0X"):
                addresses.append(int(part, 16))
            else:
                addresses.append(int(part))
        return addresses

    def read_eeprom(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        input_str = self.addr_entry.get().strip()
        if not input_str:
            return

        def _read():
            try:
                addresses = self._parse_addresses(input_str)
                results = []
                for addr in addresses:
                    val = self.app.printer.read_eeprom(addr)
                    results.append(f"0x{addr:04X} ({addr:>5d}) = 0x{val:02X} ({val:>3d})" if isinstance(val, int) else f"0x{addr:04X} = {val}")

                text = "\n".join(results)

                def _update():
                    self.read_result.delete("0.0", "end")
                    self.read_result.insert("0.0", text)

                self.parent.after(0, _update)
                self.app.log(f"Read {len(addresses)} address(es)", "info")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_read)

    def write_eeprom(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        input_str = self.write_entry.get().strip()
        if not input_str:
            return

        if not messagebox.askyesno(i18n.t("confirm_action"), i18n.t("eeprom_confirm")):
            return

        def _write():
            try:
                import ast
                addr_val = ast.literal_eval(input_str)
                if not isinstance(addr_val, dict):
                    raise ValueError("Input must be a dict: {addr: value, ...}")

                results = []
                for addr, val in addr_val.items():
                    addr = int(addr)
                    val = int(val)
                    self.app.printer.write_eeprom(addr, val)
                    results.append(f"0x{addr:04X} <- 0x{val:02X}")

                text = "\n".join(results)

                def _update():
                    self.write_result.delete("0.0", "end")
                    self.write_result.insert("0.0", text)

                self.parent.after(0, _update)
                self.app.log(f"Wrote {len(addr_val)} address(es)", "info")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_write)

    def dump_eeprom(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        def _dump():
            try:
                data = self.app.printer.dump_eeprom(start=0, end=0xFF)
                lines = []
                line = ""
                for addr in sorted(data.keys()):
                    if addr % 16 == 0:
                        if line:
                            lines.append(line)
                        line = f"0x{addr:04X}: "
                    line += f"{data[addr]:02X} "
                if line:
                    lines.append(line)

                text = "\n".join(lines)

                def _update():
                    self.dump_text.delete("0.0", "end")
                    self.dump_text.insert("0.0", text)

                self.parent.after(0, _update)
                self.app.log("EEPROM dump complete", "info")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_dump)

    def detect_config(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        self.app.log("Detecting configuration...", "info")

        def _detect():
            try:
                text = "Configuration detection started...\n"
                text += "This feature analyzes EEPROM to detect printer parameters.\n\n"

                # Try to read key info
                try:
                    keys = self.app.printer.list_known_keys()
                    text += f"Known keys: {keys}\n"
                except Exception:
                    text += "Could not read keys.\n"

                # Read serial
                try:
                    serial = self.app.printer.get_serial_number()
                    text += f"Serial: {serial}\n"
                except Exception:
                    pass

                # Read firmware
                try:
                    fw = self.app.printer.get_firmware_version()
                    text += f"Firmware: {fw}\n"
                except Exception:
                    pass

                def _update():
                    self.dump_text.delete("0.0", "end")
                    self.dump_text.insert("0.0", text)

                self.parent.after(0, _update)
                self.app.log("Detection complete", "info")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_detect)

    def detect_keys(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        self.app.log("Detecting access key (this may take a while)...", "info")

        def _detect():
            try:
                result = self.app.printer.brute_force_read_key()
                text = f"Detected key: {result}" if result else "No key found."

                def _update():
                    self.dump_text.delete("0.0", "end")
                    self.dump_text.insert("0.0", text)

                self.parent.after(0, _update)
                self.app.log("Key detection complete", "info")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_detect)

    def update_language(self):
        try:
            self.read_label.configure(text=i18n.t("read_eeprom"))
            self.addr_label.configure(text=i18n.t("address"))
            self.read_btn.configure(text=i18n.t("read_value"))
            self.write_label.configure(text=i18n.t("write_eeprom"))
            self.write_addr_label.configure(text=i18n.t("value"))
            self.write_btn.configure(text=i18n.t("write_value"))
            self.dump_btn.configure(text=i18n.t("dump_eeprom"))
            self.detect_config_btn.configure(text=i18n.t("detect_config"))
            self.detect_keys_btn.configure(text=i18n.t("detect_keys"))
        except Exception:
            pass
