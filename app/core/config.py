import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
CLIENT_ORIGINS = [o.strip() for o in os.getenv("CLIENT_ORIGIN", "http://localhost:5173").split(",")]

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set (see .env.example)")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set (see .env.example)")
