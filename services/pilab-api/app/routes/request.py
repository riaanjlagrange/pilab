from flask import Blueprint, jsonify, request
from ..services.request import request_movie, request_show

bp = Blueprint("request", __name__)


@bp.route("/api/request/movie", methods=["POST"])
def add_movie():
    data               = request.get_json(silent=True) or {}
    tmdb_id            = data.get("tmdb_id")
    quality_profile_id = data.get("quality_profile_id")
    root_folder        = data.get("root_folder")

    if not all([tmdb_id, quality_profile_id, root_folder]):
        return jsonify({"ok": False, "error": "missing_fields"}), 400

    result = request_movie(tmdb_id, quality_profile_id, root_folder)
    return jsonify(result), (200 if result["ok"] else 400)


@bp.route("/api/request/show", methods=["POST"])
def add_show():
    data               = request.get_json(silent=True) or {}
    tvdb_id            = data.get("tvdb_id")
    quality_profile_id = data.get("quality_profile_id")
    root_folder        = data.get("root_folder")

    if not all([tvdb_id, quality_profile_id, root_folder]):
        return jsonify({"ok": False, "error": "missing_fields"}), 400

    result = request_show(tvdb_id, quality_profile_id, root_folder)
    return jsonify(result), (200 if result["ok"] else 400)