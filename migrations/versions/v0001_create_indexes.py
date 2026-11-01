"""Indexes the app relies on. The unique ones enforce rules in the database itself
(one account per email, one rent split per month)."""
from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database

from migrations.base import Migration as BaseMigration


class Migration(BaseMigration):
    version = "0001"
    description = "Create indexes (users.email unique, expenses, rent_splits.month unique)"

    def up(self, db: Database) -> None:
        db["users"].create_index("email", unique=True, name="uq_users_email")
        db["expenses"].create_index([("user_id", ASCENDING), ("expense_date", DESCENDING)], name="ix_expenses_user_date")
        db["expenses"].create_index([("expense_date", DESCENDING)], name="ix_expenses_date")
        db["rent_splits"].create_index("month", unique=True, name="uq_rent_splits_month")
        db["rent_splits"].create_index("shares.user_id", name="ix_rent_splits_share_user")

    def down(self, db: Database) -> None:
        db["users"].drop_index("uq_users_email")
        db["expenses"].drop_index("ix_expenses_user_date")
        db["expenses"].drop_index("ix_expenses_date")
        db["rent_splits"].drop_index("uq_rent_splits_month")
        db["rent_splits"].drop_index("ix_rent_splits_share_user")
