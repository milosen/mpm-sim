import matplotlib.pyplot as plt
from numpy import ndarray
import nibabel as nib
from typing import Tuple, Union
from pathlib import Path

from scipy import ndimage


Slices = Tuple[slice, slice, slice]
Slice = Tuple[int, int]
SpatialDims = Tuple[int, int, int]

NONE_SLICE = (None, None)
NONE_SLICES = (NONE_SLICE, NONE_SLICE, NONE_SLICE)


def slicing(slices: Tuple[Slice, Slice, Slice]) -> Slices:
    return (
        slice(slices[0][0], slices[0][1]),
        slice(slices[1][0], slices[1][1]),
        slice(slices[2][0], slices[2][1])
    )


def dims_slices(slices: Slices) -> int:
    """Given a Slices object, how many dimensions will the sliced data have, 2 or 3?

    :param slices: Slices object
    :return: number of dimensions that the Slices object produces
    """
    if 1 in [slice_dim.stop - slice_dim.start
             if slice_dim.stop is not None and slice_dim.start is not None else 0
             for slice_dim in slices]:
        return 2
    else:
        return 3


def load_nifti(path: Union[str, Path]) -> tuple:
    """Prepare content of nifti file for further processing

    :param path: path to nifti file
    :return: tuple of (imaging data, data header)
    """
    img = nib.load(path)
    return img.get_fdata(), img.header


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
    """Interpolate 'data' by 'factor' in each dimension using nearest neighbor interpolation.

    :param data: list of tuples [(ndarray, "Title"), (ndarray, "Title"), ...]
    :param show: show and wait for user to close plot
    """
    _, axs = plt.subplots(1, len(data))
    for (d, t), ax in zip(data, axs):
        ax.imshow(d)
        ax.set_title(t)
    plt.show()


def interpolate(data: ndarray, factor: float) -> ndarray:
    """Interpolate 'data' by 'factor' in each dimension using nearest neighbor interpolation.

    :param data: data array
    :param factor: interpolation factor
    :return: interpolated ndarray
    """
    return ndimage.zoom(data, factor, order=0, mode='nearest')


def preprocess_array(data: ndarray, slices: Slices,
                     transpose_array: SpatialDims = (0, 1, 2),
                     interpolation_factor=1) -> ndarray:
    """Interpolate, slice and transpose a 3d array"""

    arr = data[slices].transpose(transpose_array)
    return interpolate(arr, interpolation_factor)


def full_dir(path: Path):
    """Get full path of the containing directory"""
    return path.absolute().parent
