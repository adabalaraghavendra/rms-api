from fastapi import APIRouter, Depends

from app.controllers.user_controller import UserController
from app.dependencies import get_user_controller, require_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.shared.pagination import PageParams, get_page_params
from app.shared.response import ApiResponse

# Admin only
router = APIRouter(prefix="/users", tags=["Members"], dependencies=[Depends(require_admin)])


@router.get("", response_model=ApiResponse[list[UserOut]])
def list_users(params: PageParams = Depends(get_page_params), ctrl: UserController = Depends(get_user_controller)):
    return ctrl.list_users(params)


@router.post("", response_model=ApiResponse[UserOut], status_code=201)
def create_user(body: UserCreate, ctrl: UserController = Depends(get_user_controller)):
    return ctrl.create(body)


@router.patch("/{user_id}", response_model=ApiResponse[UserOut])
def update_user(
    user_id: str, body: UserUpdate, admin: User = Depends(require_admin),
    ctrl: UserController = Depends(get_user_controller),
):
    return ctrl.update(admin, user_id, body)


@router.delete("/{user_id}", response_model=ApiResponse[None])
def delete_user(user_id: str, admin: User = Depends(require_admin), ctrl: UserController = Depends(get_user_controller)):
    return ctrl.delete(admin, user_id)
