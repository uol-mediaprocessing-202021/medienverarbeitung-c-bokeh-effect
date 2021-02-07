import cv2
import numpy as np
from skimage.segmentation import mark_boundaries
from skimage.segmentation import slic

from detection import mask, blur


def show_segmentation(image, segments):
    segments = slic(image, n_segments=segments, sigma=5, start_label=1)

    return np.asarray(mark_boundaries(image, segments) * 255., dtype='uint8')


# x und y sind die Koordinaten, auf die der Benutzer klickt
# num_segments ist die Anzahl der Segmente, die der Benutzer ausgewählt hat
# blur ist eine Boolean-Variable, die darüber entscheidet ob das Segment unscharf oder scharf gestellt werden soll
def edit_segment(image, num_segments, x, y, do_blur):
    if do_blur:
        # Hier das Bild mit Unschärfe einfügen
        # original = cv2.imread("blurred.jpg")
        original = blur.bokeh(np.asarray(image, dtype='uint8'))
        # original = cv2.GaussianBlur(image, (71, 71), 0)
    else:
        # Hier das Bild ohne Unschärfe einfügen
        original = cv2.imread("original.jpg")

    segments = slic(image, n_segments=num_segments, sigma=5, start_label=1)
    image, image_mask = get_mask_segment(image, segments, x, y)

    # edited = mask.apply_mask(original/255, image_mask / 255)
    edited = mask.apply_mask(original, image_mask / 255)

    result = image + edited

    return result


def get_mask_segment(image, segments, x, y):
    for (i, segVal) in enumerate(np.unique(segments)):
        image_mask = np.zeros(image.shape[:2], dtype="uint8")
        image_mask[segments == segVal] = 255
        if image_mask[x][y] == 255:
            height, width, bpp = np.shape(image)
            for py in range(0, height):
                for px in range(0, width):
                    if image_mask[py][px] == 255:
                        image[py][px][0] = 0
                        image[py][px][1] = 0
                        image[py][px][2] = 0
            return image, image_mask

# test = cv2.imread('C:/Users/malte/Desktop/luchs.jpg')
# print(type(test))
# show_segmentation(test, 100)
# edit_segment(test, 100, 80, 160, True)
