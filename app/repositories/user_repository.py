from app.models.user import User
from app.repositories.base import BaseRepository
from app.shared.object_id import to_object_id
from app.shared.pagination import Page, PageParams


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        doc = self.collection.find_one({"email": email})
        return User.from_mongo(doc) if doc else None

    def list_page(self, params: PageParams) -> Page[User]:
        return self.paginate({}, [("created_at", 1), ("_id", 1)], params)

    def list_active(self) -> list[User]:
        return [User.from_mongo(d) for d in self.collection.find({"is_active": True}).sort("name", 1)]

    def active_ids(self) -> list[str]:
        docs = self.collection.find({"is_active": True}, {"_id": 1}).sort("_id", 1)
        return [str(d["_id"]) for d in docs]

    def names_by_id(self, user_ids: set[str]) -> dict[str, str]:
        """{user_id: name} for the given ids (used to label expenses and rent shares)."""
        oids = [oid for oid in (to_object_id(i) for i in user_ids) if oid]
        if not oids:
            return {}
        return {str(d["_id"]): d["name"] for d in self.collection.find({"_id": {"$in": oids}}, {"name": 1})}
