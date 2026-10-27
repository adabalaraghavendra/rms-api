from fastapi import APIRouter, Depends

from app.controllers.summary_controller import SummaryController
from app.dependencies import current_user, get_summary_controller, require_admin
from app.models.user import User
from app.schemas.summary import AdminSummary, MySummary
from app.shared.dates import month_query
from app.shared.response import ApiResponse

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("/mine", response_model=ApiResponse[MySummary])
def my_summary(
    month: str | None = Depends(month_query),
    user: User = Depends(current_user),
    ctrl: SummaryController = Depends(get_summary_controller),
):
    return ctrl.my_summary(user, month)


@router.get("", response_model=ApiResponse[AdminSummary], dependencies=[Depends(require_admin)])
def admin_summary(
    month: str | None = Depends(month_query), ctrl: SummaryController = Depends(get_summary_controller)
):
    return ctrl.admin_summary(month)
