#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internationalization (i18n) module for Epson Printer Configuration GUI.
Supports English and Russian languages with runtime switching.
"""


class I18n:
    """Simple dictionary-based internationalization."""

    LANGUAGES = {
        "en": "English",
        "ru": "Русский",
    }

    _strings = {
        # ── Window ──
        "app_title": {
            "en": "Epson Printer Configuration",
            "ru": "Настройка принтеров Epson",
        },
        # ── Tabs ──
        "tab_status": {"en": "📊 Status", "ru": "📊 Статус"},
        "tab_maintenance": {"en": "🔧 Maintenance", "ru": "🔧 Обслуживание"},
        "tab_configuration": {"en": "⚙️ Configuration", "ru": "⚙️ Конфигурация"},
        "tab_eeprom": {"en": "📝 EEPROM", "ru": "📝 EEPROM"},
        "tab_tests": {"en": "🧪 Tests", "ru": "🧪 Тесты"},
        "tab_console": {"en": "🖥️ Console", "ru": "🖥️ Консоль"},
        "tab_about": {"en": "ℹ️ About", "ru": "ℹ️ О программе"},
        # ── Top bar ──
        "printer_model": {"en": "Printer Model:", "ru": "Модель принтера:"},
        "ip_address": {"en": "IP Address:", "ru": "IP адрес:"},
        "detect_printers": {"en": "🔍 Detect", "ru": "🔍 Поиск"},
        "connect": {"en": "Connect", "ru": "Подключить"},
        "disconnect": {"en": "Disconnect", "ru": "Отключить"},
        # ── Status tab ──
        "printer_status": {"en": "Printer Status", "ru": "Статус принтера"},
        "ink_levels": {"en": "Ink Levels", "ru": "Уровень чернил"},
        "waste_ink_levels": {"en": "Waste Ink Levels", "ru": "Уровень отработанных чернил"},
        "main_waste": {"en": "Main Waste Counter", "ru": "Основной счётчик"},
        "borderless_waste": {"en": "Borderless Waste Counter", "ru": "Счётчик без полей"},
        "serial_number": {"en": "Serial Number", "ru": "Серийный номер"},
        "firmware": {"en": "Firmware Version", "ru": "Версия прошивки"},
        "mac_address": {"en": "MAC Address", "ru": "MAC адрес"},
        "model_name": {"en": "Model", "ru": "Модель"},
        "printer_head_id": {"en": "Printer Head ID", "ru": "ID печатающей головки"},
        "total_prints": {"en": "Total Prints", "ru": "Всего отпечатков"},
        "total_scans": {"en": "Total Scans", "ru": "Всего сканирований"},
        "power_on_count": {"en": "Power On Count", "ru": "Кол-во включений"},
        "connected": {"en": "Connected", "ru": "Подключён"},
        "disconnected": {"en": "Disconnected", "ru": "Отключён"},
        "unknown": {"en": "Unknown", "ru": "Неизвестно"},
        "status_ready": {"en": "Ready", "ru": "Готов"},
        "status_printing": {"en": "Printing", "ru": "Печать"},
        "status_error": {"en": "Error", "ru": "Ошибка"},
        # ── Maintenance tab ──
        "reset_waste_ink": {"en": "Reset Waste Ink Counters", "ru": "Сброс счётчиков отработанных чернил"},
        "waste_reset_warning": {
            "en": "⚠️ Make sure to empty the waste ink pads before resetting!",
            "ru": "⚠️ Убедитесь, что памперсы заменены перед сбросом!",
        },
        "reset_main_counter": {"en": "Reset Main Counter", "ru": "Сбросить основной счётчик"},
        "reset_borderless_counter": {"en": "Reset Borderless Counter", "ru": "Сбросить безрамочный счётчик"},
        "reset_all_counters": {"en": "Reset All Counters", "ru": "Сбросить все счётчики"},
        "power_off_timer": {"en": "Power-off Timer", "ru": "Таймер выключения"},
        "current_value": {"en": "Current Value:", "ru": "Текущее значение:"},
        "minutes": {"en": "minutes", "ru": "минут"},
        "set_timer": {"en": "Set Timer", "ru": "Установить таймер"},
        "read_timer": {"en": "Read Timer", "ru": "Прочитать таймер"},
        "ti_received_time": {"en": "First TI Received Time", "ru": "Время первого включения"},
        "read_date": {"en": "Read Date", "ru": "Прочитать дату"},
        "set_date": {"en": "Set Date", "ru": "Установить дату"},
        "clean_nozzles": {"en": "Clean Nozzles", "ru": "Очистка дюз"},
        "power_clean": {"en": "Power Clean", "ru": "Глубокая очистка"},
        "normal_clean": {"en": "Normal Clean", "ru": "Обычная очистка"},
        "start_cleaning": {"en": "Start Cleaning", "ru": "Начать очистку"},
        # ── Configuration tab ──
        "read_value": {"en": "Read", "ru": "Прочитать"},
        "write_value": {"en": "Write", "ru": "Записать"},
        "current_mac": {"en": "Current MAC:", "ru": "Текущий MAC:"},
        "new_mac": {"en": "New MAC:", "ru": "Новый MAC:"},
        "current_serial": {"en": "Current Serial:", "ru": "Текущий серийный:"},
        "new_serial": {"en": "New Serial:", "ru": "Новый серийный:"},
        "printer_config": {"en": "Printer Configuration", "ru": "Конфигурация принтера"},
        "show_config": {"en": "Show Configuration", "ru": "Показать конфигурацию"},
        "show_keys": {"en": "Show Keys", "ru": "Показать ключи"},
        # ── EEPROM tab ──
        "read_eeprom": {"en": "Read EEPROM", "ru": "Чтение EEPROM"},
        "write_eeprom": {"en": "Write EEPROM", "ru": "Запись EEPROM"},
        "address": {"en": "Address(es):", "ru": "Адрес(а):"},
        "value": {"en": "Value(s):", "ru": "Значение(я):"},
        "eeprom_address_hint": {"en": "e.g.: 0x10, 0x20  or  16, 32", "ru": "напр.: 0x10, 0x20  или  16, 32"},
        "eeprom_write_hint": {"en": "e.g.: {0x10: 0, 0x20: 1}", "ru": "напр.: {0x10: 0, 0x20: 1}"},
        "dump_eeprom": {"en": "Dump EEPROM", "ru": "Дамп EEPROM"},
        "detect_config": {"en": "Detect Configuration", "ru": "Определить конфигурацию"},
        "detect_keys": {"en": "Detect Access Key", "ru": "Определить ключ доступа"},
        # ── Tests tab ──
        "nozzle_check": {"en": "Nozzle Check", "ru": "Проверка дюз"},
        "test_pattern": {"en": "Test Pattern", "ru": "Тестовый шаблон"},
        "print_test": {"en": "Print Test", "ru": "Тестовая печать"},
        "number_of_tests": {"en": "Number of tests:", "ru": "Кол-во тестов:"},
        "start_test": {"en": "Start Test", "ru": "Начать тест"},
        # ── Console tab ──
        "console_help": {
            "en": "Interactive Python console. Use 'printer' variable to access the EpsonPrinter instance.",
            "ru": "Интерактивная Python-консоль. Используйте переменную 'printer' для доступа к EpsonPrinter.",
        },
        # ── About tab ──
        "version": {"en": "Version", "ru": "Версия"},
        "license": {"en": "License", "ru": "Лицензия"},
        "github_repo": {"en": "GitHub Repository", "ru": "Репозиторий GitHub"},
        "description": {
            "en": "Epson Printer Configuration tool via SNMP (TCP/IP).\nRead and write printer EEPROM, reset waste ink counters,\nmanage printer settings across the network.",
            "ru": "Утилита настройки принтеров Epson через SNMP (TCP/IP).\nЧтение и запись EEPROM принтера, сброс счётчиков памперсов,\nуправление настройками принтера по сети.",
        },
        # ── Common ──
        "confirm": {"en": "Confirm", "ru": "Подтвердить"},
        "cancel": {"en": "Cancel", "ru": "Отмена"},
        "ok": {"en": "OK", "ru": "ОК"},
        "yes": {"en": "Yes", "ru": "Да"},
        "no": {"en": "No", "ru": "Нет"},
        "error": {"en": "Error", "ru": "Ошибка"},
        "warning": {"en": "Warning", "ru": "Предупреждение"},
        "info": {"en": "Info", "ru": "Информация"},
        "success": {"en": "Success", "ru": "Успешно"},
        "loading": {"en": "Loading...", "ru": "Загрузка..."},
        "please_wait": {"en": "Please wait...", "ru": "Пожалуйста, подождите..."},
        "no_printer": {"en": "No printer selected", "ru": "Принтер не выбран"},
        "not_connected": {
            "en": "Not connected. Please select a printer model and IP address, or press 'Detect'.",
            "ru": "Не подключён. Выберите модель принтера и IP адрес, или нажмите 'Поиск'.",
        },
        "confirm_action": {"en": "Confirm Action", "ru": "Подтверждение действия"},
        "eeprom_confirm": {
            "en": "Please copy and save the codes in the [NOTE] shown on the screen.\n"
                  "They can be used to restore the initial configuration in case of problems.\n\n"
                  "Are you sure you want to proceed?",
            "ru": "Пожалуйста, скопируйте и сохраните коды из [ПРИМЕЧАНИЕ] на экране.\n"
                  "Они могут быть использованы для восстановления начальной конфигурации при проблемах.\n\n"
                  "Вы уверены, что хотите продолжить?",
        },
        "save_config": {"en": "Save Configuration", "ru": "Сохранить конфигурацию"},
        "load_config": {"en": "Load Configuration", "ru": "Загрузить конфигурацию"},
        "file_menu": {"en": "File", "ru": "Файл"},
        "settings_menu": {"en": "Settings", "ru": "Настройки"},
        "help_menu": {"en": "Help", "ru": "Помощь"},
        "language": {"en": "Language", "ru": "Язык"},
        "theme": {"en": "Theme", "ru": "Тема"},
        "dark_theme": {"en": "Dark", "ru": "Тёмная"},
        "light_theme": {"en": "Light", "ru": "Светлая"},
        "system_theme": {"en": "System", "ru": "Системная"},
        "quit": {"en": "Quit", "ru": "Выход"},
        "web_interface": {"en": "Open Web Interface", "ru": "Открыть веб-интерфейс"},
        "copy_to_clipboard": {"en": "Copy to Clipboard", "ru": "Скопировать"},
        "scanning_network": {"en": "Scanning network...", "ru": "Сканирование сети..."},
        "printers_found": {"en": "printers found", "ru": "принтеров найдено"},
        "no_printers_found": {"en": "No printers found", "ru": "Принтеры не найдены"},
        "refresh": {"en": "Refresh", "ru": "Обновить"},
        "temp_reset_waste": {"en": "Temporary Waste Reset", "ru": "Временный сброс памперса"},
        "temp_reset_info": {
            "en": "Temporarily bypasses waste ink counter until printer restart.",
            "ru": "Временно сбрасывает счётчик отработанных чернил до перезагрузки принтера.",
        },
        "clear": {"en": "Clear", "ru": "Очистить"},
        "execute": {"en": "Execute", "ru": "Выполнить"},
        "status_bar_ready": {"en": "Ready", "ru": "Готов"},
        "status_bar_connected": {"en": "Connected to {model} @ {ip}", "ru": "Подключено к {model} @ {ip}"},
        "status_bar_disconnected": {"en": "Disconnected", "ru": "Отключено"},
        "status_bar_busy": {"en": "Busy...", "ru": "Выполняется операция..."},
        "no_data": {"en": "No data", "ru": "Нет данных"},
        "details": {"en": "Details", "ru": "Подробности"},
        "general_info": {"en": "General Information", "ru": "Общая информация"},
    }

    def __init__(self, lang: str = "en"):
        self._lang = lang if lang in self.LANGUAGES else "en"
        self._callbacks: list = []

    @property
    def lang(self) -> str:
        return self._lang

    @lang.setter
    def lang(self, value: str):
        if value in self.LANGUAGES and value != self._lang:
            self._lang = value
            active = []
            for cb in list(self._callbacks):
                try:
                    cb(value)
                    active.append(cb)
                except Exception:
                    # Widget or callback was destroyed
                    pass
            self._callbacks = active

    def t(self, key: str, **kwargs) -> str:
        """Translate a key to the current language."""
        entry = self._strings.get(key)
        if entry is None:
            return f"[{key}]"
        text = entry.get(self._lang, entry.get("en", f"[{key}]"))
        if kwargs:
            text = text.format(**kwargs)
        return text

    def on_language_change(self, callback):
        """Register a callback to be called when language changes."""
        self._callbacks.append(callback)

    def remove_callback(self, callback):
        """Remove a registered callback."""
        self._callbacks = [cb for cb in self._callbacks if cb != callback]

    def clear_callbacks(self):
        """Remove all registered callbacks."""
        self._callbacks.clear()


# Global instance
i18n = I18n()
