import requests
from flask import current_app


def request_movie(tmdb_id: int, quality_profile_id: int, root_folder: str) -> dict:
    radarr_url = current_app.config["RADARR_URL"]
    headers    = {
        "X-Api-Key":    current_app.config["RADARR_API_KEY"],
        "Content-Type": "application/json",
    }
    try:
        # Look up full movie details from TMDb via Radarr first
        lookup = requests.get(
            f"{radarr_url}/api/v3/movie/lookup/tmdb",
            headers=headers,
            params={"tmdbId": tmdb_id},
            timeout=10,
        )
        lookup.raise_for_status()
        movie = lookup.json()

        movie["qualityProfileId"]  = quality_profile_id
        movie["rootFolderPath"]    = root_folder
        movie["monitored"]         = True
        movie["addOptions"]        = {"searchForMovie": True}

        resp = requests.post(
            f"{radarr_url}/api/v3/movie",
            headers=headers,
            json=movie,
            timeout=10,
        )
        resp.raise_for_status()
        return {"ok": True, "id": resp.json().get("id")}
    except requests.HTTPError as e:
        body = e.response.json() if e.response else {}
        # 400 with "already exists" message means it's already in Radarr
        if e.response and e.response.status_code == 400:
            return {"ok": False, "error": "already_exists"}
        print(f"[Request] Radarr error: {e} — {body}", flush=True)
        return {"ok": False, "error": str(body)}
    except Exception as e:
        print(f"[Request] Radarr error: {e}", flush=True)
        return {"ok": False, "error": str(e)}


def request_show(tvdb_id: int, quality_profile_id: int, root_folder: str) -> dict:
    sonarr_url = current_app.config["SONARR_URL"]
    headers    = {
        "X-Api-Key":    current_app.config["SONARR_API_KEY"],
        "Content-Type": "application/json",
    }
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
        show = results[0]

        show["qualityProfileId"] = quality_profile_id
        show["rootFolderPath"]   = root_folder
        show["monitored"]        = True
        show["addOptions"]       = {
            "searchForMissingEpisodes": True,
            "monitor": "all",
        }

        resp = requests.post(
            f"{sonarr_url}/api/v3/series",
            headers=headers,
            json=show,
            timeout=10,
        )
        resp.raise_for_status()
        return {"ok": True, "id": resp.json().get("id")}
    except requests.HTTPError as e:
        if e.response and e.response.status_code == 400:
            return {"ok": False, "error": "already_exists"}
        print(f"[Request] Sonarr error: {e}", flush=True)
        return {"ok": False, "error": str(e)}
    except Exception as e:
        print(f"[Request] Sonarr error: {e}", flush=True)
        return {"ok": False, "error": str(e)}