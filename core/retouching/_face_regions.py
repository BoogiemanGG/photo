"""
Shared face region helper using OpenCV Haar cascades.
Returns estimated ROI rectangles for eyes, mouth, cheeks, under-eyes.
"""
import cv2
import numpy as np
import os

_face_cascade = None
_eye_cascade = None


def _load():
    global _face_cascade, _eye_cascade
    if _face_cascade is None:
        data = cv2.data.haarcascades
        _face_cascade = cv2.CascadeClassifier(
            os.path.join(data, "haarcascade_frontalface_default.xml")
        )
        _eye_cascade = cv2.CascadeClassifier(
            os.path.join(data, "haarcascade_eye_tree_eyeglasses.xml")
        )
    return _face_cascade, _eye_cascade


def get_face_regions(img: np.ndarray) -> list[dict]:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_c, eye_c = _load()
    faces = face_c.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))
    regions = []
    for fx, fy, fw, fh in faces:
        eye_y = fy + int(fh * 0.15)
        eye_h = int(fh * 0.25)
        mouth_y = fy + int(fh * 0.62)
        mouth_h = int(fh * 0.25)
        under_eye_y = fy + int(fh * 0.38)
        under_eye_h = int(fh * 0.12)
        cheek_y = fy + int(fh * 0.40)
        cheek_h = int(fh * 0.25)

        # Detect actual eye positions within face ROI
        roi_gray = gray[fy:fy + fh // 2, fx:fx + fw]
        eyes = eye_c.detectMultiScale(roi_gray, 1.1, 5, minSize=(10, 10))
        eye_rects = []
        for ex, ey, ew, eh in eyes:
            eye_rects.append((fx + ex, fy + ey, ew, eh))

        regions.append({
            "face": (fx, fy, fw, fh),
            "left_eye": eye_rects[0] if len(eye_rects) > 0 else (fx + int(fw * 0.15), eye_y, int(fw * 0.3), eye_h),
            "right_eye": eye_rects[1] if len(eye_rects) > 1 else (fx + int(fw * 0.55), eye_y, int(fw * 0.3), eye_h),
            "mouth": (fx + int(fw * 0.2), mouth_y, int(fw * 0.6), mouth_h),
            "under_left_eye": (fx + int(fw * 0.1), under_eye_y, int(fw * 0.35), under_eye_h),
            "under_right_eye": (fx + int(fw * 0.55), under_eye_y, int(fw * 0.35), under_eye_h),
            "left_cheek": (fx + int(fw * 0.05), cheek_y, int(fw * 0.3), cheek_h),
            "right_cheek": (fx + int(fw * 0.65), cheek_y, int(fw * 0.3), cheek_h),
        })
    return regions


def make_region_mask(shape: tuple, rect: tuple, blur: int = 11) -> np.ndarray:
    mask = np.zeros(shape[:2], dtype=np.float32)
    x, y, w, h = rect
    x, y = max(0, x), max(0, y)
    w = min(w, shape[1] - x)
    h = min(h, shape[0] - y)
    if w > 0 and h > 0:
        mask[y:y + h, x:x + w] = 1.0
    if blur > 1:
        mask = cv2.GaussianBlur(mask, (blur, blur), 0)
    return mask
