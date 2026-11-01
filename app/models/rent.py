import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from bson import ObjectId

from app.models.base import Document, utcnow


class RentMode(str, enum.Enum):
    EQUAL = "equal"    # divided equally between the people who pay
    CUSTOM = "custom"  # admin types each person's amount


@dataclass(kw_only=True)
class RentShare:
    """One payer's portion of a month's rent (stored inside the RentSplit document)."""

    user_id: str
    amount: float
    name: str = ""  # not stored: filled in by the repository

    @classmethod
    def from_mongo(cls, doc: dict) -> "RentShare":
        return cls(user_id=str(doc["user_id"]), amount=float(doc["amount"]))

    def to_mongo(self) -> dict:
        return {"user_id": ObjectId(self.user_id), "amount": round(self.amount, 2)}


@dataclass(kw_only=True)
class RentSplit(Document):
    """The month's rent and how it was divided. One document per month, shares embedded.  Collection: rent_splits"""

    collection: ClassVar[str] = "rent_splits"

    month: str  # 'YYYY-MM'
    total_rent: float
    mode: str
    shares: list[RentShare] = field(default_factory=list)
    created_at: datetime = field(default_factory=utcnow)

    @classmethod
    def from_mongo(cls, doc: dict) -> "RentSplit":
        return cls(
            id=str(doc["_id"]),
            month=doc["month"],
            total_rent=float(doc["total_rent"]),
            mode=doc["mode"],
            shares=[RentShare.from_mongo(s) for s in doc.get("shares", [])],
            created_at=doc["created_at"],
        )

    def to_mongo(self) -> dict:
        return {
            "month": self.month,
            "total_rent": round(self.total_rent, 2),
            "mode": self.mode,
            "shares": [s.to_mongo() for s in self.shares],
            "created_at": self.created_at,
        }
