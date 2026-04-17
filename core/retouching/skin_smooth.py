import cv2
import numpy as np
from config import SKIN_SMOOTH_DIAMETER, SKIN_SMOOTH_SIGMA


def smooth_skin(image_path: str, output_path: str,
                diameter: int = SKIN_SMOOTH_DIAMETER,
                sigma: int = SKIN_SMOOTH_SIGMA) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    smoothed = cv2.bilateralFilter(img, diameter, sigma, sigma)
    # Blend with original to preserve some texture
    result = cv2.addWeighted(smoothed, 0.75, img, 0.25, 0)
    cv2.imwrite(output_path, result)
    return output_path
