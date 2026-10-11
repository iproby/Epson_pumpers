#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maintenance Tab — Waste ink counter reset, Power-off timer, TI Date, Clean nozzles."""

from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
from i18n import i18n


class MaintenanceTab:
    """Tab for maintenance operations: waste resets, timers, date and nozzle cleaning."""

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

        # ── Section 1: Waste Ink Counters Reset ──
        self.waste_frame = ctk.CTkFrame(self.scroll)
        self.waste_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=(5, 3))
        self.waste_frame.columnconfigure(0, weight=1)

        self.waste_header = ctk.CTkLabel(
            self.waste_frame,
            text=i18n.t("reset_waste_ink"),
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.waste_header.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        # Warning banner
        self.waste_warn_box = ctk.CTkFrame(self.waste_frame, fg_color="#3e2723", corner_radius=6)
        self.waste_warn_box.grid(row=1, column=0, sticky="ew", padx=12, pady=4)
        self.waste_warn_lbl = ctk.CTkLabel(
            self.waste_warn_box,
            text=i18n.t("waste_reset_warning"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffb74d",
            wraplength=600,
            justify="left",
        )
        self.waste_warn_lbl.pack(padx=10, pady=8, fill="x")

        # Reset buttons row
        btn_row = ctk.CTkFrame(self.waste_frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=12, pady=8)

        self.reset_all_btn = ctk.CTkButton(
            btn_row,
            text=i18n.t("reset_all_counters"),
            fg_color="#c0392b",
            hover_color="#e74c3c",
            font=ctk.CTkFont(weight="bold"),
            command=self.reset_all_waste,
        )
        self.reset_all_btn.pack(side="left", padx=(0, 6))

        self.temp_reset_btn = ctk.CTkButton(
            btn_row,
            text=i18n.t("temp_reset_waste"),
            fg_color="#d35400",
            hover_color="#e67e22",
            command=self.temp_reset_waste,
        )
        self.temp_reset_btn.pack(side="left", padx=6)

        self.waste_desc = ctk.CTkLabel(
            self.waste_frame,
            text=i18n.t("temp_reset_info"),
            font=ctk.CTkFont(size=11),
            text_color="gray",
        )
        self.waste_desc.grid(row=3, column=0, sticky="w", padx=12, pady=(0, 10))

        row += 1

        # ── Section 2: Power-off Timer ──
        self.timer_frame = ctk.CTkFrame(self.scroll)
        self.timer_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=3)
        self.timer_frame.columnconfigure(1, weight=1)

        self.timer_header = ctk.CTkLabel(
            self.timer_frame,
            text=i18n.t("power_off_timer"),
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.timer_header.grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(10, 6))

        self.timer_current_lbl = ctk.CTkLabel(self.timer_frame, text=i18n.t("current_value"))
        self.timer_current_lbl.grid(row=1, column=0, sticky="w", padx=12, pady=3)
        self.timer_current_val = ctk.CTkLabel(self.timer_frame, text="—", font=ctk.CTkFont(weight="bold"))
        self.timer_current_val.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        self.timer_read_btn = ctk.CTkButton(
            self.timer_frame,
            text=i18n.t("read_timer"),
            width=90,
            command=self.read_poweroff_timer,
        )
        self.timer_read_btn.grid(row=1, column=2, padx=10, pady=3)

        # Timer preset options
        self.timer_set_lbl = ctk.CTkLabel(self.timer_frame, text="Set timer (min):")
        self.timer_set_lbl.grid(row=2, column=0, sticky="w", padx=12, pady=(3, 10))

        self.timer_preset_var = ctk.StringVar(value="120")
        self.timer_preset_menu = ctk.CTkOptionMenu(
            self.timer_frame,
            values=["0", "30", "60", "120", "240", "480", "720", "1440"],
            variable=self.timer_preset_var,
            width=100,
        )
        self.timer_preset_menu.grid(row=2, column=1, sticky="w", padx=5, pady=(3, 10))

        self.timer_set_btn = ctk.CTkButton(
            self.timer_frame,
            text=i18n.t("set_timer"),
            width=90,
            command=self.write_poweroff_timer,
        )
        self.timer_set_btn.grid(row=2, column=2, padx=10, pady=(3, 10))

        row += 1

        # ── Section 3: First TI Received Time ──
        self.date_frame = ctk.CTkFrame(self.scroll)
        self.date_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=3)
        self.date_frame.columnconfigure(1, weight=1)

        self.date_header = ctk.CTkLabel(
            self.date_frame,
            text=i18n.t("ti_received_time"),
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.date_header.grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(10, 6))

        self.date_current_lbl = ctk.CTkLabel(self.date_frame, text=i18n.t("current_value"))
        self.date_current_lbl.grid(row=1, column=0, sticky="w", padx=12, pady=3)
        self.date_current_val = ctk.CTkLabel(self.date_frame, text="—", font=ctk.CTkFont(family="Courier"))
        self.date_current_val.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        self.date_read_btn = ctk.CTkButton(
            self.date_frame,
            text=i18n.t("read_date"),
            width=90,
            command=self.read_ti_date,
        )
        self.date_read_btn.grid(row=1, column=2, padx=10, pady=3)

        self.date_new_lbl = ctk.CTkLabel(self.date_frame, text="New Date (YYYY-MM-DD):")
        self.date_new_lbl.grid(row=2, column=0, sticky="w", padx=12, pady=(3, 10))

        date_input_frame = ctk.CTkFrame(self.date_frame, fg_color="transparent")
        date_input_frame.grid(row=2, column=1, sticky="w", padx=5, pady=(3, 10))

        self.date_entry = ctk.CTkEntry(date_input_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.date_entry.pack(side="left", padx=(0, 5))
        self.date_today_btn = ctk.CTkButton(
            date_input_frame,
            text="Today",
            width=50,
            command=lambda: self.date_entry.delete(0, "end") or self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")),
        )
        self.date_today_btn.pack(side="left")

        self.date_set_btn = ctk.CTkButton(
            self.date_frame,
            text=i18n.t("set_date"),
            width=90,
            command=self.write_ti_date,
        )
        self.date_set_btn.grid(row=2, column=2, padx=10, pady=(3, 10))

        row += 1

        # ── Section 4: Clean Nozzles ──
        self.clean_frame = ctk.CTkFrame(self.scroll)
        self.clean_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=3)
        self.clean_frame.columnconfigure(0, weight=1)

        self.clean_header = ctk.CTkLabel(
            self.clean_frame,
            text=i18n.t("clean_nozzles"),
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.clean_header.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        clean_row = ctk.CTkFrame(self.clean_frame, fg_color="transparent")
        clean_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(4, 10))

        self.normal_clean_btn = ctk.CTkButton(
            clean_row,
            text=f"🧽 {i18n.t('normal_clean')}",
            command=lambda: self.clean_nozzles(power=False),
        )
        self.normal_clean_btn.pack(side="left", padx=(0, 8))

        self.power_clean_btn = ctk.CTkButton(
            clean_row,
            text=f"⚡ {i18n.t('power_clean')}",
            fg_color="#d35400",
            hover_color="#e67e22",
            command=lambda: self.clean_nozzles(power=True),
        )
        self.power_clean_btn.pack(side="left", padx=8)

    # ── Action Handlers ──

    def reset_all_waste(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        msg = (
            f"{i18n.t('waste_reset_warning')}\n\n"
            f"{i18n.t('eeprom_confirm')}"
        )
        if not messagebox.askyesno(i18n.t("confirm_action"), msg, default="no"):
            return

        self.app.log("Resetting waste ink counters...", "info")

        def _reset():
            try:
                res = self.app.printer.reset_waste_ink_levels()
                if res:
                    self.app.log(f"{i18n.t('success')}! Please power cycle the printer.", "info")
                    self.parent.after(0, lambda: messagebox.showinfo(
                        i18n.t("success"),
                        "Waste ink counter reset successfully.\nPlease restart the printer to apply changes."
                    ))
                else:
                    self.app.log("Reset operation returned failure.", "error")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_reset)

    def temp_reset_waste(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        self.app.log("Sending temporary waste bypass...", "info")

        def _temp():
            try:
                res = self.app.printer.temporary_reset_waste()
                if res:
                    self.app.log("Temporary bypass successful (valid until restart).", "info")
                    self.parent.after(0, lambda: messagebox.showinfo(
                        i18n.t("success"),
                        "Temporary reset applied. Printer will print until power cycle."
                    ))
                else:
                    self.app.log("Temporary reset failed.", "error")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_temp)

    def read_poweroff_timer(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        def _read():
            try:
                stats = self.app.printer.stats()
                po_timer = stats.get("stats", {}).get("Power off timer")
                if po_timer is not None:
                    self.parent.after(0, lambda: self.timer_current_val.configure(
                        text=f"{po_timer} {i18n.t('minutes')}"
                    ))
                    self.app.log(f"Power-off timer: {po_timer} min", "info")
                else:
                    self.app.log("Power-off timer not available in config", "warning")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_read)

    def write_poweroff_timer(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        val_str = self.timer_preset_var.get().strip()
        try:
            val = int(val_str)
        except ValueError:
            self.app.log("Invalid timer value", "error")
            return

        def _write():
            try:
                self.app.printer.write_poweroff_timer(val)
                self.app.log(f"Power-off timer set to {val} min", "info")
                self.read_poweroff_timer()
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_write)

    def read_ti_date(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        def _read():
            try:
                stats = self.app.printer.stats()
                d = stats.get("stats", {}).get("First TI received time")
                if d and d != "?":
                    try:
                        date_str = datetime.strptime(d, "%d %b %Y").strftime("%Y-%m-%d")
                    except Exception:
                        date_str = str(d)
                    self.parent.after(0, lambda: self.date_current_val.configure(text=date_str))
                    self.app.log(f"First TI Date: {date_str}", "info")
                else:
                    self.app.log("No First TI Date available", "warning")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_read)

    def write_ti_date(self):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        date_str = self.date_entry.get().strip()
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.app.log("Date format must be YYYY-MM-DD", "error")
            return

        if not messagebox.askyesno(i18n.t("confirm_action"), i18n.t("eeprom_confirm")):
            return

        def _write():
            try:
                self.app.printer.write_first_ti_received_time(dt.year, dt.month, dt.day)
                self.app.log("First TI date updated", "info")
                self.read_ti_date()
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_write)

    def clean_nozzles(self, power: bool = False):
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        clean_name = i18n.t("power_clean") if power else i18n.t("normal_clean")
        if not messagebox.askyesno(i18n.t("confirm_action"), f"Start {clean_name}?"):
            return

        def _clean():
            try:
                clean_type = 1 if power else 0
                self.app.printer.print_clean_nozzles(type=clean_type)
                self.app.log(f"{clean_name} command sent to printer", "info")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")

        self.app.run_threaded(_clean)

    def update_language(self):
        try:
            self.waste_header.configure(text=i18n.t("reset_waste_ink"))
            self.waste_warn_lbl.configure(text=i18n.t("waste_reset_warning"))
            self.reset_all_btn.configure(text=i18n.t("reset_all_counters"))
            self.temp_reset_btn.configure(text=i18n.t("temp_reset_waste"))
            self.waste_desc.configure(text=i18n.t("temp_reset_info"))
            self.timer_header.configure(text=i18n.t("power_off_timer"))
            self.timer_current_lbl.configure(text=i18n.t("current_value"))
            self.timer_read_btn.configure(text=i18n.t("read_timer"))
            self.timer_set_btn.configure(text=i18n.t("set_timer"))
            self.date_header.configure(text=i18n.t("ti_received_time"))
            self.date_current_lbl.configure(text=i18n.t("current_value"))
            self.date_read_btn.configure(text=i18n.t("read_date"))
            self.date_set_btn.configure(text=i18n.t("set_date"))
            self.clean_header.configure(text=i18n.t("clean_nozzles"))
            self.normal_clean_btn.configure(text=f"🧽 {i18n.t('normal_clean')}")
            self.power_clean_btn.configure(text=f"⚡ {i18n.t('power_clean')}")
        except Exception:
            pass
