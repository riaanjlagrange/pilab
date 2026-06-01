from flask import Blueprint, jsonify

from ..services.plex import get_plex

bp = Blueprint("plex", __name__)


@bp.route("/api/plex")
def api_plex():
    """Plex active sessions and on-deck items."""
    return jsonify(get_plex())