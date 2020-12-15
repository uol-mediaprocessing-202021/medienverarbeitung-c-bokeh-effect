import cv2
import numpy as np
import torch
import torchvision


def torch_blur(source):

    img = cv2.imread(source)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    model.eval()

    image2_normalized = img / 255.
    channels_first = np.moveaxis(image2_normalized, 2, 0)

    channels_first = torch.from_numpy(channels_first).float()

    prediction = model([channels_first])[0]
    masks = prediction['masks'].detach().numpy()
    mask = masks[0][0]

    image2_box_blurred = cv2.boxFilter(img, -1, (20, 20))

    r, g, b = cv2.split(image2_normalized)
    mr = r * mask
    mg = g * mask
    mb = b * mask
    subject = cv2.merge((mr, mg, mb))
    subject = np.asarray(subject * 255., dtype='uint8')

    inverted = np.abs(1. - mask)
    image2_box_blurred_normalized = image2_box_blurred / 255
    r, g, b = cv2.split(image2_box_blurred_normalized)
    ir = r * inverted
    ig = g * inverted
    ib = b * inverted
    background = cv2.merge((ir, ig, ib))
    background = np.asarray(background * 255., dtype='uint8')

    final = subject + background

    return final
