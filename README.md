# LandsatSentinel-preprocessing

> Creates Best Available Pixel composites from Landsat and Sentinel imagery.

Used for classifications in a small region of Krkonose Mts., Czechia.

Created at the dept. of Applied Geoinformatics and Cartography, Faculty of Science, Charles University.

## Installation

The Python scripts reqire Python 3 (tested with Python 3.9) with external libraries which can be installed by running:


```sh
pip install rasterio, geopandas, numpy, matplotlib
```

or

```sh
conda install rasterio, geopandas, numpy, matplotlib
```

The R script should install the required libraries by itself. It requires "raster", "rgdal" and "lubridate".
Tested in RStudio 2022.02.1 using R version 4.1.3.

## Usage instructions

There are 4 steps to running this procedure successfuly:

1.	Download the imagery - The script uses Level-2 (atmospherically corrected) imagery downloaded from USGS EarthExplorer (Landsat - Collection 2) and Copernicus Open Access Hub (Sentinel-2). We suggest downloading all relevant imagery with cloud cover below 75 %.

2. 	Preprocess the imagery - Run `imagery_preprocessing.py`.
	In the command line, run in as:
	```sh
	imagery_preprocessing.py path/to/imagery name-of-satellite
	```
	If running from an editor, set values for variables `path_imagery` and `satellite`.
	
	Relevant values for `satellite` are "Sentinel2", "Landsat5", "Landsat7" and "Landsat8"
	
3.	Create the composite - Run `BestAvailablePixel.R` (recommended with RStudio)
	Adjust values for the path to script `functions.R`, year and the path to preprocessed imagery (lines 20, 28, 29).
	
	Subsequently experiment with finding the most suitable values for `target_doy`, `max_doff`, `min_cdist`, `max_cdist` and weights for the individual parameters (`w_doy`, `w_cdist`).

4.	Compute new bands - Run `imagery_compute_indices.py`
	In the command line, run in as:
	```sh
	imagery_compute_indices.py path/to/composite.tif name-of-satellite
	```
	If running from an editor, set values for variables `in_path` and `satellite`.
	
	Relevant values for `satellite` are the same as for `imagery_preprocessing.py` (step 2).
	