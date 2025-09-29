# db.py
from sqlalchemy import create_engine, text
import os
from urllib.parse import quote_plus

DB_USER = os.getenv("PGUSER", "postgres")
DB_PASS = os.getenv("PGPASS", "postgres")
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("PGPORT", "5432")
DB_NAME = os.getenv("PGNAME", "argo")

def get_engine():
    password = quote_plus(DB_PASS)
    url = f"postgresql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url, pool_size=10, max_overflow=20)

def execute_sql(sql: str, params: dict = None):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return [dict(row) for row in result]
