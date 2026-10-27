from fastapi import APIRouter, Depends

from app.controllers.rent_controller import RentController
from app.dependencies import current_user, get_rent_controller, require_admin
from app.models.user import User
from app.schemas.rent import MyRentOut, RentSplitIn, RentSplitView
from app.shared.dates import month_query
from app.shared.response import ApiResponse

router = APIRouter(prefix="/rent", tags=["Rent"])


@router.get("/mine", response_model=ApiResponse[list[MyRentOut]])
def my_rent(user: User = Depends(current_user), ctrl: RentController = Depends(get_rent_controller)):
    return ctrl.my_rent(user)


@router.get("", response_model=ApiResponse[RentSplitView], dependencies=[Depends(require_admin)])
def get_split(month: str | None = Depends(month_query), ctrl: RentController = Depends(get_rent_controller)):
    return ctrl.get_split(month)


@router.put("", response_model=ApiResponse[RentSplitView], status_code=201, dependencies=[Depends(require_admin)])
def save_split(body: RentSplitIn, ctrl: RentController = Depends(get_rent_controller)):
    return ctrl.save_split(body)
