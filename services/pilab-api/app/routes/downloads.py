from flask import Blueprint, jsonify

from ..services.downloads import get_downloads, get_queue

bp = Blueprint("downloads", __name__)


@bp.route("/api/downloads")
def api_downloads():
    """Active downloads from qBittorrent."""
    return jsonify(get_downloads())


@bp.route("/api/queue")
def api_queue():
    """Full torrent queue categorised as movies and series."""
    return jsonify(get_queue())