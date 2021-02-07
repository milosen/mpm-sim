import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple

import click
import numpy as np

from mpm_sim.sample import write_nifti_sample
from mpm_sim.utils import plot_matrix, plot_echos, load_nifty
from mpm_sim.sensmap import write_nifti_sensmap
from mpm_sim.kspace import basic_2d_recon, load_h5_signal, flash_order_kspace
from bart.cfl import writecfl


_shared_options = [
    click.option('-o', '--out_dir', default=Path(os.path.join(
                      os.path.curdir, 'runs',
                      f'{datetime.now().strftime("%Y-%m-%d_%H-%M")}'
                )), help='output directory', type=click.Path())
]

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
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def out_mkdir(out_dir: Path) -> Path:
    if out_dir is not Path:
        out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Create simulation directory {out_dir}")
    return out_dir


def slicing(xslice: Tuple[int, int],
            yslice: Tuple[int, int],
            zslice: Tuple[int, int]) -> Tuple[slice, slice, slice]:
    return slice(xslice[0], xslice[1]), slice(yslice[0], yslice[1]), slice(zslice[0], zslice[1])


@click.group()
def cli():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@cli.command(help="Prepare a sample for simulation", context_settings={'show_default': True})
@click.argument('seg_file', metavar='SEG_PATH', type=str)
@click.option('--sample_name', metavar='SAMPLE_NAME', type=click.Path(),
              # help='name of sample file',
              default='sample.h5')
@add_options(_shared_options)
@add_options(_array_options)
def sample(
        seg_file, sample_name, interpolation, out_dir, xslice, yslice, zslice):
    out_dir = out_mkdir(out_dir)
    # write sample
    out_filename = out_dir / sample_name
    data_sample = write_nifti_sample(
        seg_file, h5_filename=str(out_filename),
        slicing=slicing(xslice, yslice, zslice),
        transpose_array=(0, 2, 1),
        interpolation_factor=interpolation
    )
    if out_filename.exists():
        logging.info(
            'Sample written:\n'
            f'\tSegmentation file: {seg_file}\n'
            f'\tHDF5 sample shape (Params, X, Y, Z): {data_sample.shape}\n'
            f'\tDest: {str(out_filename)}'
        )
        plot_matrix(data_sample[0, 0], 'JEMRIS sample')
    else:
        logging.error(f"Could not write sample to {str(out_filename)}.")


@cli.command(help="Prepare sensitivity maps for simulation", context_settings={'show_default': True})
@click.option('-m', '--sensmap_name', metavar='SENSMAP_NAME', type=click.Path(),
              help='name of sensmap file',
              default=Path('sensmaps.h5'))
@add_options(_shared_options)
@add_options(_array_options)
def sensmap(sensmap_name, out_dir, xslice, yslice, zslice, interpolation):
    out_dir = out_mkdir(out_dir)
    # write sample
    n_coils = 2
    mag = [f'/nobackup/maki2/former_eminem2/vaculciakova/forNikola/coil_sens/Coils_ch{ch}_Magnitude.nii'
           for ch in range(1, n_coils + 1)]
    ph = [f'/nobackup/maki2/former_eminem2/vaculciakova/forNikola/coil_sens/Coils_ch{ch}_Phase.nii'
          for ch in range(1, n_coils + 1)]
    coil_xml_path = out_dir / Path('RXext.xml')
    data_sensmap = write_nifti_sensmap(
        mag, ph, str(out_dir), str(sensmap_name), coil_xml=str(coil_xml_path),
        n_coils=n_coils,
        slicing=slicing(xslice, yslice, zslice),
        transpose_array=(0, 2, 1),
        interpolation_factor=interpolation
    )
    if coil_xml_path.exists():
        logging.info(
            'Sensmap written:\n'
            f'\tHDF5 sample shape (X, Y, Z): {data_sensmap.shape}\n'
            f'\tDest: {str(coil_xml_path)}'
        )
        plot_matrix(data_sensmap[0], 'JEMRIS sensmap')
    else:
        logging.error(f"Map(s) could not be written.")


@cli.command(help="Run a basic flash reconstruction.", context_settings={'show_default': True})
@click.argument('signals_h5', metavar='SIG_PATH', type=str)
@click.option('--dims', metavar='DIMS', type=(int, int, int),
              help='Dimensions for kspace ordering (default is a standard 0.5mm acquisition)',
              default=(434, 496, 352))
@click.option('--echos', default=6,
              help='number of echoes to take into account', type=int)
@click.option('--n_echo', default=None, type=int,
              help='plot reconstructed image from this echo. default is all echoes.')
@click.option('--n_channel', default=0,
              help='plot reconstructed image from this channel')
@click.option('--x_slice', default=0,
              help='plot reconstructed image from this slice')
def basic_flash_recon(signals_h5, dims, echos, n_echo, n_channel, x_slice):
    echo_list = basic_2d_recon(signals_h5, dims, echos, x_slice, n_channel)
    if n_echo is None:
        plot_echos(echo_list)
    else:
        plot_matrix(echo_list[n_echo])


@cli.command(help="Run a basic flash reconstruction.", context_settings={'show_default': True})
@click.argument('signals_h5', metavar='SIG_PATH', type=str)
@click.option('--dims', metavar='DIMS', type=(int, int, int),
              help='Dimensions for kspace ordering (default is a standard 0.5mm acquisition)',
              default=(434, 496, 352))
@click.option('--echos', default=6,
              help='number of echoes to take into account', type=int)
@click.option('--n_echo', default=0, type=int,
              help='plot reconstructed image from this echo. default is all echoes.')
@click.option('--n_channel', default=0,
              help='plot reconstructed image from this channel')
@click.option('--x_slice', default=0,
              help='plot reconstructed image from this slice')
def order_kspace(signals_h5, dims, echos, n_echo, n_channel, x_slice):
    _, m = load_h5_signal(signals_h5)
    kspace = flash_order_kspace(m, dimensions=dims, echos=echos)[:, n_echo, :, x_slice, n_channel]
    if n_echo % 2 == 1:
        kspace = np.flip(kspace, axis=0)
    plot_matrix(np.absolute(kspace))
    img = np.absolute(np.fft.ifftshift(np.fft.ifft2(kspace)))
    plot_matrix(img)
    kspace = kspace.reshape(kspace.shape[0], kspace.shape[1], 1, 1, 1, 1)
    print("kspace shape: ", kspace.shape)
    writecfl("slice_i6_echo_1", kspace)


@cli.command(help="Plot a slice of a nifti volume.", context_settings={'show_default': True})
@click.argument('nifti_file', metavar='FILE_PATH', type=str)
@click.option('--x_slice', default=200,
              help='plot this slice')
def plot_nifti(nifti_file, x_slice):
    data, header = load_nifty(nifti_file)
    plot_matrix(data[x_slice])


if __name__ == '__main__':
    cli()
