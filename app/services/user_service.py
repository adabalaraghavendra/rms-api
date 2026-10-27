from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.core.security import PasswordHasher
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService
from app.shared.pagination import Page, PageParams


class UserService(BaseService):
    def __init__(self, db: Session, hasher: PasswordHasher):
        super().__init__(db)
        self.users = UserRepository(db)
        self.hasher = hasher

    def list_users(self, params: PageParams) -> Page[User]:
        return self.users.list_page(params)

    def create(self, data: UserCreate) -> User:
        if self.users.get_by_email(data.email):
            raise ConflictError("Email already in use")
        user = User(
            name=data.name,
            email=data.email,
            password_hash=self.hasher.hash(data.password),
            role=data.role.value,
        )
        self.users.add(user)
        self.commit()
        return user

    def update(self, actor: User, user_id: int, data: UserUpdate) -> User:
        user = self._get(user_id)
        if user.id == actor.id and data.isActive is False:
            raise BadRequestError("You cannot deactivate yourself")
        if data.name is not None:
            user.name = data.name.strip() or user.name
        if data.isActive is not None:
            user.is_active = data.isActive
        if data.password:
            user.password_hash = self.hasher.hash(data.password)
        self.commit()
        return user

    def delete(self, actor: User, user_id: int) -> None:
        """Permanently remove a member together with their expenses and rent shares."""
        if user_id == actor.id:
            raise BadRequestError("You cannot delete yourself")
        self.users.delete(self._get(user_id))
        self.commit()

    def _get(self, user_id: int) -> User:
        user = self.users.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user
