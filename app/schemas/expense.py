from datetime import date

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import ORMModel


class ExpenseIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: str = Field(default="Other", max_length=50)
    amount: float = Field(gt=0)
    expenseDate: date = Field(default_factory=date.today)
    note: str | None = Field(default=None, max_length=500)

    @field_validator("title")
    @classmethod
    def _clean_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("category")
    @classmethod
    def _clean_category(cls, v: str) -> str:
        return v.strip() or "Other"

    @field_validator("note")
    @classmethod
    def _clean_note(cls, v: str | None) -> str | None:
        return (v or "").strip() or None


class ExpenseOut(ORMModel):
    id: str
    user_id: str
    user_name: str
    title: str
    category: str
    amount: float
    expense_date: date
    note: str | None
