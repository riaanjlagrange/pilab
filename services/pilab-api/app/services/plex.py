import requests
from urllib.parse import quote
from flask import current_app


# ── Helpers ───────────────────────────────────────────────────────────────────

def _plex_headers(token: str) -> dict:
    return {"Accept": "application/json", "X-Plex-Token": token}


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


def _thumb(plex_public_url: str, path: str | None, token: str) -> str | None:
    if not path:
        return None
    return f"{plex_public_url}{path}?X-Plex-Token={token}"


def _get_config():
    cfg = current_app.config
    return (
        cfg,
        cfg["PLEX_URL"],
        f"http://{cfg['HOST']}:32400",
        cfg["PLEX_TOKEN"],
        _plex_headers(cfg["PLEX_TOKEN"]),
    )


# ── Public API ────────────────────────────────────────────────────────────────

def get_plex_library() -> dict:
    """
    Return all movies and series in the Plex library, plus continueWatching
    (on-deck items with a viewOffset — i.e. partially watched).

    Shape: { all, movies, series, continueWatching }
    Each item matches MediaItem.
    """
    cfg, plex_url, plex_public_url, token, headers = _get_config()
    if not token:
        return {"all": [], "movies": [], "series": [], "continueWatching": []}

    machine_id = _get_machine_id(plex_url, headers)
    all_items: list[dict] = []
    continue_watching: list[dict] = []

    # ── On-deck (partially watched) ───────────────────────────────────────
    try:
        resp = requests.get(f"{plex_url}/library/onDeck", headers=headers, timeout=5)
        resp.raise_for_status()
        deck = resp.json().get("MediaContainer", {}).get("Metadata") or []

        for item in deck:
            key        = item.get("key", "")
            rating_key = item.get("ratingKey", "")
            duration   = item.get("duration", 0)
            view_offset = item.get("viewOffset", 0)

            if item.get("type") == "episode":
                title      = item.get("grandparentTitle", item.get("title"))
                subtitle   = (
                    f"S{item.get('parentIndex', 0):02d}"
                    f"E{item.get('index', 0):02d}"
                    f" · {item.get('title')}"
                )
                thumb_path = item.get("grandparentThumb") or item.get("thumb", "")
                art_path   = item.get("grandparentArt")   or item.get("art", "")
                media_type = "episode"
            else:
                title      = item.get("title")
                subtitle   = str(item.get("year", ""))
                thumb_path = item.get("thumb", "")
                art_path   = item.get("art", "")
                media_type = item.get("type", "movie")

            entry = {
                "type":         media_type,
                "title":        title,
                "subtitle":     subtitle,
                "year":         item.get("year"),
                "rating_key":   rating_key,
                "key":          key,
                "thumb_url":    _thumb(plex_public_url, thumb_path, token),
                "art_url":      _thumb(plex_public_url, art_path, token),
                "plex_link":    _plex_link(plex_public_url, machine_id, key) if key else "",
                "progress_pct": round(view_offset / duration * 100) if duration else None,
            }
            continue_watching.append(entry)
    except Exception as e:
        print(f"[Plex] on-deck error: {e}", flush=True)

    # ── Full library sections ─────────────────────────────────────────────
    try:
        resp = requests.get(f"{plex_url}/library/sections", headers=headers, timeout=5)
        resp.raise_for_status()
        sections = resp.json().get("MediaContainer", {}).get("Directory") or []

        for section in sections:
            section_key  = section.get("key")
            section_type = section.get("type")  # "movie" or "show"
            if section_type not in ("movie", "show"):
                continue

            lib_resp = requests.get(
                f"{plex_url}/library/sections/{section_key}/all",
                headers=headers,
                timeout=15,
            )
            lib_resp.raise_for_status()
            items = lib_resp.json().get("MediaContainer", {}).get("Metadata") or []

            for item in items:
                key        = item.get("key", "")
                rating_key = item.get("ratingKey", "")
                thumb_path = item.get("thumb", "")
                art_path   = item.get("art", "")
                view_offset = item.get("viewOffset", 0)
                duration    = item.get("duration", 0)

                if section_type == "show":
                    subtitle   = f"{item.get('childCount', 0)} season{'s' if item.get('childCount', 0) != 1 else ''}"
                    media_type = "show"
                else:
                    subtitle   = str(item.get("year", ""))
                    media_type = "movie"

                entry = {
                    "type":         media_type,
                    "title":        item.get("title", ""),
                    "subtitle":     subtitle,
                    "year":         item.get("year"),
                    "rating_key":   rating_key,
                    "key":          key,
                    "thumb_url":    _thumb(plex_public_url, thumb_path, token),
                    "art_url":      _thumb(plex_public_url, art_path, token),
                    "plex_link":    _plex_link(plex_public_url, machine_id, key) if key else "",
                    "progress_pct": round(view_offset / duration * 100) if duration else None,
                }
                all_items.append(entry)

    except Exception as e:
        print(f"[Plex] library error: {e}", flush=True)

    movies = [i for i in all_items if i["type"] == "movie"]
    series = [i for i in all_items if i["type"] == "show"]

    return {
        "all":             all_items,
        "movies":          movies,
        "series":          series,
        "continueWatching": continue_watching,
    }


