from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.expense import Expense
from app.repositories.base import BaseRepository
from app.shared.dates import month_bounds
from app.shared.pagination import Page, PageParams


class ExpenseRepository(BaseRepository[Expense]):
    model = Expense

    def list_page(
        self, params: PageParams, *, month: str | None = None, user_id: int | None = None
    ) -> Page[Expense]:
        """Newest first, optionally limited to one person and/or one month."""
        stmt = (
            select(Expense)
            .options(joinedload(Expense.user))
            .order_by(Expense.expense_date.desc(), Expense.id.desc())
        )
        if user_id is not None:
            stmt = stmt.where(Expense.user_id == user_id)
        if month:
            start, end = month_bounds(month)
            stmt = stmt.where(Expense.expense_date >= start, Expense.expense_date < end)
        return self.paginate(stmt, params)
