from app.models.user import User
from app.schemas.expense import ExpenseIn, ExpenseOut
from app.services.expense_service import ExpenseService
from app.shared.pagination import PageParams
from app.shared.response import ApiResponse


class ExpenseController:
    def __init__(self, service: ExpenseService):
        self.service = service

    def list_mine(self, actor: User, params: PageParams, month: str | None) -> ApiResponse:
        page = self.service.list_mine(actor, params, month).map(ExpenseOut.model_validate)
        return ApiResponse.paginated(page, "Expenses fetched")

    def list_all(self, params: PageParams, month: str | None, user_id: str | None) -> ApiResponse:
        page = self.service.list_all(params, month, user_id).map(ExpenseOut.model_validate)
        return ApiResponse.paginated(page, "Expenses fetched")

    def create(self, actor: User, body: ExpenseIn) -> ApiResponse:
        expense = self.service.create(actor, body)
        return ApiResponse.success(ExpenseOut.model_validate(expense), "Expense added")

    def update(self, actor: User, expense_id: str, body: ExpenseIn) -> ApiResponse:
        expense = self.service.update(actor, expense_id, body)
        return ApiResponse.success(ExpenseOut.model_validate(expense), "Expense updated")

    def delete(self, actor: User, expense_id: str) -> ApiResponse:
        self.service.delete(actor, expense_id)
        return ApiResponse.success(message="Expense deleted")
