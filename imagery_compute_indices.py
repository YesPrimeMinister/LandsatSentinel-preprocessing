# -*- coding: utf-8 -*-
"""
Adds new features to a Best Available Pixel composite.

Arguments:
    path to the R script composite
    satellite name - default 'Landsat8'
"""


import rasterio
import rasterio.plot
import matplotlib.pyplot as plt
import numpy as np

from os.path import join, dirname
import sys


class Composite:
    """Takes a Best Available Pixel composite from the R script and computes additional indices for classification."""
    """Exports two rasters:
    1.  composite with spectral bands, Tasseled Cap indices, NDVI, NDII, NBR2 and SRTM V3
    2.  metadata raster with three bands - CDIST, DOY and overall SCORE
    """

    def __init__(self, raster_path, satellite='Landsat8', srtm_path='data/srtm.tif'):
        """Initialises the class, reads rasters to memory."""
        self.raster_path = raster_path
        self.satellite = satellite
        self.srtm_path = srtm_path

        with rasterio.open(raster_path) as src:
            self.orig_arr = src.read()
            self.orig_meta = src.profile

        with rasterio.open(srtm_path) as src:
            self.srtm_arr = src.read()


    def _compute_tasseled_cap(self):
        """Computes first three tasseled cap components - brightness, greenness, wetness."""

        if self.satellite == 'Sentinel2':
            # based on doi.org/10.1109/JSTARS.2019.2938388
            # TBD
            pass

        if self.satellite == 'Landsat5' or self.satellite == 'Landsat7':
            # based on doi.org/10.1109/TGRS.1984.350619
            tcb = ((self.orig_arr[0, :, :] * 0.3037) +
                (self.orig_arr[1, :, :] * 0.2793) +
                (self.orig_arr[2, :, :] * 0.4743) +
                (self.orig_arr[3, :, :] * 0.5585) +
                (self.orig_arr[4, :, :] * 0.5082) +
                (self.orig_arr[5, :, :] * 0.1863))
            tcg = ((self.orig_arr[0, :, :] * -0.2848) +
                (self.orig_arr[1, :, :] * -0.2435) +
                (self.orig_arr[2, :, :] * -0.5463) +
                (self.orig_arr[3, :, :] * 0.7243) +
                (self.orig_arr[4, :, :] * 0.0840) +
                (self.orig_arr[5, :, :] * -0.1800))
            tcw = ((self.orig_arr[0, :, :] * 0.1509) +
                (self.orig_arr[1, :, :] * 0.1973) +
                (self.orig_arr[2, :, :] * 0.3279) +
                (self.orig_arr[3, :, :] * 0.3407) +
                (self.orig_arr[4, :, :] * -0.7112) +
                (self.orig_arr[5, :, :] * -0.4572))

        if self.satellite == 'Landsat8':
            # based on doi.org/10.1080/2150704X.2014.915434
            tcb = ((self.orig_arr[0, :, :] * 0.3029) +
                (self.orig_arr[1, :, :] * 0.2786) +
                (self.orig_arr[2, :, :] * 0.4733) +
                (self.orig_arr[3, :, :] * 0.5599) +
                (self.orig_arr[4, :, :] * 0.5080) +
                (self.orig_arr[5, :, :] * 0.1872))
            tcg = ((self.orig_arr[0, :, :] * -0.2941) +
                (self.orig_arr[1, :, :] * -0.2430) +
                (self.orig_arr[2, :, :] * -0.5424) +
                (self.orig_arr[3, :, :] * 0.7276) +
                (self.orig_arr[4, :, :] * 0.0713) +
                (self.orig_arr[5, :, :] * -0.1608))
            tcw = ((self.orig_arr[0, :, :] * 0.1511) +
                (self.orig_arr[1, :, :] * 0.1973) +
                (self.orig_arr[2, :, :] * 0.3283) +
                (self.orig_arr[3, :, :] * 0.3407) +
                (self.orig_arr[4, :, :] * -0.7117) +
                (self.orig_arr[5, :, :] * -0.4559))

        return np.stack([tcb, tcg, tcw], axis=0)

    def _compute_normalised_difference(self, idx1, idx2):
        """Compute normalised difference based on band indices (b1-b2)/(b1+b2).
        Multiply the result by 10 000."""
        a = self.orig_arr[idx1, :, :]
        b = self.orig_arr[idx2, :, :]
        return ((a - b) / (a + b)) * 10_000

    def add_new_bands(self):
        """Create an array with new bands (original+TC+NDVI+NDII+NBR2+SRTM)"""
        shape = self.orig_arr.shape
        self.out_arr = np.empty((shape[0]+4, shape[1], shape[2]))
        # reflectance
        self.out_arr[:-7, :, :] = self.orig_arr[:-3, :, :]
        # Tasseled Cap
        self.out_arr[-7:-4, :, :] = self._compute_tasseled_cap()
        # NDVI
        self.out_arr[-4, :, :] = self._compute_normalised_difference(3, 2)
        # NDII
        self.out_arr[-3, :, :] = self._compute_normalised_difference(4, 5)
        # NBR2
        self.out_arr[-2, :, :] = self._compute_normalised_difference(3, 5)
        # SRTM
        self.out_arr[-1, :, :] = self.srtm_arr


    def export_metadata_raster(self, out_path):
        """Creates and saves a metadata raster with three bands - CDIST, DOY, SCORE."""
        out_meta = self.orig_meta
        out_meta['count'] = 3
        with rasterio.open(out_path, "w", **out_meta) as dest:
            dest.write(self.orig_arr[-3:, :, :])


    def export_composite(self, out_path):
        """Export the composite with new bands to file."""
        out_meta = self.orig_meta
        out_meta['count'] = self.orig_arr.shape[0] + 4
        out_meta['dtype'] = 'int16'
        out_meta['nodata'] = 0
        with rasterio.open(out_path, "w", **out_meta) as dest:
            dest.write(self.out_arr)


if __name__ == '__main__':
    # this parameter need to be adjusted
    if len(sys.argv) > 1:
        in_path = sys.argv[1]
        if len(sys.argv) > 2:
            satellite = sys.argv[2]
        else:
            satellite = 'Landsat8'
    else:
        in_path = 'E:/data_krkonose/2022/results/composite_2022-0_DOY200-100.tif'
        satellite = 'Landsat8'

    # relevant paths
    root_path = dirname(in_path)
    metadata_path = join(root_path, 'out_metadata_cdist-doy-score.tif')
    out_path = join(root_path, 'out_composite_with_indices.tif')

    # computation itself
    composite = Composite(in_path, satellite)
    composite.export_metadata_raster(metadata_path)
    composite.add_new_bands()
    composite.export_composite(out_path)
    print(f'Successfully exported composite to {out_path}')
