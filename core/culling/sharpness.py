import cv2
import numpy as np
from config import SHARPNESS_MIN


def score_sharpness(image_path: str) -> dict:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"score": 0.0, "passed": False, "error": "Cannot read image"}
    score = cv2.Laplacian(img, cv2.CV_64F).var()
    return {"score": round(score, 2), "passed": score >= SHARPNESS_MIN}


def score_subject_vs_background(image_path: str) -> dict:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"subject": 0.0, "background": 0.0, "ratio": 0.0, "passed": False}
    h, w = img.shape
    cx, cy = w // 2, h // 2
    pad_x, pad_y = w // 4, h // 4
    subject = img[cy - pad_y:cy + pad_y, cx - pad_x:cx + pad_x]
    mask = np.ones(img.shape, dtype=bool)
    mask[cy - pad_y:cy + pad_y, cx - pad_x:cx + pad_x] = False
    subject_score = cv2.Laplacian(subject, cv2.CV_64F).var()
    background_score = cv2.Laplacian(img[mask].reshape(-1, 1), cv2.CV_64F).var() if mask.any() else 0
    ratio = subject_score / (background_score + 1e-6)
    return {
        "subject": round(subject_score, 2),
        "background": round(background_score, 2),
        "ratio": round(ratio, 2),
        "passed": ratio > 1.5,
    }
