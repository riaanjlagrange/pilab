import requests
from flask import current_app
from .plex import get_plex_links_for_titles


# ── Helpers ───────────────────────────────────────────────────────────────────

def _headers() -> dict:
    return {"X-Api-Key": current_app.config["RADARR_API_KEY"]}


def _get(endpoint: str, params: dict | None = None):
    cfg  = current_app.config
    resp = requests.get(
        f"{cfg['RADARR_URL']}{endpoint}",
        headers=_headers(),
        params=params,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _format_search_result(r: dict, plex_links: dict | None = None) -> dict:
    """Shape a Radarr movie object into SearchResult."""
    images  = {i.get("coverType"): i.get("remoteUrl") for i in r.get("images", [])}
    title   = r.get("title", "")
    link    = (plex_links or {}).get(title.lower())
    return {
        "source":     "radarr",
        "type":       "movie",
        "title":      title,
        "year":       r.get("year"),
        "overview":   r.get("overview", ""),
        "tmdb_id":    r.get("tmdbId"),
        "imdb_id":    r.get("imdbId"),
        "poster_url": images.get("poster"),
        "fanart_url": images.get("fanart"),
        "rating":     r.get("ratings", {}).get("imdb", {}).get("value"),
        "in_radarr":  r.get("id") is not None,
        "radarr_id":  r.get("id"),
        "in_plex":    link is not None,
        "plex_link":  link,
    }


# ── Media ─────────────────────────────────────────────────────────────────────

def get_downloaded_movies() -> list[dict]:
    """All downloaded movies, sorted by size descending."""
    try:
        movies = []
        for m in _get("/api/v3/movie"):
            if not m.get("hasFile"):
                continue
            images = {i.get("coverType"): i.get("remoteUrl") for i in m.get("images", [])}
            movies.append({
                "id":         m["id"],
                "type":       "movie",
                "title":      m["title"],
                "year":       m.get("year"),
                "size_gb":    round(m.get("sizeOnDisk", 0) / 1e9, 2),
                "added":      m.get("added", "")[:10],
                "tmdb_id":    m.get("tmdbId"),
                "imdb_id":    m.get("imdbId"),
                "poster_url": images.get("poster"),
                "fanart_url": images.get("fanart"),
            })
        movies.sort(key=lambda x: x["size_gb"], reverse=True)
        return movies
    except Exception as e:
        print(f"[Radarr] get_downloaded_movies failed: {e}", flush=True)
        return []


def get_trending_movies(limit: int = 20) -> list[dict]:
    """
    Popular/trending movies via Radarr's discover endpoint (sourced from Trakt/IMDb).
    Also marks movies already in your library with owned=True.
    """
    try:
        items = _get("/api/v3/movie/discover", params={"pageSize": limit, "page": 1})

        owned_ids: set[int] = set()
        try:
            for m in _get("/api/v3/movie"):
                if m.get("hasFile") and m.get("tmdbId"):
                    owned_ids.add(m["tmdbId"])
        except Exception:
            pass

        trending = []
        for m in items[:limit]:
            tmdb_id  = m.get("tmdbId")
            genres   = m.get("genres", [])
            overview = m.get("overview", "")
            images   = {i.get("coverType"): i.get("remoteUrl") for i in m.get("images", [])}

            subtitle = (
                ", ".join(genres[:3]) if genres
                else (overview[:80] + "…" if len(overview) > 80 else overview)
            )
            thumb = m.get("remotePoster") or images.get("poster")

            trending.append({
                "id":         None,
                "type":       "movie",
                "title":      m.get("title", ""),
                "subtitle":   subtitle,
                "year":       m.get("year"),
                "tmdb_id":    tmdb_id,
                "imdb_id":    m.get("imdbId"),
                "poster_url": thumb,
                "fanart_url": images.get("fanart"),
                "rating":     m.get("ratings", {}).get("imdb", {}).get("value"),
                "owned":      tmdb_id in owned_ids,
            })

        return trending

    except Exception as e:
        print(f"[Radarr] get_trending_movies failed: {e}", flush=True)
        return []


# ── Search ────────────────────────────────────────────────────────────────────

def search_movies(query: str) -> list[dict]:
    """Search Radarr movie lookup, enriched with Plex links."""
    try:
        resp = requests.get(
            f"{current_app.config['RADARR_URL']}/api/v3/movie/lookup",
            headers=_headers(),
            params={"term": query},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()[:8]

        titles      = [r.get("title", "") for r in results]
        plex_links  = get_plex_links_for_titles(titles)

        return [_format_search_result(r, plex_links) for r in results]

    except Exception as e:
        print(f"[Radarr] search_movies failed: {e}", flush=True)
        return []


def get_profiles() -> dict:
    """Quality profiles and root folders from Radarr."""
    try:
        url     = current_app.config["RADARR_URL"]
        headers = _headers()
        profiles = requests.get(f"{url}/api/v3/qualityProfile", headers=headers, timeout=5).json()
        folders  = requests.get(f"{url}/api/v3/rootFolder",     headers=headers, timeout=5).json()
        return {
            "quality_profiles": [{"id": p["id"], "name": p["name"]} for p in profiles],
            "root_folders":     [{"id": f["id"], "path": f["path"]} for f in folders],
        }
    except Exception as e:
        print(f"[Radarr] get_profiles failed: {e}", flush=True)
        return {"quality_profiles": [], "root_folders": []}


# ── Request ───────────────────────────────────────────────────────────────────

def request_movie(tmdb_id: int, quality_profile_id: int, root_folder: str) -> dict:
    """Add a movie to Radarr and trigger a search."""
    radarr_url = current_app.config["RADARR_URL"]
    headers    = {**_headers(), "Content-Type": "application/json"}
    try:
        lookup = requests.get(
            f"{radarr_url}/api/v3/movie/lookup/tmdb",
            headers=headers,
            params={"tmdbId": tmdb_id},
            timeout=10,
        )
        lookup.raise_for_status()
        movie = lookup.json()
        movie["qualityProfileId"] = quality_profile_id
        movie["rootFolderPath"]   = root_folder
        movie["monitored"]        = True
        movie["addOptions"]       = {"searchForMovie": True}

        resp = requests.post(
            f"{radarr_url}/api/v3/movie",
            headers=headers,
            json=movie,
            timeout=10,
        )
        resp.raise_for_status()
        return {"ok": True, "id": resp.json().get("id")}

    except requests.HTTPError as e:
        if e.response and e.response.status_code == 400:
            return {"ok": False, "error": "already_exists"}
        body = e.response.json() if e.response else {}
        print(f"[Radarr] request_movie HTTP error: {e} — {body}", flush=True)
        return {"ok": False, "error": str(body)}
    except Exception as e:
        print(f"[Radarr] request_movie failed: {e}", flush=True)
        return {"ok": False, "error": str(e)}


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_movie(movie_id: int) -> None:
    """Delete a movie from Radarr and remove its files from disk."""
    cfg  = current_app.config
    url  = (
        f"{cfg['RADARR_URL']}/api/v3/movie/{movie_id}"
        "?deleteFiles=true&addImportExclusion=false"
    )
    resp = requests.delete(url, headers=_headers(), timeout=15)
    resp.raise_for_status()