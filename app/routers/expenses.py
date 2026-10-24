from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from app.core.database import execute, fetch_all, fetch_one
from app.core.security import admin_only, current_user, valid_month

router = APIRouter(prefix="/expenses", tags=["expenses"])

SELECT = """SELECT e.id, e.user_id, u.name AS user_name, e.title, e.category, e.amount::float AS amount,
            to_char(e.expense_date, 'YYYY-MM-DD') AS expense_date, e.note
            FROM expenses e JOIN users u ON u.id = e.user_id"""


class ExpenseIn(BaseModel):
    title: str
    category: str = "Other"
    amount: float
    expenseDate: date | None = None
    note: str | None = None

    def params(self) -> dict:
        if not self.title.strip():
            raise HTTPException(400, "Title is required")
        if not self.amount > 0:
            raise HTTPException(400, "Amount must be greater than 0")
        return {"t": self.title.strip(), "c": self.category or "Other", "a": self.amount,
                "d": self.expenseDate or date.today(), "n": self.note or None}


@router.get("/mine")
def mine(month: str | None = None, me: dict = Depends(current_user)):
    if month:
        valid_month(month)
    return fetch_all(
        f"""{SELECT} WHERE e.user_id = %(u)s AND (%(m)s::text IS NULL OR to_char(e.expense_date, 'YYYY-MM') = %(m)s::text)
            ORDER BY e.expense_date DESC, e.id DESC""",
        {"u": me["id"], "m": month or None},
    )


@router.get("")
def all_expenses(month: str | None = None, userId: int | None = None, me: dict = Depends(admin_only)):
    if month:
        valid_month(month)
    return fetch_all(
        f"""{SELECT} WHERE e.room_id = %(r)s
            AND (%(m)s::text IS NULL OR to_char(e.expense_date, 'YYYY-MM') = %(m)s::text)
            AND (%(u)s::int IS NULL OR e.user_id = %(u)s::int)
            ORDER BY e.expense_date DESC, e.id DESC""",
        {"r": me["roomId"], "m": month or None, "u": userId},
    )


@router.post("", status_code=201)
def create(body: ExpenseIn, me: dict = Depends(current_user)):
    return fetch_one(
        """INSERT INTO expenses(room_id, user_id, title, category, amount, expense_date, note)
           VALUES (%(r)s, %(u)s, %(t)s, %(c)s, %(a)s, %(d)s, %(n)s) RETURNING id""",
        {"r": me["roomId"], "u": me["id"], **body.params()},
    )


def _scope(me: dict) -> tuple[str, int]:
    """Owners manage their own expenses; admins manage any in the room."""
    return ("room_id", me["roomId"]) if me["role"] == "admin" else ("user_id", me["id"])


@router.put("/{expense_id}")
def update(expense_id: int, body: ExpenseIn, me: dict = Depends(current_user)):
    col, val = _scope(me)
    n = execute(
        f"""UPDATE expenses SET title = %(t)s, category = %(c)s, amount = %(a)s, expense_date = %(d)s, note = %(n)s
            WHERE id = %(id)s AND {col} = %(v)s""",
        {"id": expense_id, "v": val, **body.params()},
    )
    if not n:
        raise HTTPException(404, "Expense not found")
    return {"ok": True}


@router.delete("/{expense_id}", status_code=204)
def remove(expense_id: int, me: dict = Depends(current_user)):
    col, val = _scope(me)
    if not execute(f"DELETE FROM expenses WHERE id = %(id)s AND {col} = %(v)s", {"id": expense_id, "v": val}):
        raise HTTPException(404, "Expense not found")
    return Response(status_code=204)
