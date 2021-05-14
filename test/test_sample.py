import unittest
import os

from numpy import ndarray

from test.helper import TestHelper as Helper
from mpm_sim.utils import plot_matrix
from mpm_sim.sample import lookup_mpm, \
    write_nifti_sample
from mpm_sim.utils import load_nifty


class TestSampleUtils(unittest.TestCase):
    def test_load_nifty(self):
        data, _ = load_nifty(Helper.data['nifti_file'])
        plot_matrix(data[:, :, Helper.test_slice], 'Original Segmentation')
        print("Test Load Nifti")
        print("Shape: ", data.shape, "; Size: ", data.size)
        self.assertIsInstance(data, ndarray, "Loaded data is not an ndarray.")

    def test_segmentation_lookup(self):
        seg_data, _ = load_nifty(Helper.data['nifti_file'])
        x, y, z = seg_data.shape
        mpm_data = lookup_mpm(seg_data)
        plot_matrix(mpm_data[:, :, Helper.test_slice, 0], 'MPM ()')
        print("Test Segmentation Lookup")
        print("Shape: ", mpm_data.shape, "; Size: ", mpm_data.size)
        self.assertEqual(mpm_data.shape, (x, y, z, 5), "Unexpected array shape.")

    def test_h5_sample(self, h5_filename='sample.h5'):
        if os.path.exists(h5_filename):
            os.remove(h5_filename)

        data = write_nifti_sample(Helper.data['nifti_file'], h5_filename=h5_filename,
                                  slicing=(slice(200, 201), slice(200, 324), slice(200, 288)),
                                  transpose_array=(0, 2, 1), interpolation_factor=6)

        self.assertTrue(os.path.exists(h5_filename))
        os.remove(h5_filename)
        self.assertIsInstance(data, ndarray)

        print("HDF5 sample shape (Params, X, Y, Z):", data.shape)
        plot_matrix(data[0, 0], 'JEMRIS sample')


if __name__ == '__main__':
    unittest.main()
