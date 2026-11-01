from pydantic import BaseModel, Field

from app.models.rent import RentMode
from app.schemas.base import ORMModel
from app.shared.dates import MONTH_PATTERN


class ShareIn(BaseModel):
    userId: str
    amount: float = Field(ge=0)


class RentSplitIn(BaseModel):
    month: str = Field(pattern=MONTH_PATTERN)
    totalRent: float = Field(ge=0)
    mode: RentMode
    shares: list[ShareIn] = []   # custom mode: who pays and how much
    userIds: list[str] = []      # equal mode: who pays (empty = every active member)


class ShareOut(ORMModel):
    user_id: str
    name: str
    amount: float


class RentSplitOut(BaseModel):
    totalRent: float
    mode: str
    shares: list[ShareOut]


class RentSplitView(BaseModel):
    month: str
    split: RentSplitOut | None  # null when the admin has not set this month yet


class MyRentOut(BaseModel):
    month: str
    total_rent: float
    amount: float
