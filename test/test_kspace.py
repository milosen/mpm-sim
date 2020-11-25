import unittest

from mpm_sim.kspace import flash_order_kspace, load_h5_signal
from numpy import absolute, fft

from mpm_sim.utils import plot_matrix
from test.helper import TestHelper as Helper


class TestKspaceUtils(unittest.TestCase):
    def test_flash_order_kspace(self):
        t, m = load_h5_signal(Helper.data['signals'])
        kspace = flash_order_kspace(m, dimensions=(1, 88, 124), echos=6)[:, 0, :, 0, 0]
        plot_matrix(absolute(fft.ifftshift(fft.ifft2(kspace))))


if __name__ == '__main__':
    unittest.main()
