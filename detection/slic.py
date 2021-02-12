import numpy as np
from skimage.segmentation import mark_boundaries
from skimage.segmentation import slic

from detection import blur
from functions import global_vars


def show_segmentation(image, original, num_segments):
    segments = slic(original, n_segments=num_segments, sigma=5, start_label=1)
    result = np.asarray(mark_boundaries(image, segments) * 255, dtype='uint8')
    return result


def edit_segment(image, original, num_segments, x_start, x_end, y_start, y_end, do_blur, blur_style, blur_dim):
    scale_equilizer = 1 - global_vars.scale_fac
    trunc_se = f"{scale_equilizer:.2f}"
    scale_equilizer = float(trunc_se)
    print('--Scale: ' + str(scale_equilizer))
    print()

    if global_vars.img_is_scaled:
        x_start = int(x_start + (x_start * scale_equilizer))
        x_end = int(x_end + (x_end * scale_equilizer))
        y_start = int(y_start + (y_start * scale_equilizer))
        y_end = int(y_end + (y_end * scale_equilizer))

    print('--COORDS_AFTER--')
    print(x_start, x_end, y_start, y_end)
    print()
    print('--Img_Shape--')
    print(image.shape)

    if do_blur:
        background = blur.bokeh(original, blur_style, blur_dim)
    else:
        background = original

    segments = slic(original, n_segments=num_segments, sigma=5, start_label=1)

    if x_start == x_end and y_start == y_end:
        image[segments == segments[y_start][x_start]] = background[segments == segments[y_start][x_start]]
        return image

    selected_segments = []
    for row in range(min(y_start, y_end), max(y_start, y_end)):
        for column in range(min(x_start, x_end), max(x_start, x_end)):
            selected_segments.append(segments[row][column])
    for (i, segVal) in enumerate(np.unique(selected_segments)):
        image[segments == segVal] = background[segments == segVal]
    return image
