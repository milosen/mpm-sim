import logging
from pathlib import Path
from typing import Tuple

import click

from mpm_sim.sample import write_nifti_sample
import mpm_sim.utils as mpm_utils
from mpm_sim.sensmap import write_nifti_sensmap
from mpm_sim.kspace import write_kspace, basic_2d_recon

_array_options = [
    click.option('-i', '--interpolation', metavar='INTERP_FACTOR', default=1,
                 help='multiply number of spin by this factor on each axis '
                      'using nearest neighbor interpolation', type=float),
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
    write_nifti_sample(seg_path, sample_path, slices=mpm_utils.slicing((xslice, yslice, zslice)),
                       transpose_array=transpose, interpolation_factor=interpolation)


@cli.command(help="Prepare sensitivity maps for simulation", context_settings={'show_default': True})
@click.option('-m', '--sensmap_name', metavar='SENSMAP_NAME', type=click.Path(),
              help='name of sensmap file',
              default=Path('sensmaps.h5'))
@add_options(_array_options)
def sensmap(sensmap_name, out_dir, xslice, yslice, zslice, interpolation, transpose):
    n_coils = 2
    mag = [f'/nobackup/maki2/former_eminem2/vaculciakova/forNikola/coil_sens/Coils_ch{ch}_Magnitude.nii'
           for ch in range(1, n_coils + 1)]
    ph = [f'/nobackup/maki2/former_eminem2/vaculciakova/forNikola/coil_sens/Coils_ch{ch}_Phase.nii'
          for ch in range(1, n_coils + 1)]
    coil_xml_path = out_dir / Path('RX.xml')
    data_sensmap = write_nifti_sensmap(
        mag, ph, str(out_dir), str(sensmap_name), coil_xml=str(coil_xml_path),
        n_coils=n_coils,
        slicing=mpm_utils.slicing(xslice, yslice, zslice),
        transpose_array=transpose,
        interpolation_factor=interpolation
    )
    if coil_xml_path.exists():
        logging.info(
            'Sensmap written:\n'
            f'\tHDF5 sample shape (X, Y, Z): {data_sensmap.shape}\n'
            f'\tDest: {str(coil_xml_path)}'
        )
        mpm_utils.plot_matrix(data_sensmap[0], 'JEMRIS sensmap')
    else:
        logging.error(f"Map(s) could not be written.")


@cli.command(help="Run a basic flash reconstruction.", context_settings={'show_default': True})
@click.argument('signals_h5', metavar='SIG_PATH', type=str)
@click.option('--dims', metavar='DIMS', type=(int, int, int),
              help='Dimensions for kspace ordering (default is a standard 0.5mm acquisition)',
              default=(434, 496, 352))
@click.option('--echos', default=6, help='number of echoes to take into account', type=int)
@click.option('--n_echo', default=None, type=int, help='plot reconstructed image from this echo. default is all echoes.')
@click.option('--n_channel', default=0, help='plot reconstructed image from this channel')
@click.option('--x_slice', default=0, help='plot reconstructed image from this slice')
def basic_flash_recon(signals_h5, dims, echos, n_echo, n_channel, x_slice):
    echo_list = basic_2d_recon(signals_h5, dims, echos, x_slice, n_channel)
    if n_echo is None:
        mpm_utils.plot_echos(echo_list)
    else:
        mpm_utils.plot_matrix(echo_list[n_echo])


@cli.command(help="Run a basic flash reconstruction.", context_settings={'show_default': True})
@click.argument('signals_h5', metavar='SIG_PATH', type=click.Path())
@click.option('--dims', metavar='DIMS', type=(int, int, int), default=(434, 352, 496),
              help='Dimensions for kspace ordering (default is a standard 0.5mm acquisition)')
@click.option('--echoes', default=6, help='number of echoes to take into account', type=int)
def kspace(signals_h5, dims, echoes):
    write_kspace(signals_h5, dims, echoes)


if __name__ == '__main__':
    cli()
