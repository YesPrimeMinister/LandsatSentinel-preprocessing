# Takes a Best Available Pixel composite from the R script and computes additional indices for classification
# Tasseled Cap indices, NDVI, NDII, NBR2, SRTM V3
# Export metadata raster - CDIST, DOY, SCORE
# Score multiplied by 10000

import rasterio
import rasterio.plot
import matplotlib.pyplot as plt
import numpy as np

from os.path import join


class Composite:
    def __init__(self, raster_path, satellite='Landsat8', srtm_path='data/srtm.tif'):
        self.raster_path = raster_path
        self.satellite = satellite
        self.srtm_path = srtm_path

        with rasterio.open(raster_path) as src:
            self.orig_arr = src.read()
            self.orig_meta = src.profile

        with rasterio.open(srtm_path) as src:
            self.srtm_arr = src.read()

        print(self.orig_meta)


    def _compute_tasseled_cap(self):
        orig_arr_float = self.orig_arr[:6, :, :].astype(np.float64) / 10_000
        if self.satellite == 'Landsat8':
            tcb = ((orig_arr_float[0, :, :] * 0.3029) +
                (orig_arr_float[1, :, :] * 0.2786) +
                (orig_arr_float[2, :, :] * 0.4733) +
                (orig_arr_float[3, :, :] * 0.5599) +
                (orig_arr_float[4, :, :] * 0.5080) +
                (orig_arr_float[5, :, :] * 0.1872))
            tcg = ((orig_arr_float[0, :, :] * -0.2941) +
                (orig_arr_float[1, :, :] * -0.2430) +
                (orig_arr_float[2, :, :] * -0.5424) +
                (orig_arr_float[3, :, :] * 0.7276) +
                (orig_arr_float[4, :, :] * 0.0713) +
                (orig_arr_float[5, :, :] * -0.1608))
            tcw = ((orig_arr_float[0, :, :] * 0.1511) +
                (orig_arr_float[1, :, :] * 0.1973) +
                (orig_arr_float[2, :, :] * 0.3283) +
                (orig_arr_float[3, :, :] * 0.3407) +
                (orig_arr_float[4, :, :] * -0.7117) +
                (orig_arr_float[5, :, :] * -0.4559))
            return np.stack([tcb, tcg, tcw], axis=0) * 1_000

    def _compute_normalised_difference(self, idx1, idx2):
        orig_arr_float = self.orig_arr[:6, :, :].astype(np.float64)
        return (((orig_arr_float[idx1, :, :] - orig_arr_float[idx2, :, :]) /
            (orig_arr_float[idx1, :, :] + orig_arr_float[idx2, :, :])) *
            10_000)

    def add_new_bands(self):
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
        # Creates raster
        out_meta = self.orig_meta
        out_meta['count'] = 3
        with rasterio.open(out_path, "w", **out_meta) as dest:
            dest.write(self.orig_arr[-3:, :, :])


    def export_composite(self, out_path):
        out_meta = self.orig_meta
        out_meta['count'] = self.orig_arr.shape[0] + 4
        out_meta['dtype'] = 'int16'
        out_meta['nodata'] = 0
        with rasterio.open(out_path, "w", **out_meta) as dest:
            dest.write(self.out_arr)


if __name__ == '__main__':

    root_path = 'E:/data_krkonose/2022/results'
    in_path = join(root_path, 'composite_2022-0_DOY200-100.tif')
    metadata_path = join(root_path, 'out_metadata_cdist-doy-score.tif')
    out_path = join(root_path, 'out_composite_with_indices.tif')

    composite = Composite(in_path)
    composite.export_metadata_raster(metadata_path)
    composite.add_new_bands()
    composite.export_composite(out_path)
