import matplotlib.pyplot as plt
from numpy import ndarray


class TestHelper:
    test_slice = 200
    data = dict(
        nifti_file='data/segmentation.nii',
        signals='data/signals.h5',
        sample='data/sample.h5'
    )


def plot_matrix(mat: ndarray, title: str = '') -> None:
    """Plot a 2D numpy array like an image."""
    cax = plt.matshow(mat)
    plt.colorbar(cax)
    plt.title(title)
    plt.show()
