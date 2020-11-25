import numpy as np
import h5py

from mpm_sim.utils import load_nifty, preprocess_array


def write_nifti_sensmap(sensmap_nii: str, sensmap_h5: str,
                        slicing=(slice(None, None), slice(None, None), slice(None, None)),
                        transpose_array=(0, 1, 2),
                        interpolation_factor=1) -> np.ndarray:
    data, _ = load_nifty(sensmap_nii)
    data = preprocess_array(data, slicing, transpose_array, interpolation_factor)
    with h5py.File(sensmap_h5, 'w') as hf:
        maps = hf.create_group('maps')
        magnitude = maps.create_group('magnitude')
        magnitude.create_dataset('00', data=data)
        phase = maps.create_group('phase')
        phase.create_dataset('00', data=data)
    return data
