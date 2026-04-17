import cv2
import numpy as np


def remove_red_eye(image_path: str, output_path: str) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    b, g, r = cv2.split(img)
    # Red channel dominance mask
    red_dominant = (r.astype(np.int32) > g.astype(np.int32) * 1.4) & \
                   (r.astype(np.int32) > b.astype(np.int32) * 1.4) & \
                   (r > 80)
    mask = red_dominant.astype(np.uint8) * 255
    # Replace red with average of g and b
    avg_gb = ((g.astype(np.int32) + b.astype(np.int32)) // 2).astype(np.uint8)
    r_fixed = np.where(mask > 0, avg_gb, r)
    result = cv2.merge([b, g, r_fixed])
    cv2.imwrite(output_path, result)
    return output_path
