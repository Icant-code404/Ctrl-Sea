import pandas as pd
from sqlalchemy import create_engine

# Replace this with your actual CSV or DataFrame
csv_path = "argo_full_flattened.csv"
df = pd.read_csv(csv_path)

# Connect to the new database "argo"
engine = create_engine("postgresql+psycopg2://postgres@localhost:5432/argo")

# Write the DataFrame into the database
# This will create (or replace) a table called argo_data
df.to_sql("argo_data", engine, if_exists="replace", index=False, chunksize=10000)

print(f"✅ Inserted {len(df)} rows into the 'argo_data' table in 'argo' database.")
