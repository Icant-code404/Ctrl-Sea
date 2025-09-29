import argopy
ds = argopy.DataFetcher().float("6901844").to_xarray()
print(ds)
