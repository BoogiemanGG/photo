import cv2
import numpy as np
from core.retouching._face_regions import get_face_regions, make_region_mask
from config import DARK_CIRCLE_BRIGHTEN


def reduce_dark_circles(image_path: str, output_path: str,
                         amount: int = DARK_CIRCLE_BRIGHTEN) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    regions = get_face_regions(img)
    if not regions:
        cv2.imwrite(output_path, img)
        return output_path
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int32)
    for r in regions:
        for key in ("under_left_eye", "under_right_eye"):
            mask = make_region_mask(img.shape, r[key], blur=15)
            hsv[:, :, 2] = np.clip(
                hsv[:, :, 2] + (mask * amount).astype(np.int32), 0, 255
            )
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, result)
    return output_path
