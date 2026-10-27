from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.shared.dates import month_bounds

_MEMBER_SUMMARY_SQL = text(
    """
    WITH members AS (
        SELECT id, name, email, role FROM users WHERE is_active
    ),
    spent AS (
        SELECT user_id, SUM(amount) AS total, COUNT(*) AS cnt
        FROM expenses WHERE expense_date >= :start AND expense_date < :end
        GROUP BY user_id
    ),
    grand AS (
        SELECT COALESCE(SUM(total), 0) AS total FROM spent WHERE user_id IN (SELECT id FROM members)
    ),
    split AS (SELECT id FROM rent_splits WHERE month = :month)
    SELECT m.id, m.name, m.email, m.role,
           CAST(COALESCE(s.total, 0) AS FLOAT) AS spent,
           CAST(COALESCE(s.cnt, 0) AS INTEGER) AS expense_count,
           CAST(ROUND((SELECT total FROM grand) / NULLIF((SELECT COUNT(*) FROM members), 0), 2) AS FLOAT) AS fair_share,
           CAST(ROUND(COALESCE(s.total, 0) - (SELECT total FROM grand) / NULLIF((SELECT COUNT(*) FROM members), 0), 2) AS FLOAT) AS balance,
           CAST(COALESCE(rs.amount, 0) AS FLOAT) AS rent
    FROM members m
    LEFT JOIN spent s ON s.user_id = m.id
    LEFT JOIN rent_shares rs ON rs.user_id = m.id AND rs.split_id = (SELECT id FROM split)
    ORDER BY m.name
    """
)


class SummaryRepository:
    """Read-only aggregate queries for the dashboards."""

    def __init__(self, db: Session):
        self.db = db

    def member_summaries(self, month: str) -> list[dict]:
        start, end = month_bounds(month)
        rows = self.db.execute(_MEMBER_SUMMARY_SQL, {"start": start, "end": end, "month": month})
        return [dict(r) for r in rows.mappings()]

    def category_totals(self, user_id: int, month: str) -> list[tuple[str, float]]:
        start, end = month_bounds(month)
        total = func.sum(Expense.amount)
        stmt = (
            select(Expense.category, total)
            .where(Expense.user_id == user_id, Expense.expense_date >= start, Expense.expense_date < end)
            .group_by(Expense.category)
            .order_by(total.desc())
        )
        return [(category, float(amount)) for category, amount in self.db.execute(stmt)]
