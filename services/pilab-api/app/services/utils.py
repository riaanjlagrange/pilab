from datetime import datetime, timezone


def format_uptime(seconds):
    """Format seconds into a human-readable uptime string."""
    if seconds is None:
        return None
    days    = int(seconds // 86400)
    hours   = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    return "just started"


def parse_docker_timestamp(ts_str):
    """Parse Docker's ISO timestamp (nanosecond precision) to a datetime."""
    try:
        if "." in ts_str:
            base, frac = ts_str.split(".")
            frac = frac.rstrip("Z")[:6].ljust(6, "0")
            return datetime.fromisoformat(f"{base}.{frac}+00:00")
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return None


def format_eta(eta_sec):
    """Convert an ETA in seconds to a human-readable string."""
    if not eta_sec or eta_sec <= 0 or eta_sec >= 8_640_000:
        return "unknown"
    hours   = eta_sec // 3600
    minutes = (eta_sec % 3600) // 60
    return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"