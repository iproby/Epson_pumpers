import socket
import threading
import warnings
from concurrent.futures import ThreadPoolExecutor

from epson_print_conf import EpsonPrinter

# suppress pysnmp warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# common printer ports
PRINTER_PORTS = [9100, 515, 631]
SCAN_WORKERS = 64


class PrinterScanner:

    def check_printer(self, ip, port):
        try:
            with socket.create_connection((ip, port), timeout=1):
                return True
        except OSError:
            return False

    def get_printer_name(self, ip):
        printer = EpsonPrinter(hostname=ip)
        try:
            printer_info = printer.get_snmp_info("Model")
            return printer_info.get("Model")
        except Exception:
            return None

    def scan_ip(self, ip):
        for port in PRINTER_PORTS:
            if self.check_printer(ip, port):
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except socket.herror:
                    hostname = "Unknown"

                return {
                    "ip": ip,
                    "hostname": hostname,
                }
        return None

    def get_all_printers(self, ip_addr="", local=False):
        if ip_addr:
            result = self.scan_ip(ip_addr)
            if result:
                result["name"] = self.get_printer_name(result["ip"])
                return [result]
            # A full IPv4 was probed and is not a printer — do not fall through
            # to a /24 scan of a local interface.
            if ip_addr.count(".") == 3 and all(
                part.isdigit() and 0 <= int(part) <= 255
                for part in ip_addr.split(".")
            ):
                return []

        try:
            local_device_ip_list = socket.gethostbyname_ex(socket.gethostname())[2]
        except socket.gaierror:
            local_device_ip_list = []

        if local:
            return local_device_ip_list  # IP list

        printers = []
        lock = threading.Lock()

        def worker(ip):
            result = self.scan_ip(ip)
            if result:
                with lock:
                    printers.append(result)

        for local_device_ip in local_device_ip_list:
            if ip_addr and not local_device_ip.startswith(ip_addr):
                continue
            base_ip = local_device_ip[: local_device_ip.rfind(".") + 1]
            ips = [f"{base_ip}{i}" for i in range(1, 255)]
            with ThreadPoolExecutor(max_workers=SCAN_WORKERS) as executor:
                list(executor.map(worker, ips))

        for item in printers:
            item["name"] = self.get_printer_name(item["ip"])
        return printers


if __name__ == "__main__":
    import sys

    ip = ""
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    scanner = PrinterScanner()
    print(scanner.get_all_printers(ip))
