import cv2
import numpy as np
from config import NOISE_MAX


def assess_noise(image_path: str) -> dict:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"score": 0.0, "passed": False}
    # Estimate noise on a flat region using median absolute deviation
    h, w = img.shape
    region = img[h // 4: 3 * h // 4, w // 4: 3 * w // 4]
    blurred = cv2.GaussianBlur(region, (5, 5), 0)
    diff = cv2.absdiff(region, blurred).astype(np.float32)
    score = float(np.mean(diff))
    return {"score": round(score, 2), "passed": score <= NOISE_MAX}
