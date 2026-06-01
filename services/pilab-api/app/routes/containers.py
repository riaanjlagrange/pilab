from flask import Blueprint, jsonify, request

from ..services.containers import get_containers

bp = Blueprint("containers", __name__)


@bp.route("/api/containers")
def api_containers():
    """All Docker containers with status and uptime.

    Query params:
      all=true  → return all containers, ignoring the hidden filter
      all=false → apply hidden filter from settings (default)
    """
    show_all = request.args.get("all", "false").lower() == "true"
    return jsonify(get_containers(apply_hidden_filter=not show_all))