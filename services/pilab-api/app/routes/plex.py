from flask import Blueprint, jsonify, request
from ..services.plex import get_plex_library, get_plex_active, search_plex

bp = Blueprint("plex", __name__)


@bp.route("/api/plex/media")
def api_plex_media():
    """All Plex library content split by type, plus continueWatching."""
    return jsonify(get_plex_library())


@bp.route("/api/plex/active")
def api_plex_active():
    """Currently active Plex sessions."""
    return jsonify(get_plex_active())


@bp.route("/api/plex/search")
def api_plex_search():
    """Search the Plex library."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    return jsonify(search_plex(q))