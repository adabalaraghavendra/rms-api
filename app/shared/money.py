from decimal import ROUND_HALF_UP, Decimal


def to_cents(amount: float | int | str) -> int:
    """12.34 -> 1234. Money is split in whole cents so shares always add up exactly."""
    return int((Decimal(str(amount)) * 100).to_integral_value(ROUND_HALF_UP))


def from_cents(cents: int) -> float:
    return cents / 100
