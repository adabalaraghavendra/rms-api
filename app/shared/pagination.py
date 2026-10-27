"""Pagination used by every listing API.

Query:    ?page=1&page_size=10
Response: "pagination": {page, page_size, total_items, total_pages, has_next, has_prev}
"""
from collections.abc import Callable
from dataclasses import dataclass
from math import ceil
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class PageParams:
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_page_params(
    page: int = Query(1, ge=1, description="Page number, starting at 1"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
) -> PageParams:
    """FastAPI dependency: `params: PageParams = Depends(get_page_params)`."""
    return PageParams(page=page, page_size=page_size)


class PageMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


@dataclass(frozen=True)
class Page(Generic[T]):
    """One page of results plus what is needed to describe it."""

    items: list[T]
    total: int
    params: PageParams

    @property
    def meta(self) -> PageMeta:
        pages = ceil(self.total / self.params.page_size) if self.total else 0
        return PageMeta(
            page=self.params.page,
            page_size=self.params.page_size,
            total_items=self.total,
            total_pages=pages,
            has_next=self.params.page < pages,
            has_prev=self.params.page > 1,
        )

    def map(self, fn: Callable[[T], U]) -> "Page[U]":
        """Convert each item (e.g. ORM entity -> response schema), keeping the paging info."""
        return Page(items=[fn(i) for i in self.items], total=self.total, params=self.params)
