import platform
import shutil
import socket
import time

import psutil


def get_uptime_seconds() -> float:
    return time.time() - psutil.boot_time()


def format_uptime(seconds: float) -> str:
    seconds = int(seconds)
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {secs}s"


def get_system_info() -> dict:
    vm = psutil.virtual_memory()
    du = shutil.disk_usage("/")

    info = {
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "hostname": socket.gethostname(),
        "cpu_physical_cores": psutil.cpu_count(logical=False),
        "cpu_logical_cores": psutil.cpu_count(logical=True),
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "memory_total_gb": round(vm.total / (1024 ** 3), 2),
        "memory_used_gb": round(vm.used / (1024 ** 3), 2),
        "memory_free_gb": round(vm.available / (1024 ** 3), 2),
        "memory_percent": vm.percent,
        "disk_total_gb": round(du.total / (1024 ** 3), 2),
        "disk_used_gb": round(du.used / (1024 ** 3), 2),
        "disk_free_gb": round(du.free / (1024 ** 3), 2),
        "uptime": format_uptime(get_uptime_seconds()),
    }

    try:
        load1, load5, load15 = psutil.getloadavg()
        info["load_average"] = {
            "1min": round(load1, 2),
            "5min": round(load5, 2),
            "15min": round(load15, 2),
        }
    except (AttributeError, OSError):
        info["load_average"] = "Not available"

    return info