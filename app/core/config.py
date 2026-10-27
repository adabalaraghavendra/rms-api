"""Application settings, read once from environment variables (.env)."""
import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _driver_url(url: str) -> str:
    """Point a plain postgres URL at SQLAlchemy's psycopg (v3) driver."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


@dataclass(frozen=True)
class Settings:
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    token_ttl_days: int = 7
    client_origins: tuple[str, ...] = ("http://localhost:5173",)

    @classmethod
    def from_env(cls) -> "Settings":
        database_url = os.getenv("DATABASE_URL")
        jwt_secret = os.getenv("JWT_SECRET")
        if not database_url:
            raise RuntimeError("DATABASE_URL is not set (see .env.example)")
        if not jwt_secret:
            raise RuntimeError("JWT_SECRET is not set (see .env.example)")
        # Comma-separated, no trailing slash: "http://localhost:5173,https://rms.example.com"
        origins = tuple(
            o.strip().rstrip("/")
            for o in os.getenv("CLIENT_ORIGIN", "http://localhost:5173").split(",")
            if o.strip()
        )
        return cls(database_url=_driver_url(database_url), jwt_secret=jwt_secret, client_origins=origins)


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
