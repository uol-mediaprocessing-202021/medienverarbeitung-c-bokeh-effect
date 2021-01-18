import cv2
import numpy as np
import torch
import torchvision
from detection import blur


def torch_blur(source):
    img = cv2.imread(source)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    model.eval()

    img = img / 255.
    channels_first = np.moveaxis(img, 2, 0)

    channels_first = torch.from_numpy(channels_first).float()

    prediction = model([channels_first])[0]
    masks = prediction['masks'].detach().numpy()
    mask = masks[0][0]

    inverted = np.abs(1. - mask)

    r, g, b = cv2.split(img)
    mr = r * mask
    mg = g * mask
    mb = b * mask

    subject = cv2.merge((mr, mg, mb))
    subject = np.asarray(subject * 255., dtype='uint8')

    ir = r * inverted
    ig = g * inverted
    ib = b * inverted
    background = cv2.merge((ir, ig, ib))

    background_bokeh = blur.bokeh(np.asarray(background * 255, dtype='uint8'))
    background_bokeh = np.asarray(background_bokeh * 255, dtype='uint8')
    combined = cv2.addWeighted(subject, 1., background_bokeh, 1., 0)

    return combined
