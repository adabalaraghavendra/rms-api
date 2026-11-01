from bson import ObjectId
from pymongo.database import Database

from app.shared.dates import month_bounds


class SummaryRepository:
    """Read-only aggregate queries for the dashboards (MongoDB aggregation pipelines)."""

    def __init__(self, db: Database):
        self.expenses = db["expenses"]

    @staticmethod
    def _in_month(month: str) -> dict:
        start, end = month_bounds(month)
        return {"expense_date": {"$gte": start.isoformat(), "$lt": end.isoformat()}}

    def spent_by_user(self, month: str) -> dict[str, tuple[float, int]]:
        """{user_id: (total spent, number of expenses)} for the month."""
        pipeline = [
            {"$match": self._in_month(month)},
            {"$group": {"_id": "$user_id", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
        ]
        return {str(r["_id"]): (float(r["total"]), int(r["count"])) for r in self.expenses.aggregate(pipeline)}

    def category_totals(self, user_id: str, month: str) -> list[tuple[str, float]]:
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id), **self._in_month(month)}},
            {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
            {"$sort": {"total": -1}},
        ]
        return [(r["_id"], float(r["total"])) for r in self.expenses.aggregate(pipeline)]
