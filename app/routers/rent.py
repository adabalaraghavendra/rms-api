from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.database import fetch_all, fetch_one, pool
from app.core.security import admin_only, current_user, valid_month

router = APIRouter(prefix="/rent", tags=["rent"])


class ShareIn(BaseModel):
    userId: int
    amount: float


class RentIn(BaseModel):
    month: str
    totalRent: float
    mode: str
    shares: list[ShareIn] = []   # custom mode: who pays and how much
    userIds: list[int] = []      # equal mode: who pays (empty = all active members)


def cents(x: float) -> int:
    return round(x * 100)


@router.get("")
def get_split(month: str | None = None, me: dict = Depends(admin_only)):
    month = valid_month(month)
    split = fetch_one("SELECT * FROM rent_splits WHERE room_id = %(r)s AND month = %(m)s", {"r": me["roomId"], "m": month})
    if not split:
        return {"month": month, "split": None}
    shares = fetch_all(
        """SELECT s.user_id, u.name, s.amount::float AS amount FROM rent_shares s
           JOIN users u ON u.id = s.user_id WHERE s.split_id = %(s)s ORDER BY u.name""",
        {"s": split["id"]},
    )
    return {"month": month, "split": {"totalRent": float(split["total_rent"]), "mode": split["mode"], "shares": shares}}


@router.put("", status_code=201)
def save_split(body: RentIn, me: dict = Depends(admin_only)):
    month = valid_month(body.month)
    total_c = cents(body.totalRent)
    if total_c < 0:
        raise HTTPException(400, "Invalid total rent")
    if body.mode not in ("equal", "custom"):
        raise HTTPException(400, "mode must be equal or custom")

    ids = [m["id"] for m in fetch_all(
        "SELECT id FROM users WHERE room_id = %(r)s AND is_active ORDER BY id", {"r": me["roomId"]})]
    if not ids:
        raise HTTPException(400, "No active members")

    if body.mode == "equal":
        payers = body.userIds or ids
        if len(set(payers)) != len(payers) or any(uid not in ids for uid in payers):
            raise HTTPException(400, "Selected members are invalid")
        # Spread leftover cents so the shares sum exactly to the total
        base, extra = divmod(total_c, len(payers))
        result = [(uid, base + (1 if i < extra else 0)) for i, uid in enumerate(payers)]
    else:
        if not body.shares:
            raise HTTPException(400, "Select at least one member who pays rent")
        result = [(s.userId, cents(s.amount)) for s in body.shares]
        if any(uid not in ids or c < 0 for uid, c in result):
            raise HTTPException(400, "Shares contain an invalid member or amount")
        if len({uid for uid, _ in result}) != len(result):
            raise HTTPException(400, "Duplicate member in shares")
        total_shares = sum(c for _, c in result)
        if total_shares != total_c:
            raise HTTPException(400, f"Shares total {total_shares / 100:.2f} but rent is {total_c / 100:.2f}")

    with pool.connection() as conn:  # one transaction: commits on success, rolls back on error
        conn.execute("DELETE FROM rent_splits WHERE room_id = %(r)s AND month = %(m)s", {"r": me["roomId"], "m": month})
        split_id = conn.execute(
            "INSERT INTO rent_splits(room_id, month, total_rent, mode) VALUES (%(r)s, %(m)s, %(t)s, %(mode)s) RETURNING id",
            {"r": me["roomId"], "m": month, "t": total_c / 100, "mode": body.mode},
        ).fetchone()["id"]
        for uid, c in result:
            conn.execute(
                "INSERT INTO rent_shares(split_id, user_id, amount) VALUES (%(s)s, %(u)s, %(a)s)",
                {"s": split_id, "u": uid, "a": c / 100},
            )
    return {"ok": True}


@router.get("/mine")
def my_rent(me: dict = Depends(current_user)):
    return fetch_all(
        """SELECT sp.month, sp.total_rent::float AS total_rent, sh.amount::float AS amount
           FROM rent_shares sh JOIN rent_splits sp ON sp.id = sh.split_id
           WHERE sh.user_id = %(u)s ORDER BY sp.month DESC""",
        {"u": me["id"]},
    )
