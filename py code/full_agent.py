# full_agent_local.py
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
import re

# -------------------------------
# PostgreSQL connection
# -------------------------------
DB_NAME = "argo"
TABLE_NAME = "argo_data"
DB_USER = "postgres"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = 5432

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# -------------------------------
# English -> SQL column mapping
# -------------------------------
COLUMN_MAP = {
    "temperature": "TEMP",
    "salinity": "PSAL",
    "pressure": "PRES",
    "latitude": "LATITUDE",
    "longitude": "LONGITUDE",
    "juld": "JULD",
    "cycle": "CYCLE_NUMBER"
}

NUMERIC_COLUMNS = {"TEMP", "PSAL", "PRES"}

# -------------------------------
# English → SQL generator
# -------------------------------
# Columns stored as text but should be treated as numeric
NUMERIC_COLUMNS = {"TEMP", "PSAL", "PRES", "LATITUDE", "LONGITUDE"}

def english_to_sql_local(query):
    query = query.lower().strip()
    
    # <column> above/below <value>
    m = re.match(r'(\w+)\s+(above|below)\s+([\d\.\-]+)', query)
    if m:
        col, cond, val = m.groups()
        col = COLUMN_MAP.get(col, col)
        operator = ">" if cond == "above" else "<"
        if col in NUMERIC_COLUMNS:
            return f'SELECT "{col}"::float AS "{col}", "LONGITUDE"::float AS "LONGITUDE", "JULD" FROM {TABLE_NAME} WHERE "{col}"::float {operator} {val} LIMIT 1000'
        else:
            return f'SELECT "{col}", "LONGITUDE", "JULD" FROM {TABLE_NAME} WHERE "{col}" {operator} {val} LIMIT 1000'

    # <column> between <val1> and <val2>
    m = re.match(r'(\w+)\s+between\s+([\d\.\-]+)\s+and\s+([\d\.\-]+)', query)
    if m:
        col, val1, val2 = m.groups()
        col = COLUMN_MAP.get(col, col)
        if col in NUMERIC_COLUMNS:
            return f'SELECT "{col}"::float AS "{col}", "LONGITUDE"::float AS "LONGITUDE", "JULD" FROM {TABLE_NAME} WHERE "{col}"::float BETWEEN {val1} AND {val2} LIMIT 1000'
        else:
            return f'SELECT "{col}", "LONGITUDE", "JULD" FROM {TABLE_NAME} WHERE "{col}" BETWEEN {val1} AND {val2} LIMIT 1000'

    # Default: select first 100 rows
    return f'SELECT * FROM {TABLE_NAME} LIMIT 100'

# -------------------------------
# Execute SQL and plot
# -------------------------------
# -------------------------------
# Run SQL and plot numeric columns
# -------------------------------
def run_sql_and_plot(sql_query):
    with engine.connect() as conn:
        try:
            # Select only the key columns that contain real data
            df = pd.read_sql(sql_query, conn)
            if df.empty:
                print("No data returned for this query.")
                return

            # Convert numeric columns to float
            for col in ["TEMP", "PSAL", "PRES", "LATITUDE", "LONGITUDE"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Show first 20 rows
            print("\nQuery Result (first 20 rows):")
            print(df.head(20))

            # Determine what to plot
            numeric_cols = [c for c in ["TEMP", "PSAL", "PRES"] if c in df.columns and df[c].notna().any()]
            if numeric_cols:
                # Scatter plot of numeric vs location
                plt.figure(figsize=(8,6))
                plt.scatter(df["LATITUDE"], df[numeric_cols[0]], c='blue', alpha=0.5)
                plt.xlabel("Latitude")
                plt.ylabel(numeric_cols[0])
                plt.title(f"{numeric_cols[0]} vs Latitude")
                plt.grid(True)
                plt.show()

                # Line plot over time if JULD exists
                if "JULD" in df.columns:
                    plt.figure(figsize=(10,6))
                    plt.plot(pd.to_datetime(df["JULD"]), df[numeric_cols[0]], marker='o', linestyle='-')
                    plt.xlabel("JULD")
                    plt.ylabel(numeric_cols[0])
                    plt.title(f"{numeric_cols[0]} over Time")
                    plt.grid(True)
                    plt.show()

            else:
                print("No numeric data available to plot.")

        except Exception as e:
            print("SQL error:", e)

# -------------------------------
# Main loop
# -------------------------------
print(f"✅ Connected to PostgreSQL. English → SQL agent for '{TABLE_NAME}' is ready!")

while True:
    english_query = input("\nEnter English query (or 'exit' to quit): ")
    if english_query.lower() == "exit":
        break

    sql_query = english_to_sql_local(english_query)
    print("\nGenerated SQL:", sql_query)
    run_sql_and_plot(sql_query)
