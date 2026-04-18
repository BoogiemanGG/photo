import cv2
from config import NOISE_STRENGTH

from core.editing.io_utils import imwrite


def reduce_noise(image_path: str, output_path: str,
                 strength: int = NOISE_STRENGTH) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    denoised = cv2.fastNlMeansDenoisingColored(img, None, strength, strength, 7, 21)
    imwrite(output_path, denoised)
    return output_path
