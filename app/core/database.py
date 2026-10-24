from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import DATABASE_URL

# Opened/closed by the app lifespan (see main.py)
pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=5, kwargs={"row_factory": dict_row}, open=False)


def fetch_all(sql: str, params: dict | None = None) -> list[dict]:
    with pool.connection() as conn:
        return conn.execute(sql, params or {}).fetchall()


def fetch_one(sql: str, params: dict | None = None) -> dict | None:
    with pool.connection() as conn:
        return conn.execute(sql, params or {}).fetchone()


def execute(sql: str, params: dict | None = None) -> int:
    """Run a write statement; returns affected row count."""
    with pool.connection() as conn:
        return conn.execute(sql, params or {}).rowcount
