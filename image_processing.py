import numpy as np
import cv2

def diff_image(image1: np.ndarray, image2: np.ndarray, mask: np.ndarray = None):
    if mask:
        diff = np.abs(image1[mask > 0] - image2[mask > 0])
    else:
        diff = np.abs(image1 - image2)

    counter = dict(zip(*np.unique(diff, return_counts=True)))

    if 0 in counter:
        return counter[0] / np.prod(diff.shape)
    else:
        return 0

def find_template(image: np.ndarray, template: np.ndarray):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    w, h = template_gray.shape[::-1]

    res = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    if len(loc) == 0:
        return []

    boxes = []
    for pt in zip(*loc[::-1]):
        boxes.append([pt[0], pt[1], w, h])

    return boxes