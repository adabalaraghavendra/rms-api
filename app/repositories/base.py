from typing import Generic, TypeVar

from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import ConflictError
from app.models.base import Document
from app.shared.object_id import to_object_id
from app.shared.pagination import Page, PageParams

ModelT = TypeVar("ModelT", bound=Document)


class BaseRepository(Generic[ModelT]):
    """Generic data access shared by all repositories. Subclasses set `model`
    (which names the collection) and add their own queries."""

    model: type[ModelT]

    def __init__(self, db: Database):
        self.db = db
        self.collection = db[self.model.collection]

    def get(self, entity_id: str) -> ModelT | None:
        oid = to_object_id(entity_id)
        doc = self.collection.find_one({"_id": oid}) if oid else None
        return self.model.from_mongo(doc) if doc else None

    def add(self, entity: ModelT) -> ModelT:
        try:
            result = self.collection.insert_one(entity.to_mongo())
        except DuplicateKeyError as exc:  # a unique index (e.g. email) was violated
            raise ConflictError("Already exists") from exc
        entity.id = str(result.inserted_id)
        return entity

    def save(self, entity: ModelT) -> ModelT:
        """Write an existing entity's current values back to the database."""
        try:
            self.collection.replace_one({"_id": to_object_id(entity.id)}, entity.to_mongo())
        except DuplicateKeyError as exc:
            raise ConflictError("Already exists") from exc
        return entity

    def delete(self, entity: ModelT) -> None:
        self.collection.delete_one({"_id": to_object_id(entity.id)})

    def paginate(self, query: dict, sort: list[tuple[str, int]], params: PageParams) -> Page[ModelT]:
        """One page of the documents matching `query`, plus the total count."""
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort(sort).skip(params.offset).limit(params.page_size)
        return Page(items=[self.model.from_mongo(d) for d in cursor], total=total, params=params)
