import threading
import time
from flask import current_app
from .ntfy import send_ntfy
from .plex import search_plex_item


def _notify_radarr(app, data: dict):
    with app.app_context():
        movie  = data.get("movie", {})
        title  = movie.get("title", "Unknown")
        year   = movie.get("year")

        time.sleep(20)

        plex_link = search_plex_item(title, year, "movie")
        host      = current_app.config["HOST"]
        fallback  = f"http://{host}:32400/web"
        click_url = plex_link or fallback

        msg = f"{title} ({year}) has finished downloading and is ready to watch."
        if plex_link:
            msg += f"\n\n▶ Watch on Plex: {plex_link}"

        print(f"[Webhook] Radarr import: {title} ({year})", flush=True)
        send_ntfy(
            title=f"🎬 {title} is ready",
            message=msg,
            priority="default",
            click_url=click_url,
            tags="white_check_mark,clapper",
        )


def _notify_sonarr(app, data: dict):
    with app.app_context():
        series   = data.get("series", {})
        episode  = data.get("episodes", [{}])[0]
        title    = series.get("title", "Unknown")
        year     = series.get("year")
        ep_title = episode.get("title", "")
        ep_str   = (
            f"S{episode.get('seasonNumber', 0):02d}"
            f"E{episode.get('episodeNumber', 0):02d}"
        )

        time.sleep(10)

        plex_link = search_plex_item(title, year, "show")
        host      = current_app.config["HOST"]
        fallback  = f"http://{host}:32400/web"
        click_url = plex_link or fallback

        msg = f"{title} · {ep_str} — {ep_title} is ready to watch."
        if plex_link:
            msg += f"\n\n▶ Watch on Plex: {plex_link}"

        print(f"[Webhook] Sonarr import: {title} {ep_str} - {ep_title}", flush=True)
        send_ntfy(
            title=f"📺 {ep_str} {title} is ready",
            message=msg,
            priority="default",
            click_url=click_url,
            tags="white_check_mark,tv",
        )


def handle_radarr(data: dict):
    if data.get("eventType") != "Download":
        return
    app = current_app._get_current_object()
    threading.Thread(target=_notify_radarr, args=(app, data), daemon=True).start()


def handle_sonarr(data: dict):
    if data.get("eventType") != "Download":
        return
    app = current_app._get_current_object()
    threading.Thread(target=_notify_sonarr, args=(app, data), daemon=True).start()