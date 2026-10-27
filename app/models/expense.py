from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import User


class Expense(Base):
    """Money one person spent on room maintenance."""

    __tablename__ = "expenses"
    __table_args__ = (
        CheckConstraint("amount > 0"),
        Index("idx_expenses_user", "user_id"),
        Index("idx_expenses_date", "expense_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text, default="Other", server_default="Other")
    amount: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False))
    expense_date: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="expenses")

    @property
    def user_name(self) -> str:
        return self.user.name
