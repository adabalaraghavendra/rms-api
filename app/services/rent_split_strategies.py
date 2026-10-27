"""How a month's rent is divided. One class per mode (strategy pattern):
add a new mode by subclassing SplitStrategy and registering it in RentService.

All maths is in whole cents so the shares always add up to the total exactly.
"""
from abc import ABC, abstractmethod

from app.core.exceptions import BadRequestError
from app.schemas.rent import RentSplitIn
from app.shared.money import to_cents

Allocation = list[tuple[int, int]]  # (user_id, cents)


class SplitStrategy(ABC):
    @abstractmethod
    def allocate(self, total_cents: int, request: RentSplitIn, active_ids: list[int]) -> Allocation:
        """Return each payer's share in cents."""

    @staticmethod
    def _check_members(user_ids: list[int], active_ids: list[int]) -> None:
        if not user_ids:
            raise BadRequestError("Select at least one member who pays rent")
        if len(set(user_ids)) != len(user_ids):
            raise BadRequestError("A member is listed twice")
        if any(uid not in active_ids for uid in user_ids):
            raise BadRequestError("Selected members must be active members")


class EqualSplit(SplitStrategy):
    """Divide equally between the chosen payers (everyone, if none are chosen)."""

    def allocate(self, total_cents: int, request: RentSplitIn, active_ids: list[int]) -> Allocation:
        payers = request.userIds or active_ids
        self._check_members(payers, active_ids)
        base, extra = divmod(total_cents, len(payers))
        # the first `extra` payers take one leftover cent each
        return [(uid, base + (1 if i < extra else 0)) for i, uid in enumerate(payers)]


class CustomSplit(SplitStrategy):
    """Use the amount typed for each payer; they must add up to the total."""

    def allocate(self, total_cents: int, request: RentSplitIn, active_ids: list[int]) -> Allocation:
        self._check_members([s.userId for s in request.shares], active_ids)
        shares = [(s.userId, to_cents(s.amount)) for s in request.shares]
        given = sum(cents for _, cents in shares)
        if given != total_cents:
            raise BadRequestError(f"Shares total {given / 100:.2f} but rent is {total_cents / 100:.2f}")
        return shares
