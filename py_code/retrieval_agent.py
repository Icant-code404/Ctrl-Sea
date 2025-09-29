# retrieval_agent.py

import pandas as pd
from sqlalchemy import create_engine

# Connect to PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:@localhost:5432/ARGO")

# Load dataset into pandas for retrieval
df = pd.read_sql("SELECT * FROM dummy_argo", engine)

# Simple retrieval function
def retrieval_agent(filters: dict):
    """
    filters: dictionary of column names and filter conditions
    Example: {"temperature": ">27", "latitude": "<20"}
    """
    query = pd.Series(True, index=df.index)  # Start with all True

    for col, cond in filters.items():
        if cond.startswith(">"):
            val = float(cond[1:])
            query &= df[col] > val
        elif cond.startswith("<"):
            val = float(cond[1:])
            query &= df[col] < val
        else:
            query &= df[col] == cond

    return df[query]

# -----------------------------
# Example Usage
# -----------------------------
if __name__ == "__main__":
    print("All rows with temperature > 27 and latitude < 20:")
    results = retrieval_agent({"temperature": ">27", "latitude": "<20"})
    print(results)
