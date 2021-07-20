import logging
from pathlib import Path

import lxml.etree as et


class Simulation:
    files = dict(
        SIMU_FILE='jemris_simulation.xml',
        SAMPLE_FILE='jemris_sample.h5',
        RX_FILE='jemris_RX.xml',
        TX_FILE='jemris_TX.xml',
        SEQUENCE_FILE='jemris_sequence.xml'
    )

    def __init__(self, sim_dir_path: Path):
        self.paths = dict(ROOT_DIR=sim_dir_path)

        if self.paths['ROOT_DIR'].exists():
            logging.info(f"Simulation directory already exists: {self.paths['ROOT_DIR']}")
        else:
            logging.info(f"Create new simulation directory: {self.paths['ROOT_DIR']}")
            sim_dir_path.mkdir()

        for key, value in Simulation.files.items():
            self.paths[key] = self.paths['ROOT_DIR'] / Path(value)

        if self.paths['SIMU_FILE'].exists():
            logging.info(f"Simulation XML File already exists: {str(self.paths['SIMU_FILE'])}")
            parser = et.XMLParser(remove_blank_text=True)
            self.simulate = et.parse(str(self.paths['SIMU_FILE']), parser).getroot()
        else:
            self.simulate = et.Element('simulate')
            self.simulate.set('Name', 'Simulation')
            self.set_defaults()
            # self.set_options(**kwargs)
            self.dump_simu_xml()

    def set_defaults(self):
        sample = et.SubElement(self.simulate, 'sample')
        rx_coilarray = et.SubElement(self.simulate, 'RXcoilarray')
        tx_coilarray = et.SubElement(self.simulate, 'TXcoilarray')
        parameter = et.SubElement(self.simulate, 'parameter')
        sequence = et.SubElement(self.simulate, 'sequence')
        model = et.SubElement(self.simulate, 'model')

        sample.set('Name', 'Sample')
        sample.set('uri', Simulation.files['SAMPLE_FILE'])

        rx_coilarray.set('uri', Simulation.files['RX_FILE'])

        tx_coilarray.set('uri', Simulation.files['TX_FILE'])

        parameter.set('ConcomitantFields', '0')
        parameter.set('EvolutionPrefix', 'evol')
        parameter.set('EvolutionSteps', '0')
        parameter.set('RandomNoise', '0')

        sequence.set('name', 'sequence')
        sequence.set('uri', Simulation.files['SEQUENCE_FILE'])

        model.set('name', 'Bloch')
        model.set('type', 'CVODE')

    def set_options(self, **kwargs):
        for pair in kwargs.items():
            logging.info(pair)

    def dump_simu_xml(self):
        xml_string = et.tostring(self.simulate, pretty_print=True, encoding='utf-8', xml_declaration=True)

        logging.info(f"Write simulation xml file: {str(self.paths['SIMU_FILE'])}")
        print(et.tostring(self.simulate, pretty_print=True, encoding=str))

        with self.paths['SIMU_FILE'].open(mode='wb') as xml:
            xml.write(xml_string)
