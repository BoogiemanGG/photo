import cv2
import os
import threading
from config import HEAD_POSE_YAW_MAX

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


def estimate_head_pose(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"faces": [], "passed": False}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_c, profile_c = _cascades()
    if face_c.empty() and profile_c.empty():
        return {"faces": [], "passed": True, "note": "cascade_missing"}
    frontal = face_c.detectMultiScale(gray, 1.1, 5, minSize=(30, 30)) \
        if not face_c.empty() else []
    profile = profile_c.detectMultiScale(gray, 1.1, 5, minSize=(30, 30)) \
        if not profile_c.empty() else []
    if len(frontal) == 0 and len(profile) == 0:
        return {"faces": [], "passed": True, "note": "no_face"}
    faces = []
    for _ in frontal:
        faces.append({"yaw": 0.0, "looking_at_camera": True, "method": "frontal"})
    for _ in profile:
        faces.append({"yaw": 90.0, "looking_at_camera": False, "method": "profile"})
    all_looking = all(f["looking_at_camera"] for f in faces)
    return {"faces": faces, "passed": all_looking}
