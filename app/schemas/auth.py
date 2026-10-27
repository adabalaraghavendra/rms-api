from pydantic import BaseModel, Field, field_validator

from app.schemas.user import UserBrief


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    token: str
    user: UserBrief


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)

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


class PasswordChange(BaseModel):
    currentPassword: str
    newPassword: str = Field(min_length=6, max_length=72)
