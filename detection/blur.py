import cv2
import numpy as np


# Erstelle look-up tabel und korrigiere gamma Wert passend dazu
def adjust_gamma(image, gamma):
    inv_gamma = 1.0 / gamma

    # look-up table
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    # Wende LUT an um gamma Werte zu ändern
    return cv2.LUT(image, table)


# Wende Bokeh Effekt auf das Bild an
def bokeh(image, style, dim):
    g_one = 0.4545
    g_two = 2.2

    # Setze gamma Werte runter
    gam = adjust_gamma(image, gamma=g_one)

    # Wende Unschärfe auf das gamma Bild an
    bok = defocus_blur(gam, style, dim)
    bok = adjust_gamma(bok.astype(np.uint8), gamma=g_two)

    # Wende Unschärfe auf das originale Bild an
    blur = defocus_blur(image, style, dim)

    # Kombiniere beide Bilder
    final = np.asarray(np.maximum(bok, blur), dtype='uint8')
    cv2.waitKey(0)

    return final


# Wendet die verschiedenen Unschärfestile an
def defocus_blur(img, style, dim):

    if style == 0:
        # Kreuze
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (dim, dim))
    elif style == 1:
        # Ringe
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dim, dim))
        kernel_element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dim - 2, dim - 2))
        kernel_element = np.r_[[np.zeros(dim - 2)], kernel_element, [np.zeros(dim - 2)]]
        kernel_element = np.c_[np.zeros(dim), kernel_element, np.zeros(dim)]
        kernel = kernel - kernel_element
    else:
        # Kreise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dim, dim))

    normalization_factor = np.count_nonzero(kernel)
    kernel = kernel / normalization_factor

    return cv2.filter2D(img, -1, kernel)
