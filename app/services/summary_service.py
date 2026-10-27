from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.rent_repository import RentRepository
from app.repositories.summary_repository import SummaryRepository
from app.schemas.summary import AdminSummary, CategoryTotal, MemberSummary, MySummary
from app.services.base import BaseService
from app.shared.dates import current_month


class SummaryService(BaseService):
    """Per member for a month:
    spent    what they paid for the room
    fair     total room spend / active members
    balance  spent - fair   (positive: the others owe them)
    rent     their rent share (from the admin's split)
    """

    def __init__(self, db: Session):
        super().__init__(db)
        self.summaries = SummaryRepository(db)
        self.rents = RentRepository(db)

    def admin_summary(self, month: str | None) -> AdminSummary:
        month = month or current_month()
        members = [MemberSummary(**row) for row in self.summaries.member_summaries(month)]
        return AdminSummary(
            month=month,
            totalSpent=round(sum(m.spent for m in members), 2),
            totalRent=round(sum(m.rent for m in members), 2),
            members=members,
        )

    def my_summary(self, actor: User, month: str | None) -> MySummary:
        month = month or current_month()
        categories = [CategoryTotal(category=c, total=t) for c, t in self.summaries.category_totals(actor.id, month)]
        return MySummary(
            month=month,
            totalSpent=round(sum(c.total for c in categories), 2),
            byCategory=categories,
            rent=self.rents.share_for_user(actor.id, month),
        )
