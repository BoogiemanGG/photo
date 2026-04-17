import cv2
import numpy as np
import os
from config import HEAD_POSE_YAW_MAX

_face_cascade = None
_profile_cascade = None


def _cascades():
    global _face_cascade, _profile_cascade
    if _face_cascade is None:
        data = cv2.data.haarcascades
        _face_cascade = cv2.CascadeClassifier(
            os.path.join(data, "haarcascade_frontalface_default.xml")
        )
        _profile_cascade = cv2.CascadeClassifier(
            os.path.join(data, "haarcascade_profileface.xml")
        )
    return _face_cascade, _profile_cascade


def estimate_head_pose(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"faces": [], "passed": False}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_c, profile_c = _cascades()
    frontal = face_c.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    profile = profile_c.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    if len(frontal) == 0 and len(profile) == 0:
        return {"faces": [], "passed": True, "note": "no_face"}
    faces = []
    for _ in frontal:
        # Frontal detection = looking at camera (yaw ≈ 0)
        faces.append({"yaw": 0.0, "looking_at_camera": True, "method": "frontal"})
    for _ in profile:
        # Profile detection = turned away
        faces.append({"yaw": 90.0, "looking_at_camera": False, "method": "profile"})
    all_looking = all(f["looking_at_camera"] for f in faces)
    return {"faces": faces, "passed": all_looking}
