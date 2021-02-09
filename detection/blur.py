import cv2
import numpy as np
from skimage.draw import disk


def adjust_gamma(image, gamma):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


def bokeh(image):
    g_one = 0.5
    g_two = 2.0
    dimension = 5

    gam = adjust_gamma(image, gamma=g_one)

    bok = defocus_blur(gam, dimension)

    bok = adjust_gamma(bok.astype(np.uint8), gamma=g_two)

    blur = defocus_blur(image, dimension)

    final = np.asarray(np.maximum(bok, blur) * 255, dtype='uint8')

    cv2.waitKey(0)

    return final


def defocus_blur(img, dim):
    kernel = disk_kernel(dim)

    r, g, b = cv2.split(img)

    r = r / 255.
    g = g / 255.
    b = b / 255.

    r = np.where(r > 0.9, r * 2, r)
    g = np.where(g > 0.9, g * 2, g)
    b = np.where(b > 0.9, b * 2, b)

    r_con = cv2.filter2D(r, -1, kernel)
    g_con = cv2.filter2D(g, -1, kernel)
    b_con = cv2.filter2D(b, -1, kernel)
    # r_con = convolve2d(r, kernel, mode='same', fillvalue=255.0).astype("uint8")
    # g_con = convolve2d(g, kernel, mode='same', fillvalue=255.0).astype("uint8")
    # b_con = convolve2d(b, kernel, mode='same', fillvalue=255.0).astype("uint8")

    r_con = np.where(r_con > 1., 1., r_con)
    g_con = np.where(g_con > 1., 1., g_con)
    b_con = np.where(b_con > 1., 1., b_con)

    convolved = cv2.merge((r_con, g_con, b_con))

    return convolved


def disk_kernel(dim):
    kernel_width = dim
    kernel = np.zeros((kernel_width, kernel_width), dtype=np.float32)
    circle_center_coord = dim / 2
    circle_radius = circle_center_coord + 1

    rr, cc = disk((circle_center_coord, circle_center_coord), circle_radius, shape=kernel.shape)
    kernel[rr, cc] = 1

    if dim == 3 or dim == 5:
        kernel = adjust(kernel, dim)

    normalization_factor = np.count_nonzero(kernel)
    kernel = kernel / normalization_factor
    return kernel


def adjust(kernel, kernel_width):
    kernel[0, 0] = 0
    kernel[0, kernel_width - 1] = 0
    kernel[kernel_width - 1, 0] = 0
    kernel[kernel_width - 1, kernel_width - 1] = 0
    return kernel
