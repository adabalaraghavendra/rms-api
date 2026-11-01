"""Password hashing and login tokens."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import Settings
from app.core.exceptions import UnauthorizedError


class PasswordHasher:
    """bcrypt wrapper (bcrypt only looks at the first 72 bytes)."""

    @staticmethod
    def _raw(password: str) -> bytes:
        return password.encode()[:72]

    def hash(self, password: str) -> str:
        return bcrypt.hashpw(self._raw(password), bcrypt.gensalt()).decode()

    def verify(self, password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(self._raw(password), hashed.encode())
        except ValueError:
            return False


class TokenService:
    """Creates and verifies signed JWT login tokens."""

    def __init__(self, settings: Settings):
        self._secret = settings.jwt_secret
        self._algorithm = settings.jwt_algorithm
        self._ttl = timedelta(days=settings.token_ttl_days)

    def create(self, user_id: str) -> str:
        payload = {"sub": str(user_id), "exp": datetime.now(timezone.utc) + self._ttl}
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def read_user_id(self, token: str) -> str:
        try:
            return str(jwt.decode(token, self._secret, algorithms=[self._algorithm])["sub"])
        except (jwt.PyJWTError, KeyError):
            raise UnauthorizedError("Invalid or expired token")
