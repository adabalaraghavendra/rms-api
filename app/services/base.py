from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError


class BaseService:
    def __init__(self, db: Session):
        self.db = db

    def commit(self) -> None:
        """Save the unit of work; a database constraint violation becomes a 409."""
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Record already exists or is in use") from exc
