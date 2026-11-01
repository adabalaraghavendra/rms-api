from pymongo.database import Database

from app.models.user import User
from app.repositories.rent_repository import RentRepository
from app.repositories.summary_repository import SummaryRepository
from app.repositories.user_repository import UserRepository
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

    def __init__(self, db: Database):
        super().__init__(db)
        self.users = UserRepository(db)
        self.rents = RentRepository(db)
        self.summaries = SummaryRepository(db)

    def admin_summary(self, month: str | None) -> AdminSummary:
        month = month or current_month()
        members = self.users.list_active()
        spent = self.summaries.spent_by_user(month)
        split = self.rents.get_by_month(month)
        rent_of = {s.user_id: s.amount for s in split.shares} if split else {}

        total = sum(spent.get(m.id, (0.0, 0))[0] for m in members)  # only active members' spending counts
        fair = round(total / len(members), 2) if members else 0.0
        rows = []
        for m in members:
            amount, count = spent.get(m.id, (0.0, 0))
            rows.append(MemberSummary(
                id=m.id, name=m.name, email=m.email, role=m.role,
                spent=round(amount, 2), expense_count=count,
                fair_share=fair, balance=round(amount - total / len(members), 2),
                rent=rent_of.get(m.id, 0.0),
            ))
        return AdminSummary(
            month=month,
            totalSpent=round(sum(r.spent for r in rows), 2),
            totalRent=round(sum(r.rent for r in rows), 2),
            members=rows,
        )

    def my_summary(self, actor: User, month: str | None) -> MySummary:
        month = month or current_month()
        categories = [CategoryTotal(category=c, total=round(t, 2)) for c, t in self.summaries.category_totals(actor.id, month)]
        return MySummary(
            month=month,
            totalSpent=round(sum(c.total for c in categories), 2),
            byCategory=categories,
            rent=self.rents.share_for_user(actor.id, month),
        )
