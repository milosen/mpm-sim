import lxml.etree as xml_etree

from mpm_sim.sample import *
from mpm_sim.sensmap import *
from mpm_sim.utils import *


class SimulationDirectory:
    """Data structure describing the specifics of a single simulation run.

    A Jemris simulation corresponds to a directory on the user's system that contains XML files for
    configuration and HDF5 files to store the arrays (e.g. the phantom/sample).
    At least a jemris_simulation.xml for the general simulation settings, a jemris_sample.h5 to store the sample
    data, and a jemris_sequence.xml for the MRI sequence definition must be provided.

    Jemris is very sensitive to deviations from the default structures of the XML configuration files.
    So, be careful when making changes. The XML configuration files that are inherent to Jemris are thus named with a
    jemris_* prefix.
    """
    files = dict(
        SIMU_FILE='jemris_simulation.xml',
        SAMPLE_FILE='jemris_sample.h5',
        SEQUENCE_FILE='jemris_sequence.xml',
        RX_FILE='jemris_RX.xml',
        TX_FILE='jemris_TX.xml'
    )

    def __init__(self, sim_dir_path: Union[str, Path]):
        sim_dir_path = Path(sim_dir_path).absolute()

        self.paths = dict(ROOT_DIR=sim_dir_path)

        if self.paths['ROOT_DIR'].exists():
            logging.info(f"Simulation directory already exists: {self.paths['ROOT_DIR']}")
        else:
            logging.info(f"Create new simulation directory: {self.paths['ROOT_DIR']}")
            sim_dir_path.mkdir()

        for key, value in SimulationDirectory.files.items():
            self.paths[key] = self.paths['ROOT_DIR'] / Path(value)

        if self.paths['SIMU_FILE'].exists():
            logging.info(f"Simulation XML File already exists: {str(self.paths['SIMU_FILE'])}")
            parser = xml_etree.XMLParser(remove_blank_text=True)
            self.simulate = xml_etree.parse(str(self.paths['SIMU_FILE']), parser).getroot()
        else:
            self.simulate = xml_etree.Element('simulate')
            self.simulate.set('Name', 'Simulation')
            self.set_defaults()
            self.dump_simu_xml()

        if not self.paths['SEQUENCE_FILE'].exists():
            logging.warning(f"Please provide a sequence file at {str(self.paths['SEQUENCE_FILE'])}. "
                            f"As a quick start, you can copy one from the templates directory.")

    def set_defaults(self):
        sample = xml_etree.SubElement(self.simulate, 'sample')

        rx_coilarray = xml_etree.SubElement(self.simulate, 'RXcoilarray')
        rx_coilarray.set('uri', str(self.paths['RX_FILE'].absolute()))

        tx_coilarray = xml_etree.SubElement(self.simulate, 'TXcoilarray')
        tx_coilarray.set('uri', str(self.paths['TX_FILE'].absolute()))

        parameter = xml_etree.SubElement(self.simulate, 'parameter')
        parameter.set('ConcomitantFields', '0')
        parameter.set('EvolutionPrefix', 'evol')
        parameter.set('EvolutionSteps', '0')
        parameter.set('RandomNoise', '0')

        sequence = xml_etree.SubElement(self.simulate, 'sequence')
        sequence.set('name', 'sequence')
        sequence.set('uri', str(self.paths['SEQUENCE_FILE'].absolute()))

        # We use the standard Bloch solver because the Bloch-McConnell solver requires complete multi-pool data which we
        # do not have. The solver engine is the CVODE solver from the Sundials library.
        model = xml_etree.SubElement(self.simulate, 'model')
        model.set('name', 'Bloch')
        model.set('type', 'CVODE')

        sample.set('Name', 'Sample')
        sample.set('uri', str(self.paths['SAMPLE_FILE'].absolute()))

    def dump_simu_xml(self):
        xml_string = xml_etree.tostring(self.simulate, pretty_print=True, encoding='utf-8', xml_declaration=True)

        logging.info(f"Write simulation xml file: {str(self.paths['SIMU_FILE'])}")
        print(xml_etree.tostring(self.simulate, pretty_print=True, encoding=str))

        with self.paths['SIMU_FILE'].open(mode='wb') as xml:
            xml.write(xml_string)

    def get_root(self):
        return self.paths['ROOT_DIR']


class Simulation:
    def __init__(self, sim_dir_path):
        self.simulation_directory = SimulationDirectory(sim_dir_path)

    def prepare_sample(self, segmentation_path, **kwargs):
        """Use a brain tissue map (segmentation) in nifti format as a template for a JEMRIS sample and write to disk."""

        logging.info("Resample volume and lookup values for multi-parametric map.")
        mpm_data = prepare_mpm(segmentation_path, **kwargs)

        logging.info("Write sample to disc in HDF5 format...")
        return write_sample(mpm_data, self.simulation_directory.paths['SAMPLE_FILE'], **kwargs)

    def prepare_rx_field(self, magmap: str, phasemap: str, **kwargs):
        coil_xml_path = self.simulation_directory.paths['RX_FILE']
        return sensmap(coil_xml_path, magmap, phasemap, **kwargs)

    def prepare_tx_field(self, magmap: str, phasemap: str, **kwargs):
        coil_xml_path = self.simulation_directory.paths['TX_FILE']
        return sensmap(coil_xml_path, magmap, phasemap, **kwargs)
