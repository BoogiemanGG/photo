import cv2
import numpy as np
from config import BLEMISH_MASK_RADIUS


def _detect_blemishes(img: np.ndarray) -> list[tuple[int, int]]:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (0, 0), 3)
    diff = cv2.absdiff(gray, blurred)
    _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
    # Morphological clean
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 20 < area < 800:  # blemish-sized spots only
            M = cv2.moments(cnt)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centers.append((cx, cy))
    return centers


def remove_blemishes(image_path: str, output_path: str,
                     radius: int = BLEMISH_MASK_RADIUS) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    spots = _detect_blemishes(img)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for cx, cy in spots:
        cv2.circle(mask, (cx, cy), radius, 255, -1)
    if mask.any():
        result = cv2.inpaint(img, mask, radius, cv2.INPAINT_TELEA)
    else:
        result = img
    cv2.imwrite(output_path, result)
    return output_path
