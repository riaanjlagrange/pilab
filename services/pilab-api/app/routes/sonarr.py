from flask import Blueprint, jsonify, request
from ..services.sonarr import (
    get_downloaded_series,
    get_trending_series,
    search_series,
    get_profiles,
    request_series,
    delete_series,
)

bp = Blueprint("sonarr", __name__)


@bp.route("/api/sonarr/media")
def api_sonarr_media():
    """Downloaded series and recently-added (trending) feed."""
    return jsonify({
        "downloaded": get_downloaded_series(),
        "trending":   get_trending_series(),
    })


@bp.route("/api/sonarr/search")
def api_sonarr_search():
    """Search Sonarr series lookup."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    return jsonify(search_series(q))


@bp.route("/api/sonarr/profiles")
def api_sonarr_profiles():
    """Quality profiles and root folders."""
    return jsonify(get_profiles())


@bp.route("/api/sonarr/request", methods=["POST"])
def api_sonarr_request():
    """Add a series to Sonarr."""
    data               = request.get_json(silent=True) or {}
    tvdb_id            = data.get("tvdb_id")
    quality_profile_id = data.get("quality_profile_id")
    root_folder        = data.get("root_folder")

    if not all([tvdb_id, quality_profile_id, root_folder]):
        return jsonify({"ok": False, "error": "missing_fields"}), 400

    result = request_series(tvdb_id, quality_profile_id, root_folder)
    return jsonify(result), (200 if result["ok"] else 400)


@bp.route("/api/sonarr/delete", methods=["POST"])
def api_sonarr_delete():
    """Delete a series from Sonarr and remove files from disk."""
    data      = request.get_json(silent=True) or {}
    series_id = data.get("id")

    if not series_id:
        return jsonify({"ok": False, "error": "missing id"}), 400

    try:
        delete_series(series_id)
        print(f"[Sonarr] Series {series_id} deleted", flush=True)
        return jsonify({"ok": True})
    except Exception as e:
        print(f"[Sonarr] delete error: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e)}), 500