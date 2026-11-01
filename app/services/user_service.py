from pymongo.database import Database

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.core.security import PasswordHasher
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.rent_repository import RentRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService
from app.shared.pagination import Page, PageParams


class UserService(BaseService):
    def __init__(self, db: Database, hasher: PasswordHasher):
        super().__init__(db)
        self.users = UserRepository(db)
        self.expenses = ExpenseRepository(db)
        self.rents = RentRepository(db)
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
        return self.users.add(user)  # the unique email index also guards against races

    def update(self, actor: User, user_id: str, data: UserUpdate) -> User:
        user = self._get(user_id)
        if user.id == actor.id and data.isActive is False:
            raise BadRequestError("You cannot deactivate yourself")
        if data.name is not None:
            user.name = data.name.strip() or user.name
        if data.isActive is not None:
            user.is_active = data.isActive
        if data.password:
            user.password_hash = self.hasher.hash(data.password)
        return self.users.save(user)

    def delete(self, actor: User, user_id: str) -> None:
        """Permanently remove a member together with their expenses and rent shares."""
        if user_id == actor.id:
            raise BadRequestError("You cannot delete yourself")
        user = self._get(user_id)
        self.expenses.delete_by_user(user.id)
        self.rents.remove_user_shares(user.id)
        self.users.delete(user)

    def _get(self, user_id: str) -> User:
        user = self.users.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user
