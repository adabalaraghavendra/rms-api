from abc import ABC, abstractmethod

from pymongo.database import Database


class Migration(ABC):
    """One versioned change to the database (indexes, data fixes, ...).

    Add a new file in migrations/versions/ named v<version>_<slug>.py that defines
    `class Migration(BaseMigration)`. Versions are applied in order and recorded in
    the `schema_migrations` collection, so each one runs only once.
    """

    version: str       # e.g. "0002" - must sort after the previous one
    description: str

    @abstractmethod
    def up(self, db: Database) -> None:
        """Apply the change."""

    def down(self, db: Database) -> None:
        """Undo the change (optional)."""
        raise NotImplementedError(f"Migration {self.version} cannot be undone")
