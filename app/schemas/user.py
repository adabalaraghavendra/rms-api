from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.user import Role
from app.schemas.base import ORMModel


class UserBrief(ORMModel):
    id: int
    name: str
    email: str
    role: str


class UserOut(UserBrief):
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=6, max_length=72)
    role: Role = Role.USER

    @field_validator("name")
    @classmethod
    def _clean_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("email")
    @classmethod
    def _clean_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("must be a valid email")
        return v


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    isActive: bool | None = None
    password: str | None = Field(default=None, min_length=6, max_length=72)
