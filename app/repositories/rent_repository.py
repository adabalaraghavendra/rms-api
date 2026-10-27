from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.models.rent import RentShare, RentSplit
from app.repositories.base import BaseRepository


class RentRepository(BaseRepository[RentSplit]):
    model = RentSplit

    def get_by_month(self, month: str) -> RentSplit | None:
        stmt = (
            select(RentSplit)
            .options(selectinload(RentSplit.shares).joinedload(RentShare.user))
            .where(RentSplit.month == month)
        )
        return self.db.scalar(stmt)

    def replace(self, month: str, total_rent: float, mode: str, allocations: list[tuple[int, float]]) -> RentSplit:
        """Store a month's split, replacing any earlier one (shares go with it)."""
        existing = self.db.scalar(select(RentSplit).where(RentSplit.month == month))
        if existing:
            self.delete(existing)
        split = RentSplit(month=month, total_rent=total_rent, mode=mode)
        split.shares = [RentShare(user_id=user_id, amount=amount) for user_id, amount in allocations]
        return self.add(split)

    def list_for_user(self, user_id: int) -> list[tuple[str, float, float]]:
        """(month, total_rent, my_amount) for every month the user pays rent, newest first."""
        stmt = (
            select(RentSplit.month, RentSplit.total_rent, RentShare.amount)
            .join(RentShare, RentShare.split_id == RentSplit.id)
            .where(RentShare.user_id == user_id)
            .order_by(RentSplit.month.desc())
        )
        return [tuple(row) for row in self.db.execute(stmt)]

    def share_for_user(self, user_id: int, month: str) -> float | None:
        stmt = (
            select(RentShare.amount)
            .join(RentSplit, RentSplit.id == RentShare.split_id)
            .where(RentShare.user_id == user_id, RentSplit.month == month)
        )
        return self.db.scalar(stmt)
