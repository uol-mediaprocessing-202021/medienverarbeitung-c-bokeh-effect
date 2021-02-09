import cv2
import numpy as np
import torch
import torchvision
from detection import blur, mask


def rcnn_blur(source):
    img = cv2.imread(source)
    background_bokeh = blur.bokeh(np.asarray(img, dtype='uint8'))

    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    model.eval()

    channels_first = np.moveaxis(img / 255., 2, 0)

    channels_first = torch.from_numpy(channels_first).float()

    prediction = model([channels_first])[0]
    image_masks = prediction['masks'].detach().numpy()
    image_mask = image_masks[0][0]

    inverted_mask = np.abs(1. - image_mask)

    subject = mask.apply_mask(img / 255., image_mask)
    background = mask.apply_mask(background_bokeh / 255., inverted_mask)

    combined = subject + background
    return combined
