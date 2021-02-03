import cv2
import numpy as np


def apply_mask(img, mask):
    r, g, b = cv2.split(img)
    mr = r * mask
    mg = g * mask
    mb = b * mask
    result = cv2.merge((mr, mg, mb))
    return np.asarray(result * 255., dtype='uint8')
