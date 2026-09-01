#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Epson Easy Reset CLI: discover printers and reset waste-ink counters."""
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
    GRAY = "\033[90m"

HLINE = "-" * 58

def clr():
    os.system("clear" if os.name != "nt" else "cls")

def banner():
    clr()
    print(C.CYAN + C.BOLD + "\n    EPSON EASY RESET\n" + C.RST)
    print(C.DIM + "    Waste-ink counter reset for Epson printers\n" + C.RST)

def hline():
    print(C.GRAY + HLINE + C.RST)

def info(msg):
    print("  [i]  " + msg)

def ok(msg):
    print(C.GREEN + "  [ok] " + C.RST + msg)

def warn(msg):
    print(C.YELLOW + "  [!]  " + C.RST + msg)

def err(msg):
    print(C.RED + "  [x]  " + C.RST + msg)

def step(num, msg):
    print("\n  [" + str(num) + "] " + C.BOLD + msg + C.RST)
    hline()

def spinner(msg, stop_event):
    chars = "|/-\\"
    i = 0
    while not stop_event.is_set():
        print("\r  " + chars[i % len(chars)] + "  " + msg, end="", flush=True)
        i += 1
        time.sleep(0.1)
    print("\r" + " " * (len(msg) + 10) + "\r", end="")

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

def menu_choice(options, title="Choose an action"):
    print("\n  " + C.BOLD + title + ":" + C.RST + "\n")
    for idx, (label, _desc) in enumerate(options, 1):
        print("    " + str(idx) + "  |  " + label)
    print("    0  |  Exit\n")
    while True:
        try:
            raw = input("  > ").strip()
            if raw == "0":
                return None
            n = int(raw)
            if 1 <= n <= len(options):
                return n - 1
        except (ValueError, EOFError):
            pass
        err("Invalid input, try again")

def is_valid_printer_host(value):
    """Return a stripped IPv4/IPv6/hostname, or None if unusable."""
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
    step("1", "Checking dependencies")
    venv_python = _venv_python()
    if venv_python != sys.executable:
        ok("Virtual environment found")
    else:
        warn("venv not found, trying system Python")
    try:
        from epson_print_conf import EpsonPrinter  # noqa: F401
        ok("epson_print_conf loaded")
        return True
    except ImportError as e:
        warn("Import failed: " + str(e))
        info("Installing requirements...")
        req = os.path.join(SCRIPT_DIR, "requirements.txt")
        ret = subprocess.run([venv_python, "-m", "pip", "install", "-r", req], cwd=SCRIPT_DIR)
        if ret.returncode == 0:
            ok("Dependencies installed")
            return True
        err("Could not install dependencies")
        err("Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt")
        return False

def ensure_printer_db():
    step("2", "Printer database")
    pickle_path = os.path.join(SCRIPT_DIR, "epson_print_conf.pickle")
    devices_xml = os.path.join(SCRIPT_DIR, "devices.xml")
    if os.path.exists(pickle_path) and os.path.getsize(pickle_path) > 100:
        ok("Pickle configuration already exists")
        return pickle_path
    if not os.path.exists(devices_xml):
        err("devices.xml not found. Copy it from the repository and retry.")
        return None
    ok("devices.xml already exists")
    info("Generating pickle configuration...")
    py = _venv_python()
    parse_script = os.path.join(SCRIPT_DIR, "parse_devices.py")
    ret = subprocess.run([py, parse_script, "-c", devices_xml, "-p", pickle_path], cwd=SCRIPT_DIR)
    if ret.returncode == 0 and os.path.exists(pickle_path):
        ok("Configuration generated")
        return pickle_path
    err("Pickle generation failed")
    return None

def find_printers_network():
    try:
        from find_printers import PrinterScanner
        scanner = PrinterScanner()
        return run_with_spinner("Scanning network...", scanner.get_all_printers) or []
    except Exception as e:
        warn("Scan error: " + str(e))
        return []

