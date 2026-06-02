from flask import Blueprint, jsonify, request
from ..services.search import (
    search_radarr,
    search_sonarr,
    get_radarr_profiles,
    get_sonarr_profiles,
)
from ..services.plex import search_plex_item

bp = Blueprint("search", __name__)


@bp.route("/api/search")
def search_plex():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    results = search_plex_item(q, year=None, item_type=None)
    return jsonify(results)


@bp.route("/api/search/radarr")
def search_radarr_route():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    return jsonify(search_radarr(q))


@bp.route("/api/search/sonarr")
def search_sonarr_route():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    return jsonify(search_sonarr(q))


@bp.route("/api/search/profiles/radarr")
def radarr_profiles():
    return jsonify(get_radarr_profiles())


@bp.route("/api/search/profiles/sonarr")
def sonarr_profiles():
    return jsonify(get_sonarr_profiles())