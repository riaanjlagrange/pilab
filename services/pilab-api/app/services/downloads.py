import requests
from flask import current_app

from .utils import format_eta


def _qbit_session():
    """Authenticate with qBittorrent and return an active session."""
    cfg  = current_app.config
    sess = requests.Session()
    resp = sess.post(
        f"{cfg['QBITTORRENT_URL']}/api/v2/auth/login",
        data={
            "username": cfg["QBITTORRENT_USER"],
            "password": cfg["QBITTORRENT_PASS"],
        },
        timeout=10,
    )
    if resp.status_code == 403:
        raise PermissionError(
            f"[qBittorrent] Login forbidden — check credentials. "
            f"Response: {resp.text}"
        )
    resp.raise_for_status()
    return sess


def _fetch_torrents():
    """Return raw torrent list from qBittorrent."""
    cfg  = current_app.config
    sess = _qbit_session()
    resp = sess.get(
        f"{cfg['QBITTORRENT_URL']}/api/v2/torrents/info",
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_downloads():
    """Return only actively downloading torrents."""
    try:
        torrents  = _fetch_torrents()
        downloads = []
        for t in torrents:
            if t.get("state") not in ("downloading", "metaDL", "forcedDL"):
                continue
            downloads.append({
                "id":       t.get("hash"),
                "name":     t.get("name"),
                "status":   t.get("state"),
                "progress": round(t.get("progress", 0) * 100, 1),
                "speed_mb": round(t.get("dlspeed", 0) / 1e6, 1),
                "eta":      format_eta(t.get("eta", -1)),
                "size_gb":  round(t.get("size", 0) / 1e9, 2),
            })
        print(f"[qBittorrent] {len(downloads)} active downloads", flush=True)
        return downloads
    except Exception as e:
        print(f"[qBittorrent] get_downloads failed: {e}", flush=True)
        return []


def get_queue():
    """Return all torrents categorised as movies or series."""
    queue_data = {"movies": [], "series": []}
    try:
        torrents = _fetch_torrents()
        print(f"[qBittorrent] {len(torrents)} torrents in queue", flush=True)

        for t in torrents:
            size      = t.get("size", 0)
            completed = t.get("completed", 0)
            progress  = round((completed / size * 100) if size > 0 else 0, 1)
            category  = (t.get("category") or "").lower()
            tags      = (t.get("tags")     or "").lower()

            item = {
                "id":           t.get("hash"),
                "title":        t.get("name"),
                "status":       t.get("state", "unknown"),
                "progress":     progress,
                "speed_mb":     round(t.get("dlspeed", 0) / 1e6, 1),
                "eta":          format_eta(t.get("eta", -1)),
                "size_gb":      round(size      / 1e9, 2),
                "completed_gb": round(completed / 1e9, 2),
                "seeds":        t.get("num_seeds",  0),
                "peers":        t.get("num_leechs", 0),
                "added_on":     t.get("added_on"),
                "category":     t.get("category", ""),
                "tags":         t.get("tags",     ""),
            }

            is_movie  = any(k in category or k in tags for k in ("radarr", "movie"))
            is_series = any(k in category or k in tags for k in ("sonarr", "tv", "series"))

            if is_movie:
                queue_data["movies"].append(item)
            elif is_series:
                queue_data["series"].append(item)
            else:
                print(
                    f"[qBittorrent] Uncategorised: {t.get('name')} "
                    f"(category='{category}', tags='{tags}')",
                    flush=True,
                )

    except Exception as e:
        print(f"[qBittorrent] get_queue failed: {e}", flush=True)

    return queue_data