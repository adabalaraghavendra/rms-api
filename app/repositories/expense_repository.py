from bson import ObjectId
from pymongo.database import Database

from app.models.expense import Expense
from app.repositories.base import BaseRepository
from app.repositories.user_repository import UserRepository
from app.shared.dates import month_bounds
from app.shared.object_id import require_object_id
from app.shared.pagination import Page, PageParams


class ExpenseRepository(BaseRepository[Expense]):
    model = Expense

    def __init__(self, db: Database):
        super().__init__(db)
        self._users = UserRepository(db)

    def _attach_user_names(self, expenses: list[Expense]) -> None:
        names = self._users.names_by_id({e.user_id for e in expenses})
        for e in expenses:
            e.user_name = names.get(e.user_id, "")

    def get(self, entity_id: str) -> Expense | None:
        expense = super().get(entity_id)
        if expense:
            self._attach_user_names([expense])
        return expense

    def list_page(
        self, params: PageParams, *, month: str | None = None, user_id: str | None = None
    ) -> Page[Expense]:
        """Newest first, optionally limited to one person and/or one month."""
        query: dict = {}
        if user_id:
            query["user_id"] = require_object_id(user_id, "userId")
        if month:
            start, end = month_bounds(month)
            query["expense_date"] = {"$gte": start.isoformat(), "$lt": end.isoformat()}
        page = self.paginate(query, [("expense_date", -1), ("_id", -1)], params)
        self._attach_user_names(page.items)
        return page

    def delete_by_user(self, user_id: str) -> int:
        return self.collection.delete_many({"user_id": ObjectId(user_id)}).deleted_count
