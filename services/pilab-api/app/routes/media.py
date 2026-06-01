from flask import Blueprint, jsonify, request

from ..services.media import get_movies, get_series, radarr_delete, sonarr_delete
from ..services.system import get_disk
from flask import current_app

bp = Blueprint("media", __name__)


@bp.route("/api/media")
def api_media():
    """All downloaded movies and series from Radarr/Sonarr."""
    return jsonify({"movies": get_movies(), "series": get_series()})


@bp.route("/api/status")
def api_status():
    """Combined disk + media snapshot for the storage manager page."""
    return jsonify({
        "disk":         get_disk(),
        "movies":       get_movies(),
        "series":       get_series(),
        "threshold_gb": current_app.config["ALERT_THRESHOLD_GB"],
    })


@bp.route("/api/delete", methods=["POST"])
def api_delete():
    """Delete a movie or series by id and type."""
    data      = request.get_json()
    item_id   = data.get("id")
    item_type = data.get("type")

    if not item_id or item_type not in ("movie", "series"):
        return jsonify({"error": "Invalid request"}), 400

    try:
        if item_type == "movie":
            radarr_delete(item_id)
            print(f"[Delete] Movie {item_id} deleted via Radarr", flush=True)
        else:
            sonarr_delete(item_id)
            print(f"[Delete] Series {item_id} deleted via Sonarr", flush=True)
        return jsonify({"success": True})
    except Exception as e:
        print(f"[Delete] Error: {e}", flush=True)
        return jsonify({"error": str(e)}), 500