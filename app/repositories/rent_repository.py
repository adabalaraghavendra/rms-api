from bson import ObjectId
from pymongo.database import Database

from app.models.rent import RentShare, RentSplit
from app.repositories.base import BaseRepository
from app.repositories.user_repository import UserRepository


class RentRepository(BaseRepository[RentSplit]):
    model = RentSplit

    def __init__(self, db: Database):
        super().__init__(db)
        self._users = UserRepository(db)

    def get_by_month(self, month: str) -> RentSplit | None:
        doc = self.collection.find_one({"month": month})
        if not doc:
            return None
        split = RentSplit.from_mongo(doc)
        names = self._users.names_by_id({s.user_id for s in split.shares})
        for share in split.shares:
            share.name = names.get(share.user_id, "")
        return split

    def replace(self, month: str, total_rent: float, mode: str, allocations: list[tuple[str, float]]) -> RentSplit:
        """Store a month's split, replacing any earlier one. One document, so it is saved atomically."""
        split = RentSplit(
            month=month,
            total_rent=total_rent,
            mode=mode,
            shares=[RentShare(user_id=user_id, amount=amount) for user_id, amount in allocations],
        )
        self.collection.replace_one({"month": month}, split.to_mongo(), upsert=True)
        return self.get_by_month(month)

    def list_for_user(self, user_id: str) -> list[tuple[str, float, float]]:
        """(month, total_rent, my_amount) for every month the user pays rent, newest first."""
        rows = []
        for doc in self.collection.find({"shares.user_id": ObjectId(user_id)}).sort("month", -1):
            split = RentSplit.from_mongo(doc)
            mine = next(s.amount for s in split.shares if s.user_id == user_id)
            rows.append((split.month, split.total_rent, mine))
        return rows

    def share_for_user(self, user_id: str, month: str) -> float | None:
        doc = self.collection.find_one({"month": month, "shares.user_id": ObjectId(user_id)})
        if not doc:
            return None
        return next(s.amount for s in RentSplit.from_mongo(doc).shares if s.user_id == user_id)

    def remove_user_shares(self, user_id: str) -> None:
        """Take a deleted member out of every month's split."""
        oid = ObjectId(user_id)
        self.collection.update_many({"shares.user_id": oid}, {"$pull": {"shares": {"user_id": oid}}})
