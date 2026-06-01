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


def search_plex_item(title: str, year: int | None, item_type: str) -> str | None:
    """Search Plex for an item and return a deep link if found."""
    cfg = current_app.config
    if not cfg["PLEX_TOKEN"]:
        return None

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
            params={"query": title, "limit": 5},
            timeout=5,
        )
        resp.raise_for_status()
        results = resp.json().get("MediaContainer", {}).get("Metadata") or []

        for item in results:
            if item.get("type") != item_type:
                continue
            if year and item.get("year") != year:
                continue
            return _plex_link(plex_public_url, machine_id, item.get("key", ""))

    except Exception as e:
        print(f"[Plex] Search error: {e}", flush=True)

    return None