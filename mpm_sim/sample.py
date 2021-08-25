import logging

import numpy as np
import h5py


from mpm_sim.utils import *


class BrainModel:
    """Definition of the lookup table for generating multi-parametric maps from tissue maps"""

    mcgill_tissues = np.array(
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
    return BrainModel.mcgill_tissues[data].astype(float)


def sample_to_jemris(data: np.ndarray, off_resonance: Union[np.ndarray, None] = None) -> np.ndarray:
    """Convert data to JEMRIS readable format.

    Sort data into JEMRIS readable configuration and return the object for further processing
    (adapted from the JEMRIS matlab-gui).
    :param data: unsorted multi-parameter map with the first 3 dimensions being space and the forth indexing the maps in
                 the order T1, T2, T2*[ms], M0
    :param off_resonance: off-resonance in rad/sec for each spin isochromat (shape = shape of spin isochromat matrix)
    :return: sorted multi-parameter map
    """

    data_shape = list(data.shape)[:-1]
    data_shape.append(5)
    jemris_sample = np.zeros(data_shape)

    # Convert relaxation times to relaxation rates.
    for i in range(3):
        jemris_sample[:, :, :, i+1] = np.reciprocal(data[:, :, :, i], where=data[:, :, :, i] != 0)

    # In Jemris, M0 is the first parameter.
    jemris_sample[:, :, :, 0] = data[:, :, :, 3]

    if off_resonance is not None:
        jemris_sample[:, :, :, 4] = off_resonance

    jemris_sample = jemris_sample.transpose((3, 0, 1, 2))

    return jemris_sample


def prepare_mpm(segmentation_path: str, **kwargs) -> ndarray:
    """Prepare a multi-parametric map for simulation based on a tissue map (segmentation)."""

    data, header = load_nifti(segmentation_path)

    args = check_array_defaults(kwargs)

    # If no resolution is provided, try to calculate from header info and interpolation factor.
    # Fallback is default resolution.
    if isinstance(args['resolution'], (float, int)):
        args['resolution'] = (args['resolution'] for _ in range(3))
    elif 'pixdim' in header:
        args['resolution'] = tuple(header['pixdim'][1:4] / args['interpolation'])

    # check offset type
    if isinstance(args['offset'], (float, int)):
        args['offset'] = (args['offset'] for _ in range(3))

    logging.info("Resample segmentation data...")
    slices = get_slicing(args)
    transformed_segmentation = resample_simulation_volume(data, slices, args['transpose'], args['interpolation'])

    logging.info("Calculate multi-parametric maps...")
    return lookup_mpm(transformed_segmentation)


def write_sample(mpm_data: ndarray, sample_file: Path, **kwargs) -> bool:
    """Write mpm data numpy array to disc as HDF5 file."""

    jemris_readable_sample = sample_to_jemris(mpm_data)

    args = check_array_defaults(kwargs)

    if sample_file.exists():
        sample_file.unlink()

    with h5py.File(sample_file, 'w') as hf:
        s = hf.create_group('sample')
        s.create_dataset('data', data=jemris_readable_sample.transpose())
        s.create_dataset('resolution', data=args['resolution'])
        s.create_dataset('offset', data=args['offset'])
        # TODO: Multi-pool exchange model. Should work by doing something like in the lines below.
        #  I could not test it, because we do not have multi-pool data
        # if pools is not None:
        #     s.create_dataset('exchange', data=np.transpose(n_pool_exchange_matrix(pools)))

    if sample_file.exists():
        logging.info('Sample written:')
        logging.info(f'HDF5 sample shape (Params, X, Y, Z): {jemris_readable_sample.shape}')
        logging.info(f'Dest: {sample_file}')
        args = check_defaults(args, {'plot': False})
        if args['plot']:
            plot_matrix(jemris_readable_sample[0, 0], 'JEMRIS sample')
        return True
    else:
        logging.error(f"Could not write sample to {sample_file}.")
        return False
