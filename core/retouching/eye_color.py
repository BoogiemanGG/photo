import cv2
import numpy as np
from core.retouching._face_regions import get_face_regions, make_region_mask


def change_eye_color(image_path: str, output_path: str,
                     target_hue: int = 120) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    regions = get_face_regions(img)
    if not regions:
        cv2.imwrite(output_path, img)
        return output_path
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).copy()
    for r in regions:
        for key in ("left_eye", "right_eye"):
            x, y, w, h = r[key]
            x, y = max(0, x), max(0, y)
            w = min(w, img.shape[1] - x)
            h = min(h, img.shape[0] - y)
            if w <= 0 or h <= 0:
                continue
            # Only change iris-colored pixels (not white sclera, not dark pupil)
            roi_v = hsv[y:y + h, x:x + w, 2]
            iris_mask = (roi_v > 40) & (roi_v < 200)
            hsv[y:y + h, x:x + w, 0][iris_mask] = target_hue // 2
            hsv[y:y + h, x:x + w, 1][iris_mask] = np.clip(
                hsv[y:y + h, x:x + w, 1][iris_mask], 80, 255
            )
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, result)
    return output_path
