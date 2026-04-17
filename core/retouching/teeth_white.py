import cv2
import numpy as np
from core.retouching._face_regions import get_face_regions, make_region_mask
from config import TEETH_WHITEN_AMOUNT


def whiten_teeth(image_path: str, output_path: str,
                 amount: int = TEETH_WHITEN_AMOUNT) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    regions = get_face_regions(img)
    if not regions:
        cv2.imwrite(output_path, img)
        return output_path
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int32)
    for r in regions:
        mask = make_region_mask(img.shape, r["mouth"], blur=11)
        # Only whiten bright pixels within mouth region (teeth, not lips)
        bright = (hsv[:, :, 2] > 110).astype(np.float32)
        combined = mask * bright
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] - (combined * amount).astype(np.int32), 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] + (combined * (amount // 2)).astype(np.int32), 0, 255)
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, result)
    return output_path
