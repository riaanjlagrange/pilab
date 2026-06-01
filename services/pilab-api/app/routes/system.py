from flask import Blueprint, jsonify

from ..services.system import get_disk, get_system

bp = Blueprint("system", __name__)


@bp.route("/api/system")
def api_system():
    """System metrics: hostname, CPU, RAM, uptime."""
    return jsonify(get_system())


@bp.route("/api/disk")
def api_disk():
    """Disk usage for the media partition."""
    return jsonify(get_disk())