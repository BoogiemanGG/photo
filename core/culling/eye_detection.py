import cv2
import os
import threading
from config import BLINK_RATIO_MIN

_local = threading.local()


def _cascades():
    if not hasattr(_local, "face"):
        data = cv2.data.haarcascades
        _local.face = cv2.CascadeClassifier(
            os.path.join(data, "haarcascade_frontalface_default.xml")
        )
        _local.eye = cv2.CascadeClassifier(
            os.path.join(data, "haarcascade_eye_tree_eyeglasses.xml")
        )
    return _local.face, _local.eye


def detect_eyes(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"eyes_open": False, "passed": False}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_c, eye_c = _cascades()
    if face_c.empty() or eye_c.empty():
        return {"all_eyes_open": None, "passed": True, "note": "cascade_missing"}
    faces = face_c.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    if len(faces) == 0:
        return {"all_eyes_open": None, "passed": True, "note": "no_face"}
    face_results = []
    for x, y, w, h in faces:
        roi = gray[y:y + h // 2, x:x + w]
        eyes = eye_c.detectMultiScale(roi, 1.1, 5, minSize=(10, 10)) \
            if not eye_c.empty() else []
        eyes_open = len(eyes) >= 2
        face_results.append({"eyes_detected": int(len(eyes)), "eyes_open": eyes_open})
    all_open = all(f["eyes_open"] for f in face_results)
    return {"faces": face_results, "all_eyes_open": all_open, "passed": all_open}
