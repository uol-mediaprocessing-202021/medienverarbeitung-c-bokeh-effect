import cv2
import numpy as np


def apply_mask(img, mask):
    b, g, r = cv2.split(img)
    a = np.full_like(r, 1)
    mb = b * mask
    mg = g * mask
    mr = r * mask
    ma = a * mask
    result = cv2.merge((mb, mg, mr, ma))
    return np.asarray(result * 255., dtype='uint8')
