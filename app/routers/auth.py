from fastapi import APIRouter, Depends

from app.controllers.auth_controller import AuthController
from app.dependencies import current_user, get_auth_controller
from app.models.user import User
from app.schemas.auth import LoginRequest, PasswordChange, ProfileUpdate, TokenOut
from app.schemas.user import UserBrief
from app.shared.response import ApiResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=ApiResponse[TokenOut])
def login(body: LoginRequest, ctrl: AuthController = Depends(get_auth_controller)):
    return ctrl.login(body)


@router.get("/me", response_model=ApiResponse[UserBrief])
def me(user: User = Depends(current_user), ctrl: AuthController = Depends(get_auth_controller)):
    return ctrl.me(user)


@router.patch("/profile", response_model=ApiResponse[UserBrief])
def update_profile(
    body: ProfileUpdate, user: User = Depends(current_user), ctrl: AuthController = Depends(get_auth_controller)
):
    return ctrl.update_profile(user, body)


@router.post("/password", response_model=ApiResponse[None])
def change_password(
    body: PasswordChange, user: User = Depends(current_user), ctrl: AuthController = Depends(get_auth_controller)
):
    return ctrl.change_password(user, body)
