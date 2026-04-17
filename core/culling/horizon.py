import cv2
import numpy as np


def detect_horizon_angle(image_path: str) -> dict:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"angle": 0.0, "needs_correction": False}
    edges = cv2.Canny(img, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80,
                             minLineLength=img.shape[1] // 4, maxLineGap=20)
    if lines is None:
        return {"angle": 0.0, "needs_correction": False}
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 != x1:
            angles.append(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
    if not angles:
        return {"angle": 0.0, "needs_correction": False}
    median_angle = float(np.median(angles))
    if median_angle > 45:
        median_angle -= 90
    elif median_angle < -45:
        median_angle += 90
    return {
        "angle": round(median_angle, 2),
        "needs_correction": abs(median_angle) > 0.5,
    }


def straighten_image(image_path: str, output_path: str) -> str:
    info = detect_horizon_angle(image_path)
    if not info["needs_correction"]:
        return image_path
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -info["angle"], 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT)
    cv2.imwrite(output_path, rotated)
    return output_path
