import re
from datetime import date, datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import JWT_SECRET

_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user: dict) -> str:
    payload = {
        "id": user["id"],
        "role": user["role"],
        "roomId": user["room_id"],
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict:
    if not creds:
        raise HTTPException(401, "Authentication required")
    try:
        return jwt.decode(creds.credentials, JWT_SECRET, algorithms=["HS256"])  # {id, role, roomId}
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")


def admin_only(user: dict = Depends(current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(403, "Admin access required")
    return user


def valid_month(month: str | None) -> str:
    """Return month (default: current) or raise 400 if not YYYY-MM."""
    month = month or date.today().strftime("%Y-%m")
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise HTTPException(400, "month must be YYYY-MM")
    return month
