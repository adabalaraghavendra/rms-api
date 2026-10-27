from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, UnauthorizedError
from app.core.security import PasswordHasher, TokenService
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import PasswordChange, ProfileUpdate
from app.services.base import BaseService


class AuthService(BaseService):
    def __init__(self, db: Session, hasher: PasswordHasher, tokens: TokenService):
        super().__init__(db)
        self.users = UserRepository(db)
        self.hasher = hasher
        self.tokens = tokens

    def login(self, email: str, password: str) -> tuple[str, User]:
        user = self.users.get_by_email(email.strip().lower())
        # One message for every failure so attackers cannot tell which emails exist.
        if not user or not user.is_active or not self.hasher.verify(password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")
        return self.tokens.create(user.id), user

    def update_profile(self, user: User, data: ProfileUpdate) -> User:
        other = self.users.get_by_email(data.email)
        if other and other.id != user.id:
            raise ConflictError("Email already in use")
        user.name, user.email = data.name, data.email
        self.commit()
        return user

    def change_password(self, user: User, data: PasswordChange) -> None:
        if not self.hasher.verify(data.currentPassword, user.password_hash):
            raise BadRequestError("Current password is incorrect")
        user.password_hash = self.hasher.hash(data.newPassword)
        self.commit()
