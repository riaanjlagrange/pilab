"""
Homelab API
===========
Central Flask backend for the homelab dashboard system.

Endpoints:
  GET  /api/system        → hostname, CPU%, RAM%, uptime
  GET  /api/disk          → free/used/total GB, percent used
  GET  /api/containers    → all Docker containers with status
  GET  /api/plex          → active sessions and on-deck items
  GET  /api/media         → downloaded movies and series
  GET  /api/downloads     → active torrents from qBittorrent
  GET  /api/queue         → Radarr and Sonarr download queue
  GET  /api/status        → combined disk + media (for storage page)
  POST /api/delete        → delete movie or series

Environment variables:
  RADARR_URL, RADARR_API_KEY
  SONARR_URL, SONARR_API_KEY
  PLEX_URL, PLEX_TOKEN
  GLANCES_URL
  QBITTORRENT_URL, QBITTORRENT_USER, QBITTORRENT_PASS
  NTFY_TOPIC, NTFY_SERVER
  ALERT_THRESHOLD_GB (default: 15)
  CHECK_INTERVAL_MINUTES (default: 60)
  MEDIA_PATH (default: /media)
  HIDDEN_CONTAINERS
"""

import os
import json
import shutil
import socket
import threading
import time
from datetime import datetime, timezone

import docker
import psutil
import requests
from flask import Flask, jsonify, request, Response, send_file
from flask_cors import CORS
from sqlalchemy import Column, DateTime, Integer, JSON, MetaData, String, Table, create_engine, select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert

app = Flask(__name__)
CORS(app)

# ── Configuration ─────────────────────────────────────────────────────────────

RADARR_URL      = os.getenv("RADARR_URL", "http://radarr:7878")
RADARR_API_KEY  = os.getenv("RADARR_API_KEY", "")
SONARR_URL      = os.getenv("SONARR_URL", "http://sonarr:8989")
SONARR_API_KEY  = os.getenv("SONARR_API_KEY", "")

# Plex is on host network mode, so we reach it via host.docker.internal
PLEX_URL        = os.getenv("PLEX_URL", "http://host.docker.internal:32400")
PLEX_TOKEN      = os.getenv("PLEX_TOKEN", "")

# Glances is on the homelab Docker network — reachable by container name
GLANCES_URL     = os.getenv("GLANCES_URL", "http://glances:61208")

# qBittorrent on the homelab Docker network
QBITTORRENT_URL = os.getenv("QBITTORRENT_URL", "http://qbittorrent:8080")
QBITTORRENT_USER = os.getenv("QBITTORRENT_USER", "admin")
QBITTORRENT_PASS = os.getenv("QBITTORRENT_PASS", "adminPassword")

# System host
PILAB_NAME      = os.getenv("PILAB_NAME", "rpi")
DOMAIN          = os.getenv("DOMAIN", "rpi.riaanjlagrange.com")

NTFY_TOPIC      = os.getenv("NTFY_TOPIC", "")
NTFY_SERVER     = os.getenv("NTFY_SERVER", "https://ntfy.sh")

ALERT_THRESHOLD_GB     = float(os.getenv("ALERT_THRESHOLD_GB", "15"))
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "60"))
MEDIA_PATH             = os.getenv("MEDIA_PATH", "/media")
STORAGE_URL            = os.getenv("STORAGE_URL", "https://storage.rpi.riaanjlagrange.com")
DASHBOARD_URL          = os.getenv("DASHBOARD_URL", "https://rpi.riaanjlagrange.com")
DATABASE_URL           = os.getenv("DATABASE_URL", "postgresql://pilab:pilab@pilab-db:5432/pilab")


HIDDEN_CONTAINERS = set(
    os.getenv("HIDDEN_CONTAINERS", "watchtower,pilab-api,pilab-db").split(",")
)

DEFAULT_SETTINGS = {
    "pilabName": PILAB_NAME,
    "diskThreshold": 85,
    "checkIntervalMinutes": 60,
    "hiddenContainers": list(HIDDEN_CONTAINERS),
    "ntfyTopic": NTFY_TOPIC,
}

