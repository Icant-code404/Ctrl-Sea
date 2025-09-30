import json
import pandas as pd
from sqlalchemy import create_engine

# -------------------------
# Database connection
# -------------------------
DB_NAME = "argo"
DB_USER = "postgres"
DB_PASSWORD = "sAmOOl95"  # replace with your actual password
DB_HOST = "localhost"
DB_PORT = 5432

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# -------------------------
# Planner Agent (Mock)
# -------------------------
def planner_agent(english_query: str) -> str:
    """
    Mock planner agent that generates SQL from an English query.
    For demo purposes, we hardcode some rules.
    """
    if "temperature above" in english_query.lower():
        temp_val = ''.join(filter(str.isdigit, english_query))
        sql = f'SELECT "TEMP", "LONGITUDE", "JULD" FROM argo_data WHERE "TEMP"::float > {temp_val} LIMIT 1000'
        return sql
    # Default fallback
    return 'SELECT * FROM argo_data LIMIT 10'

# -------------------------
# Retriever Agent (Mock)
# -------------------------
def retriever_agent(sql_query: str) -> str:
    """
    Executes SQL and returns JSON.
    """
    df = pd.read_sql(sql_query, engine)
    return df.to_json(orient="records")  # JSON array of records

# -------------------------
# Frontend simulation
# -------------------------
if __name__ == "__main__":
    english_query = input("Enter English query (or 'exit' to quit): ")
    if english_query.lower() != "exit":
        sql_query = planner_agent(english_query)
        print(f"Planner generated SQL: {sql_query}")
        
        json_result = retriever_agent(sql_query)
        print(f"Retriever returned JSON:\n{json_result}")
