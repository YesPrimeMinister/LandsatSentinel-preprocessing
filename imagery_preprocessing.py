# -*- coding: utf-8 -*-
"""
This script preprocesses Landsat Collection 2 imagery from USGS EarthExplorer.

Arguments:
    path to the folder with downloaded imagery
    satellite name - default 'Landsat8'
"""

import geopandas as gpd
import rasterio
import rasterio.mask
import numpy as np
import matplotlib.pyplot as plt

import sys
from os import mkdir, listdir
from os.path import join, isdir, basename, isfile
from glob import glob
from shutil import rmtree, unpack_archive


class DownloadedToTimeSeries:
    def __init__(self, imagery_path, boundingbox_path, satellite='Landsat8'):
        """Inits class, loads AOI to memory."""
        self.imagery_path = imagery_path
        self.boundingbox_path = boundingbox_path
        self.boundingbox_gdf = gpd.read_file(boundingbox_path)
        self.satellite = satellite

    def extract_archives(self):
        """Open archives in path_archives and put contents into temporary dir"""
        print('Extracting imagery archives...')
        # Get filenames of downloaded archives
        archives = glob(join(self.imagery_path, '*.tar'))

        # Create temp folder
        self.temp_folder = join(self.imagery_path, 'temp')
        if not isdir(self.temp_folder):
            mkdir(self.temp_folder)
            print(f'Created temporary directory: {self.temp_folder}')

        self.temp_dirs = []
        for archive in archives:
            temp_archive_dir = join(self.temp_folder,
                                    basename(archive).split('.')[0])
            self.temp_dirs.append(temp_archive_dir)
            # Temporarily commented out to not extract imagery during each test run
            mkdir(temp_archive_dir)
            unpack_archive(archive, extract_dir=temp_archive_dir)


    def select_bands(self):
        """Selects only relevant bands (Visible, NIR, SWIR, CloudDist)"""
        print('Selecting bands to keep...')
        if self.satellite == 'Sentinel2':
            print(f'Unable to select suitable bands for {self.satellite}')
        elif self.satellite == 'Landsat5':
            self.bands = ('B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'CDIST')
        elif self.satellite == 'Landsat7':
            self.bands = ('B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'CDIST')
        elif self.satellite == 'Landsat8':
            self.bands = ('B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'CDIST')
        else:
            print(f'Unrecognised satellite: {self.satellite}.')


    def find_filepaths(self):
        """Creates nested dict with paths to band files sorted by band and acquisition date."""
        self.bands_paths = {}
        for band in self.bands:
            self.bands_paths[band] = {}
            for temp_dir in self.temp_dirs:
                filepath = glob(join(temp_dir, f'*{band}.TIF'))
                date = basename(filepath[0])[17:25]
                self.bands_paths[band][date] = filepath[0]


    def combine_rasters(self):
        """Combine all spectral bands into rasters with each date as a separate band"""
        print('Combining into raster time series...')

        def _crop_by_bbox(raster_path):
            """Crop to unbuffered bounding box (data/BB_povodi_WGS_UTM33.shp)"""
            with rasterio.open(raster_path) as src:
                out_image, out_transform = rasterio.mask.mask(src,
                    self.boundingbox_gdf.geometry, crop=True)
                out_meta = src.meta
                out_meta.update({"driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform})
            return out_image, out_meta

        for band in self.bands_paths:
            self.sorted_dates = sorted(self.bands_paths[band].keys())
            cropped_rasters = {}
            for date in self.sorted_dates:
                raster_path = self.bands_paths[band][date]
                cropped_rasters[date] = _crop_by_bbox(raster_path)

            # Create empty arr
            cropped_shape = cropped_rasters[self.sorted_dates[0]][0].shape

            arr_stack = np.empty((len(self.sorted_dates), cropped_shape[1],
                                  cropped_shape[2]), dtype=np.uint16)
            for idx, cropped_raster_date in enumerate(cropped_rasters):
                arr_stack[idx, :, :] = cropped_rasters[cropped_raster_date][0][0,:,:]

            # save resulting raster
            out_filename = f'time_series_{self.sorted_dates[0]}_{self.sorted_dates[-1]}_{band}.tif'
            out_path = join(self.imagery_path, out_filename)
            out_metadata = cropped_rasters[self.sorted_dates[0]][1]
            out_metadata.update({"count": len(self.sorted_dates)})
            with rasterio.open(out_path, "w", **out_metadata) as dest:
                dest.write(arr_stack)


    def save_dates(self):
        """Exports the resulting arrays."""
        out_path = join(self.imagery_path, 'acquisition_dates.txt')
        if isfile(out_path):
            rmtree(out_path)
        with open(out_path, 'a') as txt:
            for date in self.sorted_dates:
                txt.write(f'{date}\n')


    def cleanup(self):
        """Deletes temporary folder"""
        print(f'Cleaning up, deleting temporary folder {self.temp_folder}...')
        rmtree(self.temp_folder)


if __name__ == "__main__":
    # set paths
    path_boundingbox = 'data/BB_povodi_WGS_UTM33_buffer500m.shp'

    if len(sys.argv) > 1:
        path_imagery = sys.argv[1]      #'e:/data_krkonose/2022'
        if len(sys.argv) > 2:
            satellite = sys.argv[2]
        else:
            satellite = 'Landsat8'
    else:
        path_imagery = 'e:/data_krkonose/2022'
        satellite = 'Landsat8'


    preprocess = DownloadedToTimeSeries(path_imagery, path_boundingbox, satellite)
    preprocess.extract_archives()
    preprocess.select_bands()
    preprocess.find_filepaths()
    preprocess.combine_rasters()
    preprocess.save_dates()
    preprocess.cleanup()
    print('Succesfully preprocessed!')
