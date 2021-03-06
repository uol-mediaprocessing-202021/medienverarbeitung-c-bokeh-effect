from model import mask
import cv2
import numpy as np
import torch


# Pool-Algorithmus
def pool(source, use_scale, blur_style, blur_dim):
    img = cv2.imread(source)

    mak = np.asarray(predict(img, use_scale), dtype='uint8')

    return mask.apply_mask(img, mak, blur_style, blur_dim)


# Passt Größe des Bildes für Kantenfindung an
def compress_image(img):
    height, width = img.shape[:2]

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
def predict(img, use_scale):
    image = np.copy(img)
    if use_scale == 0:
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
