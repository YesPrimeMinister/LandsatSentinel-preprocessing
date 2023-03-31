## This script preprocesses Landsat Collection 2 imagery from USGS EarthExplorer
# Specifically:
# Open the archived files into a temporary folder
# Select only important bands (B2-7, CloudDist)
# Crop to unbuffered bounding box (data/BB_povodi_WGS_UTM33.shp)
# Combine all features into rasters with each date as a separate band
# Cleanup - delete temporary folder
# Returns: Raster for each stack you select

# import libraries
from osgeo import gdal
import geopandas as gpd

from os import mkdir, listdir
from os.path import join, isdir, basename
from glob import glob
from shutil import rmtree, unpack_archive


class DownloadedToTimeSeries:
    def __init__(self, imagery_path, boundingbox_path, satellite='Landsat8'):
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
            #mkdir(temp_archive_dir)
            #unpack_archive(archive, extract_dir=temp_archive_dir)


    def select_bands(self):
        # Select only important bands (B2-7, CloudDist)
        print('Selecting bands to keep...')
        if self.satellite == 'Sentinel2':
            print(f'Unable to select suitable bands for {self.satellite}')
        elif self.satellite == 'Landsat5':
            print(f'Unable to select suitable bands for {self.satellite}')
        elif self.satellite == 'Landsat7':
            print(f'Unable to select suitable bands for {self.satellite}')
        elif self.satellite == 'Landsat8':
            self.bands = ('B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'CDIST')
        else:
            print(f'Unrecognised satellite: {self.satellite}')


    def find_filepaths(self):
        """Creates nested dict with paths to band files sorted by band and acquisition date."""
        self.bands_paths = {}
        for band in self.bands:
            self.bands_paths[band] = {}
            for temp_dir in self.temp_dirs:
                filepath = glob(join(temp_dir, f'*{band}.TIF'))
                date = basename(filepath[0])[17:25]
                self.bands_paths[band][date] = filepath[0]
        print(self.bands_paths)

    def combine_rasters(self):
        print('Combining into raster time series...')

        def _crop_by_bbox(raster_path, vector_path):
            # Crop to unbuffered bounding box (data/BB_povodi_WGS_UTM33.shp)
            cropped_raster = []
            return cropped_raster

        for band in self.bands_paths:
            for date in self.bands_paths[date]:
                cropped_raster = _crop_by_bbox(self.bands_paths)


    def cleanup(self):
        print(f'Cleaning up, deleting temporary folder {self.temp_folder}...')
        #rmtree(join(path_imagery, 'temp'))

# read vector files
#gdf_buffered = gpd.read_file(path_buffered)
#print(gdf_buffered)

if __name__ == "__main__":
    # set paths
    path_imagery = 'e:/data_krkonose/2022' # set to args
    path_boundingbox = 'data/BB_povodi_WGS_UTM33.shp'

    preprocess = DownloadedToTimeSeries(path_imagery, path_boundingbox)
    preprocess.extract_archives()
    preprocess.select_bands()
    preprocess.find_filepaths()

    preprocess.cleanup()
    print('Succesfully preprocessed!')
