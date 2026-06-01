from flask import Blueprint, jsonify, request

from ..services.settings import get_settings, save_settings

bp = Blueprint("settings", __name__)


@bp.route("/api/settings", methods=["GET"])
def api_settings_get():
    """Return current settings."""
    return jsonify(get_settings())


@bp.route("/api/settings", methods=["POST"])
def api_settings_set():
    """Update settings (merges with existing, does not replace)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if save_settings(data):
        print("[Settings] Updated", flush=True)
        return jsonify({"success": True})

    return jsonify({"error": "Failed to save settings"}), 500