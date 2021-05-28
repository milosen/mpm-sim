import numpy as np
import h5py
from pathlib import Path

from mpm_sim.utils import load_nifty

if __name__ == '__main__':
    n_coils = 32
    base = '/nobackup/maki2/former_eminem2/vaculciakova/forNikola/coil_sens'
    magmaps_nii = [f'{base}/Coils_ch{ch}_Magnitude.nii' for ch in range(1, n_coils + 1)]
    phasemaps_nii = [f'{base}/Coils_ch{ch}_Phase.nii' for ch in range(1, n_coils + 1)]

    data_magmaps = np.stack([load_nifty(magmap_nii)[0] for magmap_nii in magmaps_nii])
    data_phasemaps = np.stack([load_nifty(phasemap_nii)[0] for phasemap_nii in phasemaps_nii])

    data_maps = np.stack([data_magmaps, data_phasemaps])

    with h5py.File(Path("data/sensmaps.h5")) as hf:
        maps = hf.create_group('maps')
        maps.create_dataset('data', data=data_maps)

    print(data_maps.shape)
