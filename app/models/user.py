import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Text, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.expense import Expense
    from app.models.rent import RentShare


class Role(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """A person living in the room. The admin is a member too."""

    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('admin','user')"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text, default=Role.USER.value, server_default=Role.USER.value)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Deleting a user removes their expenses and rent shares too.
    expenses: Mapped[list["Expense"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    rent_shares: Mapped[list["RentShare"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN.value
