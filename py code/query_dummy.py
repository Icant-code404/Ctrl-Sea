import pandas as pd

csv_path = "argo_full_flattened.csv"
df = pd.read_csv(csv_path)

print("Rows:", len(df))
print("Columns:", list(df.columns))
print(df.head())
