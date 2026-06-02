import os

from flask import Flask
from flask_cors import CORS

from .config import config_map, ProductionConfig
from .database import init_db
from .errors import register_error_handlers


def create_app(config=None):
    """Application factory.

    Args:
        config: A config class to use. If None, reads FLASK_ENV from the
                environment and picks from config_map (defaults to production).
    """
    app = Flask(__name__)

    if config is None:
        env = os.getenv("FLASK_ENV", "production")
        config = config_map.get(env, ProductionConfig)

    app.config.from_object(config)
    CORS(app, resources={r"/*": {"origins": "*"}})  # Allow CORS for API routes

    # ── Database ───────────────────────────────────────────────────────────
    init_db(app)

    # ── Docker client ──────────────────────────────────────────────────────
    _init_docker(app)

    # ── Blueprints (imported here to avoid circular imports) ───────────────
    from .routes.system     import bp as system_bp
    from .routes.containers import bp as containers_bp
    from .routes.media      import bp as media_bp
    from .routes.downloads  import bp as downloads_bp
    from .routes.plex       import bp as plex_bp
    from .routes.settings   import bp as settings_bp
    from .routes.webhooks   import bp as webhooks_bp
    from .routes.search     import bp as search_bp
    from .routes.request    import bp as request_bp


    app.register_blueprint(system_bp)
    app.register_blueprint(containers_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(downloads_bp)
    app.register_blueprint(plex_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(request_bp)

    # ── Error handlers ─────────────────────────────────────────────────────
    register_error_handlers(app)

    # ── Background monitor ─────────────────────────────────────────────────
    from .monitor import start_monitor
    start_monitor(app)

    return app


def _init_docker(app):
    """Connect to the Docker socket and store client on app.extensions."""
    try:
        import docker
        client = docker.from_env()
        client.ping()
        app.extensions["docker_client"] = client
        print("[Docker] Connected to Docker socket", flush=True)
    except Exception as e:
        print(f"[Docker] Could not connect to Docker socket: {e}", flush=True)
        app.extensions["docker_client"] = None