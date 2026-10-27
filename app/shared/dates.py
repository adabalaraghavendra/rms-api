from datetime import date

from fastapi import Query

MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"  # "YYYY-MM"


def current_month() -> str:
    return date.today().strftime("%Y-%m")


def month_bounds(month: str) -> tuple[date, date]:
    """[start, end) dates covering the month, e.g. 2026-10 -> (2026-10-01, 2026-11-01)."""
    year, mon = (int(p) for p in month.split("-"))
    start = date(year, mon, 1)
    end = date(year + 1, 1, 1) if mon == 12 else date(year, mon + 1, 1)
    return start, end


def month_query(month: str | None = Query(None, pattern=MONTH_PATTERN, description="YYYY-MM")) -> str | None:
    """FastAPI dependency for an optional ?month=YYYY-MM filter."""
    return month
