import numpy as np

def diff_image(image1: np.ndarray, image2: np.ndarray):
    diff = np.abs(image1 - image2)
    counter = dict(zip(*np.unique(diff, return_counts=True)))

    if 0 in counter:
        return counter[0] / np.prod(diff.shape)
    else:
        return 0