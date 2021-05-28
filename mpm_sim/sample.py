from typing import Union, Tuple
from pathlib import Path
import logging

import numpy as np
import h5py


import mpm_sim.utils as mpm_utils


class BrainModel:
    """Definition of the lookup table for building multi-parametric
    maps from segmentations"""
    tissue = np.array(
        # T1, T2, T2*[ms], M0, CS[rad/sec]
        [[0, 0, 0, 0.00, 0],  # Background
         [2569, 329, 158, 1.00, 0],  # 1 = CSF
         [833, 83, 69, 0.86, 0],  # 2 = GM
         [500, 70, 61, 0.77, 0],  # 3 = WM
         [350, 70, 58, 1.00, 220*2*np.pi],  # 4 = Fat (CS @ 1.5 Tesla)
         [900, 47, 30, 1.00, 0],  # % 5 = Muscle / Skin
         [2569, 329, 58, 1.00, 0],  # % 6 = Skin
         [0, 0, 0, 0.00, 0],  # 7 = Skull
         [833, 83, 69, 0.86, 0],  # 8 = Glial Matter
         [500, 70, 61, 0.77, 0]]  # 9 = Meat
    )
    classes = 9


def lookup_mpm(data: np.ndarray) -> np.ndarray:
    """Turn segmentation into multi-parametric map by via lookup.

    Replace tissue segmented voxel with respective multi-parameter vector
    (of length 5) each representing one spin isochromat:

    - M0 (equilibrium magnetization)
    - T1, T2, T2*[ms] (relaxation values)
    - CS[rad/sec] (chemical shift)

    :param data: segmented imaging data
    :return: multi-parametric map with shape (<shape of data>, 5)
    """
    data = data.astype(int)
    return BrainModel.tissue[data].astype(float)


def mk_h5_sample(data: np.ndarray, db: Union[np.ndarray, None] = None) -> np.ndarray:
    """Convert data to JEMRIS readable format.

    Convert data to hdf5 format in JEMRIS readable configuration and return the object
    for further processing (adapted from the JEMRIS matlab-gui).
    :param data: multi-parameter map
    :param db: off-resonance in rad/sec for each spin isochromat (shape equal to shape of spin isochromat matrix)
    :return: h5 object
    """
    data[data <= 0] = 0
    sample = np.zeros(data.shape)
    for i in range(3):
        sample[:, :, :, i+1] = np.reciprocal(data[:, :, :, i], where=data[:, :, :, i] > 0)
    sample[:, :, :, 0] = data[:, :, :, 3]
    if db is None:
        sample[:, :, :, 4] = np.zeros(data[:, :, :, 3].shape)
    else:
        sample[:, :, :, 4] = db
    sample = sample.transpose((3, 0, 1, 2))

    return sample


def write_nifti_sample(segmentation_path: Path, sample_path: Path = Path('sample.h5'),
                       slices: mpm_utils.Slices = mpm_utils.NONE_SLICES,
                       transpose_array: Tuple[int, int, int] = (0, 1, 2),
                       interpolation_factor: int = 1,
                       resolution_mm: Union[tuple, int, float] = None,
                       offset: Union[tuple, int, float] = (0, 0, 0)) -> bool:
    """Use a brain segmentation in nifti format as a template for a JEMRIS
    sample and write the sample to disk.

    - slice segmentation template
    - interpolate sliced segmentation template
    - use resulting volume as a template for generation of a multi-parameter map

    :param segmentation_path: path to brain segmentation file
    :param sample_path: target path for JEMRIS sample
    :param slices: slice object (will be applied to the template before interpolation and lookup)
    :param transpose_array: re-define directions (x, y, z) if necessary.
    :param interpolation_factor: augment each voxel dimension by this factor
    (with 3D samples, this will result in n-cubed spin isochromats)
    :param resolution_mm: size of each spin compartment in mm (voxel size after interpolation).
                          Default: None (try to calc from header data)
    :param offset: Offset for sample position in space. Default: no offset will be applied.
    :return: True on success
    """
    data, header = mpm_utils.load_nifty(segmentation_path)

    # check resolution and offset parameters
    # if no resolution is provided, calculate from header info and interpolation factor
    if resolution_mm is None:
        resolution_mm = tuple(header['pixdim'][1:4] / interpolation_factor)
    elif isinstance(resolution_mm, (float, int)):
        resolution_mm = (resolution_mm for _ in range(3))

    if isinstance(offset, (float, int)):
        offset = (offset for _ in range(3))

    # apply transformations
    transformed_data = mpm_utils.preprocess_array(data, slices, transpose_array, interpolation_factor)

    # look up sample parameters
    mpm_data = lookup_mpm(transformed_data)

    # translate to jemris readable format
    h5_sample = mk_h5_sample(mpm_data)

    # write h5 sample to disc
    if sample_path.exists():
        sample_path.unlink()

    with h5py.File(sample_path, 'w') as hf:
        s = hf.create_group('sample')
        s.create_dataset('data', data=h5_sample.transpose())
        s.create_dataset('resolution', data=resolution_mm)
        s.create_dataset('offset', data=offset)
        # if pools is not None:
        #     hf.create_dataset('exchange', data=np.transpose(n_pool_exchange_matrix(pools)))

    if sample_path.exists():
        logging.info('Sample written:')
        logging.info(f'Segmentation file: {segmentation_path}')
        logging.info(f'HDF5 sample shape (Params, X, Y, Z): {h5_sample.shape}')
        logging.info(f'Dest: {sample_path}')
        mpm_utils.plot_matrix(h5_sample[0, 0], 'JEMRIS sample')
        return True
    else:
        logging.error(f"Could not write sample to {sample_path}.")
        return False
