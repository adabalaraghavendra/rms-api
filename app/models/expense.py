from dataclasses import dataclass, field
from datetime import date, datetime
from typing import ClassVar

from bson import ObjectId

from app.models.base import Document, utcnow


@dataclass(kw_only=True)
class Expense(Document):
    """Money one person spent on room maintenance.  Collection: expenses

    expense_date is stored as 'YYYY-MM-DD' text, which sorts and range-filters correctly.
    """

    collection: ClassVar[str] = "expenses"

    user_id: str
    title: str
    amount: float
    expense_date: date
    category: str = "Other"
    note: str | None = None
    created_at: datetime = field(default_factory=utcnow)
    user_name: str = ""  # not stored: filled in by the repository from the users collection

    @classmethod
    def from_mongo(cls, doc: dict) -> "Expense":
        return cls(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            title=doc["title"],
            category=doc.get("category", "Other"),
            amount=float(doc["amount"]),
            expense_date=date.fromisoformat(doc["expense_date"]),
            note=doc.get("note"),
            created_at=doc["created_at"],
        )

    def to_mongo(self) -> dict:
        return {
            "user_id": ObjectId(self.user_id),
            "title": self.title,
            "category": self.category,
            "amount": round(self.amount, 2),
            "expense_date": self.expense_date.isoformat(),
            "note": self.note,
            "created_at": self.created_at,
        }
