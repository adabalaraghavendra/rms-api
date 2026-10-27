"""Create the first admin from .env (ADMIN_NAME / ADMIN_EMAIL / ADMIN_PASSWORD).

Run after the tables exist (alembic upgrade head):  python -m scripts.seed_admin
Does nothing if that email already exists.
"""
import os

from app.core.database import SessionLocal
from app.core.security import PasswordHasher
from app.models.user import Role, User
from app.repositories.user_repository import UserRepository


def main() -> None:
    email = os.getenv("ADMIN_EMAIL", "admin@example.com").strip().lower()
    with SessionLocal() as db:
        users = UserRepository(db)
        if users.get_by_email(email):
            print(f"Admin already exists: {email}")
            return
        users.add(User(
            name=os.getenv("ADMIN_NAME", "Admin"),
            email=email,
            password_hash=PasswordHasher().hash(os.getenv("ADMIN_PASSWORD", "Admin@123")),
            role=Role.ADMIN.value,
        ))
        db.commit()
        print(f"Admin created: {email}")


if __name__ == "__main__":
    main()
