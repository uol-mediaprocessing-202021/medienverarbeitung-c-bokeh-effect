import cv2
import numpy as np


def bokeh(image):

    triangle = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ], dtype='float')

    mask = triangle
    kernel = cv2.getGaussianKernel(11, 10)
    kernel = kernel * kernel.transpose() * mask
    kernel = kernel / np.sum(kernel)

    r, g, b = cv2.split(image)

    r = r / 255.
    g = g / 255.
    b = b / 255.

    r = np.where(r > 0.9, r * 2, r)
    g = np.where(g > 0.9, g * 2, g)
    b = np.where(b > 0.9, b * 2, b)

    fr = cv2.filter2D(r, -1, kernel)
    fg = cv2.filter2D(g, -1, kernel)
    fb = cv2.filter2D(b, -1, kernel)

    fr = np.where(fr > 1., 1., fr)
    fg = np.where(fg > 1., 1., fg)
    fb = np.where(fb > 1., 1., fb)

    result = cv2.merge((fr, fg, fb))
    return result
