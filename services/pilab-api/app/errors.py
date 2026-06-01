from flask import jsonify


def register_error_handlers(app):
    """Register JSON error handlers for all common HTTP errors.

    Called from create_app() so every blueprint benefits automatically.
    All errors return consistent { "error": "..." } JSON — never HTML.
    """

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "detail": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        print(f"[Error] Unhandled exception: {e}", flush=True)
        return jsonify({"error": "Internal server error"}), 500