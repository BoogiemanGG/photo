import cv2
import numpy as np
import os
from config import BLINK_RATIO_MIN

_face_cascade = None
_eye_cascade = None


def _cascades():
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


def detect_eyes(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"eyes_open": False, "passed": False}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_c, eye_c = _cascades()
    faces = face_c.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    if len(faces) == 0:
        return {"all_eyes_open": None, "passed": True, "note": "no_face"}
    face_results = []
    for x, y, w, h in faces:
        roi = gray[y:y + h // 2, x:x + w]  # upper half — where eyes are
        eyes = eye_c.detectMultiScale(roi, 1.1, 5, minSize=(10, 10))
        eyes_open = len(eyes) >= 2
        face_results.append({"eyes_detected": int(len(eyes)), "eyes_open": eyes_open})
    all_open = all(f["eyes_open"] for f in face_results)
    return {"faces": face_results, "all_eyes_open": all_open, "passed": all_open}
