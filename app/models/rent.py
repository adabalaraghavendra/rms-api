import enum
from datetime import datetime

from sqlalchemy import CHAR, CheckConstraint, DateTime, ForeignKey, Numeric, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import User


class RentMode(str, enum.Enum):
    EQUAL = "equal"    # divided equally between the people who pay
    CUSTOM = "custom"  # admin types each person's amount


class RentSplit(Base):
    """The month's rent and how it was divided. One per month."""

    __tablename__ = "rent_splits"
    __table_args__ = (CheckConstraint("total_rent >= 0"), CheckConstraint("mode IN ('equal','custom')"))

    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[str] = mapped_column(CHAR(7), unique=True)  # 'YYYY-MM'
    total_rent: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False))
    mode: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    shares: Mapped[list["RentShare"]] = relationship(
        back_populates="split", cascade="all, delete-orphan", order_by="RentShare.id"
    )


class RentShare(Base):
    """One payer's portion of a month's rent."""

    __tablename__ = "rent_shares"
    __table_args__ = (CheckConstraint("amount >= 0"), UniqueConstraint("split_id", "user_id"))

    id: Mapped[int] = mapped_column(primary_key=True)
    split_id: Mapped[int] = mapped_column(ForeignKey("rent_splits.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False))

    split: Mapped[RentSplit] = relationship(back_populates="shares")
    user: Mapped[User] = relationship(back_populates="rent_shares")

    @property
    def name(self) -> str:
        return self.user.name
