# full_argo_demo.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text

# ------------------------------
# 1️⃣ Connect to PostgreSQL
# ------------------------------
# Note: no password for your setup
engine = create_engine("postgresql+psycopg2://postgres:@localhost:5432/ARGO")

# ------------------------------
# 2️⃣ Create a dummy Argo dataset
# ------------------------------
np.random.seed(42)
num_records = 100

dummy_data = {
    "id": range(1, num_records + 1),
    "latitude": np.random.uniform(5, 25, num_records),   # roughly Indian Ocean latitudes
    "longitude": np.random.uniform(65, 95, num_records), # roughly Indian Ocean longitudes
    "temperature": np.random.uniform(20, 30, num_records), # in Celsius
    "salinity": np.random.uniform(34, 36, num_records),    # PSU
    "depth": np.random.uniform(0, 2000, num_records)       # in meters
}

df = pd.DataFrame(dummy_data)

# ------------------------------
# 3️⃣ Load dataset into PostgreSQL
# ------------------------------
df.to_sql("dummy_argo", engine, if_exists="replace", index=False)
print("✅ Dummy dataset loaded into PostgreSQL.")

# ------------------------------
# 4️⃣ Query the dataset
# ------------------------------
with engine.connect() as conn:
    print("\nAll rows with id and temperature:")
    result = conn.execute(text("SELECT id, temperature FROM dummy_argo"))
    for row in result:
        print(row)

    print("\nRows with temperature > 27°C:")
    result = conn.execute(text("SELECT * FROM dummy_argo WHERE temperature > 27"))
    for row in result:
        print(row)

# ------------------------------
# 5️⃣ Load into pandas for visualization
# ------------------------------
df_from_db = pd.read_sql("SELECT * FROM dummy_argo", engine)

# ------------------------------
# 6️⃣ Visualize the dataset
# ------------------------------
sns.set(style="whitegrid")

# Scatter plot: Temperature vs Location
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_from_db,
    x="longitude",
    y="latitude",
    hue="temperature",
    palette="coolwarm",
    s=100
)
plt.title("Dummy Argo Float Locations with Temperature")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()

# Histogram: Temperature distribution
plt.figure(figsize=(8, 5))
sns.histplot(df_from_db["temperature"], bins=15, kde=True, color="orange")
plt.title("Temperature Distribution")
plt.xlabel("Temperature (°C)")
plt.ylabel("Count")
plt.show()

# Scatter plot: Salinity vs Depth
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df_from_db, x="depth", y="salinity", hue="temperature", palette="viridis")
plt.title("Salinity vs Depth")
plt.xlabel("Depth (m)")
plt.ylabel("Salinity (PSU)")
plt.show()
