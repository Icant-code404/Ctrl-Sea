import os

data_folder = r"\2025"  # top-level folder

# Walk through all subfolders
nc_files = []
for root, dirs, files in os.walk(data_folder):
    for f in files:
        if f.endswith(".nc"):
            nc_files.append(os.path.join(root, f))

print("Found .nc files:", nc_files)