def find_printers_usb():
    usb_printers = []
    try:
        result = subprocess.run(["system_profiler", "SPUSBDataType"], capture_output=True, text=True, timeout=10)
        current = None
        for line in result.stdout.split("\n"):
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
    step("3", "Looking for printers")
    all_printers = []
    info("USB printers...")
    for p in find_printers_usb():
        ok("USB: " + p["name"])
        all_printers.append({"source": "USB", "name": p["name"], "ip": None})
    info("Network printers (may take ~30s)...")
    for p in find_printers_network():
        name = p.get("name", "Unknown")
        ip = p.get("ip", "?")
        ok("Network: " + str(name) + " (" + str(ip) + ")")
        all_printers.append({"source": "Network", "name": name, "ip": ip})
    return all_printers

def get_available_actions(printer):
    actions = []
    parm = printer.parm
    if not parm:
        return actions
    actions.append(("Full printer status", "stats"))
    if "main_waste" in parm:
        actions.append(("Show waste ink level", "show_waste"))
    if "raw_waste_reset" in parm or "main_waste" in parm:
        actions.append(("PERMANENT waste-ink reset", "reset_waste"))
    actions.append(("Temporary waste-ink reset", "temp_reset"))
    if "serial_number" in parm:
        actions.append(("Show serial number", "serial"))
    if "stats" in parm:
        actions.append(("Printer statistics", "show_stats"))
    actions.append(("Nozzle check print", "nozzle_check"))
    actions.append(("Head cleaning", "clean"))
    actions.append(("Power cleaning", "power_clean"))
    actions.append(("Open web interface", "web"))
    return actions

def execute_action(printer, action_id, model_name):
    hline()
    try:
        if action_id == "stats":
            import pprint
            data = run_with_spinner("Requesting data...", printer.stats)
            if data:
                print()
                pprint.pprint(data, width=100, compact=True)
            else:
                warn("No data. Check the connection.")
        elif action_id == "show_waste":
            levels = run_with_spinner("Requesting...", printer.get_waste_ink_levels)
            if levels:
                print()
                for key, val in levels.items():
                    print("    " + key.replace("_", " ").title() + ": " + str(val) + "%")
                print()
            else:
                warn("Could not read waste ink level.")
        elif action_id == "reset_waste":
            warn("PERMANENT waste-ink counter reset!")
            warn("Also rinse or replace the physical absorber.")
            confirm = input("  Are you sure? (yes/no): ").strip().lower()
            if confirm in ("yes", "y", "da", "d"):
                result = run_with_spinner("Writing EEPROM...", printer.reset_waste_ink_levels)
                if result:
                    ok("Waste-ink counter reset. Reboot the printer.")
                else:
                    err("Reset failed. Check connection and configuration.")
            else:
                info("Cancelled.")
        elif action_id == "temp_reset":
            result = run_with_spinner("Sending command...", printer.temporary_reset_waste)
            if result:
                ok("Temporary reset done (until reboot).")
            else:
                err("Temporary reset failed.")
        elif action_id == "serial":
            sn = run_with_spinner("Requesting...", printer.get_serial_number)
            if sn:
                ok("Serial number: " + str(sn))
            else:
                warn("Could not read serial number.")
        elif action_id == "show_stats":
            data = run_with_spinner("Requesting...", lambda: printer.get_stats())
            if data:
                print()
                for key, val in data.items():
                    print("    " + str(key) + ": " + str(val))
                print()
            else:
                warn("Statistics unavailable.")
        elif action_id == "nozzle_check":
            result = printer.print_check_nozzles(type=0)
            if result:
                ok("Nozzle check sent to printer.")
            else:
                err("Failed to send nozzle check.")
        elif action_id == "clean":
            confirm = input("  Start cleaning? (yes/no): ").strip().lower()
            if confirm in ("yes", "y", "da", "d"):
                try:
                    result = printer.clean_nozzles(0)
                    if result:
                        ok("Cleaning started.")
                    else:
                        err("Cleaning failed.")
                except Exception as e:
                    err(str(e))
            else:
                info("Cancelled.")
        elif action_id == "power_clean":
            warn("Power cleaning uses more ink.")
            confirm = input("  Continue? (yes/no): ").strip().lower()
            if confirm in ("yes", "y", "da", "d"):
                try:
                    result = printer.clean_nozzles(1)
                    if result:
                        ok("Power cleaning started.")
                    else:
                        err("Power cleaning failed.")
                except Exception as e:
                    err(str(e))
            else:
                info("Cancelled.")
        elif action_id == "web":
            try:
                host = is_valid_printer_host(printer.hostname) if printer.hostname else None
                if host:
                    webbrowser.open("http://" + host)
                    ok("Opening http://" + host)
                else:
                    err("Printer address is not set.")
            except Exception:
                err("Could not open the browser.")
    except TimeoutError:
        err("Timeout talking to the printer.")
    except Exception as e:
        err(str(e))
    print()
    input("  Press Enter to continue...")

