import logging

from mpm_sim.utils import *
from mpm_sim.kspace import write_kspace
from mpm_sim.simulation import Simulation


def add_options(options):
    """This function helps decorating the command line tools with an array of options, which reduces repetition."""
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group()
def cli():
    """Command line interface entry point."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@cli.command(help="Initialize new simulation and lay out the necessary directory structure.",
             context_settings={'show_default': True})
@click.argument('sim_dir_path', type=click.Path())
@click.argument('segmentation_path', type=click.Path())
@add_options(SAMPLE_OPTIONS)
def init(**kwargs):
    sim_dir_path = kwargs.pop('sim_dir_path')
    simu = Simulation(sim_dir_path)

    segmentation_path = kwargs.pop('segmentation_path')
    simu.prepare_sample(segmentation_path, **kwargs)


@cli.command(help="Sort samples of a fully sampled FLASH sequence into their corresponding kspace.",
             context_settings={'show_default': True})
@click.argument('signals_path', metavar='SIG_PATH', type=click.Path())
@click.option('--dims', metavar='DIMS', type=(int, int, int), default=(434, 352, 496),
              help='Dimensions for kspace ordering (default is a standard 0.5mm acquisition)')
@click.option('--echoes', default=6, help='number of echoes to take into account', type=int)
def kspace(**kwargs):
    signals_path = kwargs.pop('signals_path')
    write_kspace(signals_path, **kwargs)


@cli.command(help="Prepare receive sensitivity maps for simulation.", context_settings={'show_default': True})
@click.argument('magnitude_map_path', type=click.Path())
@click.argument('phase_map_path', type=click.Path())
@click.argument('sim_dir_path', type=click.Path())
@click.option('--coil_name', type=bool, help='Name of the coil.', default='coil')
@click.option('--overwrite/--no-overwrite', type=bool, help='Overwrite old coil xml file if it exists.', default=False)
@add_options(SAMPLE_OPTIONS)
def prepare_rx_field(**kwargs):
    magnitude_map_path = kwargs.pop('magnitude_map_path')
    phase_map_path = kwargs.pop('phase_map_path')
    sim_dir_path = kwargs.pop('sim_dir_path')

    simu = Simulation(sim_dir_path)
    simu.prepare_rx_field(magnitude_map_path, phase_map_path, **kwargs)


if __name__ == '__main__':
    cli()
