import threading
import time


def start_monitor(app):
    """Start the background disk monitor as a daemon thread.

    Passes the app instance so the thread can push an app context,
    which is required for DB access and current_app inside the loop.
    """
    thread = threading.Thread(target=_monitor_loop, args=(app,), daemon=True)
    thread.start()


def _monitor_loop(app):
    with app.app_context():
        from .services.settings import get_settings
        from .services.system import get_disk
        from .services.ntfy import send_ntfy
        from flask import current_app

        host = current_app.config["HOST"]

        settings = get_settings()
        check_interval = settings.get("checkIntervalMinutes", 60)
        threshold = settings.get("diskThreshold", 85)

        print(
            f"[Monitor] Starting — {check_interval}min interval, "
            f"{threshold}% threshold",
            flush=True,
        )

        # Brief startup delay so the rest of the app is ready
        time.sleep(5)

        alert_sent = False

        while True:
            try:
                settings = get_settings()
                threshold = settings.get("diskThreshold", 85)
                check_interval = settings.get("checkIntervalMinutes", 60)

                disk = get_disk()
                used_pct = disk["percent_used"]
                print(f"[Monitor] Disk usage: {used_pct}%", flush=True)

                if used_pct >= threshold and not alert_sent:
                    storage_link = f"http://{host}:5173/manager?tab=queue"
                    send_ntfy(
                        title=f"Disk Usage Alert - {used_pct}%",
                        message=(
                            f"Disk usage is at {used_pct}% "
                            f"(threshold: {threshold}%)\n"
                            f"Used: {disk['used_gb']} GB / "
                            f"{disk['total_gb']} GB\n"
                            f"Free: {disk['free_gb']} GB\n\n"
                            f"Manage storage: {storage_link}"
                        ),
                        priority="high",
                        click_url=storage_link,
                        tags="warning,floppy_disk",
                    )
                    alert_sent = True

                elif used_pct < threshold and alert_sent:
                    alert_sent = False
                    print(
                        "[Monitor] Usage below threshold — alert flag reset",
                        flush=True,
                    )

            except Exception as e:
                print(f"[Monitor] Error: {e}", flush=True)

            time.sleep(check_interval * 60)