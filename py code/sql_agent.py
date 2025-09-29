# sql_agent.py

from sqlalchemy import create_engine, text

# Connect to PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:@localhost:5432/ARGO")

# Simple SQL Agent function
def sql_agent(query: str):
    """
    Takes a natural language query,
    maps it to SQL, executes it, and returns results.
    """
    # Step 1: Convert query to SQL (manual mapping for now)
    # Later you can integrate LLM for automatic SQL generation
    if "temperature >" in query:
        threshold = float(query.split(">")[1].strip())
        sql_query = f"SELECT * FROM dummy_argo WHERE temperature > {threshold}"
    elif "average salinity" in query.lower():
        sql_query = "SELECT AVG(salinity) as avg_salinity FROM dummy_argo"
    else:
        sql_query = "SELECT * FROM dummy_argo LIMIT 10"

    # Step 2: Execute SQL
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        rows = result.fetchall()
    return rows

# -----------------------------
# Example Usage
# -----------------------------
if __name__ == "__main__":
    print("Rows with temperature > 27°C:")
    res = sql_agent("temperature > 27")
    for r in res:
        print(r)

    print("\nAverage salinity:")
    res = sql_agent("average salinity")
    for r in res:
        print(r)
