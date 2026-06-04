import requests
from flask import current_app
from .plex import get_plex_links_for_titles


# ── Helpers ───────────────────────────────────────────────────────────────────

def _headers() -> dict:
    return {"X-Api-Key": current_app.config["SONARR_API_KEY"]}


def _get(endpoint: str, params: dict | None = None):
    cfg  = current_app.config
    resp = requests.get(
        f"{cfg['SONARR_URL']}{endpoint}",
        headers=_headers(),
        params=params,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _format_search_result(s: dict, plex_links: dict | None = None) -> dict:
    """Shape a Sonarr series object into SearchResult."""
    images = {i.get("coverType"): i.get("remoteUrl") for i in s.get("images", [])}
    title  = s.get("title", "")
    link   = (plex_links or {}).get(title.lower())
    return {
        "source":     "sonarr",
        "type":       "show",
        "title":      title,
        "year":       s.get("year"),
        "overview":   s.get("overview", ""),
        "tvdb_id":    s.get("tvdbId"),
        "imdb_id":    s.get("imdbId"),
        "poster_url": images.get("poster"),
        "fanart_url": images.get("fanart"),
        "rating":     s.get("ratings", {}).get("value"),
        "status":     s.get("status"),
        "network":    s.get("network"),
        "in_sonarr":  s.get("id") is not None,
        "sonarr_id":  s.get("id"),
        "in_plex":    link is not None,
        "plex_link":  link,
    }


# ── Media ─────────────────────────────────────────────────────────────────────

def get_downloaded_series() -> list[dict]:
    """All downloaded series with episodes, sorted by size descending."""
    try:
        series_list = []
        for s in _get("/api/v3/series"):
            stats = s.get("statistics", {})
            eps   = stats.get("episodeFileCount", 0)
            if eps == 0:
                continue
            images = {i.get("coverType"): i.get("remoteUrl") for i in s.get("images", [])}
            series_list.append({
                "id":         s["id"],
                "type":       "series",
                "title":      s["title"],
                "year":       s.get("year"),
                "size_gb":    round(stats.get("sizeOnDisk", 0) / 1e9, 2),
                "added":      s.get("added", "")[:10],
                "episodes":   eps,
                "seasons":    stats.get("seasonCount", 0),
                "tvdb_id":    s.get("tvdbId"),
                "imdb_id":    s.get("imdbId"),
                "poster_url": images.get("poster"),
                "fanart_url": images.get("fanart"),
                "status":     s.get("status"),
                "network":    s.get("network"),
            })
        series_list.sort(key=lambda x: x["size_gb"], reverse=True)
        return series_list
    except Exception as e:
        print(f"[Sonarr] get_downloaded_series failed: {e}", flush=True)
        return []


def get_trending_series(limit: int = 20) -> list[dict]:
    """
    Recently-added series from Sonarr that have downloaded episodes,
    sorted by added date descending.

    Sonarr has no discover/trending endpoint, so most-recently-grabbed
    is the best native proxy. Swap body for a Trakt call if needed later.
    """
    try:
        series_with_files = [
            s for s in _get("/api/v3/series")
            if s.get("statistics", {}).get("episodeFileCount", 0) > 0
        ]
        series_with_files.sort(key=lambda s: s.get("added", ""), reverse=True)

        trending = []
        for s in series_with_files[:limit]:
            stats    = s.get("statistics", {})
            genres   = s.get("genres", [])
            overview = s.get("overview", "")
            eps      = stats.get("episodeFileCount", 0)
            seasons  = stats.get("seasonCount", 0)
            images   = {i.get("coverType"): i.get("remoteUrl") for i in s.get("images", [])}

            if genres:
                subtitle = ", ".join(genres[:3])
            elif seasons:
                subtitle = f"{seasons} season{'s' if seasons != 1 else ''} · {eps} episode{'s' if eps != 1 else ''}"
            else:
                subtitle = overview[:80] + "…" if len(overview) > 80 else overview

            trending.append({
                "id":         s["id"],
                "type":       "series",
                "title":      s.get("title", ""),
                "subtitle":   subtitle,
                "year":       s.get("year"),
                "tvdb_id":    s.get("tvdbId"),
                "imdb_id":    s.get("imdbId"),
                "poster_url": images.get("poster"),
                "fanart_url": images.get("fanart"),
                "episodes":   eps,
                "seasons":    seasons,
                "status":     s.get("status"),
                "network":    s.get("network"),
            })

        return trending

    except Exception as e:
        print(f"[Sonarr] get_trending_series failed: {e}", flush=True)
        return []


# ── Search ────────────────────────────────────────────────────────────────────

def search_series(query: str) -> list[dict]:
    """Search Sonarr series lookup, enriched with Plex links."""
    try:
        resp = requests.get(
            f"{current_app.config['SONARR_URL']}/api/v3/series/lookup",
            headers=_headers(),
            params={"term": query},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()[:8]

        titles     = [r.get("title", "") for r in results]
        plex_links = get_plex_links_for_titles(titles)

        return [_format_search_result(r, plex_links) for r in results]

    except Exception as e:
        print(f"[Sonarr] search_series failed: {e}", flush=True)
        return []


def get_profiles() -> dict:
    """Quality profiles and root folders from Sonarr."""
    try:
        url     = current_app.config["SONARR_URL"]
        headers = _headers()
        profiles = requests.get(f"{url}/api/v3/qualityProfile", headers=headers, timeout=5).json()
        folders  = requests.get(f"{url}/api/v3/rootFolder",     headers=headers, timeout=5).json()
        return {
            "quality_profiles": [{"id": p["id"], "name": p["name"]} for p in profiles],
            "root_folders":     [{"id": f["id"], "path": f["path"]} for f in folders],
        }
    except Exception as e:
        print(f"[Sonarr] get_profiles failed: {e}", flush=True)
        return {"quality_profiles": [], "root_folders": []}


# ── Request ───────────────────────────────────────────────────────────────────

def request_series(tvdb_id: int, quality_profile_id: int, root_folder: str) -> dict:
    """Add a series to Sonarr and trigger a search."""
    sonarr_url = current_app.config["SONARR_URL"]
    headers    = {**_headers(), "Content-Type": "application/json"}
    try:
        lookup = requests.get(
            f"{sonarr_url}/api/v3/series/lookup",
            headers=headers,
            params={"term": f"tvdb:{tvdb_id}"},
            timeout=10,
        )
        lookup.raise_for_status()
        results = lookup.json()
        if not results:
            return {"ok": False, "error": "not_found"}

        series = results[0]
        series["qualityProfileId"] = quality_profile_id
        series["rootFolderPath"]   = root_folder
        series["monitored"]        = True
        series["addOptions"]       = {
            "searchForMissingEpisodes": True,
            "monitor": "all",
        }

        resp = requests.post(
            f"{sonarr_url}/api/v3/series",
            headers=headers,
            json=series,
            timeout=10,
        )
        resp.raise_for_status()
        return {"ok": True, "id": resp.json().get("id")}

    except requests.HTTPError as e:
        if e.response and e.response.status_code == 400:
            return {"ok": False, "error": "already_exists"}
        body = e.response.json() if e.response else {}
        print(f"[Sonarr] request_series HTTP error: {e} — {body}", flush=True)
        return {"ok": False, "error": str(body)}
    except Exception as e:
        print(f"[Sonarr] request_series failed: {e}", flush=True)
        return {"ok": False, "error": str(e)}


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_series(series_id: int) -> None:
    """Delete a series from Sonarr and remove its files from disk."""
    cfg  = current_app.config
    url  = f"{cfg['SONARR_URL']}/api/v3/series/{series_id}?deleteFiles=true"
    resp = requests.delete(url, headers=_headers(), timeout=15)
    resp.raise_for_status()