"""The one response shape every endpoint uses:

    {"status": "success" | "error", "message": "...", "data": ..., "pagination": {...} | null}
"""
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

from app.shared.pagination import Page, PageMeta

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    status: Literal["success", "error"] = "success"
    message: str = ""
    data: T | None = None
    pagination: PageMeta | None = None

    @classmethod
    def success(cls, data=None, message: str = "Success") -> "ApiResponse":
        return cls(status="success", message=message, data=data)

    @classmethod
    def paginated(cls, page: Page, message: str = "Success") -> "ApiResponse":
        """List response: `data` is the page's items, `pagination` describes the page."""
        return cls(status="success", message=message, data=page.items, pagination=page.meta)

    @classmethod
    def error(cls, message: str) -> "ApiResponse":
        return cls(status="error", message=message)
