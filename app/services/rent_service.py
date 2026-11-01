from pymongo.database import Database

from app.core.exceptions import BadRequestError
from app.models.rent import RentMode, RentSplit
from app.repositories.rent_repository import RentRepository
from app.repositories.user_repository import UserRepository
from app.schemas.rent import RentSplitIn
from app.services.base import BaseService
from app.services.rent_split_strategies import CustomSplit, EqualSplit, SplitStrategy
from app.shared.money import from_cents, to_cents


class RentService(BaseService):
    def __init__(self, db: Database):
        super().__init__(db)
        self.rents = RentRepository(db)
        self.users = UserRepository(db)
        self._strategies: dict[RentMode, SplitStrategy] = {
            RentMode.EQUAL: EqualSplit(),
            RentMode.CUSTOM: CustomSplit(),
        }

    def get_split(self, month: str) -> RentSplit | None:
        return self.rents.get_by_month(month)

    def save_split(self, data: RentSplitIn) -> RentSplit:
        """Create or replace the split for a month."""
        active_ids = self.users.active_ids()
        if not active_ids:
            raise BadRequestError("No active members")
        total_cents = to_cents(data.totalRent)
        allocations = self._strategies[data.mode].allocate(total_cents, data, active_ids)
        return self.rents.replace(
            data.month,
            from_cents(total_cents),
            data.mode.value,
            [(user_id, from_cents(cents)) for user_id, cents in allocations],
        )

    def my_rent(self, user_id: str) -> list[tuple[str, float, float]]:
        return self.rents.list_for_user(user_id)
