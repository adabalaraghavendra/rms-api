from fastapi import APIRouter, Depends, Query

from app.controllers.expense_controller import ExpenseController
from app.dependencies import current_user, get_expense_controller, require_admin
from app.models.user import User
from app.schemas.expense import ExpenseIn, ExpenseOut
from app.shared.dates import month_query
from app.shared.pagination import PageParams, get_page_params
from app.shared.response import ApiResponse

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/mine", response_model=ApiResponse[list[ExpenseOut]])
def list_my_expenses(
    params: PageParams = Depends(get_page_params),
    month: str | None = Depends(month_query),
    user: User = Depends(current_user),
    ctrl: ExpenseController = Depends(get_expense_controller),
):
    return ctrl.list_mine(user, params, month)


@router.get("", response_model=ApiResponse[list[ExpenseOut]], dependencies=[Depends(require_admin)])
def list_all_expenses(
    params: PageParams = Depends(get_page_params),
    month: str | None = Depends(month_query),
    userId: str | None = Query(None, description="Only this member's expenses (user id)"),
    ctrl: ExpenseController = Depends(get_expense_controller),
):
    return ctrl.list_all(params, month, userId)


@router.post("", response_model=ApiResponse[ExpenseOut], status_code=201)
def create_expense(
    body: ExpenseIn, user: User = Depends(current_user), ctrl: ExpenseController = Depends(get_expense_controller)
):
    return ctrl.create(user, body)


@router.put("/{expense_id}", response_model=ApiResponse[ExpenseOut])
def update_expense(
    expense_id: str, body: ExpenseIn, user: User = Depends(current_user),
    ctrl: ExpenseController = Depends(get_expense_controller),
):
    return ctrl.update(user, expense_id, body)


@router.delete("/{expense_id}", response_model=ApiResponse[None])
def delete_expense(
    expense_id: str, user: User = Depends(current_user), ctrl: ExpenseController = Depends(get_expense_controller)
):
    return ctrl.delete(user, expense_id)
