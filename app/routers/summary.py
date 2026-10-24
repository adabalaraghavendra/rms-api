from fastapi import APIRouter, Depends

from app.core.database import fetch_all, fetch_one
from app.core.security import admin_only, current_user, valid_month

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("")
def admin_summary(month: str | None = None, me: dict = Depends(admin_only)):
    """Per active member: spent, fair share (total / members), balance (spent - fair), rent share."""
    month = valid_month(month)
    members = fetch_all(
        """WITH members AS (SELECT id, name, email, role FROM users WHERE room_id = %(r)s AND is_active),
           spent AS (
             SELECT user_id, SUM(amount) AS total, COUNT(*) AS cnt FROM expenses
             WHERE room_id = %(r)s AND to_char(expense_date, 'YYYY-MM') = %(m)s GROUP BY user_id),
           grand AS (SELECT COALESCE(SUM(total), 0) AS total FROM spent WHERE user_id IN (SELECT id FROM members)),
           split AS (SELECT id FROM rent_splits WHERE room_id = %(r)s AND month = %(m)s)
           SELECT m.id, m.name, m.email, m.role,
             COALESCE(s.total, 0)::float AS spent,
             COALESCE(s.cnt, 0)::int AS expense_count,
             ROUND((SELECT total FROM grand) / (SELECT COUNT(*) FROM members), 2)::float AS fair_share,
             ROUND(COALESCE(s.total, 0) - (SELECT total FROM grand) / (SELECT COUNT(*) FROM members), 2)::float AS balance,
             COALESCE(rs.amount, 0)::float AS rent
           FROM members m
           LEFT JOIN spent s ON s.user_id = m.id
           LEFT JOIN rent_shares rs ON rs.user_id = m.id AND rs.split_id = (SELECT id FROM split)
           ORDER BY m.name""",
        {"r": me["roomId"], "m": month},
    )
    return {
        "month": month,
        "totalSpent": sum(m["spent"] for m in members),
        "totalRent": sum(m["rent"] for m in members),
        "members": members,
    }


@router.get("/mine")
def my_summary(month: str | None = None, me: dict = Depends(current_user)):
    month = valid_month(month)
    by_category = fetch_all(
        """SELECT category, SUM(amount)::float AS total FROM expenses
           WHERE user_id = %(u)s AND to_char(expense_date, 'YYYY-MM') = %(m)s GROUP BY category ORDER BY total DESC""",
        {"u": me["id"], "m": month},
    )
    rent = fetch_one(
        """SELECT sh.amount::float AS amount FROM rent_shares sh JOIN rent_splits sp ON sp.id = sh.split_id
           WHERE sh.user_id = %(u)s AND sp.month = %(m)s""",
        {"u": me["id"], "m": month},
    )
    return {
        "month": month,
        "totalSpent": sum(c["total"] for c in by_category),
        "byCategory": by_category,
        "rent": rent["amount"] if rent else None,
    }
