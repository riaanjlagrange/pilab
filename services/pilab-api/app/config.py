import os


class Config:
    # ── Secrets (hard fail if missing in production) ───────────────────────
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://pilab:pilab@pilab-db:5432/pilab"
    )

    # ── Service URLs (safe defaults — Docker network container names) ──────
    RADARR_URL       = os.getenv("RADARR_URL",       "http://radarr:7878")
    SONARR_URL       = os.getenv("SONARR_URL",       "http://sonarr:8989")
    PLEX_URL         = os.getenv("PLEX_URL",         "http://host.docker.internal:32400")
    PLEX_PORT        = int(os.getenv("PLEX_PORT",    "32400"))
    GLANCES_URL      = os.getenv("GLANCES_URL",      "http://glances:61208")
    QBITTORRENT_URL  = os.getenv("QBITTORRENT_URL",  "http://qbittorrent:8080")
    NTFY_SERVER      = os.getenv("NTFY_SERVER",      "https://ntfy.sh")

    # ── API keys / credentials ─────────────────────────────────────────────
    RADARR_API_KEY   = os.getenv("RADARR_API_KEY",   "")
    SONARR_API_KEY   = os.getenv("SONARR_API_KEY",   "")
    PLEX_TOKEN       = os.getenv("PLEX_TOKEN",       "")
    QBITTORRENT_USER = os.getenv("QBITTORRENT_USER", "admin")
    QBITTORRENT_PASS = os.getenv("QBITTORRENT_PASS", "adminPassword")
    NTFY_TOPIC       = os.getenv("NTFY_TOPIC",       "")

    # ── System ─────────────────────────────────────────────────────────────
    PILAB_NAME  = os.getenv("PILAB_NAME", "rpi")
    HOST        = os.getenv("HOST",       "localhost")
    MEDIA_PATH  = os.getenv("MEDIA_PATH", "/media")

    # ── Typed values (cast once here, never elsewhere) ─────────────────────
    ALERT_THRESHOLD_GB     = float(os.getenv("ALERT_THRESHOLD_GB",     "15"))
    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES",   "60"))

    # ── Container visibility ───────────────────────────────────────────────
    HIDDEN_CONTAINERS = set(
        os.getenv("HIDDEN_CONTAINERS", "watchtower,pilab-api,pilab-db").split(",")
    )

    # ── Flask ──────────────────────────────────────────────────────────────
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
}