"""One-time setup: create the tables on Neon and seed the room + first admin.

Run from the backend folder:  python -m scripts.init_db
"""
from pathlib import Path

import os

import psycopg

from app.core.config import DATABASE_URL  # also loads .env
from app.core.security import hash_password

SCHEMA = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"


def main() -> None:
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(SCHEMA.read_text())
        print("Schema ready.")

        row = conn.execute("SELECT id FROM rooms LIMIT 1").fetchone()
        room_id = row[0] if row else conn.execute(
            "INSERT INTO rooms(name) VALUES (%s) RETURNING id", (os.getenv("ROOM_NAME", "My Room"),)
        ).fetchone()[0]

        email = os.getenv("ADMIN_EMAIL", "admin@example.com").lower()
        conn.execute(
            """INSERT INTO users(room_id, name, email, password_hash, role) VALUES (%s, %s, %s, %s, 'admin')
               ON CONFLICT (email) DO NOTHING""",
            (room_id, os.getenv("ADMIN_NAME", "Admin"), email, hash_password(os.getenv("ADMIN_PASSWORD", "Admin@123"))),
        )
        print(f"Admin available: {email}")


if __name__ == "__main__":
    main()
