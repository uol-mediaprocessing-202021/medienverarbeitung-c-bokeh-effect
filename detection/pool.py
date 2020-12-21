from detection import blur
import ssl
import cv2
import numpy as np
import torch


def apply_mask(img, mask):
    r, g, b = cv2.split(img)
    mr = r * mask
    mg = g * mask
    mb = b * mask
    result = cv2.merge((mr, mg, mb))
    return np.asarray(result * 255., dtype='uint8')


def pool(source):
    ssl._create_default_https_context = ssl._create_unverified_context

    img = cv2.imread(source)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img_blurred = cv2.boxFilter(img, -1, (20, 20))
    # img_blurred = cv2.GaussianBlur(img, (7, 7), 0)
    mask = predict(img)
    mask = mask / 255
    mask_inverted = np.abs(1. - mask)
    subject = apply_mask(img/255, mask)
    background = apply_mask(img_blurred/255, mask_inverted)
    result = subject + background
    # cv2.imwrite('result.jpg', result)
    return result


# Prediction mit PoolNET
def predict(img):
    image = np.copy(img)
    image_numpy = np.array(image, dtype=np.float32)
    image_numpy = image_numpy.transpose((2, 0, 1))
    image_tensor = torch.Tensor(image_numpy)
    image_tensor = torch.autograd.Variable(image_tensor.unsqueeze(0))

    poolnet = torch.load("poolnet.pth")

    prediction = poolnet(image_tensor)

    saliency_map = np.squeeze(torch.sigmoid(prediction).cpu().data.numpy())
    saliency_map_scaled = saliency_map * 255
    return saliency_map_scaled
