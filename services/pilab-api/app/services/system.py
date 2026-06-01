import time

import psutil
import requests
from flask import current_app

from .utils import format_uptime


def get_system():
    """Fetch hostname, CPU%, RAM%, and uptime.

    Tries Glances first; falls back to psutil if Glances is unavailable.
    """
    pilab_name  = current_app.config["PILAB_NAME"]
    glances_url = current_app.config["GLANCES_URL"]

    result = {
        "pilab_name":     pilab_name,
        "cpu_percent":    0,
        "ram_percent":    0,
        "ram_used_gb":    0,
        "ram_total_gb":   0,
        "uptime_seconds": 0,
        "uptime_human":   "unknown",
    }

    try:
        cpu_resp = requests.get(f"{glances_url}/api/4/cpu", timeout=3)
        result["cpu_percent"] = round(cpu_resp.json().get("total", 0), 1)

        mem_resp = requests.get(f"{glances_url}/api/4/mem", timeout=3)
        mem = mem_resp.json()
        result["ram_percent"]  = round(mem.get("percent", 0), 1)
        result["ram_used_gb"]  = round(mem.get("used",    0) / 1e9, 2)
        result["ram_total_gb"] = round(mem.get("total",   0) / 1e9, 2)

        with open("/proc/uptime") as f:
            uptime_seconds = int(float(f.read().split()[0]))
        result["uptime_seconds"] = uptime_seconds
        result["uptime_human"]   = format_uptime(uptime_seconds)

    except Exception as e:
        print(f"[System] Glances unavailable, falling back to psutil: {e}", flush=True)
        try:
            cpu    = psutil.cpu_percent(interval=0.5)
            ram    = psutil.virtual_memory()
            uptime = int(time.time() - psutil.boot_time())
            result["cpu_percent"]    = round(cpu, 1)
            result["ram_percent"]    = round(ram.percent, 1)
            result["ram_used_gb"]    = round(ram.used  / 1e9, 2)
            result["ram_total_gb"]   = round(ram.total / 1e9, 2)
            result["uptime_seconds"] = uptime
            result["uptime_human"]   = format_uptime(uptime)
        except Exception as e2:
            print(f"[System] psutil also failed: {e2}", flush=True)

    return result


def get_disk():
    """Fetch disk usage for the configured media partition."""
    import shutil
    media_path         = current_app.config["MEDIA_PATH"]
    alert_threshold_gb = current_app.config["ALERT_THRESHOLD_GB"]

    usage = shutil.disk_usage(media_path)
    return {
        "total_gb":     round(usage.total / 1e9, 2),
        "used_gb":      round(usage.used   / 1e9, 2),
        "free_gb":      round(usage.free   / 1e9, 2),
        "percent_used": round((usage.used / usage.total) * 100, 1),
        "threshold_gb": alert_threshold_gb,
    }