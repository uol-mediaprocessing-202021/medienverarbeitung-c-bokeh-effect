import cv2
import numpy as np
from model import blur

# Wende Unschärfe auf Bild unter Verwendung der Maske
def apply_mask(img, mask, blur_style, blur_dim):
    mask_inverted = np.invert(mask)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    mask_inverted = cv2.cvtColor(mask_inverted, cv2.COLOR_GRAY2BGR)

    subject = np.asarray(((img / 255) * (mask / 255)) * 255, dtype='uint8')
    background = np.asarray(((img / 255) * (mask_inverted / 255)) * 255, dtype='uint8')

    background_bokeh = np.asarray(blur.bokeh(background, blur_style, blur_dim), dtype='uint8')

    background_bokeh = np.asarray(((background_bokeh / 255) * (mask_inverted / 255)) * 255, dtype='uint8')

    result = subject + background_bokeh

    return result
  