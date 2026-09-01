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
import ipaddress
import subprocess
import threading
import warnings
import webbrowser

warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

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
    ╔══════════════════════════════════════════════════════╗
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
    print(f"{C.GRAY}{'\u2500' * 58}{C.RST}")

def info(msg):
    print(f"  {C.CYAN}\u2139{C.RST}  {msg}")

def ok(msg):
    print(f"  {C.GREEN}\u2714{C.RST}  {msg}")

def warn(msg):
    print(f"  {C.YELLOW}\u26a0{C.RST}  {msg}")

def err(msg):
    print(f"  {C.RED}\u2716{C.RST}  {msg}")

def step(num, msg):
    print(f"\n  {C.MAGENTA}{C.BOLD}[{num}]{C.RST} {C.BOLD}{msg}{C.RST}")
    hline()

def spinner(msg, stop_event):
    chars = "\u280b\u2819\u2839\u2838\u283c\u2834\u2826\u2827\u2807\u280f"
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

def menu_choice(options, title="\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435"):
    print(f"\n  {C.BOLD}{C.WHITE}{title}:{C.RST}\n")
    for idx, (label, _desc) in enumerate(options, 1):
        print(f"    {C.CYAN}{C.BOLD}{idx}{C.RST}  \u2502  {label}")
    print(f"    {C.RED}{C.BOLD}0{C.RST}  \u2502  \u0412\u044b\u0445\u043e\u0434\n")
    while True:
        try:
            raw = input(f"  {C.YELLOW}\u25b8{C.RST} \u0412\u0430\u0448 \u0432\u044b\u0431\u043e\u0440: ").strip()
            if raw == "0":
                return None
            n = int(raw)
            if 1 <= n <= len(options):
                return n - 1
        except (ValueError, EOFError):
            pass
        err("\u041d\u0435\u0432\u0435\u0440\u043d\u044b\u0439 \u0432\u0432\u043e\u0434, \u043f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u0435\u0449\u0451 \u0440\u0430\u0437")


def is_valid_printer_host(value):
    """Return a stripped IPv4/IPv6/hostname, or None if the value is unusable."""
    host = (value or "").strip()
    if not host:
        return None
    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        pass
    if all(part.isdigit() for part in host.split(".")) and "." in host:
        return None
    if "://" in host or "/" in host or " " in host or ";" in host:
        return None
    labels = host.split(".")
    if not labels or len(host) > 253:
        return None
    for label in labels:
        if not label or len(label) > 63:
            return None
        if label.startswith("-") or label.endswith("-"):
            return None
        if not all(c.isalnum() or c == "-" for c in label):
            return None
    return host


