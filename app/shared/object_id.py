"""MongoDB ids are ObjectIds in the database and plain strings in the API."""
from bson import ObjectId
from bson.errors import InvalidId

from app.core.exceptions import BadRequestError


def to_object_id(value: str | None) -> ObjectId | None:
    """'65f0...' -> ObjectId, or None when the text is not a valid id."""
    try:
        return ObjectId(value) if value else None
    except (InvalidId, TypeError):
        return None


def require_object_id(value: str, what: str = "id") -> ObjectId:
    oid = to_object_id(value)
    if oid is None:
        raise BadRequestError(f"Invalid {what}")
    return oid
