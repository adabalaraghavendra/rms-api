import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from app.models.base import Document, utcnow


class Role(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


@dataclass(kw_only=True)
class User(Document):
    """A person living in the room. The admin is a member too.  Collection: users"""

    collection: ClassVar[str] = "users"

    name: str
    email: str
    password_hash: str
    role: str = Role.USER.value
    is_active: bool = True
    created_at: datetime = field(default_factory=utcnow)

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN.value

    @classmethod
    def from_mongo(cls, doc: dict) -> "User":
        return cls(
            id=str(doc["_id"]),
            name=doc["name"],
            email=doc["email"],
            password_hash=doc["password_hash"],
            role=doc.get("role", Role.USER.value),
            is_active=doc.get("is_active", True),
            created_at=doc["created_at"],
        )

    def to_mongo(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }
