import numpy as np
import h5py
from typing import List, Tuple
import logging
import os

from mpm_sim.utils import load_nifty, preprocess_array


def dims_slicing(slicing: Tuple[slice, slice, slice]) -> int:
    if 1 in [slice_dim.stop - slice_dim.start
             if slice_dim.stop is not None and slice_dim.start is not None else 0
             for slice_dim in slicing]:
        return 2
    else:
        return 3


def generate_coil_xml(dim: int = 3, extent: float = 248, filename='sensmaps.h5',
                      points: int = 496, n_coils: int = 2):
    j = ''
    extcoil = j.join([
        f'\t<EXTERNALCOIL Dim="{dim}" Extent="{extent}" Filename="{f"{coil}" + filename}" Name="C{coil}" Points="{points}"/>\n'
        for coil in range(1, n_coils + 1)
    ])
    return f'<?xml version="1.0" encoding="utf-8"?>\n<CoilArray>\n{extcoil}</CoilArray>'


def square(data_magmap, data_phasemap):
    edge_size = max(data_magmap.shape)
    pad = tuple(
        (0, edge_size - dim_size) if dim_size != 1 else (0, 0) for dim_size in data_magmap.shape
    )
    data_magmap = np.pad(data_magmap, pad,
                         'linear_ramp', end_values=0)
    data_phasemap = np.pad(data_phasemap, pad,
                           'linear_ramp', end_values=0)
    return data_magmap, data_phasemap, edge_size


def write_nifti_sensmap(magmaps_nii: List[str], phasemaps_nii: List[str], outdir: str,
                        sensmap_name: str, coil_xml: str,
                        n_coils=1, slicing=(slice(None, None),
                                            slice(None, None),
                                            slice(None, None)),
                        transpose_array: Tuple[int, int, int] = (0, 1, 2),
                        interpolation_factor: int = 1,  resolution: float = 0.5) -> np.ndarray:
    try:
        test_arr = preprocess_array(load_nifty(magmaps_nii[0])[0], slicing,
                                    transpose_array, interpolation_factor)
        edge_size = max(test_arr.shape)
    except IndexError as err:
        logging.error("The file lists must not be empty")
        raise

    for idx, (magmap_nii, phasemap_nii) in enumerate(zip(magmaps_nii, phasemaps_nii)):
        data_magmap, data_phasemap, edge_size = square(
            # load_nifty(...)[0] is just the data, without the header
            data_magmap=preprocess_array(load_nifty(magmap_nii)[0], slicing,
                                         transpose_array, interpolation_factor),
            data_phasemap=preprocess_array(load_nifty(phasemap_nii)[0], slicing, transpose_array,
                                           interpolation_factor)
        )
        if dims_slicing(slicing) == 2:
            data_magmap = np.reshape(data_magmap, (edge_size, edge_size))
            data_phasemap = np.reshape(data_phasemap, (edge_size, edge_size))
        with h5py.File(os.path.join(outdir, f"{idx+1}" + sensmap_name), 'w') as hf:
            maps = hf.create_group('maps')
            maps.create_dataset('magnitude', data=data_magmap.transpose())
            maps.create_dataset('phase', data=data_phasemap.transpose())
            logging.info(f'Convering sensmaps: {magmap_nii} and {phasemap_nii}')
    with open(coil_xml, mode='w') as xml:
        xml.write(generate_coil_xml(
            n_coils=n_coils, filename=sensmap_name,
            points=edge_size, extent=edge_size*resolution,
            dim=dims_slicing(slicing)
        ))
    return test_arr
