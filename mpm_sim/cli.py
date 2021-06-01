import logging
from pathlib import Path

import click

from mpm_sim.sample import write_sample
import mpm_sim.utils as mpm_utils
from mpm_sim.sensmap import write_sensmap
from mpm_sim.kspace import write_kspace

_array_options = [
    click.option('-i', '--interpolation', metavar='INTERP_FACTOR', default=1,
                 help='multiply number of spin by this factor on each axis '
                      'using nearest neighbor interpolation', type=int),
    click.option('-x', '--xslice', metavar='X_SLICE', type=(int, int),
                 help='slicing in x direction', default=(None, None)),
    click.option('-y', '--yslice', metavar='Y_SLICE', type=(int, int),
                 help='slicing in y direction', default=(None, None)),
    click.option('-z', '--zslice', metavar='Z_SLICE', type=(int, int),
                 help='slicing in z direction', default=(None, None)),
    click.option('-t', '--transpose', metavar='TRANSPOSE', type=(int, int, int),
                 help='slicing in z direction', default=(0, 2, 1)),
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group()
def cli():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@cli.command(help="Prepare a sample for simulation", context_settings={'show_default': True})
@click.argument('seg_path', metavar='SEGMENATION_PATH', type=click.Path())
@click.option('--sample_path', type=click.Path(), help='name of sample file', default=Path('sample.h5'))
@add_options(_array_options)
def sample(seg_path, sample_path, xslice, yslice, zslice, interpolation, transpose):
    write_sample(Path(seg_path), sample_path, slices=mpm_utils.slicing((xslice, yslice, zslice)),
                 transpose_array=transpose, interpolation_factor=interpolation)


@cli.command(help="Prepare sensitivity maps for simulation", context_settings={'show_default': True})
@click.argument('magnitude_map_path', metavar='MAGNITUDE_MAP_PATH', type=click.Path())
@click.argument('phase_map_path', metavar='PHASE_MAP_PATH', type=click.Path())
@click.option('-o', '--out', metavar='OUT_PATH', type=click.Path(), help='Name of coil file', default=Path('sensmap.h5'))
@click.option('--overwrite/--no-overwrite', type=bool, help='Start new coil xml file', default=False)
@add_options(_array_options)
def sensmap(magnitude_map_path, phase_map_path, out, xslice, yslice, zslice, interpolation, transpose, overwrite):
    write_sensmap(
        Path(magnitude_map_path), Path(phase_map_path), Path(out),
        slices=mpm_utils.slicing((xslice, yslice, zslice)), transpose_array=transpose,
        overwrite=overwrite
    )


@cli.command(help="Run a basic flash reconstruction.", context_settings={'show_default': True})
@click.argument('signals_h5', metavar='SIG_PATH', type=click.Path())
@click.option('--dims', metavar='DIMS', type=(int, int, int), default=(434, 352, 496),
              help='Dimensions for kspace ordering (default is a standard 0.5mm acquisition)')
@click.option('--echoes', default=6, help='number of echoes to take into account', type=int)
def kspace(signals_h5, dims, echoes):
    write_kspace(Path(signals_h5), dims, echoes)


if __name__ == '__main__':
    cli()