import matplotlib.pyplot as plt
from numpy import ndarray
import nibabel as nib
from typing import Tuple, Union
from pathlib import Path

from scipy import ndimage
import click

NONE_SLICE = (None, None)
NONE_SLICING = (NONE_SLICE, NONE_SLICE, NONE_SLICE)

ARRAY_DEFAULTS = dict(
    interpolation=1,
    xslice=(None, None),
    yslice=(None, None),
    zslice=(None, None),
    transpose=(0, 2, 1),
    resolution=0.5,
    offset=0,
)

SAMPLE_OPTIONS = [
    click.option('-i', '--interpolation', metavar='INTERP_FACTOR', default=ARRAY_DEFAULTS['interpolation'],
                 help='multiply number of spin by this factor on each axis '
                      'using nearest neighbor interpolation', type=int),
    click.option('-x', '--xslice', metavar='X_SLICE', type=(int, int),
                 help='slicing in x direction', default=ARRAY_DEFAULTS['xslice']),
    click.option('-y', '--yslice', metavar='Y_SLICE', type=(int, int),
                 help='slicing in y direction', default=ARRAY_DEFAULTS['yslice']),
    click.option('-z', '--zslice', metavar='Z_SLICE', type=(int, int),
                 help='slicing in z direction', default=ARRAY_DEFAULTS['zslice']),
    click.option('-t', '--transpose', metavar='TRANSPOSE', type=(int, int, int),
                 help='transpose array dimensions', default=ARRAY_DEFAULTS['transpose']),
    click.option('-r', '--resolution', metavar='RESOLUTION', type=int,
                 help='transpose array dimensions', default=ARRAY_DEFAULTS['resolution']),
    click.option('-o', '--offset', metavar='OFFSET', type=int,
                 help='transpose array dimensions', default=ARRAY_DEFAULTS['offset']),
]


def load_nifti(path: Union[str, Path], header: bool = True) -> Union[tuple, ndarray]:
    """Prepare content of nifti file for further processing"""
    img = nib.load(path)
    img_ndarray = img.get_fdata()
    if header:
        return img_ndarray, img.header
    return img_ndarray


def plot_matrix(mat: ndarray, title: str = '') -> None:
    """Plot a 2D numpy array like an image."""
    cax = plt.matshow(mat, cmap='gray', interpolation='none')
    plt.colorbar(cax)
    plt.title(title)
    plt.draw()
    plt.show()


def overlay(im1: ndarray, im2: ndarray, title: str = '') -> None:
    """Plot two 2D numpy arrays with the second as an overlay to the first with alpha=0.5."""
    plt.figure().set_tight_layout(False)
    cax = plt.imshow(im1, interpolation=None, cmap='gray')
    plt.imshow(im2, interpolation=None, alpha=0.5)
    plt.colorbar(cax)
    plt.title(title)
    plt.draw()
    plt.show()


def plot_list(data: list) -> None:
    """Plot a list of images."""
    _, axs = plt.subplots(1, len(data))
    for (d, t), ax in zip(data, axs):
        ax.imshow(d)
        ax.set_title(t)
    plt.show()


def interpolate(data: ndarray, factor: float) -> ndarray:
    """Interpolate 'data' by 'factor' in each dimension using nearest neighbor interpolation."""
    return ndimage.zoom(data, factor, order=0, mode='nearest')


def resample_simulation_volume(
        data: ndarray, slices: Tuple[slice, ...],
        transpose_array: Tuple[int, ...] = (0, 1, 2),
        interpolation_factor: int = 1
) -> ndarray:
    """Interpolate, slice and transpose a 3d array"""
    template = data[slices]
    template = template.transpose(transpose_array)
    template = interpolate(template, interpolation_factor)
    return template


def full_dir(path: Path) -> Path:
    """Get full path of the containing directory"""
    return path.absolute().parent


def check_defaults(kwargs: dict, defaults: dict) -> dict:
    """Provide default values for kwargs."""
    for keyword, default_value in defaults.items():
        if keyword not in kwargs:
            kwargs[keyword] = default_value
    return kwargs


def check_array_defaults(kwargs: dict) -> dict:
    """run check_defaults with the defaults for 3d array data"""
    return check_defaults(kwargs, ARRAY_DEFAULTS)
