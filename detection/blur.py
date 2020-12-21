import cv2
import numpy as np
from pool_net import PoolNetInterface


def torch_blur(source):

    img = cv2.imread(source)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    weight_path = "model/no_edge_model.ckpt"

    # Load model
    model = PoolNetInterface(weight_path, device="gpu")

    # Call function
    mask = model.process(source)

    img = img / 255.  # Normalize image

    cv2.imshow('mask', mask)

    inverted = np.abs(1. - mask)

    r, g, b = cv2.split(img)
    mr = r * mask
    mg = g * mask
    mb = b * mask
    subject = cv2.merge((mr, mg, mb))

    ir = r * inverted
    ig = g * inverted
    ib = b * inverted
    background = cv2.merge((ir, ig, ib))

    subject = np.asarray(subject * 255., dtype='uint8')

    background_bokeh = bokeh(np.asarray(background * 255, dtype='uint8'))
    background_bokeh = np.asarray(background_bokeh * 255, dtype='uint8')
    combined = cv2.addWeighted(subject, 1., background_bokeh, 1., 0)

    return combined


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
    kernel = cv2.getGaussianKernel(11, 5)
    kernel = kernel * kernel.transpose() * mask  # Is the 2D filter
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
