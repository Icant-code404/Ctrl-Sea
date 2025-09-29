import xarray as xr
import pandas as pd
import glob

# Top-level data folder
data_folder = r"C:\SIH-ARGO\2025"

# Recursively collect all .nc files
nc_files = glob.glob(f"{data_folder}/**/*.nc", recursive=True)
print(f"Found {len(nc_files)} .nc files.")

all_dfs = []

for f in nc_files:
    try:
        ds = xr.open_dataset(f)
        
        # Only take important vars (check which ones exist)
        vars_to_extract = [v for v in ["LATITUDE", "LONGITUDE", "JULD", "PRES", "TEMP", "PSAL"] if v in ds.variables]
        
        if not vars_to_extract:
            print(f"⚠️ Skipping {f} - no science vars found")
            continue

        df = ds[vars_to_extract].to_dataframe().reset_index()

        if not df.empty:
            all_dfs.append(df)

        ds.close()
    except Exception as e:
        print(f"⚠️ Error processing {f}: {e}")

# Combine
if all_dfs:
    full_df = pd.concat(all_dfs, ignore_index=True)
    print(full_df.head())
    print("✅ Total rows combined:", len(full_df))

    full_df.to_csv("argo_science.csv", index=False)
    print("💾 Saved science data to argo_science.csv")
else:
    print("❌ Still no data extracted. Try inspecting one file manually.")
