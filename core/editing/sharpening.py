import cv2
import numpy as np
from config import SHARPEN_AMOUNT, SHARPEN_RADIUS

from core.editing.io_utils import imwrite


def sharpen(image_path: str, output_path: str,
            amount: float = SHARPEN_AMOUNT,
            radius: float = SHARPEN_RADIUS) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    sigma = radius * 3
    blurred = cv2.GaussianBlur(img, (0, 0), sigma)
    sharpened = cv2.addWeighted(img, 1 + amount, blurred, -amount, 0)
    imwrite(output_path, sharpened)
    return output_path
