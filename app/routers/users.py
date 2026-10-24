from fastapi import APIRouter, Depends, HTTPException, Response
from psycopg.errors import UniqueViolation
from pydantic import BaseModel

from app.core.database import fetch_all, fetch_one, pool
from app.core.security import admin_only, hash_password

router = APIRouter(tags=["users"], dependencies=[Depends(admin_only)])

COLS = "id, name, email, role, is_active, created_at"


class UserIn(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"


class UserPatch(BaseModel):
    name: str | None = None
    isActive: bool | None = None
    password: str | None = None


class RoomPatch(BaseModel):
    name: str | None = None
    monthlyRent: float | None = None


@router.get("/users")
def list_users(me: dict = Depends(admin_only)):
    return fetch_all(f"SELECT {COLS} FROM users WHERE room_id = %(r)s ORDER BY created_at", {"r": me["roomId"]})


@router.post("/users", status_code=201)
def create_user(body: UserIn, me: dict = Depends(admin_only)):
    if not body.name.strip() or not body.email.strip():
        raise HTTPException(400, "Name and email are required")
    if len(body.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    if body.role not in ("admin", "user"):
        raise HTTPException(400, "Invalid role")
    try:
        return fetch_one(
            f"""INSERT INTO users(room_id, name, email, password_hash, role)
                VALUES (%(r)s, %(n)s, %(e)s, %(p)s, %(role)s) RETURNING {COLS}""",
            {"r": me["roomId"], "n": body.name.strip(), "e": body.email.lower().strip(),
             "p": hash_password(body.password), "role": body.role},
        )
    except UniqueViolation:
        raise HTTPException(409, "Already exists")


@router.patch("/users/{user_id}")
def update_user(user_id: int, body: UserPatch, me: dict = Depends(admin_only)):
    if user_id == me["id"] and body.isActive is False:
        raise HTTPException(400, "You cannot deactivate yourself")
    if body.password is not None and len(body.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    row = fetch_one(
        f"""UPDATE users SET name = COALESCE(%(n)s::text, name),
                             is_active = COALESCE(%(a)s::boolean, is_active),
                             password_hash = COALESCE(%(p)s::text, password_hash)
            WHERE id = %(id)s AND room_id = %(r)s RETURNING {COLS}""",
        {"n": body.name, "a": body.isActive, "p": hash_password(body.password) if body.password else None,
         "id": user_id, "r": me["roomId"]},
    )
    if not row:
        raise HTTPException(404, "User not found")
    return row


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, me: dict = Depends(admin_only)):
    """Permanently remove a member together with their expenses and rent shares."""
    if user_id == me["id"]:
        raise HTTPException(400, "You cannot delete yourself")
    with pool.connection() as conn:  # single transaction
        if not conn.execute("SELECT 1 FROM users WHERE id = %(id)s AND room_id = %(r)s",
                            {"id": user_id, "r": me["roomId"]}).fetchone():
            raise HTTPException(404, "User not found")
        conn.execute("DELETE FROM rent_shares WHERE user_id = %(id)s", {"id": user_id})
        conn.execute("DELETE FROM expenses WHERE user_id = %(id)s", {"id": user_id})
        conn.execute("DELETE FROM users WHERE id = %(id)s", {"id": user_id})
    return Response(status_code=204)


@router.get("/room")
def get_room(me: dict = Depends(admin_only)):
    return fetch_one("SELECT id, name, monthly_rent::float AS monthly_rent FROM rooms WHERE id = %(r)s", {"r": me["roomId"]})


@router.patch("/room")
def update_room(body: RoomPatch, me: dict = Depends(admin_only)):
    return fetch_one(
        """UPDATE rooms SET name = COALESCE(%(n)s::text, name), monthly_rent = COALESCE(%(m)s::numeric, monthly_rent)
           WHERE id = %(r)s RETURNING id, name, monthly_rent::float AS monthly_rent""",
        {"n": body.name, "m": body.monthlyRent, "r": me["roomId"]},
    )
