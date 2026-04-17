import cv2
import numpy as np
from config import MOTION_BLUR_THRESHOLD


def detect_motion_blur(image_path: str) -> dict:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"score": 0.0, "has_motion_blur": True, "passed": False}
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude = np.log(np.abs(fshift) + 1)
    h, w = magnitude.shape
    cy, cx = h // 2, w // 2
    radius = min(h, w) // 8
    mask = np.zeros((h, w), dtype=bool)
    Y, X = np.ogrid[:h, :w]
    mask[(Y - cy) ** 2 + (X - cx) ** 2 <= radius ** 2] = True
    high_freq = float(np.mean(magnitude[~mask]))
    has_blur = high_freq < MOTION_BLUR_THRESHOLD
    return {
        "high_freq_energy": round(high_freq, 3),
        "has_motion_blur": has_blur,
        "passed": not has_blur,
    }
