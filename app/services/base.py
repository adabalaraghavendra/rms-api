from pymongo.database import Database


class BaseService:
    """Parent of every service. Services hold business rules and use repositories;
    they never build queries themselves."""

    def __init__(self, db: Database):
        self.db = db
