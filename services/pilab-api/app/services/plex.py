import requests
from flask import current_app


def get_plex():
    """Fetch active Plex sessions and on-deck items."""
    cfg = current_app.config
    if not cfg["PLEX_TOKEN"]:
        return {"now_playing": [], "on_deck": []}

    headers = {
        "Accept":       "application/json",
        "X-Plex-Token": cfg["PLEX_TOKEN"],
    }
    plex_url    = cfg["PLEX_URL"]
    now_playing = []
    on_deck     = []

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
            entry = {
                "type": item.get("type"),
                "year": item.get("year"),
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

            duration    = item.get("duration",   0)
            view_offset = item.get("viewOffset", 0)
            if duration:
                entry["progress_pct"] = round(view_offset / duration * 100)
            on_deck.append(entry)

    except Exception as e:
        print(f"[Plex] On deck error: {e}", flush=True)

    return {"now_playing": now_playing, "on_deck": on_deck}