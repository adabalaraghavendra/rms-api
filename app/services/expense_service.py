from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.expense import Expense
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseIn
from app.services.base import BaseService
from app.shared.pagination import Page, PageParams


class ExpenseService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.expenses = ExpenseRepository(db)

    def list_mine(self, actor: User, params: PageParams, month: str | None) -> Page[Expense]:
        return self.expenses.list_page(params, month=month, user_id=actor.id)

    def list_all(self, params: PageParams, month: str | None, user_id: int | None) -> Page[Expense]:
        return self.expenses.list_page(params, month=month, user_id=user_id)

    def create(self, actor: User, data: ExpenseIn) -> Expense:
        expense = Expense(
            user_id=actor.id,
            title=data.title,
            category=data.category,
            amount=data.amount,
            expense_date=data.expenseDate,
            note=data.note,
        )
        self.expenses.add(expense)
        self.commit()
        return expense

    def update(self, actor: User, expense_id: int, data: ExpenseIn) -> Expense:
        expense = self._get_manageable(actor, expense_id)
        expense.title, expense.category = data.title, data.category
        expense.amount, expense.expense_date, expense.note = data.amount, data.expenseDate, data.note
        self.commit()
        return expense

    def delete(self, actor: User, expense_id: int) -> None:
        self.expenses.delete(self._get_manageable(actor, expense_id))
        self.commit()

    def _get_manageable(self, actor: User, expense_id: int) -> Expense:
        """Owners manage their own expenses; the admin can manage any."""
        expense = self.expenses.get(expense_id)
        if not expense or (not actor.is_admin and expense.user_id != actor.id):
            raise NotFoundError("Expense not found")
        return expense
