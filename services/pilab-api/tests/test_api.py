"""
Basic smoke tests for the homelab API.

Run with:  pytest tests/
"""
import pytest
from app import create_app
from app.config import DevelopmentConfig


class TestingConfig(DevelopmentConfig):
    TESTING        = True
    DATABASE_URL   = "sqlite://"   # in-memory, no Postgres needed
    MEDIA_PATH     = "/tmp"
    PLEX_TOKEN     = ""
    RADARR_API_KEY = ""
    SONARR_API_KEY = ""
    NTFY_TOPIC     = ""


@pytest.fixture
def app():
    app = create_app(config=TestingConfig)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


# ── Factory ────────────────────────────────────────────────────────────────

def test_create_app_returns_flask_app(app):
    from flask import Flask
    assert isinstance(app, Flask)


def test_config_is_testing(app):
    assert app.config["TESTING"] is True


def test_debug_true_in_dev_config(app):
    assert app.config["DEBUG"] is True


# ── Routes ─────────────────────────────────────────────────────────────────

def test_system_endpoint(client, mocker):
    mocker.patch(
        "app.services.system.get_system",
        return_value={"cpu_percent": 10, "ram_percent": 50},
    )
    resp = client.get("/api/system")
    assert resp.status_code == 200
    assert resp.get_json()["cpu_percent"] == 10


def test_disk_endpoint(client, mocker):
    mocker.patch(
        "app.services.system.get_disk",
        return_value={"percent_used": 42.0},
    )
    resp = client.get("/api/disk")
    assert resp.status_code == 200
    assert resp.get_json()["percent_used"] == 42.0


def test_containers_endpoint(client, mocker):
    mocker.patch(
        "app.services.containers.get_containers",
        return_value=[{"name": "plex", "status": "running"}],
    )
    resp = client.get("/api/containers")
    assert resp.status_code == 200
    assert resp.get_json()[0]["name"] == "plex"


def test_plex_endpoint_no_token(client):
    """With no PLEX_TOKEN set, /api/plex should return empty lists."""
    resp = client.get("/api/plex")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["now_playing"] == []
    assert data["on_deck"]     == []


def test_media_endpoint(client, mocker):
    mocker.patch("app.services.media.get_movies", return_value=[])
    mocker.patch("app.services.media.get_series", return_value=[])
    resp = client.get("/api/media")
    assert resp.status_code == 200
    assert "movies" in resp.get_json()


def test_downloads_endpoint(client, mocker):
    mocker.patch("app.services.downloads.get_downloads", return_value=[])
    resp = client.get("/api/downloads")
    assert resp.status_code == 200


def test_queue_endpoint(client, mocker):
    mocker.patch(
        "app.services.downloads.get_queue",
        return_value={"movies": [], "series": []},
    )
    resp = client.get("/api/queue")
    assert resp.status_code == 200


def test_delete_invalid_type(client):
    resp = client.post(
        "/api/delete",
        json={"id": 1, "type": "podcast"},
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_delete_missing_id(client):
    resp = client.post(
        "/api/delete",
        json={"type": "movie"},
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_settings_get(client):
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    assert "pilabName" in resp.get_json()


def test_settings_post_no_body(client):
    resp = client.post("/api/settings", json=None, content_type="application/json")
    assert resp.status_code == 400


def test_webhook_radarr_get(client):
    resp = client.get("/api/webhooks/radarr")
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True


def test_webhook_sonarr_get(client):
    resp = client.get("/api/webhooks/sonarr")
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True