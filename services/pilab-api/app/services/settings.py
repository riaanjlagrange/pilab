from flask import current_app
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from ..database import settings_table
from sqlalchemy import func


def _default_settings():
    cfg = current_app.config
    return {
        "pilabName":            cfg["PILAB_NAME"],
        "diskThreshold":        85,
        "checkIntervalMinutes": cfg["CHECK_INTERVAL_MINUTES"],
        "hiddenContainers":     list(cfg["HIDDEN_CONTAINERS"]),
        "ntfyTopic":            cfg["NTFY_TOPIC"],
    }


def get_settings():
    """Load settings from DB, merged over defaults.

    If the DB is unavailable, returns defaults silently.
    """
    settings = _default_settings()
    engine   = current_app.extensions.get("db_engine")
    if not engine:
        return settings

    try:
        with engine.begin() as conn:
            # Seed row 1 with defaults if it doesn't exist yet
            conn.execute(
                pg_insert(settings_table)
                .values(id=1, data=settings)
                .on_conflict_do_nothing(index_elements=[settings_table.c.id])
            )
            row = conn.execute(
                select(settings_table.c.data).where(settings_table.c.id == 1)
            ).scalar_one_or_none()
            if isinstance(row, dict):
                settings.update(row)
    except Exception as e:
        print(f"[Settings] Error reading settings: {e}", flush=True)

    return settings


def save_settings(new_settings):
    """Merge new_settings over current settings and persist to DB.

    Returns True on success, False on failure.
    """
    engine = current_app.extensions.get("db_engine")
    if not engine:
        print("[Settings] Database unavailable", flush=True)
        return False

    merged = _default_settings()
    merged.update(get_settings())
    merged.update(new_settings)

    try:
        with engine.begin() as conn:
            conn.execute(
                pg_insert(settings_table)
                .values(id=1, data=merged)
                .on_conflict_do_update(
                    index_elements=[settings_table.c.id],
                    set_={"data": merged, "updated_at": func.now()},
                )
            )
        return True
    except Exception as e:
        print(f"[Settings] Error saving settings: {e}", flush=True)
        return False