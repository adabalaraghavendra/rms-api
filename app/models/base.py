from dataclasses import dataclass
from datetime import datetime, timezone
from typing import ClassVar


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(kw_only=True)
class Document:
    """Parent of every model: a plain object that maps to one MongoDB document.

    `id` is the document's _id as text (None until it has been saved).
    Subclasses say which collection they live in and how to convert to/from the stored dict.
    """

    collection: ClassVar[str]
    id: str | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "Document":
        raise NotImplementedError

    def to_mongo(self) -> dict:
        """The dict to store (without _id; MongoDB assigns it on insert)."""
        raise NotImplementedError
