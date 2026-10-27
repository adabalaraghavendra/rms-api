import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
# Comma-separated list, e.g. "http://localhost:5173,https://rms.example.com" (no trailing slash)
CLIENT_ORIGINS = [o.strip().rstrip("/") for o in os.getenv("CLIENT_ORIGIN").split(",") if o.strip()]

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set (see .env.example)")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set (see .env.example)")
