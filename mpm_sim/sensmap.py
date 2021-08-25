import logging

import lxml.etree as et
import h5py

from mpm_sim.utils import *


BIAS_INTERPOLATION = 1


def register_coil(coil_xml_path: Path, extent: float, points: int, dim: int = 3, overwrite: bool = False):
    """Register coil, which means referencing the RX or TX field of the coil in the coil array file."""

    if coil_xml_path.exists() and overwrite is False:
        logging.info("Append new coil to coil array file.")
        parser = et.XMLParser(remove_blank_text=True)
        coil_array = et.parse(str(coil_xml_path), parser).getroot()
    else:
        if overwrite is True:
            logging.info("Replace old coil array file.")
        else:
            logging.info("Create new coil array file.")
        coil_array = et.Element('CoilArray')

    external_coil = et.SubElement(coil_array, 'EXTERNALCOIL')
    map_name = f"{coil_xml_path.stem}_coil_{len(coil_array.getchildren()) - 1}"
    map_path = full_dir(coil_xml_path) / Path(map_name).with_suffix('.h5')
    external_coil.set('Name', map_name)
    external_coil.set('Dim', str(dim))
    external_coil.set('Points', str(points))
    external_coil.set('Extent', str(extent))
    external_coil.set('Filename', str(map_path))

    print(et.tostring(coil_array))

    xml_string = et.tostring(coil_array, pretty_print=True, encoding='utf-8', xml_declaration=True)

    with coil_xml_path.open(mode='wb') as xml:
        xml.write(xml_string)

    return map_path


def sensmap(coil_xml_path: Path, magmap: str, phasemap: str, **kwargs):
    """Import sensitivity maps from nifti format.

    In Jemris, the files for coil configuration (xml) and field data (h5) are identical for RX and TX coils.
    """

    kwargs = check_array_defaults(kwargs)

    logging.info(f'Preprocess map data...')
    slices = get_slicing(kwargs)
    data_magmap = resample_simulation_volume(load_nifti(magmap)[0], slices, kwargs['transpose'], BIAS_INTERPOLATION)
    data_phasemap = resample_simulation_volume(load_nifti(phasemap)[0], slices, kwargs['transpose'], BIAS_INTERPOLATION)

    data_magmap = data_magmap.squeeze()
    data_phasemap = data_phasemap.squeeze()
    assert data_magmap.shape == data_phasemap.shape

    logging.info(f'Write coil XML file (location: {coil_xml_path})...')
    dims = len(data_magmap.shape)
    num_points = max(data_magmap.shape)  # Jemris treats the fields as if they were square shaped
    extent = num_points * kwargs['resolution']
    map_path = register_coil(coil_xml_path, extent=extent, points=num_points, dim=dims, overwrite=kwargs['overwrite'])

    logging.info(f'Writing maps to HDF5 (location: {map_path.absolute()})...')
    with h5py.File(map_path, 'w') as hf:
        maps = hf.create_group('maps')
        maps.create_dataset('magnitude', data=data_magmap.transpose())
        maps.create_dataset('phase', data=data_phasemap.transpose())
