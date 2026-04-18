import cv2
import numpy as np
from config import VIGNETTE_STRENGTH

from core.editing.io_utils import imwrite


def add_vignette(image_path: str, output_path: str,
                 strength: float = VIGNETTE_STRENGTH) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    h, w = img.shape[:2]
    X = cv2.getGaussianKernel(w, w * 0.5)
    Y = cv2.getGaussianKernel(h, h * 0.5)
    kernel = Y * X.T
    mask = kernel / kernel.max()
    vignette_mask = 1 - strength * (1 - mask)
    result = (img * vignette_mask[:, :, np.newaxis]).clip(0, 255).astype(np.uint8)
    imwrite(output_path, result)
    return output_path


def remove_vignette(image_path: str, output_path: str) -> str:
    img = cv2.imread(image_path).astype(np.float32)
    if img is None:
        return image_path
    h, w = img.shape[:2]
    X = cv2.getGaussianKernel(w, w * 0.5)
    Y = cv2.getGaussianKernel(h, h * 0.5)
    kernel = Y * X.T
    mask = kernel / kernel.max()
    corrected = np.clip(img / (mask[:, :, np.newaxis] + 0.1), 0, 255).astype(np.uint8)
    imwrite(output_path, corrected)
    return output_path
