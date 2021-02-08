import cv2
import numpy as np
from skimage.segmentation import mark_boundaries
from skimage.segmentation import slic

from detection import mask, blur


def show_segmentation(ori_image, image, segments):
    segments = slic(ori_image, n_segments=segments, sigma=5, start_label=1)
    cv2.imshow('Test', ori_image)
    cv2.waitKey(0)
    cv2.imshow('Test2', image)
    cv2.waitKey(0)
    #TODO: Farbausgabe korrigieren
    result = np.asarray(mark_boundaries(image, segments) * 255, dtype='uint8')

    return result


# x und y sind die Koordinaten, auf die der Benutzer klickt
# num_segments ist die Anzahl der Segmente, die der Benutzer ausgewählt hat
# blur ist eine Boolean-Variable, die darüber entscheidet ob das Segment unscharf oder scharf gestellt werden soll
def edit_segment(ori_image, image, num_segments, x_start, x_end, y_start, y_end, do_blur):
    if do_blur:
        # Hier das Bild mit Unschärfe einfügen
        # original = cv2.imread("blurred.jpg")
        original = blur.bokeh(np.asarray(ori_image, dtype='uint8'))
        # original = cv2.GaussianBlur(image, (71, 71), 0)
    else:
        # Hier das Bild ohne Unschärfe einfügen
        original = ori_image / 255
    cv2.imshow('Test3', original)
    cv2.waitKey(0)
    segments = slic(ori_image, n_segments=num_segments, sigma=5, start_label=1)

    image_mask = get_mask_segments(image, segments, x_start, x_end, y_start, y_end)

    cv2.imshow('Test1', image_mask)
    cv2.waitKey(0)

    image_mask_inverse = np.abs(1. - image_mask)

    cv2.imshow('Test2', image_mask_inverse)
    cv2.waitKey(0)

    image = mask.apply_mask(image / 255, image_mask_inverse)

    edited = mask.apply_mask(original, image_mask)

    result = image + edited
    result = cv2.cvtColor(np.asarray(result, dtype='uint8'), cv2.COLOR_RGB2BGR)

    return result


def get_mask_segments(image, segments, x_start, x_end, y_start, y_end):
    image_mask = np.zeros(image.shape[:2], dtype="uint8")
    if x_start == x_end and y_start == y_end:
        image_mask[segments == segments[y_start][x_start]] = 255
        return image_mask / 255
    selected_segments = []
    for row in range(min(y_start, y_end), max(y_start, y_end)):
        for column in range(min(x_start, x_end), max(x_start, x_end)):
            selected_segments.append(segments[row][column])
    for (i, segVal) in enumerate(np.unique(selected_segments)):
        #print("[x] inspecting segment %d" % i)
        image_mask[segments == segVal] = 255
    return image_mask / 255


# test = cv2.imread('blue-4430534_640.jpg')
# test_blurred = blur.bokeh(test)
# cv2.imshow('Test', show_segmentation(test, test_blurred, 300))
# cv2.waitKey(0)
# cv2.imshow('Edited', edit_segment(test, test, 100, 0, 30, 100, 200, True))
#
# cv2.waitKey(0)
