from pydantic import BaseModel


class MemberSummary(BaseModel):
    id: int
    name: str
    email: str
    role: str
    spent: float
    expense_count: int
    fair_share: float
    balance: float   # spent - fair_share (positive: the others owe them)
    rent: float


class AdminSummary(BaseModel):
    month: str
    totalSpent: float
    totalRent: float
    members: list[MemberSummary]


class CategoryTotal(BaseModel):
    category: str
    total: float


class MySummary(BaseModel):
    month: str
    totalSpent: float
    byCategory: list[CategoryTotal]
    rent: float | None  # null until the admin sets this month's rent split
