"""Drop the rooms table: the app manages a single room, so room_id is not needed.

Removes room_id from users, expenses and rent_splits, then drops rooms.
rent_splits becomes unique per month alone.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-27
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import context, op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if not context.is_offline_mode():  # the check needs a live connection (skipped for --sql)
        room_count = op.get_bind().execute(sa.text("SELECT COUNT(*) FROM rooms")).scalar()
        if room_count > 1:
            raise RuntimeError(
                f"Found {room_count} rooms. This migration assumes a single room; "
                "merge the data into one room first."
            )

    # Dropping a column also drops the FK, index and unique constraint that use it.
    op.drop_column("rent_splits", "room_id")        # also drops UNIQUE (room_id, month)
    op.create_unique_constraint("uq_rent_splits_month", "rent_splits", ["month"])
    op.drop_column("expenses", "room_id")           # also drops idx_expenses_room_date
    op.create_index("idx_expenses_date", "expenses", ["expense_date"])
    op.drop_column("users", "room_id")
    op.drop_table("rooms")


def downgrade() -> None:
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("monthly_rent", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.execute("INSERT INTO rooms (name) VALUES ('My Room')")

    for table in ("users", "expenses", "rent_splits"):
        op.add_column(table, sa.Column("room_id", sa.Integer, nullable=True))
        op.execute(f"UPDATE {table} SET room_id = (SELECT MIN(id) FROM rooms)")
        op.alter_column(table, "room_id", nullable=False)
        op.create_foreign_key(f"{table}_room_id_fkey", table, "rooms", ["room_id"], ["id"])

    op.drop_index("idx_expenses_date", table_name="expenses")
    op.create_index("idx_expenses_room_date", "expenses", ["room_id", "expense_date"])
    op.drop_constraint("uq_rent_splits_month", "rent_splits", type_="unique")
    op.create_unique_constraint("rent_splits_room_id_month_key", "rent_splits", ["room_id", "month"])
