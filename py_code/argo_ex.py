import pandas as pd
import numpy as np

# Number of dummy profiles
num_profiles = 10
num_measurements = 50

# Create dummy data
data = {
    "float_id": np.repeat(np.arange(1, num_profiles+1), num_measurements),
    "time": pd.date_range("2025-01-01", periods=num_measurements).tolist() * num_profiles,
    "latitude": np.random.uniform(-20, 20, num_profiles*num_measurements),
    "longitude": np.random.uniform(60, 90, num_profiles*num_measurements),
    "pressure": np.random.uniform(0, 2000, num_profiles*num_measurements),
    "temperature": np.random.uniform(2, 30, num_profiles*num_measurements),
    "salinity": np.random.uniform(30, 37, num_profiles*num_measurements)
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV (optional)
df.to_csv("dummy_argo.csv", index=False)

print("Dummy Argo dataset created successfully!")
print(df.head())
