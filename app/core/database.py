"""MongoDB connection (PyMongo). One client per process; it manages its own connection pool."""
from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import get_settings


@lru_cache
def get_client() -> MongoClient:
    return MongoClient(
        get_settings().mongodb_uri,
        tz_aware=True,                    # datetimes come back timezone-aware (UTC)
        maxPoolSize=10,
        serverSelectionTimeoutMS=10_000,  # fail fast with a clear error if the server is unreachable
    )


def get_database() -> Database:
    return get_client()[get_settings().mongodb_db]


def get_db() -> Database:
    """FastAPI dependency: the database handed to repositories."""
    return get_database()


def ping() -> None:
    """Raises if MongoDB cannot be reached."""
    get_client().admin.command("ping")


def close_client() -> None:
    if get_client.cache_info().currsize:
        get_client().close()
        get_client.cache_clear()
