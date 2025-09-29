import xarray as xr

# Example remote Argo NetCDF file URL
url = "https://data.nodc.noaa.gov/thredds/dodsC/argo/dac/meds/6901053/6901053_prof.nc"

# Open dataset directly
ds = xr.open_dataset(url)
print(ds)
