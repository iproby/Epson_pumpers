#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Epson Easy Reset — красивый CLI для сброса памперса Epson принтеров.
Автоматическая настройка, поиск принтеров и интерактивное меню.
"""

import os
import sys
import time
import pickle
import socket
import subprocess
import threading
import warnings
import textwrap

warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# ─── Цвета и стили ───────────────────────────────────────────────────────────
class C:
    RST = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    BG_DARK = "\033[48;5;236m"
    GRAY = "\033[90m"

def clr():
    os.system("clear" if os.name != "nt" else "cls")

def banner():
    clr()
    logo = f"""
{C.CYAN}{C.BOLD}
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   ███████╗██████╗ ███████╗ ██████╗ ███╗   ██╗        ║
    ║   ██╔════╝██╔══██╗██╔════╝██╔═══██╗████╗  ██║        ║
    ║   █████╗  ██████╔╝███████╗██║   ██║██╔██╗ ██║        ║
    ║   ██╔══╝  ██╔═══╝ ╚════██║██║   ██║██║╚██╗██║        ║
    ║   ███████╗██║     ███████║╚██████╔╝██║ ╚████║        ║
    ║   ╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝        ║
    ║                                                       ║
    ║        {C.YELLOW}★  E A S Y   R E S E T  ★{C.CYAN}                  ║
    ║        {C.DIM}{C.WHITE}Сброс памперса Epson принтеров{C.RST}{C.CYAN}{C.BOLD}             ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝{C.RST}
