"""Initial schema (rooms, users, expenses, rent_splits, rent_shares).

This is the schema as first created by the original setup script, so a database
that already has these tables is brought under Alembic with:  alembic stamp 0001

Revision ID: 0001
Revises:
Create Date: 2026-10-27
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("monthly_rent", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email"),
        sa.CheckConstraint("role IN ('admin','user')"),
    )
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("category", sa.Text, nullable=False, server_default="Other"),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("expense_date", sa.Date, nullable=False, server_default=sa.func.current_date()),
        sa.Column("note", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("amount > 0"),
    )
    op.create_index("idx_expenses_user", "expenses", ["user_id"])
    op.create_index("idx_expenses_room_date", "expenses", ["room_id", "expense_date"])
    op.create_table(
        "rent_splits",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("month", sa.CHAR(7), nullable=False),
        sa.Column("total_rent", sa.Numeric(12, 2), nullable=False),
        sa.Column("mode", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("total_rent >= 0"),
        sa.CheckConstraint("mode IN ('equal','custom')"),
        sa.UniqueConstraint("room_id", "month"),
    )
    op.create_table(
        "rent_shares",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("split_id", sa.Integer, sa.ForeignKey("rent_splits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.CheckConstraint("amount >= 0"),
        sa.UniqueConstraint("split_id", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("rent_shares")
    op.drop_table("rent_splits")
    op.drop_index("idx_expenses_room_date", table_name="expenses")
    op.drop_index("idx_expenses_user", table_name="expenses")
    op.drop_table("expenses")
    op.drop_table("users")
    op.drop_table("rooms")
