import matplotlib.pyplot as plt
from numpy import ndarray
import nibabel as nib
from typing import Tuple, List

from scipy import ndimage


def load_nifty(path: str) -> tuple:
    """Prepare content of nifti file for further processing

    :param path: path to nifti file
    :return: tuple of (imaging data, data header)
    """
    img = nib.load(path)
    return img.get_fdata(), img.header


def plot_matrix(mat: ndarray, title: str = '') -> None:
    """Plot a 2D numpy array like an image."""
    cax = plt.matshow(mat, cmap='gray')
    plt.colorbar(cax)
    plt.title(title)
    plt.show()


def overlay(im1: ndarray, im2: ndarray, title: str = '') -> None:
    """Plot a 2D numpy array like an image."""
    plt.figure().set_tight_layout(False)
    cax = plt.imshow(im1, interpolation=None, cmap='gray')
    plt.imshow(im2, interpolation=None, alpha=0.5)
    plt.colorbar(cax)
    plt.title(title)
    plt.show()


def interpolate(data: ndarray, factor: float) -> ndarray:
    """Interpolate 'data' by 'factor' in each dimension using nearest neighbor interpolation.

    :param data: data array
    :param factor: interpolation factor
    :return: interpolated ndarray
    """
    return ndimage.zoom(data, factor, order=0, mode='nearest')


def preprocess_array(data: ndarray, slicing: Tuple[slice, slice, slice] = (
                             slice(None, None), slice(None, None), slice(None, None)
                     ),
                     transpose_array: Tuple[int, int, int] = (0, 1, 2),
                     interpolation_factor=1) -> ndarray:
    """Interpolate, slice and transpose a 3d array"""
    return interpolate(data[slicing].transpose(transpose_array), interpolation_factor)


def plot_echos(arr: List[ndarray], title: str = '') -> None:
    """Plot a 2D numpy array like an image."""
    f, axarr = plt.subplots(2, 3)
    for i, mat in enumerate(arr):
        axarr[i//3, i%3].imshow(mat, cmap='gray')
    plt.title(title)
    plt.show()

