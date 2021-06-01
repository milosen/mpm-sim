import numpy as np
import h5py
from typing import Tuple
import logging
from pathlib import Path

import mpm_sim.utils as mpm_utils
import lxml.etree as et


def register_coil(extent: float, points: int,
                  dim: int = 3, map_path: Path = Path('sensmaps.h5'),
                  coil_xml_path: Path = None, overwrite: bool = False):

    if coil_xml_path is None:
        coil_xml_path = map_path.absolute().parent / Path("RX.xml")

    if coil_xml_path.exists() and overwrite is False:
        parser = et.XMLParser(remove_blank_text=True)
        coil_array = et.parse(str(coil_xml_path), parser).getroot()
    else:
        coil_array = et.Element('CoilArray')

    external_coil = et.SubElement(coil_array, 'EXTERNALCOIL')

    external_coil.set('Dim', str(dim))
    external_coil.set('Points', str(points))
    external_coil.set('Extent', str(extent))
    external_coil.set('Filename', str(map_path))
    external_coil.set('Name', str(map_path.stem))

    print(et.tostring(coil_array))

    xml_string = et.tostring(coil_array, pretty_print=True, encoding='utf-8', xml_declaration=True)

    with coil_xml_path.open(mode='wb') as xml:
        xml.write(xml_string)


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


def write_sensmap(magmap: Path, phasemap: Path, map_path: Path, slices=mpm_utils.NONE_SLICES,
                  transpose_array: Tuple[int, int, int] = (0, 1, 2), resolution: float = 0.5,
                  overwrite: bool = False):

    if map_path.suffix == '':
        map_path = map_path.with_suffix('.h5')

    interp = 1
    data_magmap = mpm_utils.preprocess_array(mpm_utils.load_nifti(magmap)[0], slices, transpose_array, interp)
    data_phasemap = mpm_utils.preprocess_array(mpm_utils.load_nifti(phasemap)[0], slices, transpose_array, interp)

    magmap_shape = tuple(t for t in data_magmap.shape if t != 1)
    phasemap_shape = tuple(t for t in data_phasemap.shape if t != 1)

    logging.info(f'Preprocess map data (shape: {magmap_shape})...')

    assert magmap_shape == phasemap_shape

    if len(magmap_shape) == 2:
        data_magmap = np.reshape(data_magmap, (magmap_shape[0], magmap_shape[1]))
        data_phasemap = np.reshape(data_phasemap, (magmap_shape[0], magmap_shape[1]))
        dims = 2
    else:
        dims = 3

    logging.info(f'Writing maps to HDF5 (location: {map_path.absolute()})...')
    with h5py.File(map_path, 'w') as hf:
        maps = hf.create_group('maps')
        maps.create_dataset('magnitude', data=data_magmap.transpose())
        maps.create_dataset('phase', data=data_phasemap.transpose())

    coil_xml_path = map_path.absolute().parent / Path('RX.xml')
    logging.info(f'Writing coil XML file (location: {coil_xml_path})...')
    register_coil(
        extent=max(magmap_shape)*resolution, points=max(magmap_shape),
        map_path=map_path, dim=dims, overwrite=overwrite
    )