"""
    print(logo)

def hline():
    print(f"{C.GRAY}{'─' * 58}{C.RST}")

def info(msg):
    print(f"  {C.CYAN}ℹ{C.RST}  {msg}")

def ok(msg):
    print(f"  {C.GREEN}✔{C.RST}  {msg}")

def warn(msg):
    print(f"  {C.YELLOW}⚠{C.RST}  {msg}")

def err(msg):
    print(f"  {C.RED}✖{C.RST}  {msg}")

def step(num, msg):
    print(f"\n  {C.MAGENTA}{C.BOLD}[{num}]{C.RST} {C.BOLD}{msg}{C.RST}")
    hline()

def spinner(msg, stop_event):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    i = 0
    while not stop_event.is_set():
        print(f"\r  {C.CYAN}{chars[i % len(chars)]}{C.RST}  {msg}", end="", flush=True)
        i += 1
        time.sleep(0.1)
    print(f"\r{' ' * (len(msg) + 10)}\r", end="")

def run_with_spinner(msg, func):
    stop = threading.Event()
    t = threading.Thread(target=spinner, args=(msg, stop), daemon=True)
    t.start()
    try:
        result = func()
    finally:
        stop.set()
        t.join()
    return result

def menu_choice(options, title="Выберите действие"):
    print(f"\n  {C.BOLD}{C.WHITE}{title}:{C.RST}\n")
    for idx, (label, _desc) in enumerate(options, 1):
        print(f"    {C.CYAN}{C.BOLD}{idx}{C.RST}  │  {label}")
    print(f"    {C.RED}{C.BOLD}0{C.RST}  │  Выход\n")
    while True:
        try:
            raw = input(f"  {C.YELLOW}▸{C.RST} Ваш выбор: ").strip()
            if raw == "0":
                return None
            n = int(raw)
            if 1 <= n <= len(options):
                return n - 1
        except (ValueError, EOFError):
            pass
        err("Неверный ввод, попробуйте ещё раз")

# ─── Автоустановка зависимостей ──────────────────────────────────────────────
def ensure_deps():
    step("1", "Проверка зависимостей")
    venv_python = os.path.join(SCRIPT_DIR, "venv", "bin", "python3")
    if os.path.exists(venv_python):
        ok("Virtual environment найден")
    else:
        warn("venv не найден, попробую системный Python")
        venv_python = sys.executable

    try:
        # Проверяем импорт основного модуля
        from epson_print_conf import EpsonPrinter
        ok("epson_print_conf загружен")
        return True
    except ImportError as e:
        warn(f"Не удалось импортировать: {e}")
        info("Устанавливаю зависимости...")
        ret = os.system(f"cd {SCRIPT_DIR} && source venv/bin/activate && pip install -r requirements.txt -q 2>/dev/null")
        if ret == 0:
            ok("Зависимости установлены")
            return True
        else:
            err("Не удалось установить зависимости")
            err("Запустите вручную: cd epson_print_conf && source venv/bin/activate && pip install -r requirements.txt")
            return False

# ─── Скачивание базы принтеров ───────────────────────────────────────────────
def ensure_printer_db():
    step("2", "База данных принтеров")
    pickle_path = os.path.join(SCRIPT_DIR, "epson_print_conf.pickle")
    devices_xml = os.path.join(SCRIPT_DIR, "devices.xml")

    if os.path.exists(pickle_path) and os.path.getsize(pickle_path) > 100:
        ok("Pickle-конфигурация уже существует")
        return pickle_path

    if not os.path.exists(devices_xml):
        info("Скачиваю базу принтеров devices.xml...")
        url = "https://github.com/user-attachments/files/23294840/devices.xml"
        ret = os.system(f'curl -sL -o "{devices_xml}" "{url}"')
        if ret != 0 or not os.path.exists(devices_xml):
            err("Не удалось скачать devices.xml")
            return None
        ok(f"Скачано: {os.path.getsize(devices_xml) // 1024} KB")
    else:
        ok("devices.xml уже существует")

    info("Генерирую pickle-конфигурацию...")
    cmd = f'cd "{SCRIPT_DIR}" && source venv/bin/activate 2>/dev/null; python3 parse_devices.py -c devices.xml -p epson_print_conf.pickle 2>&1'
    ret = os.system(cmd)
    if ret == 0 and os.path.exists(pickle_path):
        ok("Конфигурация сгенерирована")
        return pickle_path
    else:
        err("Ошибка генерации pickle")
        return None

# ─── Поиск принтеров ────────────────────────────────────────────────────────
def find_printers_network():
    """Поиск принтеров в сети."""
    try:
        from find_printers import PrinterScanner
        scanner = PrinterScanner()
        printers = run_with_spinner("Сканирую сеть...", scanner.get_all_printers)
        return printers or []
    except Exception as e:
        warn(f"Ошибка сканирования: {e}")
        return []

def find_printers_usb():
    """Поиск USB-принтеров через system_profiler (macOS)."""
    usb_printers = []
    try:
        result = subprocess.run(
            ["system_profiler", "SPUSBDataType"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.split("\n")
        current = None
        for line in lines:
            stripped = line.strip()
            if "epson" in stripped.lower() and ":" in stripped:
                current = {"name": stripped.rstrip(":").strip(), "type": "USB"}
            if current and "Serial Number" in stripped:
                current["serial"] = stripped.split(":")[-1].strip()
            if current and stripped == "":
                if "name" in current:
                    usb_printers.append(current)
                current = None
        if current and "name" in current:
            usb_printers.append(current)
    except Exception:
        pass
    return usb_printers

def discover_printers():
    step("3", "Поиск принтеров")
    all_printers = []

    # USB
    info("Поиск USB-принтеров...")
    usb = find_printers_usb()
    for p in usb:
        ok(f"USB: {p['name']}")
        all_printers.append({"source": "USB", "name": p["name"], "ip": None})

    # Сеть
    info("Поиск сетевых принтеров (может занять ~30 сек)...")
    net = find_printers_network()
    for p in net:
        name = p.get("name", "Unknown")
        ip = p.get("ip", "?")
        ok(f"Сеть: {name} ({ip})")
        all_printers.append({"source": "Network", "name": name, "ip": ip})

    return all_printers

# ─── Главное меню операций ───────────────────────────────────────────────────
def get_available_actions(printer):
    """Возвращаем список доступных действий для принтера."""
    actions = []
    parm = printer.parm
    if not parm:
        return actions

    actions.append(("📊  Полный статус принтера", "stats"))

    if "main_waste" in parm:
        actions.append(("🔍  Показать уровень памперса (waste ink)", "show_waste"))

    if "raw_waste_reset" in parm or "main_waste" in parm:
        actions.append((f"{C.GREEN}♻️   Сброс памперса (ПОСТОЯННЫЙ){C.RST}", "reset_waste"))

    actions.append(("🔄  Временный сброс памперса", "temp_reset"))

    if "serial_number" in parm:
        actions.append(("🔢  Показать серийный номер", "serial"))

    if "stats" in parm:
        actions.append(("📈  Статистика принтера", "show_stats"))

    actions.append(("🖨️   Тест дюз (печать)", "nozzle_check"))
    actions.append(("🧹  Прочистка головки", "clean"))
    actions.append(("💪  Усиленная прочистка", "power_clean"))
    actions.append(("🌐  Открыть веб-интерфейс", "web"))

    return actions

def execute_action(printer, action_id, model_name):
    hline()
    try:
        if action_id == "stats":
            info("Получаю информацию о принтере...")
            import pprint
            data = run_with_spinner("Запрашиваю данные...", printer.stats)
            if data:
                print()
                pprint.pprint(data, width=100, compact=True)
            else:
                warn("Нет данных. Проверьте подключение.")

        elif action_id == "show_waste":
            info("Чтение уровня памперса...")
            levels = run_with_spinner("Запрашиваю...", printer.get_waste_ink_levels)
            if levels:
                print()
                for key, val in levels.items():
                    label = key.replace("_", " ").title()
                    bar_len = min(int(val / 2), 50)
                    color = C.GREEN if val < 50 else C.YELLOW if val < 80 else C.RED
                    bar = f"{color}{'█' * bar_len}{C.GRAY}{'░' * (50 - bar_len)}{C.RST}"
                    print(f"    {label:.<30s} [{bar}] {color}{val}%{C.RST}")
                print()
            else:
                warn("Не удалось прочитать уровень памперса.")

        elif action_id == "reset_waste":
            warn(f"{C.BOLD}ВНИМАНИЕ! Это ПОСТОЯННЫЙ сброс счётчика памперса!{C.RST}")
            warn("Физически памперс (абсорбер) тоже нужно промыть или заменить!")
            print()
            confirm = input(f"  {C.RED}▸{C.RST} Вы уверены? (да/нет): ").strip().lower()
            if confirm in ("да", "yes", "y", "д"):
                info("Сбрасываю счётчик памперса...")
                result = run_with_spinner("Записываю в EEPROM...", printer.reset_waste_ink_levels)
                if result:
                    ok(f"{C.GREEN}{C.BOLD}Счётчик памперса успешно сброшен!{C.RST}")
                    ok("Перезагрузите принтер для применения изменений.")
                else:
                    err("Ошибка сброса. Проверьте подключение и конфигурацию.")
            else:
                info("Операция отменена.")

        elif action_id == "temp_reset":
            info("Выполняю временный сброс...")
            result = run_with_spinner("Отправляю команду...", printer.temporary_reset_waste)
            if result:
                ok("Временный сброс выполнен!")
                warn("Сброс действует до перезагрузки принтера.")
            else:
                err("Ошибка временного сброса.")

        elif action_id == "serial":
            info("Чтение серийного номера...")
            sn = run_with_spinner("Запрашиваю...", printer.get_serial_number)
            if sn:
                ok(f"Серийный номер: {C.BOLD}{C.WHITE}{sn}{C.RST}")
            else:
                warn("Не удалось прочитать серийный номер.")

        elif action_id == "show_stats":
            info("Чтение статистики...")
            data = run_with_spinner("Запрашиваю...", lambda: printer.get_stats())
            if data:
                print()
                for key, val in data.items():
                    print(f"    {C.CYAN}{key}{C.RST}: {val}")
                print()
            else:
                warn("Статистика недоступна.")

        elif action_id == "nozzle_check":
            info("Отправляю тест дюз на печать...")
            result = printer.print_check_nozzles(type=0)
            if result:
                ok("Тест дюз отправлен на печать.")
            else:
                err("Ошибка отправки теста дюз.")

        elif action_id == "clean":
            confirm = input(f"  {C.YELLOW}▸{C.RST} Начать прочистку? (да/нет): ").strip().lower()
            if confirm in ("да", "yes", "y", "д"):
                info("Запускаю прочистку...")
                try:
                    result = printer.clean_nozzles(0)
                    if result:
                        ok("Прочистка запущена.")
                    else:
                        err("Ошибка прочистки.")
                except Exception as e:
                    err(f"Ошибка: {e}")
            else:
                info("Отменено.")

        elif action_id == "power_clean":
            warn("Усиленная прочистка расходует больше чернил!")
            confirm = input(f"  {C.YELLOW}▸{C.RST} Продолжить? (да/нет): ").strip().lower()
            if confirm in ("да", "yes", "y", "д"):
                info("Запускаю усиленную прочистку...")
                try:
                    result = printer.clean_nozzles(1)
                    if result:
                        ok("Усиленная прочистка запущена.")
                    else:
                        err("Ошибка усиленной прочистки.")
                except Exception as e:
                    err(f"Ошибка: {e}")
            else:
                info("Отменено.")

        elif action_id == "web":
            try:
                ip = printer.hostname
                if ip:
                    os.system(f'open "http://{ip}"')
                    ok(f"Открываю http://{ip} в браузере...")
                else:
                    err("IP-адрес принтера не задан.")
            except Exception:
                err("Не удалось открыть браузер.")

    except TimeoutError:
        err("Таймаут при обращении к принтеру.")
    except Exception as e:
        err(f"Ошибка: {e}")

    print()
    input(f"  {C.GRAY}Нажмите Enter для продолжения...{C.RST}")

# ─── Основной процесс ───────────────────────────────────────────────────────
def main():
    banner()

    # 1. Зависимости
    if not ensure_deps():
        sys.exit(1)

    from epson_print_conf import EpsonPrinter

    # 2. База принтеров
    pickle_path = ensure_printer_db()
    conf_dict = {}
    if pickle_path:
        try:
            with open(pickle_path, "rb") as f:
                conf_dict = pickle.load(f)
            ok(f"Загружено моделей: {len(conf_dict)}")
        except Exception as e:
            warn(f"Ошибка загрузки pickle: {e}")

    # 3. Поиск принтеров или ручной ввод
    step("3", "Подключение к принтеру")
    print()
    connect_opts = [
        ("🔍  Автопоиск принтеров в сети и USB", "auto"),
        ("📝  Ввести IP-адрес вручную", "manual"),
    ]
    choice = menu_choice(connect_opts, "Как подключиться к принтеру?")
    if choice is None:
        print(f"\n  {C.CYAN}До свидания!{C.RST}\n")
        sys.exit(0)

    target_ip = None
    model_name = None

    if connect_opts[choice][1] == "auto":
        found = discover_printers()
        if not found:
            warn("Принтеры не найдены автоматически.")
            print()
            target_ip = input(f"  {C.YELLOW}▸{C.RST} Введите IP-адрес принтера: ").strip()
        elif len(found) == 1 and found[0]["ip"]:
            target_ip = found[0]["ip"]
            model_name = found[0].get("name")
            ok(f"Используем: {model_name} ({target_ip})")
        else:
            net_printers = [p for p in found if p["ip"]]
            if not net_printers:
                warn("Найдены только USB-принтеры. Программа работает через сеть.")
                target_ip = input(f"  {C.YELLOW}▸{C.RST} Введите IP-адрес принтера: ").strip()
            else:
                opts = [(f"{p['name']} ({p['ip']})", p) for p in net_printers]
                idx = menu_choice(opts, "Выберите принтер")
                if idx is None:
                    sys.exit(0)
                target_ip = net_printers[idx]["ip"]
                model_name = net_printers[idx].get("name")
    else:
        target_ip = input(f"\n  {C.YELLOW}▸{C.RST} IP-адрес принтера: ").strip()

    if not target_ip:
        err("IP-адрес не указан.")
        sys.exit(1)

    # 4. Определение модели
    step("4", "Определение модели принтера")
    info(f"Подключаюсь к {target_ip}...")

    # Создаём временный принтер для определения модели
    temp_printer = EpsonPrinter(conf_dict=conf_dict, hostname=target_ip)
    try:
        snmp_info = run_with_spinner("Запрашиваю модель...",
            lambda: temp_printer.get_snmp_info("Model"))
        if snmp_info and "Model" in snmp_info:
            detected = snmp_info["Model"]
            ok(f"Обнаружена модель: {C.BOLD}{C.WHITE}{detected}{C.RST}")
            # Пытаемся найти короткое имя модели
            for m in temp_printer.valid_printers:
                if m.lower() in detected.lower() or detected.lower().replace(" series", "").strip() in m.lower():
                    model_name = m
                    break
            if not model_name:
                # Попробуем найти по части имени
                parts = detected.replace("EPSON ", "").replace(" Series", "").strip().split()
                for part in parts:
                    for m in temp_printer.valid_printers:
                        if part.lower() == m.lower():
                            model_name = m
                            break
                    if model_name:
                        break
    except Exception as e:
        warn(f"Не удалось определить модель автоматически: {e}")

    if not model_name:
        warn("Модель не определена автоматически.")
        print()
        info("Доступные модели:")
        valid = sorted(temp_printer.valid_printers)
        # Показываем в колонках
        cols = 4
        for i in range(0, len(valid), cols):
            row = valid[i:i+cols]
            print("    " + "  ".join(f"{C.CYAN}{m:<20s}{C.RST}" for m in row))
        print()
        model_name = input(f"  {C.YELLOW}▸{C.RST} Введите модель принтера: ").strip()

    if not model_name:
        err("Модель не указана.")
        sys.exit(1)

    # 5. Подключаемся к принтеру
    step("5", f"Подключение к {model_name}")
    printer = EpsonPrinter(
        conf_dict=conf_dict,
        model=model_name,
        hostname=target_ip
    )
    if not printer.parm:
        err(f"Модель '{model_name}' не найдена в конфигурации.")
        err("Попробуйте другое имя модели.")
        sys.exit(1)

    ok(f"Принтер: {C.BOLD}{model_name}{C.RST}")
    ok(f"Адрес:   {C.BOLD}{target_ip}{C.RST}")

    # Проверяем соединение
    try:
        sn = run_with_spinner("Проверяю связь...", printer.get_serial_number)
        if sn:
            ok(f"Серийный номер: {C.BOLD}{sn}{C.RST}")
            ok(f"{C.GREEN}Соединение установлено!{C.RST}")
        else:
            warn("Серийный номер не получен, но попробуем продолжить.")
    except Exception:
        warn("Проверка связи не удалась, попробуем продолжить.")

    # 6. Главное меню
    while True:
        banner()
        print(f"  {C.BOLD}Принтер:{C.RST} {C.CYAN}{model_name}{C.RST}  │  {C.BOLD}IP:{C.RST} {C.CYAN}{target_ip}{C.RST}")
        hline()

        actions = get_available_actions(printer)
        if not actions:
            err("Нет доступных операций для этой модели.")
            break

        idx = menu_choice(actions, "Доступные операции")
        if idx is None:
            print(f"\n  {C.CYAN}До свидания! 👋{C.RST}\n")
            break

        action_id = actions[idx][1]
        execute_action(printer, action_id, model_name)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.CYAN}Прервано пользователем. До свидания!{C.RST}\n")
        sys.exit(0)
