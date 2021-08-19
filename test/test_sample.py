import pytest
import logging

from test.helper import TestHelper as Helper
from mpm_sim.utils import plot_list
from mpm_sim.sample import lookup_mpm
from mpm_sim.utils import load_nifti


class TestSample:
    def test_load_nifty(self):
        data, _ = load_nifti(Helper.data['seg'])
        # plot_matrix(data[:, :, Helper.test_slice], 'Original Segmentation')
        logging.info("Test Load Nifti")
        logging.info("Shape: ", data.shape, "; Size: ", data.size)

    def test_segmentation_lookup(self):
        seg_data, _ = load_nifti(Helper.data['seg'])
        x, y, z = seg_data.shape
        mpm_data = lookup_mpm(seg_data)
        plot_list([
            (seg_data[:, :, Helper.test_slice], 'Original Segmentation'),
            (mpm_data[:, :, Helper.test_slice, 0], 'T1 Map')
        ])
        logging.info("Test Segmentation Lookup")
        logging.info("Shape: ", mpm_data.shape, "; Size: ", mpm_data.size)
        assert mpm_data.shape == (x, y, z, 5), "Unexpected array shape."


if __name__ == '__main__':
    pytest.main(['-v'])
