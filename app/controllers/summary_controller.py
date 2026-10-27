from app.models.user import User
from app.services.summary_service import SummaryService
from app.shared.response import ApiResponse


class SummaryController:
    def __init__(self, service: SummaryService):
        self.service = service

    def admin_summary(self, month: str | None) -> ApiResponse:
        return ApiResponse.success(self.service.admin_summary(month), "Summary fetched")

    def my_summary(self, actor: User, month: str | None) -> ApiResponse:
        return ApiResponse.success(self.service.my_summary(actor, month), "Summary fetched")
