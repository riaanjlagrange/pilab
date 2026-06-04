import threading
import time
from flask import current_app
from .ntfy import send_ntfy
from .plex import search_plex 


def _find_plex_link(title: str, year: int | None, media_type: str) -> str | None:
    """
    Search Plex and return the plex_link for the first result that matches
    title + type. Returns None if not found.
    """
    try:
        results = search_plex(title)
        for r in results:
            if r.get("type") != media_type:
                continue
            if r.get("title", "").lower() != title.lower():
                continue
            if year and r.get("year") and r["year"] != year:
                continue
            return r.get("plex_link") or None
    except Exception as e:
        print(f"[Webhook] Plex search error: {e}", flush=True)
    return None


def _notify_radarr(app, data: dict):
    with app.app_context():
        movie  = data.get("movie", {})
        title  = movie.get("title", "Unknown")
        year   = movie.get("year")
        time.sleep(20)
        plex_link = _find_plex_link(title, year, "movie")
        host      = current_app.config["HOST"]
        click_url = plex_link or f"http://{host}:32400/web"
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
        plex_link = _find_plex_link(title, year, "show")
        host      = current_app.config["HOST"]
        click_url = plex_link or f"http://{host}:32400/web"
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