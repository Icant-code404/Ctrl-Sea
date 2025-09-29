# load_argo.py
import glob
import pandas as pd
import xarray as xr
from sqlalchemy import create_engine

# -------------------------------
# Configuration
# -------------------------------
NC_FOLDER = "./2025"         # folder containing .nc files
CSV_FILE = "argo_science.csv"
DB_NAME = "postgres"
TABLE_NAME = "argo_data"
CHUNK_SIZE = 500_000         # adjust for faster DB insert
DB_USER = "postgres"
DB_PASSWORD = "krispyfries"             # empty if using trust authentication
DB_HOST = "localhost"
DB_PORT = 5432

# -------------------------------
# Function to load all .nc files
# -------------------------------
def load_argo_dataframe():
    files = glob.glob(f"{NC_FOLDER}/**/*.nc", recursive=True)
    print(f"Found {len(files)} .nc files.")

    all_data = []

    for file in files:
        ds = xr.open_dataset(file)

        # Only extract variables that actually exist
        vars_to_extract = [v for v in ['N_PROF','N_LEVELS','PRES','TEMP','PSAL','LATITUDE','LONGITUDE','JULD'] if v in ds.variables]
        if not vars_to_extract:
            continue

        df = ds[vars_to_extract].to_dataframe().reset_index()
        all_data.append(df)

    if not all_data:
        print("❌ No valid data found in .nc files.")
        return pd.DataFrame()

    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"✅ Total rows combined: {len(combined_df)}")
    return combined_df

# -------------------------------
# Main script
# -------------------------------
if __name__ == "__main__":
    # Load data
    df = load_argo_dataframe()
    if df.empty:
        exit()

    # Save CSV for backup
    df.to_csv(CSV_FILE, index=False)
    print(f"💾 Saved science data to {CSV_FILE}")

    # Insert into PostgreSQL
    print("🗄️ Inserting into PostgreSQL...")
    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    total_rows = len(df)
    for start in range(0, total_rows, CHUNK_SIZE):
        end = start + CHUNK_SIZE
        chunk = df.iloc[start:end]
        chunk.to_sql(TABLE_NAME, engine, if_exists="append", index=False)
        print(f"Inserted rows {start} to {min(end, total_rows)}")

    print(f"✅ All {total_rows} rows inserted into '{TABLE_NAME}' in database '{DB_NAME}'")
