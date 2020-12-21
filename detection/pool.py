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

    mask = predict(img)
    mask = mask / 255
    mask_inverted = np.abs(1. - mask)

    r, g, b = cv2.split(img)
    ir = r * mask_inverted
    ig = g * mask_inverted
    ib = b * mask_inverted
    background = cv2.merge((ir, ig, ib))

    subject = apply_mask(img/255, mask)
    background_bokeh = blur.bokeh(np.asarray(background, dtype='uint8'))
    background_bokeh = np.asarray(background_bokeh * 255, dtype='uint8')
    result = cv2.addWeighted(subject, 1., background_bokeh, 1., 0)

    return result


def compress_image(img):
    height, width = img.shape[:2]
    scale_percent = 0

    if width > height:
        scale_percent = int(500 * 100 / width)
    else:
        scale_percent = int(500 * 100 / height)

    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    return resized


# Prediction mit PoolNET
def predict(img):
    image = np.copy(img)
    height, width = image.shape[:2]
    if height > 500 or width > 500:
        image = compress_image(img)
    image_numpy = np.array(image, dtype=np.float32)
    image_numpy = image_numpy.transpose((2, 0, 1))
    image_tensor = torch.Tensor(image_numpy)
    image_tensor = torch.autograd.Variable(image_tensor.unsqueeze(0))

    poolnet = torch.load("poolnet.pth")

    prediction = poolnet(image_tensor)

    saliency_map = np.squeeze(torch.sigmoid(prediction).cpu().data.numpy())
    saliency_map_scaled = saliency_map * 255
    return cv2.resize(saliency_map_scaled, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
