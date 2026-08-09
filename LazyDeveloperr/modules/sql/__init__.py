from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from LazyDeveloperr import DB_URI
from LazyDeveloperr import LOGGER as log

if not DB_URI or "elephantsql.com" in DB_URI:
    log.warning("[SQL] ElephantSQL / Invalid DATABASE_URL detected. Falling back to local SQLite database.")
    DB_URI = "sqlite:///lazydeveloperr.db"
elif DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)


def start() -> scoped_session:
    if DB_URI.startswith("sqlite"):
        engine = create_engine(DB_URI)
    else:
        engine = create_engine(DB_URI, client_encoding="utf8", pool_pre_ping=True, pool_recycle=300)
    log.info("[Database] Connecting to database...")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
try:
    SESSION = start()
except Exception as e:
    log.exception(f"[Database] Failed to connect due to {e}")
    exit()

log.info("[Database] Connection successful, session started.")
