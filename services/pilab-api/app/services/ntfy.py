import requests
from flask import current_app

from .settings import get_settings


def send_ntfy(title, message, priority="high", click_url=None, tags="white_check_mark"):
    """Send a push notification via ntfy.

    Topic is read from the live settings so it can be changed at runtime
    without restarting the container.
    """
    cfg        = current_app.config
    settings   = get_settings()
    ntfy_topic = settings.get("ntfyTopic", cfg["NTFY_TOPIC"])

    if not ntfy_topic:
        print("[ntfy] ntfyTopic not set — skipping", flush=True)
        return

    # ntfy headers must be ASCII-safe
    safe_title = title.encode("ascii", "ignore").decode("ascii").strip()

    headers = {
        "Title":    safe_title,
        "Priority": priority,
        "Tags":     tags,
        "Click":    click_url or f"http://{cfg['HOST']}:5173",
    }

    try:
        resp = requests.post(
            f"{cfg['NTFY_SERVER']}/{ntfy_topic}",
            data=message.encode("utf-8"),
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        print(f"[ntfy] Sent: {safe_title}", flush=True)
    except Exception as e:
        print(f"[ntfy] Failed: {e}", flush=True)