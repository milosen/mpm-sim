import pytest

from mpm_sim.utils import load_nifti, plot_list


class TestSensmap:
    def test_sensmap(self):
        data1, _ = load_nifti(
            "data/sensmaps/Coils_ch1_Magnitude.nii"
        )
        data2, _ = load_nifti(
            "data/sensmaps/Coils_ch2_Magnitude.nii"
        )
        plot_list([(data1[:, :, 200], 'Sens ch1 mag'), (data2[:, :, 200], 'Sens ch2 mag')])


if __name__ == '__main__':
    pytest.main(['-v'])
