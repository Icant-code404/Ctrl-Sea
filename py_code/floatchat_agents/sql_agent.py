# sql_agent.py
import pandas as pd
from sqlalchemy import create_engine
import re

# -------------------------------
# DB Config (adjust if needed)
# -------------------------------
DB_NAME = "postgres"
TABLE_NAME = "argo_data"
DB_USER = "postgres"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = 5432

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Column mapping
COLUMN_MAP = {
    "temperature": "TEMP",
    "salinity": "PSAL",
    "pressure": "PRES",
    "latitude": "LATITUDE",
    "longitude": "LONGITUDE",
    "juld": "JULD",
    "cycle": "CYCLE_NUMBER"
}
NUMERIC_COLUMNS = {"TEMP", "PSAL", "PRES", "LATITUDE", "LONGITUDE"}

class SQLAgent:
    def __init__(self, engine, table_name=TABLE_NAME):
        self.engine = engine
        self.table = table_name

    def english_to_sql(self, query: str) -> str:
        q = query.lower().strip()

        # <column> above/below <value>
        m = re.match(r'(\w+)\s+(above|below)\s+([\d\.\-]+)', q)
        if m:
            col, cond, val = m.groups()
            col = COLUMN_MAP.get(col, col)
            operator = ">" if cond == "above" else "<"
            return f'SELECT "{col}"::float AS "{col}", "LONGITUDE"::float, "LATITUDE"::float, "JULD" FROM {self.table} WHERE "{col}"::float {operator} {val} LIMIT 1000'

        # <column> between <val1> and <val2>
        m = re.match(r'(\w+)\s+between\s+([\d\.\-]+)\s+and\s+([\d\.\-]+)', q)
        if m:
            col, val1, val2 = m.groups()
            col = COLUMN_MAP.get(col, col)
            return f'SELECT "{col}"::float AS "{col}", "LONGITUDE"::float, "LATITUDE"::float, "JULD" FROM {self.table} WHERE "{col}"::float BETWEEN {val1} AND {val2} LIMIT 1000'

        # Default: select first 100
        return f'SELECT * FROM {self.table} LIMIT 100'

    def run_query(self, sql_query: str) -> pd.DataFrame:
        with self.engine.connect() as conn:
            return pd.read_sql(sql_query, conn)

