import pytest

from numpy import absolute, fft, flip

from mpm_sim.kspace import flash_order_kspace, load_h5_signal
from mpm_sim.utils import plot_list, load_nifti
from test.helper import TestHelper as Helper


class TestKspace:
    def test_flash_order_kspace(self):
        t, signal = load_h5_signal(Helper.data['signals'])
        sample, _ = load_nifti(Helper.data['seg'])
        kspace = flash_order_kspace(signal, dimensions=(1, 88, 124), echoes=6)[:, 0, :, 0, 0]
        plot_list([
            (flip(sample[200, 200:324, 200:288], axis=(0, 1)), "Original"),
            (absolute(fft.ifftshift(fft.ifft2(kspace))), "Recon")
        ])


if __name__ == '__main__':
    pytest.main(['-v'])
