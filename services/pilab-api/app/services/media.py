import requests
from flask import current_app


# ── Radarr ────────────────────────────────────────────────────────────────────

def _radarr_get(endpoint):
    cfg  = current_app.config
    resp = requests.get(
        f"{cfg['RADARR_URL']}{endpoint}",
        headers={"X-Api-Key": cfg["RADARR_API_KEY"]},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def radarr_delete(movie_id):
    """Delete a movie from Radarr and remove its files from disk."""
    cfg = current_app.config
    url = (
        f"{cfg['RADARR_URL']}/api/v3/movie/{movie_id}"
        "?deleteFiles=true&addImportExclusion=false"
    )
    resp = requests.delete(
        url,
        headers={"X-Api-Key": cfg["RADARR_API_KEY"]},
        timeout=15,
    )
    resp.raise_for_status()


def get_movies():
    """Return all downloaded movies, sorted by size descending."""
    try:
        movies = []
        for m in _radarr_get("/api/v3/movie"):
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

def _sonarr_get(endpoint):
    cfg  = current_app.config
    resp = requests.get(
        f"{cfg['SONARR_URL']}{endpoint}",
        headers={"X-Api-Key": cfg["SONARR_API_KEY"]},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def sonarr_delete(series_id):
    """Delete a series from Sonarr and remove its files from disk."""
    cfg  = current_app.config
    url  = f"{cfg['SONARR_URL']}/api/v3/series/{series_id}?deleteFiles=true"
    resp = requests.delete(
        url,
        headers={"X-Api-Key": cfg["SONARR_API_KEY"]},
        timeout=15,
    )
    resp.raise_for_status()


def get_series():
    """Return all downloaded series with episodes, sorted by size descending."""
    try:
        series_list = []
        for s in _sonarr_get("/api/v3/series"):
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