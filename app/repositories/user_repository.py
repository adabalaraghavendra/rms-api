from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository
from app.shared.pagination import Page, PageParams


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def list_page(self, params: PageParams) -> Page[User]:
        return self.paginate(select(User).order_by(User.created_at, User.id), params)

    def active_ids(self) -> list[int]:
        return list(self.db.scalars(select(User.id).where(User.is_active.is_(True)).order_by(User.id)))
