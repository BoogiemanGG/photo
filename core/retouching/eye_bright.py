import cv2
import numpy as np
from core.retouching._face_regions import get_face_regions, make_region_mask
from config import EYE_BRIGHTEN_AMOUNT


def brighten_eyes(image_path: str, output_path: str,
                  amount: int = EYE_BRIGHTEN_AMOUNT) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    regions = get_face_regions(img)
    if not regions:
        cv2.imwrite(output_path, img)
        return output_path
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int32)
    for r in regions:
        for key in ("left_eye", "right_eye"):
            mask = make_region_mask(img.shape, r[key], blur=9)
            # Brighten and slightly desaturate (whiten sclera)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] + (mask * amount).astype(np.int32), 0, 255)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] - (mask * 20).astype(np.int32), 0, 255)
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, result)
    return output_path