def _venv_python():
    """Prefer run.sh's .venv, then legacy venv/, then the current interpreter."""
    candidates = [
        os.path.join(SCRIPT_DIR, ".venv", "bin", "python3"),
        os.path.join(SCRIPT_DIR, ".venv", "bin", "python"),
        os.path.join(SCRIPT_DIR, "venv", "bin", "python3"),
        os.path.join(SCRIPT_DIR, "venv", "bin", "python"),
        os.path.join(SCRIPT_DIR, ".venv", "Scripts", "python.exe"),
        os.path.join(SCRIPT_DIR, "venv", "Scripts", "python.exe"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return sys.executable

def ensure_deps():
    step("1", "\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0437\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0441\u0442\u0435\u0439")
    venv_python = _venv_python()
    if venv_python != sys.executable:
        ok("Virtual environment \u043d\u0430\u0439\u0434\u0435\u043d")
    else:
        warn("venv \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d, \u043f\u043e\u043f\u0440\u043e\u0431\u0443\u044e \u0441\u0438\u0441\u0442\u0435\u043c\u043d\u044b\u0439 Python")

    try:
        from epson_print_conf import EpsonPrinter  # noqa: F401
        ok("epson_print_conf \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043d")
        return True
    except ImportError as e:
        warn(f"\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0438\u043c\u043f\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c: {e}")
        info("\u0423\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u044e \u0437\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0441\u0442\u0438...")
        req = os.path.join(SCRIPT_DIR, "requirements.txt")
        ret = subprocess.run(
            [venv_python, "-m", "pip", "install", "-r", req],
            cwd=SCRIPT_DIR,
        )
        if ret.returncode == 0:
            ok("\u0417\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0441\u0442\u0438 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u044b")
            return True
        err("\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c \u0437\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0441\u0442\u0438")
        err("\u0417\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u0435 \u0432\u0440\u0443\u0447\u043d\u0443\u044e: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt")
        return False

def ensure_printer_db():
    step("2", "\u0411\u0430\u0437\u0430 \u0434\u0430\u043d\u043d\u044b\u0445 \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u043e\u0432")
    pickle_path = os.path.join(SCRIPT_DIR, "epson_print_conf.pickle")
    devices_xml = os.path.join(SCRIPT_DIR, "devices.xml")

    if os.path.exists(pickle_path) and os.path.getsize(pickle_path) > 100:
        ok("Pickle-\u043a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044f \u0443\u0436\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442")
        return pickle_path

    if not os.path.exists(devices_xml):
        err("devices.xml \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d \u0432 \u043a\u0430\u0442\u0430\u043b\u043e\u0433\u0435 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b.")
        err("\u0421\u043a\u043e\u043f\u0438\u0440\u0443\u0439\u0442\u0435 devices.xml \u0438\u0437 \u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u044f \u0438 \u043f\u043e\u0432\u0442\u043e\u0440\u0438\u0442\u0435 \u0437\u0430\u043f\u0443\u0441\u043a.")
        return None
    ok("devices.xml \u0443\u0436\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442")

    info("\u0413\u0435\u043d\u0435\u0440\u0438\u0440\u0443\u044e pickle-\u043a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044e...")
    py = _venv_python()
    parse_script = os.path.join(SCRIPT_DIR, "parse_devices.py")
    ret = subprocess.run(
        [py, parse_script, "-c", devices_xml, "-p", pickle_path],
        cwd=SCRIPT_DIR,
    )
    if ret.returncode == 0 and os.path.exists(pickle_path):
        ok("\u041a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044f \u0441\u0433\u0435\u043d\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u0430")
        return pickle_path
    err("\u041e\u0448\u0438\u0431\u043a\u0430 \u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u0438 pickle")
    return None

def find_printers_network():
    try:
        from find_printers import PrinterScanner
        scanner = PrinterScanner()
        printers = run_with_spinner("\u0421\u043a\u0430\u043d\u0438\u0440\u0443\u044e \u0441\u0435\u0442\u044c...", scanner.get_all_printers)
        return printers or []
    except Exception as e:
        warn(f"\u041e\u0448\u0438\u0431\u043a\u0430 \u0441\u043a\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f: {e}")
        return []

def find_printers_usb():
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
    step("3", "\u041f\u043e\u0438\u0441\u043a \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u043e\u0432")
    all_printers = []
    info("\u041f\u043e\u0438\u0441\u043a USB-\u043f\u0440\u0438\u043d\u0442\u0435\u0440\u043e\u0432...")
    usb = find_printers_usb()
    for p in usb:
        ok(f"USB: {p['name']}")
        all_printers.append({"source": "USB", "name": p["name"], "ip": None})
    info("\u041f\u043e\u0438\u0441\u043a \u0441\u0435\u0442\u0435\u0432\u044b\u0445 \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u043e\u0432 (\u043c\u043e\u0436\u0435\u0442 \u0437\u0430\u043d\u044f\u0442\u044c ~30 \u0441\u0435\u043a)...")
    net = find_printers_network()
    for p in net:
        name = p.get("name", "Unknown")
        ip = p.get("ip", "?")
        ok(f"\u0421\u0435\u0442\u044c: {name} ({ip})")
        all_printers.append({"source": "Network", "name": name, "ip": ip})
    return all_printers

def get_available_actions(printer):
    actions = []
    parm = printer.parm
    if not parm:
        return actions
    actions.append(("\U0001f4ca  \u041f\u043e\u043b\u043d\u044b\u0439 \u0441\u0442\u0430\u0442\u0443\u0441 \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0430", "stats"))
    if "main_waste" in parm:
        actions.append(("\U0001f50d  \u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u0443\u0440\u043e\u0432\u0435\u043d\u044c \u043f\u0430\u043c\u043f\u0435\u0440\u0441\u0430 (waste ink)", "show_waste"))
    if "raw_waste_reset" in parm or "main_waste" in parm:
        actions.append((f"{C.GREEN}\u267b\ufe0f   \u0421\u0431\u0440\u043e\u0441 \u043f\u0430\u043c\u043f\u0435\u0440\u0441\u0430 (\u041f\u041e\u0421\u0422\u041e\u042f\u041d\u041d\u042b\u0419){C.RST}", "reset_waste"))
    actions.append(("\U0001f504  \u0412\u0440\u0435\u043c\u0435\u043d\u043d\u044b\u0439 \u0441\u0431\u0440\u043e\u0441 \u043f\u0430\u043c\u043f\u0435\u0440\u0441\u0430", "temp_reset"))
    if "serial_number" in parm:
        actions.append(("\U0001f522  \u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u0441\u0435\u0440\u0438\u0439\u043d\u044b\u0439 \u043d\u043e\u043c\u0435\u0440", "serial"))
    if "stats" in parm:
        actions.append(("\U0001f4c8  \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0430", "show_stats"))
    actions.append(("\U0001f5a8\ufe0f   \u0422\u0435\u0441\u0442 \u0434\u044e\u0437 (\u043f\u0435\u0447\u0430\u0442\u044c)", "nozzle_check"))
    actions.append(("\U0001f9f9  \u041f\u0440\u043e\u0447\u0438\u0441\u0442\u043a\u0430 \u0433\u043e\u043b\u043e\u0432\u043a\u0438", "clean"))
    actions.append(("\U0001f4aa  \u0423\u0441\u0438\u043b\u0435\u043d\u043d\u0430\u044f \u043f\u0440\u043e\u0447\u0438\u0441\u0442\u043a\u0430", "power_clean"))
    actions.append(("\U0001f310  \u041e\u0442\u043a\u0440\u044b\u0442\u044c \u0432\u0435\u0431-\u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441", "web"))
    return actions

def execute_action(printer, action_id, model_name):
    hline()
    try:
        if action_id == "stats":
            info("\u041f\u043e\u043b\u0443\u0447\u0430\u044e \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044e \u043e \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0435...")
            import pprint
            data = run_with_spinner("\u0417\u0430\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u044e \u0434\u0430\u043d\u043d\u044b\u0435...", printer.stats)
            if data:
                print()
                pprint.pprint(data, width=100, compact=True)
            else:
                warn("\u041d\u0435\u0442 \u0434\u0430\u043d\u043d\u044b\u0445. \u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435.")
        elif action_id == "show_waste":
            info("\u0427\u0442\u0435\u043d\u0438\u0435 \u0443\u0440\u043e\u0432\u043d\u044f \u043f\u0430\u043c\u043f\u0435\u0440\u0441\u0430...")
            levels = run_with_spinner("\u0417\u0430\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u044e...", printer.get_waste_ink_levels)
            if levels:
                print()
                for key, val in levels.items():
                    label = key.replace("_", " ").title()
                    bar_len = min(int(val / 2), 50)
                    color = C.GREEN if val < 50 else C.YELLOW if val < 80 else C.RED
                    bar = f"{color}{'\u2588' * bar_len}{C.GRAY}{'\u2591' * (50 - bar_len)}{C.RST}"
                    print(f"    {label:.<30s} [{bar}] {color}{val}%{C.RST}")
                print()
            else:
                warn("\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043f\u0440\u043e\u0447\u0438\u0442\u0430\u0442\u044c \u0443\u0440\u043e\u0432\u0435\u043d\u044c \u043f\u0430\u043c\u043f\u0435\u0440\u0441\u0430.")
        elif action_id == "reset_waste":
            warn(f"{C.BOLD}\u0412\u041d\u0418\u041c\u0410\u041d\u0418\u0415! \u042d\u0442\u043e \u041f\u041e\u0421\u0422\u041e\u042f\u041d\u041d\u042b\u0419 \u0441\u0431\u0440\u043e\u0441 \u0441\u0447\u0451\u0442\u0447\u0438\u043a\u0430 \u043f\u0430\u043c\u043f\u0435\u0440\u0441\u0430!{C.RST}")
            warn("\u0424\u0438\u0437\u0438\u0447\u0435\u0441\u043a\u0438 \u043f\u0430\u043c\u043f\u0435\u0440\u0441 (\u0430\u0431\u0441\u043e\u0440\u0431\u0435\u0440) \u0442\u043e\u0436\u0435 \u043d\u0443\u0436\u043d\u043e \u043f\u0440\u043e\u043c\u044b\u0442\u044c \u0438\u043b\u0438 \u0437\u0430\u043c\u0435\u043d\u0438\u0442\u044c!")
            print()
            confirm = input(f"  {C.RED}\u25b8{C.RST} \u0412\u044b \u0443\u0432\u0435\u0440\u0435\u043d\u044b? (\u0434\u0430/\u043d\u0435\u0442): ").strip().lower()
            if confirm in ("\u0434\u0430", "yes", "y", "\u0434"):
                info("\u0421\u0431\u0440\u0430\u0441\u044b\u0432\u0430\u044e \u0441\u0447\u0451\u0442\u0447\u0438\u043a \u043f\u0430\u043c\u043f\u0435\u0440\u0441\u0430...")
                result = run_with_spinner("\u0417\u0430\u043f\u0438\u0441\u044b\u0432\u0430\u044e \u0432 EEPROM...", printer.reset_waste_ink_levels)
                if result:
                    ok(f"{C.GREEN}{C.BOLD}\u0421\u0447\u0451\u0442\u0447\u0438\u043a \u043f\u0430\u043c\u043f\u0435\u0440\u0441\u0430 \u0443\u0441\u043f\u0435\u0448\u043d\u043e \u0441\u0431\u0440\u043e\u0448\u0435\u043d!{C.RST}")
                    ok("\u041f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u0435 \u043f\u0440\u0438\u043d\u0442\u0435\u0440 \u0434\u043b\u044f \u043f\u0440\u0438\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0439.")
                else:
                    err("\u041e\u0448\u0438\u0431\u043a\u0430 \u0441\u0431\u0440\u043e\u0441\u0430. \u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u0438 \u043a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044e.")
            else:
                info("\u041e\u043f\u0435\u0440\u0430\u0446\u0438\u044f \u043e\u0442\u043c\u0435\u043d\u0435\u043d\u0430.")
        elif action_id == "temp_reset":
            info("\u0412\u044b\u043f\u043e\u043b\u043d\u044f\u044e \u0432\u0440\u0435\u043c\u0435\u043d\u043d\u044b\u0439 \u0441\u0431\u0440\u043e\u0441...")
            result = run_with_spinner("\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u044f\u044e \u043a\u043e\u043c\u0430\u043d\u0434\u0443...", printer.temporary_reset_waste)
            if result:
                ok("\u0412\u0440\u0435\u043c\u0435\u043d\u043d\u044b\u0439 \u0441\u0431\u0440\u043e\u0441 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d!")
                warn("\u0421\u0431\u0440\u043e\u0441 \u0434\u0435\u0439\u0441\u0442\u0432\u0443\u0435\u0442 \u0434\u043e \u043f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438 \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0430.")
            else:
                err("\u041e\u0448\u0438\u0431\u043a\u0430 \u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e\u0433\u043e \u0441\u0431\u0440\u043e\u0441\u0430.")
        elif action_id == "serial":
            info("\u0427\u0442\u0435\u043d\u0438\u0435 \u0441\u0435\u0440\u0438\u0439\u043d\u043e\u0433\u043e \u043d\u043e\u043c\u0435\u0440\u0430...")
            sn = run_with_spinner("\u0417\u0430\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u044e...", printer.get_serial_number)
            if sn:
                ok(f"\u0421\u0435\u0440\u0438\u0439\u043d\u044b\u0439 \u043d\u043e\u043c\u0435\u0440: {C.BOLD}{C.WHITE}{sn}{C.RST}")
            else:
                warn("\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043f\u0440\u043e\u0447\u0438\u0442\u0430\u0442\u044c \u0441\u0435\u0440\u0438\u0439\u043d\u044b\u0439 \u043d\u043e\u043c\u0435\u0440.")
        elif action_id == "show_stats":
            info("\u0427\u0442\u0435\u043d\u0438\u0435 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0438...")
            data = run_with_spinner("\u0417\u0430\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u044e...", lambda: printer.get_stats())
            if data:
                print()
                for key, val in data.items():
                    print(f"    {C.CYAN}{key}{C.RST}: {val}")
                print()
            else:
                warn("\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u043d\u0430.")
        elif action_id == "nozzle_check":
            info("\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u044f\u044e \u0442\u0435\u0441\u0442 \u0434\u044e\u0437 \u043d\u0430 \u043f\u0435\u0447\u0430\u0442\u044c...")
            result = printer.print_check_nozzles(type=0)
            if result:
                ok("\u0422\u0435\u0441\u0442 \u0434\u044e\u0437 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d \u043d\u0430 \u043f\u0435\u0447\u0430\u0442\u044c.")
            else:
                err("\u041e\u0448\u0438\u0431\u043a\u0430 \u043e\u0442\u043f\u0440\u0430\u0432\u043a\u0438 \u0442\u0435\u0441\u0442\u0430 \u0434\u044e\u0437.")
        elif action_id == "clean":
            confirm = input(f"  {C.YELLOW}\u25b8{C.RST} \u041d\u0430\u0447\u0430\u0442\u044c \u043f\u0440\u043e\u0447\u0438\u0441\u0442\u043a\u0443? (\u0434\u0430/\u043d\u0435\u0442): ").strip().lower()
            if confirm in ("\u0434\u0430", "yes", "y", "\u0434"):
                info("\u0417\u0430\u043f\u0443\u0441\u043a\u0430\u044e \u043f\u0440\u043e\u0447\u0438\u0441\u0442\u043a\u0443...")
                try:
                    result = printer.clean_nozzles(0)
                    if result:
                        ok("\u041f\u0440\u043e\u0447\u0438\u0441\u0442\u043a\u0430 \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u0430.")
                    else:
                        err("\u041e\u0448\u0438\u0431\u043a\u0430 \u043f\u0440\u043e\u0447\u0438\u0441\u0442\u043a\u0438.")
                except Exception as e:
                    err(f"\u041e\u0448\u0438\u0431\u043a\u0430: {e}")
            else:
                info("\u041e\u0442\u043c\u0435\u043d\u0435\u043d\u043e.")
        elif action_id == "power_clean":
            warn("\u0423\u0441\u0438\u043b\u0435\u043d\u043d\u0430\u044f \u043f\u0440\u043e\u0447\u0438\u0441\u0442\u043a\u0430 \u0440\u0430\u0441\u0445\u043e\u0434\u0443\u0435\u0442 \u0431\u043e\u043b\u044c\u0448\u0435 \u0447\u0435\u0440\u043d\u0438\u043b!")
            confirm = input(f"  {C.YELLOW}\u25b8{C.RST} \u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u044c? (\u0434\u0430/\u043d\u0435\u0442): ").strip().lower()
            if confirm in ("\u0434\u0430", "yes", "y", "\u0434"):
                info("\u0417\u0430\u043f\u0443\u0441\u043a\u0430\u044e \u0443\u0441\u0438\u043b\u0435\u043d\u043d\u0443\u044e \u043f\u0440\u043e\u0447\u0438\u0441\u0442\u043a\u0443...")
                try:
                    result = printer.clean_nozzles(1)
                    if result:
                        ok("\u0423\u0441\u0438\u043b\u0435\u043d\u043d\u0430\u044f \u043f\u0440\u043e\u0447\u0438\u0441\u0442\u043a\u0430 \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u0430.")
                    else:
                        err("\u041e\u0448\u0438\u0431\u043a\u0430 \u0443\u0441\u0438\u043b\u0435\u043d\u043d\u043e\u0439 \u043f\u0440\u043e\u0447\u0438\u0441\u0442\u043a\u0438.")
                except Exception as e:
                    err(f"\u041e\u0448\u0438\u0431\u043a\u0430: {e}")
            else:
                info("\u041e\u0442\u043c\u0435\u043d\u0435\u043d\u043e.")
        elif action_id == "web":
            try:
                ip = printer.hostname
                host = is_valid_printer_host(ip) if ip else None
                if host:
                    webbrowser.open(f"http://{host}")
                    ok(f"\u041e\u0442\u043a\u0440\u044b\u0432\u0430\u044e http://{host} \u0432 \u0431\u0440\u0430\u0443\u0437\u0435\u0440\u0435...")
                else:
                    err("IP-\u0430\u0434\u0440\u0435\u0441 \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0430 \u043d\u0435 \u0437\u0430\u0434\u0430\u043d.")
            except Exception:
                err("\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043e\u0442\u043a\u0440\u044b\u0442\u044c \u0431\u0440\u0430\u0443\u0437\u0435\u0440.")
    except TimeoutError:
        err("\u0422\u0430\u0439\u043c\u0430\u0443\u0442 \u043f\u0440\u0438 \u043e\u0431\u0440\u0430\u0449\u0435\u043d\u0438\u0438 \u043a \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0443.")
    except Exception as e:
        err(f"\u041e\u0448\u0438\u0431\u043a\u0430: {e}")
    print()
    input(f"  {C.GRAY}\u041d\u0430\u0436\u043c\u0438\u0442\u0435 Enter \u0434\u043b\u044f \u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0435\u043d\u0438\u044f...{C.RST}")

def _ask_printer_host(prompt):
    raw = input(prompt).strip()
    host = is_valid_printer_host(raw)
    if not host:
        err("\u041d\u0435\u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u044b\u0439 IP-\u0430\u0434\u0440\u0435\u0441 \u0438\u043b\u0438 \u0438\u043c\u044f \u0445\u043e\u0441\u0442\u0430.")
        return None
    return host

def main():
    banner()
    if not ensure_deps():
        sys.exit(1)
    from epson_print_conf import EpsonPrinter
    pickle_path = ensure_printer_db()
    conf_dict = {}
    if pickle_path:
        try:
            with open(pickle_path, "rb") as f:
                conf_dict = pickle.load(f)
            ok(f"\u0417\u0430\u0433\u0440\u0443\u0436\u0435\u043d\u043e \u043c\u043e\u0434\u0435\u043b\u0435\u0439: {len(conf_dict)}")
        except Exception as e:
            warn(f"\u041e\u0448\u0438\u0431\u043a\u0430 \u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438 pickle: {e}")
    step("3", "\u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u043a \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0443")
    print()
    connect_opts = [
        ("\U0001f50d  \u0410\u0432\u0442\u043e\u043f\u043e\u0438\u0441\u043a \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u043e\u0432 \u0432 \u0441\u0435\u0442\u0438 \u0438 USB", "auto"),
        ("\U0001f4dd  \u0412\u0432\u0435\u0441\u0442\u0438 IP-\u0430\u0434\u0440\u0435\u0441 \u0432\u0440\u0443\u0447\u043d\u0443\u044e", "manual"),
    ]
    choice = menu_choice(connect_opts, "\u041a\u0430\u043a \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u0442\u044c\u0441\u044f \u043a \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0443?")
    if choice is None:
        print(f"\n  {C.CYAN}\u0414\u043e \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u044f!{C.RST}\n")
        sys.exit(0)
    target_ip = None
    model_name = None
    if connect_opts[choice][1] == "auto":
        found = discover_printers()
        if not found:
            warn("\u041f\u0440\u0438\u043d\u0442\u0435\u0440\u044b \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u044b \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438.")
            print()
            target_ip = _ask_printer_host(f"  {C.YELLOW}\u25b8{C.RST} \u0412\u0432\u0435\u0434\u0438\u0442\u0435 IP-\u0430\u0434\u0440\u0435\u0441 \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0430: ")
        elif len(found) == 1 and found[0]["ip"]:
            target_ip = found[0]["ip"]
            model_name = found[0].get("name")
            ok(f"\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u043c: {model_name} ({target_ip})")
        else:
            net_printers = [p for p in found if p["ip"]]
            if not net_printers:
                warn("\u041d\u0430\u0439\u0434\u0435\u043d\u044b \u0442\u043e\u043b\u044c\u043a\u043e USB-\u043f\u0440\u0438\u043d\u0442\u0435\u0440\u044b. \u041f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0430 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u0447\u0435\u0440\u0435\u0437 \u0441\u0435\u0442\u044c.")
                target_ip = _ask_printer_host(f"  {C.YELLOW}\u25b8{C.RST} \u0412\u0432\u0435\u0434\u0438\u0442\u0435 IP-\u0430\u0434\u0440\u0435\u0441 \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0430: ")
            else:
                opts = [(f"{p['name']} ({p['ip']})", p) for p in net_printers]
                idx = menu_choice(opts, "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0440\u0438\u043d\u0442\u0435\u0440")
                if idx is None:
                    sys.exit(0)
                target_ip = net_printers[idx]["ip"]
                model_name = net_printers[idx].get("name")
    else:
        target_ip = _ask_printer_host(f"\n  {C.YELLOW}\u25b8{C.RST} IP-\u0430\u0434\u0440\u0435\u0441 \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0430: ")
    if not target_ip:
        err("IP-\u0430\u0434\u0440\u0435\u0441 \u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d.")
        sys.exit(1)
    target_ip = is_valid_printer_host(target_ip)
    if not target_ip:
        err("\u041d\u0435\u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u044b\u0439 IP-\u0430\u0434\u0440\u0435\u0441 \u0438\u043b\u0438 \u0438\u043c\u044f \u0445\u043e\u0441\u0442\u0430.")
        sys.exit(1)
    step("4", "\u041e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u0435 \u043c\u043e\u0434\u0435\u043b\u0438 \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0430")
    info(f"\u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0430\u044e\u0441\u044c \u043a {target_ip}...")
    temp_printer = EpsonPrinter(conf_dict=conf_dict, hostname=target_ip)
    try:
        snmp_info = run_with_spinner("\u0417\u0430\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u044e \u043c\u043e\u0434\u0435\u043b\u044c...",
            lambda: temp_printer.get_snmp_info("Model"))
        if snmp_info and "Model" in snmp_info:
            detected = snmp_info["Model"]
            ok(f"\u041e\u0431\u043d\u0430\u0440\u0443\u0436\u0435\u043d\u0430 \u043c\u043e\u0434\u0435\u043b\u044c: {C.BOLD}{C.WHITE}{detected}{C.RST}")
            for m in temp_printer.valid_printers:
                if m.lower() in detected.lower() or detected.lower().replace(" series", "").strip() in m.lower():
                    model_name = m
                    break
            if not model_name:
                parts = detected.replace("EPSON ", "").replace(" Series", "").strip().split()
                for part in parts:
                    for m in temp_printer.valid_printers:
                        if part.lower() == m.lower():
                            model_name = m
                            break
                    if model_name:
                        break
    except Exception as e:
        warn(f"\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0438\u0442\u044c \u043c\u043e\u0434\u0435\u043b\u044c \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438: {e}")
    if not model_name:
        warn("\u041c\u043e\u0434\u0435\u043b\u044c \u043d\u0435 \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0430 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438.")
        print()
        info("\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0435 \u043c\u043e\u0434\u0435\u043b\u0438:")
        valid = sorted(temp_printer.valid_printers)
        cols = 4
        for i in range(0, len(valid), cols):
            row = valid[i:i+cols]
            print("    " + "  ".join(f"{C.CYAN}{m:<20s}{C.RST}" for m in row))
        print()
        model_name = input(f"  {C.YELLOW}\u25b8{C.RST} \u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043c\u043e\u0434\u0435\u043b\u044c \u043f\u0440\u0438\u043d\u0442\u0435\u0440\u0430: ").strip()
    if not model_name:
        err("\u041c\u043e\u0434\u0435\u043b\u044c \u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0430.")
        sys.exit(1)
    step("5", f"\u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u043a {model_name}")
    printer = EpsonPrinter(conf_dict=conf_dict, model=model_name, hostname=target_ip)
    if not printer.parm:
        err(f"\u041c\u043e\u0434\u0435\u043b\u044c '{model_name}' \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430 \u0432 \u043a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u0438.")
        err("\u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u0434\u0440\u0443\u0433\u043e\u0435 \u0438\u043c\u044f \u043c\u043e\u0434\u0435\u043b\u0438.")
        sys.exit(1)
    ok(f"\u041f\u0440\u0438\u043d\u0442\u0435\u0440: {C.BOLD}{model_name}{C.RST}")
    ok(f"\u0410\u0434\u0440\u0435\u0441:   {C.BOLD}{target_ip}{C.RST}")
    try:
        sn = run_with_spinner("\u041f\u0440\u043e\u0432\u0435\u0440\u044f\u044e \u0441\u0432\u044f\u0437\u044c...", printer.get_serial_number)
        if sn:
            ok(f"\u0421\u0435\u0440\u0438\u0439\u043d\u044b\u0439 \u043d\u043e\u043c\u0435\u0440: {C.BOLD}{sn}{C.RST}")
            ok(f"{C.GREEN}\u0421\u043e\u0435\u0434\u0438\u043d\u0435\u043d\u0438\u0435 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043e!{C.RST}")
        else:
            warn("\u0421\u0435\u0440\u0438\u0439\u043d\u044b\u0439 \u043d\u043e\u043c\u0435\u0440 \u043d\u0435 \u043f\u043e\u043b\u0443\u0447\u0435\u043d, \u043d\u043e \u043f\u043e\u043f\u0440\u043e\u0431\u0443\u0435\u043c \u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u044c.")
    except Exception:
        warn("\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0441\u0432\u044f\u0437\u0438 \u043d\u0435 \u0443\u0434\u0430\u043b\u0430\u0441\u044c, \u043f\u043e\u043f\u0440\u043e\u0431\u0443\u0435\u043c \u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u044c.")
    while True:
        banner()
        print(f"  {C.BOLD}\u041f\u0440\u0438\u043d\u0442\u0435\u0440:{C.RST} {C.CYAN}{model_name}{C.RST}  \u2502  {C.BOLD}IP:{C.RST} {C.CYAN}{target_ip}{C.RST}")
        hline()
        actions = get_available_actions(printer)
        if not actions:
            err("\u041d\u0435\u0442 \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0445 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0439 \u0434\u043b\u044f \u044d\u0442\u043e\u0439 \u043c\u043e\u0434\u0435\u043b\u0438.")
            break
        idx = menu_choice(actions, "\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0435 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0438")
        if idx is None:
            print(f"\n  {C.CYAN}\u0414\u043e \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u044f! \U0001f44b{C.RST}\n")
            break
        action_id = actions[idx][1]
        execute_action(printer, action_id, model_name)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.CYAN}\u041f\u0440\u0435\u0440\u0432\u0430\u043d\u043e \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u043c. \u0414\u043e \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u044f!{C.RST}\n")
        sys.exit(0)