def get_plex_active() -> list[dict]:
    """
    Return currently active Plex sessions.
    Each item has user, state, progress, and media info.
    """
    cfg, plex_url, plex_public_url, token, headers = _get_config()
    if not token:
        return []

    machine_id  = _get_machine_id(plex_url, headers)
    now_playing = []

    try:
        resp  = requests.get(f"{plex_url}/status/sessions", headers=headers, timeout=5)
        resp.raise_for_status()
        items = resp.json().get("MediaContainer", {}).get("Metadata") or []

        for item in items:
            key        = item.get("key", "")
            duration   = item.get("duration", 0)
            view_offset = item.get("viewOffset", 0)

            if item.get("type") == "episode":
                title      = item.get("grandparentTitle", item.get("title"))
                subtitle   = (
                    f"S{item.get('parentIndex', 0):02d}"
                    f"E{item.get('index', 0):02d}"
                    f" · {item.get('title')}"
                )
                thumb_path = item.get("grandparentThumb") or item.get("thumb", "")
                media_type = "episode"
            else:
                title      = item.get("title", "")
                subtitle   = str(item.get("year", ""))
                thumb_path = item.get("thumb", "")
                media_type = item.get("type", "movie")

            now_playing.append({
                "type":         media_type,
                "title":        title,
                "subtitle":     subtitle,
                "year":         item.get("year"),
                "rating_key":   item.get("ratingKey", ""),
                "key":          key,
                "thumb_url":    _thumb(plex_public_url, thumb_path, token),
                "art_url":      None,
                "plex_link":    _plex_link(plex_public_url, machine_id, key) if key else "",
                "progress_pct": round(view_offset / duration * 100) if duration else None,
                # session-specific extras
                "user":  item.get("User", {}).get("title", ""),
                "state": item.get("Player", {}).get("state", "playing"),
            })

    except Exception as e:
        print(f"[Plex] sessions error: {e}", flush=True)

    return now_playing


def search_plex(query: str) -> list[dict]:
    """
    Search the Plex library. Returns results shaped as SearchResult.
    """
    cfg, plex_url, plex_public_url, token, headers = _get_config()
    if not token:
        return []

    machine_id = _get_machine_id(plex_url, headers)

    try:
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
            key        = item.get("key", "")
            thumb_path = item.get("thumb", "")
            art_path   = item.get("art", "")
            item_type  = item.get("type", "")

            # For episodes, surface the show title instead
            title = (
                item.get("grandparentTitle")
                if item_type == "episode"
                else item.get("title", "")
            )

            output.append({
                "source":      "plex",
                "type":        "show" if item_type in ("show", "episode") else "movie",
                "title":       title,
                "year":        item.get("year"),
                "overview":    item.get("summary", ""),
                "rating":      item.get("rating"),
                "poster_url":  _thumb(plex_public_url, thumb_path, token),
                "fanart_url":  _thumb(plex_public_url, art_path, token),
                "plex_link":   _plex_link(plex_public_url, machine_id, key) if key else None,
                "in_plex":     True,
                "in_radarr":   False,
                "in_sonarr":   False,
            })

        return output

    except Exception as e:
        print(f"[Plex] search error: {e}", flush=True)
        return []


def get_plex_links_for_titles(titles: list[str]) -> dict[str, str]:
    """
    Helper used by Radarr/Sonarr search enrichment.
    Returns { normalized_title: plex_link } for any title that exists in Plex.
    """
    cfg, plex_url, plex_public_url, token, headers = _get_config()
    if not token or not titles:
        return {}

    machine_id = _get_machine_id(plex_url, headers)
    link_map: dict[str, str] = {}

    for title in titles:
        try:
            resp = requests.get(
                f"{plex_url}/search",
                headers=headers,
                params={"query": title, "limit": 5},
                timeout=5,
            )
            resp.raise_for_status()
            results = resp.json().get("MediaContainer", {}).get("Metadata") or []
            for item in results:
                item_title = (
                    item.get("grandparentTitle")
                    if item.get("type") == "episode"
                    else item.get("title", "")
                )
                if item_title.lower() == title.lower():
                    key = item.get("key", "")
                    if key:
                        link_map[title.lower()] = _plex_link(plex_public_url, machine_id, key)
                    break
        except Exception:
            pass

    return link_map