import importlib
import pkgutil
from datetime import datetime, timezone

from pymongo.database import Database

from migrations import versions
from migrations.base import Migration


class MigrationRunner:
    """Applies the migrations in migrations/versions/ in order and remembers which ones ran."""

    COLLECTION = "schema_migrations"

    def __init__(self, db: Database):
        self.db = db
        self.log = db[self.COLLECTION]
        self.log.create_index("version", unique=True, name="uq_schema_migrations_version")

    def all_migrations(self) -> list[Migration]:
        found = []
        for info in pkgutil.iter_modules(versions.__path__):
            module = importlib.import_module(f"{versions.__name__}.{info.name}")
            found.append(module.Migration())
        found.sort(key=lambda m: m.version)
        if len({m.version for m in found}) != len(found):
            raise RuntimeError("Two migrations share the same version number")
        return found

    def applied_versions(self) -> list[str]:
        return sorted(d["version"] for d in self.log.find({}, {"version": 1}))

    def pending(self) -> list[Migration]:
        done = set(self.applied_versions())
        return [m for m in self.all_migrations() if m.version not in done]

    def upgrade(self) -> list[str]:
        """Apply every pending migration; returns the versions applied."""
        applied = []
        for migration in self.pending():
            migration.up(self.db)
            self.log.insert_one({
                "version": migration.version,
                "description": migration.description,
                "applied_at": datetime.now(timezone.utc),
            })
            applied.append(migration.version)
        return applied

    def downgrade(self, steps: int = 1) -> list[str]:
        """Undo the most recently applied migrations."""
        by_version = {m.version: m for m in self.all_migrations()}
        reverted = []
        for version in reversed(self.applied_versions()[-steps:]):
            by_version[version].down(self.db)
            self.log.delete_one({"version": version})
            reverted.append(version)
        return reverted
