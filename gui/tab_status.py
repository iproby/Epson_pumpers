#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Status Tab — Printer status, ink levels, waste ink levels, and device stats."""

from datetime import datetime
import customtkinter as ctk
from i18n import i18n


# Color mapping for ink levels
INK_COLORS = {
    "black": "#2c3e50",
    "matte black": "#1e272e",
    "light black": "#57606f",
    "light light black": "#808e9b",
    "cyan": "#00a8ff",
    "light cyan": "#4cd137",
    "magenta": "#e84393",
    "light magenta": "#fd79a8",
    "yellow": "#fbc531",
    "dark yellow": "#e1b12c",
    "grey": "#718093",
    "gray": "#718093",
    "red": "#e74c3c",
    "orange": "#e67e22",
    "green": "#2ecc71",
}


def _get_ink_color(name: str) -> str:
    key = name.lower().strip()
    for color_name, hex_code in sorted(INK_COLORS.items(), key=lambda x: len(x[0]), reverse=True):
        if color_name in key:
            return hex_code
    return "#3498db"


class StatusTab:
    """Tab displaying printer status, visual ink levels, and waste counters."""

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.ink_widgets = []
        self.setup_ui()
        i18n.on_language_change(lambda _: self.update_language())

    def setup_ui(self):
        self.scroll = ctk.CTkScrollableFrame(self.parent)
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.scroll.columnconfigure(0, weight=1)

        row = 0

        # ── Header Action Bar ──
        header_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=(2, 6))
        header_frame.columnconfigure(0, weight=1)

        self.last_updated_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.last_updated_label.grid(row=0, column=0, sticky="w", padx=5)

        self.refresh_btn = ctk.CTkButton(
            header_frame,
            text=f"🔄 {i18n.t('refresh')}",
            width=100,
            command=self.refresh_status,
        )
        self.refresh_btn.grid(row=0, column=1, sticky="e", padx=5)

        row += 1

        # ── Section 1: Printer Status & Identity ──
        self.status_frame = ctk.CTkFrame(self.scroll)
        self.status_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=3)
        self.status_frame.columnconfigure(1, weight=1)
        self.status_frame.columnconfigure(3, weight=1)

        self.status_header = ctk.CTkLabel(
            self.status_frame,
            text=i18n.t("printer_status"),
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.status_header.grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(10, 6))

        # Status badge
        self.state_lbl = ctk.CTkLabel(self.status_frame, text=i18n.t("printer_status") + ":")
        self.state_lbl.grid(row=1, column=0, sticky="w", padx=12, pady=3)
        self.state_val = ctk.CTkLabel(
            self.status_frame,
            text=i18n.t("disconnected"),
            font=ctk.CTkFont(weight="bold"),
            text_color="#e74c3c",
        )
        self.state_val.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        # Model
        self.model_lbl = ctk.CTkLabel(self.status_frame, text=i18n.t("model_name") + ":")
        self.model_lbl.grid(row=1, column=2, sticky="w", padx=12, pady=3)
        self.model_val = ctk.CTkLabel(self.status_frame, text="—", font=ctk.CTkFont(weight="bold"))
        self.model_val.grid(row=1, column=3, sticky="w", padx=5, pady=3)

        # Serial Number
        self.sn_lbl = ctk.CTkLabel(self.status_frame, text=i18n.t("serial_number") + ":")
        self.sn_lbl.grid(row=2, column=0, sticky="w", padx=12, pady=3)
        self.sn_val = ctk.CTkLabel(self.status_frame, text="—", font=ctk.CTkFont(family="Courier"))
        self.sn_val.grid(row=2, column=1, sticky="w", padx=5, pady=3)

        # MAC Address
        self.mac_lbl = ctk.CTkLabel(self.status_frame, text=i18n.t("mac_address") + ":")
        self.mac_lbl.grid(row=2, column=2, sticky="w", padx=12, pady=3)
        self.mac_val = ctk.CTkLabel(self.status_frame, text="—", font=ctk.CTkFont(family="Courier"))
        self.mac_val.grid(row=2, column=3, sticky="w", padx=5, pady=3)

        # Firmware
        self.fw_lbl = ctk.CTkLabel(self.status_frame, text=i18n.t("firmware") + ":")
        self.fw_lbl.grid(row=3, column=0, sticky="w", padx=12, pady=3)
        self.fw_val = ctk.CTkLabel(self.status_frame, text="—")
        self.fw_val.grid(row=3, column=1, sticky="w", padx=5, pady=3)

        # Head ID
        self.head_lbl = ctk.CTkLabel(self.status_frame, text=i18n.t("printer_head_id") + ":")
        self.head_lbl.grid(row=3, column=2, sticky="w", padx=12, pady=(3, 10))
        self.head_val = ctk.CTkLabel(self.status_frame, text="—")
        self.head_val.grid(row=3, column=3, sticky="w", padx=5, pady=(3, 10))

        row += 1

        # ── Section 2: Waste Ink Counters ──
        self.waste_frame = ctk.CTkFrame(self.scroll)
        self.waste_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=4)
        self.waste_frame.columnconfigure(1, weight=1)

        self.waste_header = ctk.CTkLabel(
            self.waste_frame,
            text=i18n.t("waste_ink_levels"),
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.waste_header.grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 6))

        # Main waste
        self.main_waste_lbl = ctk.CTkLabel(self.waste_frame, text=i18n.t("main_waste") + ":")
        self.main_waste_lbl.grid(row=1, column=0, sticky="w", padx=12, pady=4)
        self.main_waste_bar = ctk.CTkProgressBar(self.waste_frame)
        self.main_waste_bar.set(0)
        self.main_waste_bar.grid(row=1, column=1, sticky="ew", padx=10, pady=4)
        self.main_waste_pct = ctk.CTkLabel(self.waste_frame, text="0.0%", width=60, anchor="e")
        self.main_waste_pct.grid(row=1, column=2, sticky="e", padx=12, pady=4)

        # Borderless waste
        self.borderless_waste_lbl = ctk.CTkLabel(self.waste_frame, text=i18n.t("borderless_waste") + ":")
        self.borderless_waste_lbl.grid(row=2, column=0, sticky="w", padx=12, pady=(4, 10))
        self.borderless_waste_bar = ctk.CTkProgressBar(self.waste_frame)
        self.borderless_waste_bar.set(0)
        self.borderless_waste_bar.grid(row=2, column=1, sticky="ew", padx=10, pady=(4, 10))
        self.borderless_waste_pct = ctk.CTkLabel(self.waste_frame, text="0.0%", width=60, anchor="e")
        self.borderless_waste_pct.grid(row=2, column=2, sticky="e", padx=12, pady=(4, 10))

        row += 1

        # ── Section 3: Ink Levels (Cartridges) ──
        self.ink_frame = ctk.CTkFrame(self.scroll)
        self.ink_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=4)
        self.ink_frame.columnconfigure(1, weight=1)

        self.ink_header = ctk.CTkLabel(
            self.ink_frame,
            text=i18n.t("ink_levels"),
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.ink_header.grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 6))

        self.ink_placeholder = ctk.CTkLabel(
            self.ink_frame,
            text=i18n.t("no_data"),
            text_color="gray",
        )
        self.ink_placeholder.grid(row=1, column=0, columnspan=3, padx=12, pady=(4, 10), sticky="w")

        row += 1

        # ── Section 4: Statistics ──
        self.stats_frame = ctk.CTkFrame(self.scroll)
        self.stats_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=4)
        self.stats_frame.columnconfigure(1, weight=1)
        self.stats_frame.columnconfigure(3, weight=1)

        self.stats_header = ctk.CTkLabel(
            self.stats_frame,
            text=i18n.t("general_info"),
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.stats_header.grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(10, 6))

        # Total prints
        self.prints_lbl = ctk.CTkLabel(self.stats_frame, text=i18n.t("total_prints") + ":")
        self.prints_lbl.grid(row=1, column=0, sticky="w", padx=12, pady=3)
        self.prints_val = ctk.CTkLabel(self.stats_frame, text="—")
        self.prints_val.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        # Total scans
        self.scans_lbl = ctk.CTkLabel(self.stats_frame, text=i18n.t("total_scans") + ":")
        self.scans_lbl.grid(row=1, column=2, sticky="w", padx=12, pady=3)
        self.scans_val = ctk.CTkLabel(self.stats_frame, text="—")
        self.scans_val.grid(row=1, column=3, sticky="w", padx=5, pady=3)

        # Power on count
        self.power_on_lbl = ctk.CTkLabel(self.stats_frame, text=i18n.t("power_on_count") + ":")
        self.power_on_lbl.grid(row=2, column=0, sticky="w", padx=12, pady=(3, 10))
        self.power_on_val = ctk.CTkLabel(self.stats_frame, text="—")
        self.power_on_val.grid(row=2, column=1, sticky="w", padx=5, pady=(3, 10))

    def refresh_status(self):
        """Fetch all printer information in a background thread."""
        if not self.app.printer:
            self.app.log(i18n.t("not_connected"), "warning")
            return

        self.app.log(i18n.t("please_wait"), "info")
        self.refresh_btn.configure(state="disabled")

        def _fetch():
            data = {}
            try:
                # 1. Device identity
                try:
                    data["serial"] = self.app.printer.get_serial_number()
                except Exception:
                    data["serial"] = None

                try:
                    data["mac"] = self.app.printer.get_wifi_mac_address()
                except Exception:
                    data["mac"] = None

                try:
                    data["firmware"] = self.app.printer.get_firmware_version()
                except Exception:
                    data["firmware"] = None

                try:
                    data["head_id"] = self.app.printer.get_printer_head_id()
                except Exception:
                    data["head_id"] = None

                # 2. Status & ink levels
                try:
                    data["printer_status"] = self.app.printer.get_printer_status()
                except Exception:
                    data["printer_status"] = None

                # 3. Waste ink
                try:
                    data["waste"] = self.app.printer.get_waste_ink_levels()
                except Exception:
                    data["waste"] = None

                # 4. Statistics
                try:
                    data["stats"] = self.app.printer.get_stats()
                except Exception:
                    data["stats"] = None

                # Schedule UI update on main thread
                self.parent.after(0, lambda: self._apply_data(data))
                self.app.log(i18n.t("success"), "info")
            except Exception as e:
                self.app.log(f"{i18n.t('error')}: {e}", "error")
            finally:
                self.parent.after(0, lambda: self.refresh_btn.configure(state="normal"))

        self.app.run_threaded(_fetch)

    def _apply_data(self, data):
        """Update UI widgets with parsed data."""
        now_str = datetime.now().strftime("%H:%M:%S")
        self.last_updated_label.configure(text=f"Updated: {now_str}")

        # Model and basic identity
        model_name = self.app.printer.model if self.app.printer else "—"
        self.model_val.configure(text=model_name)
        self.sn_val.configure(text=data.get("serial") or "—")
        self.mac_val.configure(text=data.get("mac") or "—")
        self.fw_val.configure(text=data.get("firmware") or "—")
        self.head_val.configure(text=data.get("head_id") or "—")

        # Status text & color
        pstatus = data.get("printer_status")
        if isinstance(pstatus, dict):
            status_tuple = pstatus.get("status")
            status_text = status_tuple[1] if status_tuple else i18n.t("status_ready")
            is_ready = pstatus.get("ready", True)
            err = pstatus.get("errcode")

            if err:
                self.state_val.configure(text=f"{status_text} ({err})", text_color="#e74c3c")
            elif is_ready:
                self.state_val.configure(text=status_text, text_color="#2ecc71")
            else:
                self.state_val.configure(text=status_text, text_color="#e67e22")

            # Ink levels
            inks = pstatus.get("ink_level")
            self._update_ink_bars(inks)
        elif self.app.printer:
            self.state_val.configure(text=i18n.t("connected"), text_color="#2ecc71")

        # Waste counters
        waste = data.get("waste")
        if isinstance(waste, dict):
            main_pct = float(waste.get("main_waste", 0.0))
            self.main_waste_bar.set(min(1.0, main_pct / 100.0))
            self.main_waste_pct.configure(text=f"{main_pct:.1f}%")
            self._set_bar_color(self.main_waste_bar, self.main_waste_pct, main_pct)

            border_pct = float(waste.get("borderless_waste", 0.0))
            self.borderless_waste_bar.set(min(1.0, border_pct / 100.0))
            self.borderless_waste_pct.configure(text=f"{border_pct:.1f}%")
            self._set_bar_color(self.borderless_waste_bar, self.borderless_waste_pct, border_pct)

        # Statistics
        stats = data.get("stats")
        if isinstance(stats, dict):
            self.prints_val.configure(text=str(stats.get("Total pages printed", stats.get("Total prints", "—"))))
            self.scans_val.configure(text=str(stats.get("Total scans", stats.get("Scan count", "—"))))
            self.power_on_val.configure(text=str(stats.get("Power on count", stats.get("Power on", "—"))))

    def _set_bar_color(self, bar, label, pct: float):
        """Set progress bar and label color based on waste percentage."""
        if pct >= 90.0:
            color = "#e74c3c"  # Red
        elif pct >= 70.0:
            color = "#e67e22"  # Orange
        else:
            color = "#2ecc71"  # Green
        bar.configure(progress_color=color)
        label.configure(text_color=color)

    def _update_ink_bars(self, inks):
        """Render cartridge progress bars dynamically."""
        for w in self.ink_widgets:
            w.destroy()
        self.ink_widgets.clear()

        if not inks:
            self.ink_placeholder.grid(row=1, column=0, columnspan=3, padx=12, pady=(4, 10), sticky="w")
            return

        self.ink_placeholder.grid_remove()

        # inks is list of tuples: (colour_id, ink_color_id, name, ink_name, level)
        for idx, item in enumerate(inks):
            if isinstance(item, (list, tuple)) and len(item) >= 5:
                _, _, name, ink_name, level = item[:5]
            else:
                continue

            row_idx = idx + 1
            color_hex = _get_ink_color(ink_name or name)

            display_name = f"{name} ({ink_name})" if ink_name and ink_name != name else str(name)
            lbl = ctk.CTkLabel(self.ink_frame, text=display_name + ":", width=140, anchor="w")
            lbl.grid(row=row_idx, column=0, sticky="w", padx=12, pady=3)

            pct_val = max(0, min(100, int(level)))
            bar = ctk.CTkProgressBar(self.ink_frame, progress_color=color_hex)
            bar.set(pct_val / 100.0)
            bar.grid(row=row_idx, column=1, sticky="ew", padx=10, pady=3)

            pct_lbl = ctk.CTkLabel(self.ink_frame, text=f"{pct_val}%", width=50, anchor="e")
            pct_lbl.grid(row=row_idx, column=2, sticky="e", padx=12, pady=3)

            self.ink_widgets.extend([lbl, bar, pct_lbl])

    def update_language(self):
        try:
            self.refresh_btn.configure(text=f"🔄 {i18n.t('refresh')}")
            self.status_header.configure(text=i18n.t("printer_status"))
            self.state_lbl.configure(text=i18n.t("printer_status") + ":")
            self.model_lbl.configure(text=i18n.t("model_name") + ":")
            self.sn_lbl.configure(text=i18n.t("serial_number") + ":")
            self.mac_lbl.configure(text=i18n.t("mac_address") + ":")
            self.fw_lbl.configure(text=i18n.t("firmware") + ":")
            self.head_lbl.configure(text=i18n.t("printer_head_id") + ":")
            self.waste_header.configure(text=i18n.t("waste_ink_levels"))
            self.main_waste_lbl.configure(text=i18n.t("main_waste") + ":")
            self.borderless_waste_lbl.configure(text=i18n.t("borderless_waste") + ":")
            self.ink_header.configure(text=i18n.t("ink_levels"))
            self.stats_header.configure(text=i18n.t("general_info"))
            self.prints_lbl.configure(text=i18n.t("total_prints") + ":")
            self.scans_lbl.configure(text=i18n.t("total_scans") + ":")
            self.power_on_lbl.configure(text=i18n.t("power_on_count") + ":")
        except Exception:
            pass
