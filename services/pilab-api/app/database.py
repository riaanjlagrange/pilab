from sqlalchemy import Column, DateTime, Integer, JSON, MetaData, Table, create_engine, func

metadata = MetaData()

settings_table = Table(
    "settings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("data", JSON, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    ),
)

# Populated by init_db() — accessed via current_app.extensions["db_engine"]
db_engine = None


def init_db(app):
    """Create the SQLAlchemy engine and ensure tables exist.

    Stores the engine on app.extensions so services can reach it via
    current_app.extensions["db_engine"] without circular imports.
    """
    global db_engine
    database_url = app.config["DATABASE_URL"]
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        metadata.create_all(engine)
        app.extensions["db_engine"] = engine
        db_engine = engine
        print("[Database] Connected and tables verified", flush=True)
    except Exception as e:
        print(f"[Database] Could not connect: {e}", flush=True)
        app.extensions["db_engine"] = None