import os
from typing import Union

import numpy as np
import h5py
import nibabel as nib
from scipy import ndimage


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


def load_nifty(path) -> tuple:
    """Prepare content of nifti file for further processing

    :param path: path to nifti file
    :return: tuple of (imaging data, data header)
    """
    img = nib.load(path)
    return img.get_fdata(), img.header


def lookup_mpm(data: np.ndarray) -> np.ndarray:
    """Turn segmentations into multi-parametric maps by using a lookup for
    parameters of tissue classes.

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


def interpolate(data: np.ndarray, factor: float) -> np.ndarray:
    """Interpolate 'data' by 'factor' in each dimension using nearest neighbor interpolation.

    :param data: data array
    :param factor: interpolation factor
    :return: interpolated ndarray
    """
    return ndimage.zoom(data, factor, order=0, mode='nearest')


def mk_h5_sample(data: np.ndarray, h5_filename: str = 'sample.h5', db: Union[np.ndarray, None] = None,
                 resolution_mm: Union[tuple, list] = (1, 1, 1),
                 offset: Union[tuple, int, float] = (0, 0, 0)) -> np.ndarray:
    """Convert data to JEMRIS readable format.

    Convert data to hdf5 format in JEMRIS readable configuration, write it to disk and return the written object
    for further processing if applicable (adapted from JEMRIS' matlab-gui).
    :param data: multi-parameter map
    :param h5_filename: target filename. Default: sample.h5
    :param db: off-resonance in rad/sec for each spin isochromat (shape equal to shape of spin isochromat matrix)
    :param resolution_mm: size of the spin isochromat volume (either tuple for dimensions, scalar in isotropic case).
    Default: 1mm isotropic resolution will be assumed.
    :param offset: Offset for sample position in space. Default: no offset will be applied.
    :return: object written to disc
    """
    if isinstance(resolution_mm, (float, int)):
        resolution_mm = (resolution_mm for _ in range(3))

    if isinstance(offset, (float, int)):
        offset = (offset for _ in range(3))

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

    # write sample
    if os.path.exists(h5_filename):
        os.remove(h5_filename)

    with h5py.File(h5_filename, 'w') as hf:
        s = hf.create_group('sample')
        s.create_dataset('data', data=sample.transpose())
        s.create_dataset('resolution', data=resolution_mm)
        s.create_dataset('offset', data=offset)
        # if pools is not None:
        #     hf.create_dataset('exchange', data=np.transpose(n_pool_exchange_matrix(pools)))

    return sample


def jemris_sample_from_nifti(nifti_path, h5_filename='sample.h5',
                             slicing=(slice(None, None), slice(None, None), slice(None, None)),
                             transpose_array=(0, 1, 2),
                             interpolation_factor=1,
                             resolution_mm=None):
    """Use a brain segmentation in nifti format as a template for a JEMRIS
    sample and write the sample to disk.

    - slice segmentation template
    - interpolate sliced segmentation template
    - use resulting volume as a template for generation of a multi-parameter map

    :param nifti_path: path to brain segmentation file
    :param h5_filename: target path for JEMRIS sample
    :param slicing: slice object (will be applied to the template before interpolation and lookup)
    :param transpose_array: re-define directions (x, y, z) if necessary.
    :param interpolation_factor: augment each voxel dimension by this factor
    (with 3D samples, this will result in n-cubed spin isochromats)
    :param resolution_mm: size of each voxel in mm after interpolation
    :return:
    """
    data, header = load_nifty(nifti_path)
    # if no resolution is provided, calculate from header info and interpolation factor
    if resolution_mm is None:
        resolution_mm = tuple(header['pixdim'][1:4] / interpolation_factor)
    # apply transformations
    transformed_data = interpolate(data[slicing].transpose(transpose_array), interpolation_factor)
    # look up sample parameters
    mpm_data = lookup_mpm(transformed_data)
    # translate to jemris readable format and write it to disk
    return mk_h5_sample(mpm_data, h5_filename=h5_filename, resolution_mm=resolution_mm)
