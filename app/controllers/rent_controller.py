from app.models.rent import RentSplit
from app.models.user import User
from app.schemas.rent import MyRentOut, RentSplitIn, RentSplitOut, RentSplitView, ShareOut
from app.services.rent_service import RentService
from app.shared.dates import current_month
from app.shared.response import ApiResponse


class RentController:
    def __init__(self, service: RentService):
        self.service = service

    @staticmethod
    def _view(month: str, split: RentSplit | None) -> RentSplitView:
        if split is None:
            return RentSplitView(month=month, split=None)
        shares = [ShareOut.model_validate(s) for s in split.shares]
        return RentSplitView(
            month=month, split=RentSplitOut(totalRent=split.total_rent, mode=split.mode, shares=shares)
        )

    def get_split(self, month: str | None) -> ApiResponse:
        month = month or current_month()
        return ApiResponse.success(self._view(month, self.service.get_split(month)), "Rent split fetched")

    def save_split(self, body: RentSplitIn) -> ApiResponse:
        split = self.service.save_split(body)
        return ApiResponse.success(self._view(body.month, split), "Rent split saved")

    def my_rent(self, actor: User) -> ApiResponse:
        rows = [MyRentOut(month=m, total_rent=t, amount=a) for m, t, a in self.service.my_rent(actor.id)]
        return ApiResponse.success(rows, "Rent history fetched")
