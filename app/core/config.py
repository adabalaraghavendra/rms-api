"""Application settings, read once from environment variables (.env)."""
import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str
    mongodb_db: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    token_ttl_days: int = 7
    client_origins: tuple[str, ...] = ("http://localhost:5173",)

    @classmethod
    def from_env(cls) -> "Settings":
        mongodb_uri = os.getenv("MONGODB_URI")
        jwt_secret = os.getenv("JWT_SECRET")
        if not mongodb_uri:
            raise RuntimeError("MONGODB_URI is not set (see .env.example)")
        if not jwt_secret:
            raise RuntimeError("JWT_SECRET is not set (see .env.example)")
        # Comma-separated, no trailing slash: "http://localhost:5173,https://rms.example.com"
        origins = tuple(
            o.strip().rstrip("/")
            for o in os.getenv("CLIENT_ORIGIN", "http://localhost:5173").split(",")
            if o.strip()
        )
        return cls(
            mongodb_uri=mongodb_uri,
            mongodb_db=os.getenv("MONGODB_DB", "room_management"),
            jwt_secret=jwt_secret,
            client_origins=origins,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
