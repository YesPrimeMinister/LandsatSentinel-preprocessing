# LandsatSentinel-preprocessing

> Creates Best Available Pixel composites from Landsat and Sentinel imagery.

Used for classifications in a small region of Krkonose Mts., Czechia.

Created by Jakub Dvořák and Markéta Potůčková at the dept. of Applied Geoinformatics and Cartography, Faculty of Science, Charles University. Originally based on an exercise in the Earth Observation course at Humboldt University, Berlin.

## Installation

The Python scripts reqire Python 3 (tested with Python 3.9) with rasterio and geopandas, which can be installed by running:


```sh
pip install rasterio, geopandas
```

or

```sh
conda install rasterio, geopandas
```

The R script should install the required libraries by itself. It requires "raster", "rgdal" and "lubridate".
Tested in RStudio 2022.02.1 using R version 4.1.3.

## Usage instructions

There are 4 steps to running this procedure successfuly:

1.	Download the imagery - Save all imagery for a year into one folder. The script uses Level-2 (atmospherically corrected) imagery downloaded from USGS EarthExplorer (Landsat - Collection 2) and Copernicus Open Access Hub (Sentinel-2). We suggest downloading all relevant imagery with cloud cover below 75 %.

2. 	Preprocess the imagery - Run `imagery_preprocessing.py`.
	In the command line, run as:
	```sh
	imagery_preprocessing.py path/to/imagery name-of-satellite
	```
	If running from an editor, set values for variables `path_imagery` and `satellite`.
	
	The only relevant values for `satellite` are "Landsat5", "Landsat7" and "Landsat8" for now.
	
3.	Create the composite - Run `BestAvailablePixel.R` (recommended with RStudio)
	Adjust values for the path to script `functions.R`, year and the path to preprocessed imagery (lines 20, 28, 29).
	
	Subsequently experiment with finding the most suitable values for `target_doy`, `max_doff`, `min_cdist`, `max_cdist` and weights for the individual parameters (`w_doy`, `w_cdist`).

4.	Compute new bands - Run `imagery_compute_indices.py`
	In the command line, run as:
	```sh
	imagery_compute_indices.py path/to/composite.tif name-of-satellite
	```
	If running from an editor, set values for variables `in_path` and `satellite`.
	
	Relevant values for `satellite` are the same as for `imagery_preprocessing.py` (step 2).

## Results

The scripts produce two result rasters - _out_composite_with_indices.tif_ and _out_metadata_cdist-doy-score.tif_ 

*	_out_composite_with_indices.tif_ for landsat has 13 bands:

			L5/7 -	B1, B2, B3, B4, B5, B7, TCB, TCG, TCW, NDVI, NDII, NBR2, SRTM

			L8	 -	B2, B3, B4, B5, B6, B7, TCB, TCG, TCW, NDVI, NDII, NBR2, SRTM

*	_out_metadata_cdist-doy-score.tif_ has three bands:
			cdist - Cloud distance in metres
			doy - day of year from which the pixel is selected
			score - overall score for each pixel