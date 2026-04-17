import cv2
import numpy as np
from config import SHINE_THRESHOLD


def remove_shine(image_path: str, output_path: str,
                 threshold: int = SHINE_THRESHOLD) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int32)
    shine_mask = (hsv[:, :, 2] > threshold) & (hsv[:, :, 1] < 40)
    # Reduce brightness of shiny areas toward threshold
    hsv[:, :, 2] = np.where(
        shine_mask,
        np.clip(hsv[:, :, 2] - (hsv[:, :, 2] - threshold) // 2, 0, 255),
        hsv[:, :, 2],
    )
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, result)
    return output_path
