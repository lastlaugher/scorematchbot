import numpy as np
import cv2

def diff_image(image1: np.ndarray, image2: np.ndarray, mask: np.ndarray = None, color: bool = True):
    if not color:
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    if mask is not None:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
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

    res = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCORR_NORMED, template_gray)
    _, max_val, _,  max_loc = cv2.minMaxLoc(res)

    threshold = 0.8
    if max_val < threshold:
        return None

    return [max_loc[0], max_loc[1], w, h]

def crop(image: np.ndarray, bounding_box: list):
    x = bounding_box[0]
    y = bounding_box[1]
    width = bounding_box[2]
    height = bounding_box[3]

    return image[y:y + height, x:x + width]

def hsv2eh(image: np.ndarray):
    '''
    Convert HSV image into EH (Extended Hue) image, which non-colors are considered such as white, gray, and black
    EH plane value
    0-179: original H
    180-255: linear transformed value from V(0-255) if S < 20
    '''

    eh = image[:,:,0]
    for h in range(eh.shape[0]):
        for w in range(eh.shape[1]):
            if image[h, w, 1] < 20:
                eh[h, w] = int(image[h, w, 2] / 255 * (255 - 180)) + 180 

    return eh