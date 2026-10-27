"""SQLAlchemy engine, session factory and declarative Base."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

# Neon drops idle connections and suspends the database when unused:
# pool_pre_ping tests a connection before use, pool_recycle retires old ones.
engine = create_engine(
    get_settings().database_url,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "connect_timeout": 15,  # a suspended Neon database needs a moment to wake up
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 3,
    },
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent of every ORM model (its metadata is what Alembic compares against)."""


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one session per request. Services own the commit;
    anything uncommitted is rolled back when the session closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
