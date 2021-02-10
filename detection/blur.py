import cv2
import numpy as np


def adjust_gamma(image, gamma):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(image, table)


def bokeh(image, style, dim):
    g_one = 0.4545
    g_two = 2.2

    gam = adjust_gamma(image, gamma=g_one)
    bok = defocus_blur(gam, style, dim)
    bok = adjust_gamma(bok.astype(np.uint8), gamma=g_two)
    blur = defocus_blur(image, style, dim)
    final = np.asarray(np.maximum(bok, blur), dtype='uint8')
    cv2.waitKey(0)

    return final


def defocus_blur(img, style, dim):
    if style == 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (dim, dim))
    elif style == 1:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dim, dim))
        kernel_element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dim - 2, dim - 2))
        kernel_element = np.r_[[np.zeros(dim - 2)], kernel_element, [np.zeros(dim - 2)]]
        kernel_element = np.c_[np.zeros(dim), kernel_element, np.zeros(dim)]
        kernel = kernel - kernel_element
    else:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dim, dim))

    normalization_factor = np.count_nonzero(kernel)
    kernel = kernel / normalization_factor

    return cv2.filter2D(img, -1, kernel)


# test = cv2.imread('Tiefer-Blick-in-den-Kosmos.jpg')
# test_blurred = bokeh(test, 1, 51)
# # lookUpTable1 = np.empty((1, 256), np.uint8)
# # lookUpTable2 = np.empty((1, 256), np.uint8)
# # for i in range(256):
# #     lookUpTable1[0, i] = np.clip(pow(i / 255.0, 0.4545) * 255.0, 0, 255)
# #     lookUpTable2[0, i] = np.clip(pow(i / 255.0, 2.2) * 255.0, 0, 255)
# # res = cv2.LUT(test, lookUpTable1)
# # bokeh = defocus_blur(test, 9)
# # bokeh = cv2.LUT(bokeh, lookUpTable2)
# # test_blurred = defocus_blur(test, 9)
# cv2.imshow('Original', test)
# cv2.imshow('Gaussian', cv2.GaussianBlur(test, (7, 7), 0))
# # cv2.imshow('test', defocus_blur(test, 15))
# cv2.imshow('Test', test_blurred)
# cv2.waitKey(0)
