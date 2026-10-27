from app.models.user import User
from app.schemas.auth import LoginRequest, PasswordChange, ProfileUpdate, TokenOut
from app.schemas.user import UserBrief
from app.services.auth_service import AuthService
from app.shared.response import ApiResponse


class AuthController:
    def __init__(self, service: AuthService):
        self.service = service

    def login(self, body: LoginRequest) -> ApiResponse:
        token, user = self.service.login(body.email, body.password)
        return ApiResponse.success(TokenOut(token=token, user=UserBrief.model_validate(user)), "Login successful")

    def me(self, user: User) -> ApiResponse:
        return ApiResponse.success(UserBrief.model_validate(user), "Profile fetched")

    def update_profile(self, user: User, body: ProfileUpdate) -> ApiResponse:
        updated = self.service.update_profile(user, body)
        return ApiResponse.success(UserBrief.model_validate(updated), "Profile updated")

    def change_password(self, user: User, body: PasswordChange) -> ApiResponse:
        self.service.change_password(user, body)
        return ApiResponse.success(message="Password changed")
