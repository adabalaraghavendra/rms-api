"""Dependency wiring: who is calling, and a controller (with its service) per request."""
from functools import lru_cache

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.database import Database

from app.controllers.auth_controller import AuthController
from app.controllers.expense_controller import ExpenseController
from app.controllers.rent_controller import RentController
from app.controllers.summary_controller import SummaryController
from app.controllers.user_controller import UserController
from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import PasswordHasher, TokenService
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.expense_service import ExpenseService
from app.services.rent_service import RentService
from app.services.summary_service import SummaryService
from app.services.user_service import UserService

_bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_hasher() -> PasswordHasher:
    return PasswordHasher()


@lru_cache
def get_tokens() -> TokenService:
    return TokenService(get_settings())


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Database = Depends(get_db),
    tokens: TokenService = Depends(get_tokens),
) -> User:
    """The logged-in user. Checked against the database on every call, so a
    deactivated or deleted member loses access immediately."""
    if not creds:
        raise UnauthorizedError("Authentication required")
    user = UserRepository(db).get(tokens.read_user_id(creds.credentials))
    if not user or not user.is_active:
        raise UnauthorizedError("User no longer active")
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise ForbiddenError("Admin access required")
    return user


def get_auth_controller(
    db: Database = Depends(get_db),
    hasher: PasswordHasher = Depends(get_hasher),
    tokens: TokenService = Depends(get_tokens),
) -> AuthController:
    return AuthController(AuthService(db, hasher, tokens))


def get_user_controller(
    db: Database = Depends(get_db), hasher: PasswordHasher = Depends(get_hasher)
) -> UserController:
    return UserController(UserService(db, hasher))


def get_expense_controller(db: Database = Depends(get_db)) -> ExpenseController:
    return ExpenseController(ExpenseService(db))


def get_rent_controller(db: Database = Depends(get_db)) -> RentController:
    return RentController(RentService(db))


def get_summary_controller(db: Database = Depends(get_db)) -> SummaryController:
    return SummaryController(SummaryService(db))
