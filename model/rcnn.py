import cv2
import numpy as np
import torch
import torchvision
from model import mask


# RCNN-Algorithmus
def rcnn_blur(source, blur_style, blur_dim):
    img = cv2.imread(source)

    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    model.eval()

    channels_first = np.moveaxis(img / 255, 2, 0)

    channels_first = torch.from_numpy(channels_first).float()

    prediction = model([channels_first])[0]
    image_masks = prediction['masks'].detach().numpy()

    image_mask = np.asarray(image_masks[0][0] * 255, dtype='uint8')

    return mask.apply_mask(img, image_mask, blur_style, blur_dim)
