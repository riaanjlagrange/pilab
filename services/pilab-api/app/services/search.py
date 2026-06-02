import requests
from flask import current_app


def _radarr_headers() -> dict:
    return {"X-Api-Key": current_app.config["RADARR_API_KEY"]}


def _sonarr_headers() -> dict:
    return {"X-Api-Key": current_app.config["SONARR_API_KEY"]}


def search_radarr(query: str) -> list:
    try:
        resp = requests.get(
            f"{current_app.config['RADARR_URL']}/api/v3/movie/lookup",
            headers=_radarr_headers(),
            params={"term": query},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()[:8]
        formatted = [_format_radarr_result(r) for r in results]

        # Enrich with Plex info
        plex_links = _get_plex_search_results(query)
        for result in formatted:
            for plex_result in plex_links:
                if plex_result["title"].lower() == result["title"].lower():
                    result["plex_link"] = plex_result.get("plex_link")
                    result["in_plex"] = True
                    break

        return formatted
    except Exception as e:
        print(f"[Search] Radarr error: {e}", flush=True)
        return []


def search_sonarr(query: str) -> list:
    try:
        resp = requests.get(
            f"{current_app.config['SONARR_URL']}/api/v3/series/lookup",
            headers=_sonarr_headers(),
            params={"term": query},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()[:8]
        formatted = [_format_sonarr_result(r) for r in results]

        # Enrich with Plex info
        plex_links = _get_plex_search_results(query)
        for result in formatted:
            for plex_result in plex_links:
                if plex_result["title"].lower() == result["title"].lower():
                    result["plex_link"] = plex_result.get("plex_link")
                    result["in_plex"] = True
                    break

        return formatted
    except Exception as e:
        print(f"[Search] Sonarr error: {e}", flush=True)
        return []


def _get_plex_search_results(query: str) -> list:
    """Get search results from Plex with plex_link."""
    from .plex import search_plex_library
    try:
        return search_plex_library(query)
    except Exception as e:
        print(f"[Search] Plex enrichment error: {e}", flush=True)
        return []


def get_radarr_profiles() -> dict:
    try:
        radarr_url = current_app.config["RADARR_URL"]
        headers    = _radarr_headers()

        profiles = requests.get(
            f"{radarr_url}/api/v3/qualityProfile",
            headers=headers, timeout=5,
        ).json()

        folders = requests.get(
            f"{radarr_url}/api/v3/rootFolder",
            headers=headers, timeout=5,
        ).json()

        return {
            "quality_profiles": [{"id": p["id"], "name": p["name"]} for p in profiles],
            "root_folders":     [{"id": f["id"], "path": f["path"]} for f in folders],
        }
    except Exception as e:
        print(f"[Search] Radarr profiles error: {e}", flush=True)
        return {"quality_profiles": [], "root_folders": []}


def get_sonarr_profiles() -> dict:
    try:
        sonarr_url = current_app.config["SONARR_URL"]
        headers    = _sonarr_headers()

        profiles = requests.get(
            f"{sonarr_url}/api/v3/qualityProfile",
            headers=headers, timeout=5,
        ).json()

        folders = requests.get(
            f"{sonarr_url}/api/v3/rootFolder",
            headers=headers, timeout=5,
        ).json()

        return {
            "quality_profiles": [{"id": p["id"], "name": p["name"]} for p in profiles],
            "root_folders":     [{"id": f["id"], "path": f["path"]} for f in folders],
        }
    except Exception as e:
        print(f"[Search] Sonarr profiles error: {e}", flush=True)
        return {"quality_profiles": [], "root_folders": []}


def _format_radarr_result(r: dict) -> dict:
    images = {i.get("coverType"): i.get("remoteUrl") for i in r.get("images", [])}
    return {
        "source":      "radarr",
        "type":        "movie",
        "title":       r.get("title", ""),
        "year":        r.get("year"),
        "overview":    r.get("overview", ""),
        "tmdb_id":     r.get("tmdbId"),
        "imdb_id":     r.get("imdbId"),
        "poster_url":  images.get("poster"),
        "fanart_url":  images.get("fanart"),
        "rating":      r.get("ratings", {}).get("imdb", {}).get("value"),
        "in_radarr":   r.get("id") is not None,
        "radarr_id":   r.get("id"),
        "in_plex":     False,
        "plex_link":  None,
    }


def _format_sonarr_result(r: dict) -> dict:
    images = {i.get("coverType"): i.get("remoteUrl") for i in r.get("images", [])}
    return {
        "source":      "sonarr",
        "type":        "show",
        "title":       r.get("title", ""),
        "year":        r.get("year"),
        "overview":    r.get("overview", ""),
        "tvdb_id":     r.get("tvdbId"),
        "imdb_id":     r.get("imdbId"),
        "poster_url":  images.get("poster"),
        "fanart_url":  images.get("fanart"),
        "rating":      r.get("ratings", {}).get("value"),
        "in_sonarr":   r.get("id") is not None,
        "sonarr_id":   r.get("id"),
        "status":      r.get("status"),
        "network":     r.get("network"),
        "in_plex":     False,
        "plex_link":  None,
    }