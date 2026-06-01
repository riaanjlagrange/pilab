from flask import Blueprint, jsonify, request
from ..services.webhooks import handle_radarr, handle_sonarr

bp = Blueprint("webhooks", __name__)

@bp.route("/api/webhooks/radarr", methods=["GET", "POST"])
def webhook_radarr():
    if request.method == "GET":
        return jsonify({"ok": True})
    handle_radarr(request.get_json(silent=True) or {})
    return jsonify({"ok": True})

@bp.route("/api/webhooks/sonarr", methods=["GET", "POST"])
def webhook_sonarr():
    if request.method == "GET":
        return jsonify({"ok": True})
    handle_sonarr(request.get_json(silent=True) or {})
    return jsonify({"ok": True})