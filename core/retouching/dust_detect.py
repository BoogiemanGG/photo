import cv2
import numpy as np


def detect_sensor_dust(image_path: str) -> dict:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"spots": [], "count": 0}
    blurred = cv2.GaussianBlur(img, (0, 0), 5)
    diff = cv2.absdiff(img, blurred)
    _, thresh = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    spots = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 50 < area < 3000:
            M = cv2.moments(cnt)
            if M["m00"] > 0:
                spots.append({
                    "x": int(M["m10"] / M["m00"]),
                    "y": int(M["m01"] / M["m00"]),
                    "area": int(area),
                })
    return {"spots": spots, "count": len(spots)}


def remove_dust_spots(image_path: str, output_path: str) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    result = detect_sensor_dust(image_path)
    if not result["spots"]:
        cv2.imwrite(output_path, img)
        return output_path
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for spot in result["spots"]:
        radius = max(8, int((spot["area"] ** 0.5) * 0.6))
        cv2.circle(mask, (spot["x"], spot["y"]), radius, 255, -1)
    repaired = cv2.inpaint(img, mask, 10, cv2.INPAINT_TELEA)
    cv2.imwrite(output_path, repaired)
    return output_path