settings_metadata = MetaData()
settings_table = Table(
    "settings",
    settings_metadata,
    Column("id", Integer, primary_key=True),
    Column("data", JSON, nullable=False),
    Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
)

try:
    db_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    settings_metadata.create_all(db_engine)
    print("[Database] Connected to settings database", flush=True)
except Exception as e:
    print(f"[Database] Could not connect to settings database: {e}", flush=True)
    db_engine = None

# ── Docker client ─────────────────────────────────────────────────────────────
try:
    docker_client = docker.from_env()
    docker_client.ping()
    print("[Docker] Connected to Docker socket", flush=True)
except Exception as e:
    print(f"[Docker] Could not connect to Docker socket: {e}", flush=True)
    docker_client = None

# ── Helpers ───────────────────────────────────────────────────────────────────

def format_uptime(seconds):
    """Format seconds to human-readable uptime: '1d 1h', '1h 1m', etc."""
    if seconds is None:
        return None
    days    = int(seconds // 86400)
    hours   = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "just started"

def parse_docker_timestamp(ts_str):
    """Parse Docker's ISO timestamp with nanosecond precision."""
    try:
        if '.' in ts_str:
            base, frac = ts_str.split('.')
            frac = frac.rstrip('Z')[:6].ljust(6, '0')
            return datetime.fromisoformat(f"{base}.{frac}+00:00")
        else:
            return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except Exception:
        return None

# ── System metrics ────────────────────────────────────────────────────────────

def get_system():
    """Fetch hostname, CPU%, RAM%, and uptime from Glances or psutil."""
    pilab_name = get_settings().get("pilabName", PILAB_NAME)
    result = {
        "pilab_name":    pilab_name,
        "cpu_percent":   0,
        "ram_percent":   0,
        "ram_used_gb":   0,
        "ram_total_gb":  0,
        "uptime_seconds": 0,
        "uptime_human":  "unknown",
    }

    try:
        cpu_resp = requests.get(f"{GLANCES_URL}/api/4/cpu", timeout=3)
        result["cpu_percent"] = round(cpu_resp.json().get("total", 0), 1)

        mem_resp = requests.get(f"{GLANCES_URL}/api/4/mem", timeout=3)
        mem = mem_resp.json()
        result["ram_percent"]  = round(mem.get("percent", 0), 1)
        result["ram_used_gb"]  = round(mem.get("used", 0) / 1e9, 2)
        result["ram_total_gb"] = round(mem.get("total", 0) / 1e9, 2)

        with open('/proc/uptime', 'r') as f:
            uptime_seconds = int(float(f.read().split()[0]))
        result["uptime_seconds"] = uptime_seconds
        result["uptime_human"]   = format_uptime(uptime_seconds)

    except Exception as e:
        print(f"[System] Glances unavailable, falling back to psutil: {e}", flush=True)
        try:
            cpu  = psutil.cpu_percent(interval=0.5)
            ram  = psutil.virtual_memory()
            boot = psutil.boot_time()
            uptime = int(time.time() - boot)
            result["cpu_percent"]    = round(cpu, 1)
            result["ram_percent"]    = round(ram.percent, 1)
            result["ram_used_gb"]    = round(ram.used / 1e9, 2)
            result["ram_total_gb"]   = round(ram.total / 1e9, 2)
            result["uptime_seconds"] = uptime
            result["uptime_human"]   = format_uptime(uptime)
        except Exception as e2:
            print(f"[System] psutil also failed: {e2}", flush=True)

    return result

# ── Disk ──────────────────────────────────────────────────────────────────────

def get_disk():
    """Fetch disk usage for the media partition."""
    usage = shutil.disk_usage(MEDIA_PATH)
    return {
        "total_gb":     round(usage.total / 1e9, 2),
        "used_gb":      round(usage.used  / 1e9, 2),
        "free_gb":      round(usage.free  / 1e9, 2),
        "percent_used": round((usage.used / usage.total) * 100, 1),
        "threshold_gb": ALERT_THRESHOLD_GB,
    }

# ── Docker containers ─────────────────────────────────────────────────────────

def get_containers(apply_hidden_filter=True):
    """Fetch all Docker containers (running and stopped).

    Args:
        apply_hidden_filter: If True, exclude containers in settings.hiddenContainers.
                           If False, return all containers.
    """
    if not docker_client:
        return []
    try:
        hidden = set()
        if apply_hidden_filter:
            settings = get_settings()
            hidden = set(settings.get("hiddenContainers", []))

        result = []
        for c in docker_client.containers.list(all=True):
            if c.name in hidden:
                continue

            uptime_seconds = None
            if c.status == "running":
                started = parse_docker_timestamp(c.attrs['State']['StartedAt'])
                if started:
                    uptime_seconds = int(
                        (datetime.now(timezone.utc) - started).total_seconds()
                    )

            result.append({
                "name":          c.name,
                "status":        c.status,
                "uptime_seconds": uptime_seconds,
                "uptime_human":  format_uptime(uptime_seconds),
            })

        result.sort(key=lambda x: (x["status"] != "running", x["name"].lower()))
        return result

    except Exception as e:
        print(f"[Docker] Failed to list containers: {e}", flush=True)
        return []

# ── Plex ──────────────────────────────────────────────────────────────────────

def get_plex():
    """Fetch active sessions and on-deck items from Plex."""
    if not PLEX_TOKEN:
        return {"now_playing": [], "on_deck": []}

    headers = {
        "Accept":        "application/json",
        "X-Plex-Token":  PLEX_TOKEN,
    }
    now_playing = []
    on_deck     = []

    try:
        resp = requests.get(f"{PLEX_URL}/status/sessions", headers=headers, timeout=5)
        resp.raise_for_status()
        items = resp.json().get("MediaContainer", {}).get("Metadata") or []
        for item in items:
            entry = {
                "type":  item.get("type"),   # "movie" or "episode"
                "title": item.get("title"),
                "user":  item.get("User", {}).get("title", ""),
                "state": item.get("Player", {}).get("state", "playing"),
            }
            if item.get("type") == "episode":
                entry["show"]    = item.get("grandparentTitle", "")
                entry["episode"] = (
                    f"S{item.get('parentIndex', 0):02d}"
                    f"E{item.get('index', 0):02d}"
                )
            duration    = item.get("duration", 0)
            view_offset = item.get("viewOffset", 0)
            if duration:
                entry["progress_pct"] = round(view_offset / duration * 100)
            now_playing.append(entry)
    except Exception as e:
        print(f"[Plex] Sessions error: {e}", flush=True)

    try:
        resp = requests.get(
            f"{PLEX_URL}/library/onDeck",
            headers=headers,
            timeout=5
        )
        resp.raise_for_status()
        items = resp.json().get("MediaContainer", {}).get("Metadata") or []
        for item in items[:8]:
            entry = {
                "type":     item.get("type"),
                "year":     item.get("year"),
            }
            if item.get("type") == "episode":
                entry["title"]    = item.get("grandparentTitle", item.get("title"))
                entry["subtitle"] = (
                    f"S{item.get('parentIndex', 0):02d}"
                    f"E{item.get('index', 0):02d}"
                    f" · {item.get('title')}"
                )
            else:
                entry["title"]    = item.get("title")
                entry["subtitle"] = str(item.get("year", ""))

            duration    = item.get("duration", 0)
            view_offset = item.get("viewOffset", 0)
            if duration:
                entry["progress_pct"] = round(view_offset / duration * 100)

            on_deck.append(entry)
    except Exception as e:
        print(f"[Plex] On deck error: {e}", flush=True)

    return {"now_playing": now_playing, "on_deck": on_deck}

# ── Radarr ────────────────────────────────────────────────────────────────────

def radarr_get(endpoint):
    resp = requests.get(
        f"{RADARR_URL}{endpoint}",
        headers={"X-Api-Key": RADARR_API_KEY},
        timeout=15
    )
    resp.raise_for_status()
    return resp.json()

def radarr_delete(movie_id):
    """Delete movie from Radarr and remove files."""
    url = (
        f"{RADARR_URL}/api/v3/movie/{movie_id}"
        f"?deleteFiles=true&addImportExclusion=false"
    )
    resp = requests.delete(url, headers={"X-Api-Key": RADARR_API_KEY}, timeout=15)
    resp.raise_for_status()

def get_movies():
    try:
        movies = []
        for m in radarr_get("/api/v3/movie"):
            if m.get("hasFile"):
                movies.append({
                    "id":      m["id"],
                    "title":   m["title"],
                    "year":    m.get("year", ""),
                    "size_gb": round(m.get("sizeOnDisk", 0) / 1e9, 2),
                    "added":   m.get("added", "")[:10],
                    "type":    "movie",
                })
        movies.sort(key=lambda x: x["size_gb"], reverse=True)
        return movies
    except Exception as e:
        print(f"[Radarr] Failed: {e}", flush=True)
        return []

# ── Sonarr ────────────────────────────────────────────────────────────────────

def sonarr_get(endpoint):
    resp = requests.get(
        f"{SONARR_URL}{endpoint}",
        headers={"X-Api-Key": SONARR_API_KEY},
        timeout=15
    )
    resp.raise_for_status()
    return resp.json()

def sonarr_delete(series_id):
    """Delete series from Sonarr and remove files."""
    url = f"{SONARR_URL}/api/v3/series/{series_id}?deleteFiles=true"
    resp = requests.delete(url, headers={"X-Api-Key": SONARR_API_KEY}, timeout=15)
    resp.raise_for_status()

def get_series():
    try:
        series_list = []
        for s in sonarr_get("/api/v3/series"):
            stats = s.get("statistics", {})
            eps   = stats.get("episodeFileCount", 0)
            if eps > 0:
                series_list.append({
                    "id":       s["id"],
                    "title":    s["title"],
                    "year":     s.get("year", ""),
                    "size_gb":  round(stats.get("sizeOnDisk", 0) / 1e9, 2),
                    "added":    s.get("added", "")[:10],
                    "episodes": eps,
                    "type":     "series",
                })
        series_list.sort(key=lambda x: x["size_gb"], reverse=True)
        return series_list
    except Exception as e:
        print(f"[Sonarr] Failed: {e}", flush=True)
        return []

# ── qBittorrent ───────────────────────────────────────────────────────────────

def get_downloads():
    """Fetch active torrents from qBittorrent."""
    try:
        sess = requests.Session()
        login_url = f"{QBITTORRENT_URL}/api/v2/auth/login"
        login_resp = sess.post(login_url, data={"username": QBITTORRENT_USER, "password": QBITTORRENT_PASS}, timeout=10)
        if login_resp.status_code == 403:
            print(f"[qBittorrent] Login forbidden - check credentials. Response: {login_resp.text}", flush=True)
            return []
        login_resp.raise_for_status()

        resp = sess.get(f"{QBITTORRENT_URL}/api/v2/torrents/info", timeout=10)
        resp.raise_for_status()
        torrents = resp.json()

        downloads = []
        for t in torrents:
            if t.get("state") in ("downloading", "metaDL", "forcedDL"):
                size_gb = round(t.get("size", 0) / 1e9, 2)
                progress = round(t.get("progress", 0) * 100, 1)
                speed = t.get("dlspeed", 0)
                speed_mb = round(speed / 1e6, 1) if speed else 0
                eta_sec = t.get("eta", -1)

                if eta_sec > 0:
                    hours = eta_sec // 3600
                    minutes = (eta_sec % 3600) // 60
                    eta = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                else:
                    eta = "unknown"

                downloads.append({
                    "name":     t.get("name"),
                    "progress": progress,
                    "speed_mb": speed_mb,
                    "eta":      eta,
                    "size_gb":  size_gb,
                    "state":    t.get("state"),
                })

        return downloads
    except Exception as e:
        print(f"[qBittorrent] Failed: {e}", flush=True)
        return []

def get_queue():
    """Fetch queue from Radarr and Sonarr."""
    queue_data = {"movies": [], "series": []}

    try:
        movies_response = radarr_get("/api/v3/queue")
        movies_queue = movies_response.get("records", []) if isinstance(movies_response, dict) else []
        for item in movies_queue:
            if item.get("title") and item.get("id"):
                size = item.get("size", 0)
                sizeleft = item.get("sizeleft", 0)
                progress = ((size - sizeleft) / size * 100) if size > 0 else 0
                queue_data["movies"].append({
                    "id":     item["id"],
                    "title":  item.get("title"),
                    "status": item.get("status", "unknown"),
                    "progress": round(progress, 1),
                })
    except Exception as e:
        print(f"[Radarr Queue] Failed: {e}", flush=True)

    try:
        series_response = sonarr_get("/api/v3/queue")
        series_queue = series_response.get("records", []) if isinstance(series_response, dict) else []
        for item in series_queue:
            if item.get("title") and item.get("id"):
                size = item.get("size", 0)
                sizeleft = item.get("sizeleft", 0)
                progress = ((size - sizeleft) / size * 100) if size > 0 else 0
                queue_data["series"].append({
                    "id":     item["id"],
                    "title":  item.get("title"),
                    "status": item.get("status", "unknown"),
                    "progress": round(progress, 1),
                })
    except Exception as e:
        print(f"[Sonarr Queue] Failed: {e}", flush=True)

    return queue_data

def get_settings():
    """Load settings from the database and merge them with defaults."""
    settings = DEFAULT_SETTINGS.copy()
    if not db_engine:
        return settings

    try:
        with db_engine.begin() as conn:
            conn.execute(
                pg_insert(settings_table)
                .values(id=1, data=DEFAULT_SETTINGS)
                .on_conflict_do_nothing(index_elements=[settings_table.c.id])
            )
            row = conn.execute(select(settings_table.c.data).where(settings_table.c.id == 1)).scalar_one_or_none()
            if isinstance(row, dict):
                settings.update(row)
    except Exception as e:
        print(f"[Settings] Error reading settings: {e}", flush=True)
    return settings

def save_settings(settings):
    """Save settings to the database."""
    if not db_engine:
        print("[Settings] Database unavailable", flush=True)
        return False

    merged = DEFAULT_SETTINGS.copy()
    merged.update(get_settings())
    merged.update(settings)
    try:
        with db_engine.begin() as conn:
            conn.execute(
                pg_insert(settings_table)
                .values(id=1, data=merged)
                .on_conflict_do_update(
                    index_elements=[settings_table.c.id],
                    set_={"data": merged, "updated_at": func.now()},
                )
            )
        return True
    except Exception as e:
        print(f"[Settings] Error saving settings: {e}", flush=True)
        return False

# ── Flask routes ──────────────────────────────────────────────────────────────

@app.route("/api/system")
def api_system():
    """System metrics: hostname, CPU, RAM, uptime"""
    return jsonify(get_system())

@app.route("/api/disk")
def api_disk():
    """Disk usage for the media partition"""
    return jsonify(get_disk())

@app.route("/api/containers")
def api_containers():
    """All Docker containers with status and uptime.

    Query params:
      all=true  → return all containers (no hidden filter)
      all=false → apply hidden filter (default)
    """
    show_all = request.args.get("all", "false").lower() == "true"
    return jsonify(get_containers(apply_hidden_filter=not show_all))

@app.route("/api/plex")
def api_plex():
    """Plex active sessions and on-deck items"""
    return jsonify(get_plex())

@app.route("/api/media")
def api_media():
    """All downloaded movies and series from Radarr/Sonarr"""
    return jsonify({"movies": get_movies(), "series": get_series()})

@app.route("/api/downloads")
def api_downloads():
    """Active downloads from qBittorrent"""
    return jsonify(get_downloads())

@app.route("/api/queue")
def api_queue():
    """Download queue from Radarr and Sonarr"""
    return jsonify(get_queue())

@app.route("/api/status")
def api_status():
    """Combined disk + media endpoint for storage manager."""
    return jsonify({
        "disk":         get_disk(),
        "movies":       get_movies(),
        "series":       get_series(),
        "threshold_gb": ALERT_THRESHOLD_GB,
    })

@app.route("/api/delete", methods=["POST"])
def api_delete():
    """Delete a movie or series by id and type."""
    data      = request.get_json()
    item_id   = data.get("id")
    item_type = data.get("type")

    if not item_id or item_type not in ("movie", "series"):
        return jsonify({"error": "Invalid request"}), 400

    try:
        if item_type == "movie":
            radarr_delete(item_id)
            print(f"[Delete] Movie {item_id} deleted via Radarr", flush=True)
        else:
            sonarr_delete(item_id)
            print(f"[Delete] Series {item_id} deleted via Sonarr", flush=True)
        return jsonify({"success": True})
    except Exception as e:
        print(f"[Delete] Error: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings", methods=["GET"])
def api_settings_get():
    """Get all settings."""
    return jsonify(get_settings())

@app.route("/api/settings", methods=["POST"])
def api_settings_set():
    """Update settings."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if save_settings(data):
        print(f"[Settings] Updated", flush=True)
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Failed to save settings"}), 500

# ── ntfy helpers ──────────────────────────────────────────────────────────────

def send_ntfy(title, message, priority="high"):
	settings = get_settings()
	ntfy_topic = settings.get("ntfyTopic", NTFY_TOPIC)
	if not ntfy_topic:
		print("[ntfy] ntfyTopic not set — skipping", flush=True)
		return
	safe_title = title.encode("ascii", "ignore").decode("ascii").strip()
	headers = {
		"Title":    safe_title,
		"Priority": priority,
		"Tags":     "warning,floppy_disk",
		"Click":    f"https://{DOMAIN}/media?tab=media",
	}
	try:
		resp = requests.post(
			f"{NTFY_SERVER}/{ntfy_topic}",
			data=message.encode("utf-8"),
			headers=headers,
			timeout=10
		)
		resp.raise_for_status()
		print(f"[ntfy] Sent: {safe_title}", flush=True)
	except Exception as e:
		print(f"[ntfy] Failed: {e}", flush=True)

# ── Background monitor thread ─────────────────────────────────────────────────

alert_sent = False

def monitor_loop():
    """Monitor disk space and send notifications when above threshold."""
    global alert_sent
    settings = get_settings()
    threshold = settings.get("diskThreshold", 85)
    check_interval = settings.get("checkIntervalMinutes", 60)
    print(
        f"[Monitor] Starting — {check_interval}min interval, "
        f"{threshold}% threshold",
        flush=True
    )
    time.sleep(5)

    while True:
        try:
            settings = get_settings()
            threshold = settings.get("diskThreshold", 85)
            disk = get_disk()
            used_pct = disk["percent_used"]
            print(f"[Monitor] Disk usage: {used_pct}%", flush=True)

            if used_pct >= threshold and not alert_sent:
                storage_link = f"https://{DOMAIN}/media?tab=media"
                send_ntfy(
                    f"Disk Usage Alert - {used_pct}%",
                    (
                        f"Disk usage is at {used_pct}% (threshold: {threshold}%)\n"
                        f"Used: {disk['used_gb']} GB / {disk['total_gb']} GB\n"
                        f"Free: {disk['free_gb']} GB\n\n"
                        f"Manage storage: {storage_link}"
                    )
                )
                alert_sent = True

            elif used_pct < threshold and alert_sent:
                alert_sent = False
                print("[Monitor] Usage below threshold — alert flag reset", flush=True)

        except Exception as e:
            print(f"[Monitor] Error: {e}", flush=True)

        time.sleep(check_interval * 60)

threading.Thread(target=monitor_loop, daemon=True).start()

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)