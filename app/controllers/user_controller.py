from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services.user_service import UserService
from app.shared.pagination import PageParams
from app.shared.response import ApiResponse


class UserController:
    def __init__(self, service: UserService):
        self.service = service

    def list_users(self, params: PageParams) -> ApiResponse:
        page = self.service.list_users(params).map(UserOut.model_validate)
        return ApiResponse.paginated(page, "Members fetched")

    def create(self, body: UserCreate) -> ApiResponse:
        user = self.service.create(body)
        return ApiResponse.success(UserOut.model_validate(user), "Member added")

    def update(self, actor: User, user_id: str, body: UserUpdate) -> ApiResponse:
        user = self.service.update(actor, user_id, body)
        return ApiResponse.success(UserOut.model_validate(user), "Member updated")

    def delete(self, actor: User, user_id: str) -> ApiResponse:
        self.service.delete(actor, user_id)
        return ApiResponse.success(message="Member deleted")
