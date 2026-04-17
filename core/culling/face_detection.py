import cv2
import os
import threading

_local = threading.local()


def _cascades():
    if not hasattr(_local, "face"):
        data = cv2.data.haarcascades
        _local.face = cv2.CascadeClassifier(
            os.path.join(data, "haarcascade_frontalface_default.xml")
        )
        _local.profile = cv2.CascadeClassifier(
            os.path.join(data, "haarcascade_profileface.xml")
        )
    return _local.face, _local.profile


def detect_faces(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"count": 0, "faces": [], "passed": False}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_c, profile_c = _cascades()
    frontal = face_c.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(frontal) == 0:
        profile = profile_c.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        all_faces = list(profile)
    else:
        all_faces = list(frontal)
    faces = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
             for x, y, w, h in all_faces]
    return {"count": len(faces), "faces": faces, "passed": len(faces) > 0}
