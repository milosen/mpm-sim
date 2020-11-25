import unittest

from mpm_sim.utils import plot_matrix, load_nifty


class TestSens(unittest.TestCase):
    def test_sens(self):
        data, header = load_nifty(
            "/nobackup/maki2/former_eminem2/vaculciakova/forNikola/coil_sens/Coils_ch10_Magnitude.nii"
        )
        plot_matrix(data[:, :, 200], 'Sens ch10 mag')
        data, header = load_nifty(
            "/nobackup/maki2/former_eminem2/vaculciakova/forNikola/coil_sens/Coils_ch20_Magnitude.nii"
        )
        plot_matrix(data[:, :, 200], 'Sens ch20 mag')
        data, header = load_nifty(
            "/nobackup/maki2/former_eminem2/vaculciakova/forNikola/coil_sens/Coils_ch30_Magnitude.nii"
        )
        plot_matrix(data[:, :, 200], 'Sens ch30 mag')


if __name__ == '__main__':
    unittest.main()
