import time

from flask import Blueprint, current_app, jsonify, request

from ..services.ntfy import send_ntfy

bp = Blueprint("webhooks", __name__)


@bp.route("/api/webhooks/radarr", methods=["GET", "POST"])
def webhook_radarr():
    """Radarr calls this when a movie is imported."""
    if request.method == "GET":
        return jsonify({"ok": True})

    data  = request.get_json(silent=True) or {}
    event = data.get("eventType")

    if event != "Download":
        return jsonify({"ok": True})

    movie  = data.get("movie", {})
    title  = movie.get("title", "Unknown")
    year   = movie.get("year")
    host   = current_app.config["HOST"]
    plex_url = f"http://{host}:32400/web"

    # Give Plex a moment to scan the imported file before notifying
    time.sleep(10)

    msg = f"{title} ({year}) has finished downloading and is ready to watch."
    msg += f"\n\n▶ Watch on Plex: {plex_url}"

    print(f"[Webhook] Radarr import: {title} ({year})", flush=True)
    send_ntfy(
        title=f"🎬 {title} is ready",
        message=msg,
        priority="default",
        click_url=plex_url,
        tags="white_check_mark,clapper",
    )
    return jsonify({"ok": True})


@bp.route("/api/webhooks/sonarr", methods=["GET", "POST"])
def webhook_sonarr():
    """Sonarr calls this when an episode is imported."""
    if request.method == "GET":
        return jsonify({"ok": True})

    data  = request.get_json(silent=True) or {}
    event = data.get("eventType")

    if event != "Download":
        return jsonify({"ok": True})

    series   = data.get("series", {})
    episode  = data.get("episodes", [{}])[0]
    title    = series.get("title", "Unknown")
    year     = series.get("year")
    ep_title = episode.get("title", "")
    ep_str   = (
        f"S{episode.get('seasonNumber', 0):02d}"
        f"E{episode.get('episodeNumber', 0):02d}"
    )
    host     = current_app.config["HOST"]
    plex_url = f"http://{host}:32400/web"

    # Give Plex a moment to scan the imported file before notifying
    time.sleep(10)

    msg = f"{title} · {ep_str} — {ep_title} is ready to watch."
    msg += f"\n\n▶ Watch on Plex: {plex_url}"

    print(f"[Webhook] Sonarr import: {title} {ep_str} - {ep_title}", flush=True)
    send_ntfy(
        title=f"📺 {ep_str} {title} is ready",
        message=msg,
        priority="default",
        click_url=plex_url,
        tags="white_check_mark,tv",
    )
    return jsonify({"ok": True})