def _ask_printer_host(prompt):
    host = is_valid_printer_host(input(prompt).strip())
    if not host:
        err("Invalid IP address or hostname.")
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
            ok("Loaded models: " + str(len(conf_dict)))
        except Exception as e:
            warn("Pickle load error: " + str(e))
    step("3", "Connect to printer")
    print()
    connect_opts = [
        ("Auto-discover printers on network and USB", "auto"),
        ("Enter IP address manually", "manual"),
    ]
    choice = menu_choice(connect_opts, "How to connect?")
    if choice is None:
        print("\n  Goodbye.\n")
        sys.exit(0)
    target_ip = None
    model_name = None
    if connect_opts[choice][1] == "auto":
        found = discover_printers()
        if not found:
            warn("No printers found automatically.")
            target_ip = _ask_printer_host("  Printer IP: ")
        elif len(found) == 1 and found[0]["ip"]:
            target_ip = found[0]["ip"]
            model_name = found[0].get("name")
            ok("Using: " + str(model_name) + " (" + str(target_ip) + ")")
        else:
            net_printers = [p for p in found if p["ip"]]
            if not net_printers:
                warn("Only USB printers found. This tool talks over the network.")
                target_ip = _ask_printer_host("  Printer IP: ")
            else:
                opts = [(str(p["name"]) + " (" + str(p["ip"]) + ")", p) for p in net_printers]
                idx = menu_choice(opts, "Select a printer")
                if idx is None:
                    sys.exit(0)
                target_ip = net_printers[idx]["ip"]
                model_name = net_printers[idx].get("name")
    else:
        target_ip = _ask_printer_host("\n  Printer IP: ")
    if not target_ip:
        err("IP address not provided.")
        sys.exit(1)
    target_ip = is_valid_printer_host(target_ip)
    if not target_ip:
        err("Invalid IP address or hostname.")
        sys.exit(1)
    step("4", "Detect printer model")
    info("Connecting to " + target_ip + "...")
    temp_printer = EpsonPrinter(conf_dict=conf_dict, hostname=target_ip)
    try:
        snmp_info = run_with_spinner("Requesting model...", lambda: temp_printer.get_snmp_info("Model"))
        if snmp_info and "Model" in snmp_info:
            detected = snmp_info["Model"]
            ok("Detected model: " + str(detected))
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
        warn("Could not auto-detect model: " + str(e))
    if not model_name:
        warn("Model not auto-detected.")
        valid = sorted(temp_printer.valid_printers)
        cols = 4
        for i in range(0, len(valid), cols):
            print("    " + "  ".join("{:<20s}".format(m) for m in valid[i:i + cols]))
        model_name = input("  Printer model: ").strip()
    if not model_name:
        err("Model not provided.")
        sys.exit(1)
    step("5", "Connecting to " + model_name)
    printer = EpsonPrinter(conf_dict=conf_dict, model=model_name, hostname=target_ip)
    if not printer.parm:
        err("Model '" + model_name + "' not found in configuration.")
        sys.exit(1)
    ok("Printer: " + model_name)
    ok("Address: " + target_ip)
    try:
        sn = run_with_spinner("Checking link...", printer.get_serial_number)
        if sn:
            ok("Serial number: " + str(sn))
            ok("Connection established.")
        else:
            warn("Serial number not returned; continuing anyway.")
    except Exception:
        warn("Link check failed; continuing anyway.")
    while True:
        banner()
        print("  Printer: " + model_name + "  |  IP: " + target_ip)
        hline()
        actions = get_available_actions(printer)
        if not actions:
            err("No operations available for this model.")
            break
        idx = menu_choice(actions, "Available operations")
        if idx is None:
            print("\n  Goodbye.\n")
            break
        execute_action(printer, actions[idx][1], model_name)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye.\n")
        sys.exit(0)
