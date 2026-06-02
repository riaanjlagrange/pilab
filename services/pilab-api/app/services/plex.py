import requests
from urllib.parse import quote
from flask import current_app


def _get_machine_id(plex_url: str, headers: dict) -> str:
    try:
        resp = requests.get(f"{plex_url}/identity", headers=headers, timeout=5)
        resp.raise_for_status()
        return resp.json().get("MediaContainer", {}).get("machineIdentifier", "")
    except Exception:
        return ""


def _plex_link(plex_public_url: str, machine_id: str, key: str) -> str:
    return (
        f"{plex_public_url}/web/index.html#!/server/{machine_id}/details"
        f"?key={quote(key, safe='')}"
    )


def get_plex():
    """Fetch active Plex sessions and on-deck items."""
    cfg = current_app.config
    if not cfg["PLEX_TOKEN"]:
        return {"now_playing": [], "on_deck": []}

    headers = {
        "Accept":       "application/json",
        "X-Plex-Token": cfg["PLEX_TOKEN"],
    }
    plex_url        = cfg["PLEX_URL"]
    plex_public_url = f"http://{cfg['HOST']}:32400"
    token           = cfg["PLEX_TOKEN"]
    machine_id      = _get_machine_id(plex_url, headers)
    now_playing     = []
    on_deck         = []

    # ── Active sessions ────────────────────────────────────────────────────
    try:
        resp  = requests.get(f"{plex_url}/status/sessions", headers=headers, timeout=5)
        resp.raise_for_status()
        items = resp.json().get("MediaContainer", {}).get("Metadata") or []

        for item in items:
            entry = {
                "type":  item.get("type"),
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
                thumb_path = item.get("grandparentThumb") or item.get("thumb", "")
            else:
                thumb_path = item.get("thumb", "")

            key = item.get("key", "")
            entry["thumb_url"] = f"{plex_public_url}{thumb_path}?X-Plex-Token={token}" if thumb_path else None
            entry["plex_link"] = _plex_link(plex_public_url, machine_id, key) if key else None

            duration    = item.get("duration",   0)
            view_offset = item.get("viewOffset", 0)
            if duration:
                entry["progress_pct"] = round(view_offset / duration * 100)

            now_playing.append(entry)

    except Exception as e:
        print(f"[Plex] Sessions error: {e}", flush=True)

    # ── On deck ────────────────────────────────────────────────────────────
    try:
        resp  = requests.get(f"{plex_url}/library/onDeck", headers=headers, timeout=5)
        resp.raise_for_status()
        items = resp.json().get("MediaContainer", {}).get("Metadata") or []

        for item in items[:8]:
            key        = item.get("key", "")
            rating_key = item.get("ratingKey", "")
            entry = {
                "type":       item.get("type"),
                "year":       item.get("year"),
                "rating_key": rating_key,
                "plex_link":  _plex_link(plex_public_url, machine_id, key) if key else None,
            }

            if item.get("type") == "episode":
                entry["title"]    = item.get("grandparentTitle", item.get("title"))
                entry["subtitle"] = (
                    f"S{item.get('parentIndex', 0):02d}"
                    f"E{item.get('index', 0):02d}"
                    f" · {item.get('title')}"
                )
                thumb_path = item.get("grandparentThumb") or item.get("thumb", "")
                art_path   = item.get("grandparentArt")   or item.get("art", "")
            else:
                entry["title"]    = item.get("title")
                entry["subtitle"] = str(item.get("year", ""))
                thumb_path        = item.get("thumb", "")
                art_path          = item.get("art", "")

            entry["thumb_url"] = f"{plex_public_url}{thumb_path}?X-Plex-Token={token}" if thumb_path else None
            entry["art_url"]   = f"{plex_public_url}{art_path}?X-Plex-Token={token}"   if art_path   else None

            duration    = item.get("duration",   0)
            view_offset = item.get("viewOffset", 0)
            if duration:
                entry["progress_pct"] = round(view_offset / duration * 100)

            on_deck.append(entry)

    except Exception as e:
        print(f"[Plex] On deck error: {e}", flush=True)

    return {"now_playing": now_playing, "on_deck": on_deck}


def search_plex_item(title: str, year: int | None, item_type: str) -> list:
    """Search Plex library and return formatted results, enriched with Radarr/Sonarr info."""
    cfg = current_app.config
    if not cfg["PLEX_TOKEN"]:
        return []

    headers = {
        "Accept":       "application/json",
        "X-Plex-Token": cfg["PLEX_TOKEN"],
    }
    plex_url        = cfg["PLEX_URL"]
    plex_public_url = f"http://{cfg['HOST']}:32400"
    token           = cfg["PLEX_TOKEN"]

    try:
        machine_id = _get_machine_id(plex_url, headers)

        resp = requests.get(
            f"{plex_url}/search",
            headers=headers,
            params={"query": title, "limit": 8},
            timeout=5,
        )
        resp.raise_for_status()
        results = resp.json().get("MediaContainer", {}).get("Metadata") or []

        # Get Radarr and Sonarr data for enrichment
        radarr_movies = _get_radarr_movies() if cfg.get("RADARR_URL") else {}
        sonarr_series = _get_sonarr_series() if cfg.get("SONARR_URL") else {}

        formatted = []
        for item in results:
            if item_type and item.get("type") != item_type:
                continue
            if year and item.get("year") != year:
                continue

            thumb_path = item.get("thumb", "")
            art_path   = item.get("art", "")
            key        = item.get("key", "")
            item_title = item.get("title", "")
            item_year  = item.get("year")
            item_type_val = item.get("type")

            # Check if in Radarr/Sonarr
            in_radarr = False
            radarr_id = None
            in_sonarr = False
            sonarr_id = None

            if item_type_val == "movie":
                for raid, rmovie in radarr_movies.items():
                    if rmovie["title"].lower() == item_title.lower():
                        in_radarr = True
                        radarr_id = raid
                        break
            else:
                for sid, sseries in sonarr_series.items():
                    if sseries["title"].lower() == item_title.lower():
                        in_sonarr = True
                        sonarr_id = sid
                        break

            entry = {
                "source":     "plex",
                "type":       "movie" if item_type_val == "movie" else "show",
                "title":      item_title,
                "year":       item_year,
                "overview":   item.get("summary", ""),
                "rating":     item.get("rating"),
                "poster_url": f"{plex_public_url}{thumb_path}?X-Plex-Token={token}" if thumb_path else None,
                "fanart_url": f"{plex_public_url}{art_path}?X-Plex-Token={token}" if art_path else None,
                "plex_link":  _plex_link(plex_public_url, machine_id, key) if key else None,
                "in_radarr":  in_radarr,
                "radarr_id":  radarr_id,
                "in_sonarr":  in_sonarr,
                "sonarr_id":  sonarr_id,
            }

            if item_type_val == "show":
                entry["network"] = item.get("network")
                entry["status"]   = item.get("status")

            formatted.append(entry)

        return formatted

    except Exception as e:
        print(f"[Plex] Search error: {e}", flush=True)

    return []


def _get_radarr_movies() -> dict:
    """Get all movies from Radarr as {id: {title, year}}."""
    try:
        resp = requests.get(
            f"{current_app.config['RADARR_URL']}/api/v3/movie",
            headers={"X-Api-Key": current_app.config["RADARR_API_KEY"]},
            timeout=5,
        )
        resp.raise_for_status()
        return {m["id"]: {"title": m["title"], "year": m.get("year")} for m in resp.json()}
    except Exception as e:
        print(f"[Plex] Radarr fetch error: {e}", flush=True)
        return {}


def _get_sonarr_series() -> dict:
    """Get all series from Sonarr as {id: {title, year}}."""
    try:
        resp = requests.get(
            f"{current_app.config['SONARR_URL']}/api/v3/series",
            headers={"X-Api-Key": current_app.config["SONARR_API_KEY"]},
            timeout=5,
        )
        resp.raise_for_status()
        return {s["id"]: {"title": s["title"], "year": s.get("year")} for s in resp.json()}
    except Exception as e:
        print(f"[Plex] Sonarr fetch error: {e}", flush=True)
        return {}

def search_plex_library(query: str) -> list[dict]:
    """Search Plex library and return a list of {title, year, plex_link} for matching."""
    cfg = current_app.config
    if not cfg.get("PLEX_TOKEN"):
        return []

    headers = {
        "Accept":       "application/json",
        "X-Plex-Token": cfg["PLEX_TOKEN"],
    }
    plex_url        = cfg["PLEX_URL"]
    plex_public_url = f"http://{cfg['HOST']}:32400"

    try:
        machine_id = _get_machine_id(plex_url, headers)

        resp = requests.get(
            f"{plex_url}/search",
            headers=headers,
            params={"query": query, "limit": 20},
            timeout=5,
        )
        resp.raise_for_status()
        results = resp.json().get("MediaContainer", {}).get("Metadata") or []

        output = []
        for item in results:
            key  = item.get("key", "")
            # For episodes, match against the show title
            title = (
                item.get("grandparentTitle") 
                if item.get("type") == "episode" 
                else item.get("title", "")
            )
            output.append({
                "title":     title,
                "year":      item.get("year"),
                "type":      item.get("type"),
                "plex_link": _plex_link(plex_public_url, machine_id, key) if key else None,
                "in_plex": True,
                "sources": "plex",
            })
        return output

    except Exception as e:
        print(f"[Plex] Library search error: {e}", flush=True)
        return []