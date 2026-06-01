from datetime import datetime, timezone

from flask import current_app

from .utils import format_uptime, parse_docker_timestamp


def get_containers(apply_hidden_filter=True):
    """Fetch all Docker containers (running and stopped).

    Args:
        apply_hidden_filter: If True, exclude containers listed in
                             settings.hiddenContainers.
    """
    docker_client = current_app.extensions.get("docker_client")
    if not docker_client:
        return []

    try:
        hidden = set()
        if apply_hidden_filter:
            from .settings import get_settings
            hidden = set(get_settings().get("hiddenContainers", []))

        result = []
        for c in docker_client.containers.list(all=True):
            if c.name in hidden:
                continue

            uptime_seconds = None
            if c.status == "running":
                started = parse_docker_timestamp(c.attrs["State"]["StartedAt"])
                if started:
                    uptime_seconds = int(
                        (datetime.now(timezone.utc) - started).total_seconds()
                    )

            result.append({
                "name":           c.name,
                "status":         c.status,
                "uptime_seconds": uptime_seconds,
                "uptime_human":   format_uptime(uptime_seconds),
            })

        result.sort(key=lambda x: (x["status"] != "running", x["name"].lower()))
        return result

    except Exception as e:
        print(f"[Docker] Failed to list containers: {e}", flush=True)
        return []