from typing import Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.shared.pagination import Page, PageParams

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic data access shared by all repositories. Subclasses set `model`
    and add their own queries. Repositories flush; services commit."""

    model: type[ModelT]

    def __init__(self, db: Session):
        self.db = db

    def get(self, entity_id: int) -> ModelT | None:
        return self.db.get(self.model, entity_id)

    def add(self, entity: ModelT) -> ModelT:
        self.db.add(entity)
        self.db.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self.db.delete(entity)
        self.db.flush()

    def paginate(self, stmt: Select, params: PageParams) -> Page[ModelT]:
        """Run `stmt` for one page and count the total, whatever its filters are."""
        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        rows = self.db.scalars(stmt.limit(params.page_size).offset(params.offset)).unique().all()
        return Page(items=list(rows), total=total, params=params)
