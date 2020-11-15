import unittest
import os

from mpm_utils.sample import load_nifty, interpolate, lookup_mpm, \
    jemris_sample_from_nifti
from numpy import ndarray

from test.helper import TestHelper as Helper
from test.helper import plot_matrix


class TestSampleUtils(unittest.TestCase):
    def test_load_nifty(self):
        data, _ = load_nifty(Helper.data['nifti_file'])
        plot_matrix(data[:, :, Helper.test_slice], 'Original Segmentation')
        print("Test Load Nifti")
        print("Shape: ", data.shape, "; Size: ", data.size)
        self.assertIsInstance(data, ndarray, "Loaded data is not an ndarray.")

    def test_interpolation(self, factor=2):
        data, _ = load_nifty(Helper.data['nifti_file'])
        interpolated_data = interpolate(data, factor=factor)
        plot_matrix(
            interpolated_data[:, :, int(Helper.test_slice*factor)],
            'Interpolated Segmentation'
        )
        print("Test Interpolation")
        print("Shape: ", interpolated_data.shape, "; Size: ", interpolated_data.size)
        self.assertEqual(factor**3*data.size, interpolated_data.size, "Unexpected array size.")

    def test_segmentation_lookup(self):
        seg_data, _ = load_nifty(Helper.data['nifti_file'])
        x, y, z = seg_data.shape
        mpm_data = lookup_mpm(seg_data)
        plot_matrix(mpm_data[:, :, Helper.test_slice, 0], 'MPM')
        print("Test Segmentation Lookup")
        print("Shape: ", mpm_data.shape, "; Size: ", mpm_data.size)
        self.assertEqual(mpm_data.shape, (x, y, z, 5), "Unexpected array shape.")

    def test_h5_sample(self, h5_filename='sample.h5'):
        if os.path.exists(h5_filename):
            os.remove(h5_filename)

        data = jemris_sample_from_nifti(Helper.data['nifti_file'], h5_filename=h5_filename,
                                        slicing=(slice(200, 201), slice(200, 324), slice(200, 288)),
                                        transpose_array=(0, 2, 1), interpolation_factor=4)

        self.assertTrue(os.path.exists(h5_filename))
        self.assertIsInstance(data, ndarray)

        print("HDF5 sample shape (Params, X, Y, Z):", data.shape)
        plot_matrix(data[0, 0], 'JEMRIS sample')


if __name__ == '__main__':
    unittest.main()
