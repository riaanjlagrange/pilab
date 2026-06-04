from flask import Blueprint, jsonify, request
from ..services.radarr import (
    get_downloaded_movies,
    get_trending_movies,
    search_movies,
    get_profiles,
    request_movie,
    delete_movie,
)

bp = Blueprint("radarr", __name__)


@bp.route("/api/radarr/media")
def api_radarr_media():
    """Downloaded movies and trending/discover feed."""
    return jsonify({
        "downloaded": get_downloaded_movies(),
        "trending":   get_trending_movies(),
    })


@bp.route("/api/radarr/search")
def api_radarr_search():
    """Search Radarr movie lookup."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    return jsonify(search_movies(q))


@bp.route("/api/radarr/profiles")
def api_radarr_profiles():
    """Quality profiles and root folders."""
    return jsonify(get_profiles())


@bp.route("/api/radarr/request", methods=["POST"])
def api_radarr_request():
    """Add a movie to Radarr."""
    data               = request.get_json(silent=True) or {}
    tmdb_id            = data.get("tmdb_id")
    quality_profile_id = data.get("quality_profile_id")
    root_folder        = data.get("root_folder")

    if not all([tmdb_id, quality_profile_id, root_folder]):
        return jsonify({"ok": False, "error": "missing_fields"}), 400

    result = request_movie(tmdb_id, quality_profile_id, root_folder)
    return jsonify(result), (200 if result["ok"] else 400)


@bp.route("/api/radarr/delete", methods=["POST"])
def api_radarr_delete():
    """Delete a movie from Radarr and remove files from disk."""
    data     = request.get_json(silent=True) or {}
    movie_id = data.get("id")

    if not movie_id:
        return jsonify({"ok": False, "error": "missing id"}), 400

    try:
        delete_movie(movie_id)
        print(f"[Radarr] Movie {movie_id} deleted", flush=True)
        return jsonify({"ok": True})
    except Exception as e:
        print(f"[Radarr] delete error: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e)}), 500