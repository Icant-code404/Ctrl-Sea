# main.py
"""
Fully self-contained CLI hybrid agent:
- SQL queries on Postgres
- Semantic search on Chroma
- Fallbacks for missing DBs
"""

import pandas as pd
from sqlalchemy import create_engine
import re
import os

# Try imports for embeddings + Chroma
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False
    print("⚠️ chromadb or sentence-transformers not installed. Semantic search disabled.")

# -------------------------------
# PostgreSQL config
# -------------------------------
DB_NAME = "postgres"
TABLE_NAME = "argo_data"
DB_USER = "postgres"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = 5432

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

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

# -------------------------------
# Vector DB setup
# -------------------------------
if HAS_VECTOR:
    CHROMA_PATH = "./chroma_db"
    COLLECTION_NAME = "argo_meta"
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        collection = client.get_collection(COLLECTION_NAME)
    else:
        print("⚠️ Chroma collection not found. Creating empty collection.")
        collection = client.create_collection(COLLECTION_NAME)
    model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------
# Helper functions
# -------------------------------
def english_to_sql(query: str) -> str:
    q = query.lower().strip()
    m = re.match(r'(\w+)\s+(above|below)\s+([\d\.\-]+)', q)
    if m:
        col, cond, val = m.groups()
        col = COLUMN_MAP.get(col, col)
        operator = ">" if cond == "above" else "<"
        return f'SELECT "{col}"::float AS "{col}", "LONGITUDE"::float, "LATITUDE"::float, "JULD" FROM {TABLE_NAME} WHERE "{col}"::float {operator} {val} LIMIT 1000'
    m = re.match(r'(\w+)\s+between\s+([\d\.\-]+)\s+and\s+([\d\.\-]+)', q)
    if m:
        col, val1, val2 = m.groups()
        col = COLUMN_MAP.get(col, col)
        return f'SELECT "{col}"::float AS "{col}", "LONGITUDE"::float, "LATITUDE"::float, "JULD" FROM {TABLE_NAME} WHERE "{col}"::float BETWEEN {val1} AND {val2} LIMIT 1000'
    return f'SELECT * FROM {TABLE_NAME} LIMIT 100'

def run_sql(sql_query: str) -> pd.DataFrame:
    try:
        with engine.connect() as conn:
            return pd.read_sql(sql_query, conn)
    except Exception as e:
        print(f"⚠️ SQL error: {e}")
        return pd.DataFrame()

def run_vector_query(user_query: str, top_k=5):
    if not HAS_VECTOR:
        return []
    try:
        q_emb = model.encode([user_query]).tolist()
        results = collection.query(query_embeddings=q_emb, n_results=top_k)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return [{"text": d, "metadata": m} for d, m in zip(docs, metas)]
    except Exception as e:
        print(f"⚠️ Vector search error: {e}")
        return []

def handle_query(user_query: str):
    lower = user_query.lower()
    if any(tok in lower for tok in ("between", "above", "below", "latitude", "longitude", "lat", "lon", "juld", "on", "in")):
        sql = english_to_sql(user_query)
        df = run_sql(sql)
        return {"type": "sql_result", "sql": sql, "data": df.head(10).to_dict(orient="records")}
    else:
        hits = run_vector_query(user_query)
        return {"type": "semantic_result", "data": hits}

def pretty_print(result):
    if result.get("type") == "sql_result":
        print("\n📊 SQL Query Result")
        print(f"SQL: {result.get('sql')}")
        rows = result.get("data", [])
        if not rows:
            print("No rows returned.")
            return
        df = pd.DataFrame(rows)
        # Format numeric columns to 2 decimal places
        for col in ["TEMP", "PSAL", "PRES", "LATITUDE", "LONGITUDE"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
        print(df.to_string(index=False))

    elif result.get("type") == "semantic_result":
        print("\n🔍 Semantic Search Result")
        hits = result.get("data", [])
        if not hits:
            print("No results found.")
            return
        # Flatten semantic hits into DataFrame
        df_rows = []
        for hit in hits:
            row = {"text": hit["text"]}
            row.update(hit.get("metadata", {}))
            df_rows.append(row)
        df = pd.DataFrame(df_rows)
        # Format numeric columns to 2 decimal places
        for col in ["TEMP", "PSAL", "PRES", "LATITUDE", "LONGITUDE"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
        print(df.to_string(index=False))

    else:
        print("\n⚠️ Error:", result.get("error", "Unknown error"))


# -------------------------------
# CLI loop
# -------------------------------
def main():
    print("=== FloatChat CLI Hybrid Agent ===")
    print("Type a query (or 'exit' to quit)\n")
    while True:
        user_query = input(">> ").strip()
        if user_query.lower() in ("exit", "quit"):
            print("Exiting. Bye!")
            break
        if not user_query:
            continue
        result = handle_query(user_query)
        pretty_print(result)
        print("-" * 60)

if __name__ == "__main__":
    main()
