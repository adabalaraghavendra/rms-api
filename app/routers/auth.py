from fastapi import APIRouter, Depends, HTTPException
from psycopg.errors import UniqueViolation
from pydantic import BaseModel

from app.core.database import execute, fetch_one
from app.core.security import create_token, current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginIn(BaseModel):
    email: str
    password: str


def public_user(u: dict) -> dict:
    return {"id": u["id"], "name": u["name"], "email": u["email"], "role": u["role"], "roomId": u["room_id"]}


@router.post("/login")
def login(body: LoginIn):
    user = fetch_one("SELECT * FROM users WHERE email = %(e)s", {"e": body.email.lower().strip()})
    if not user or not user["is_active"] or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    return {"token": create_token(user), "user": public_user(user)}


class ProfileIn(BaseModel):
    name: str
    email: str


class PasswordIn(BaseModel):
    currentPassword: str
    newPassword: str


@router.patch("/profile")
def update_profile(body: ProfileIn, auth: dict = Depends(current_user)):
    if not body.name.strip() or not body.email.strip():
        raise HTTPException(400, "Name and email are required")
    try:
        row = fetch_one(
            "UPDATE users SET name = %(n)s, email = %(e)s WHERE id = %(id)s RETURNING *",
            {"n": body.name.strip(), "e": body.email.lower().strip(), "id": auth["id"]},
        )
    except UniqueViolation:
        raise HTTPException(409, "Email already in use")
    return public_user(row)


@router.post("/password")
def change_password(body: PasswordIn, auth: dict = Depends(current_user)):
    user = fetch_one("SELECT * FROM users WHERE id = %(id)s", {"id": auth["id"]})
    if not verify_password(body.currentPassword, user["password_hash"]):
        raise HTTPException(400, "Current password is incorrect")
    if len(body.newPassword) < 6:
        raise HTTPException(400, "New password must be at least 6 characters")
    execute("UPDATE users SET password_hash = %(p)s WHERE id = %(id)s",
            {"p": hash_password(body.newPassword), "id": auth["id"]})
    return {"ok": True}


@router.get("/me")
def me(auth: dict = Depends(current_user)):
    user = fetch_one("SELECT * FROM users WHERE id = %(id)s AND is_active", {"id": auth["id"]})
    if not user:
        raise HTTPException(401, "User no longer active")
    return public_user(user)
