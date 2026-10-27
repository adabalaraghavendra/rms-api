from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import DATABASE_URL

# Opened/closed by the app lifespan (see main.py).
# Neon drops idle connections and suspends the database when unused, so pooled
# connections can silently die. The settings below keep the pool healthy:
pool = ConnectionPool(
    DATABASE_URL,
    min_size=1,
    max_size=5,
    kwargs={
        "row_factory": dict_row,
        "connect_timeout": 15,      # allow time for a suspended Neon database to wake up
        "keepalives": 1,            # TCP keepalives so idle links are not silently dropped
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 3,
    },
    check=ConnectionPool.check_connection,  # test a connection before use; replace it if dead
    max_idle=120,                           # close connections idle for 2 minutes
    max_lifetime=600,                       # recycle every 10 minutes
    open=False,
)


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
