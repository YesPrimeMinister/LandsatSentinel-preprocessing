## This script preprocesses Landsat Collection 2 imagery from USGS EarthExplorer
# Specifically:
# Open the archived files into a temporary folder
# Select only important bands (B1-7, CloudDist)
# Crop imagery by buffered bounding box (data/BB_povodi_WGS_UTM33_buffer500m.shp)
# Compute Additional spectral indices
# Crop to unbuffered bounding box (data/BB_povodi_WGS_UTM33.shp)
# Combine all features into rasters with each date as a separate band
# Cleanup - delete temporary folder
# Returns: Raster for each stack you select


import geopandas as gpd
