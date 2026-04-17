import cv2
import mediapipe as mp
import numpy as np
from config import BLINK_RATIO_MIN

_mesh = None
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


def _get_mesh():
    global _mesh
    if _mesh is None:
        _mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=10,
            refine_landmarks=True, min_detection_confidence=0.5
        )
    return _mesh


def _ear(landmarks, indices, w, h):
    pts = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in indices])
    A = np.linalg.norm(pts[1] - pts[5])
    B = np.linalg.norm(pts[2] - pts[4])
    C = np.linalg.norm(pts[0] - pts[3])
    return (A + B) / (2.0 * C + 1e-6)


def detect_eyes(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"eyes_open": False, "passed": False}
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _get_mesh().process(rgb)
    if not results.multi_face_landmarks:
        return {"eyes_open": None, "passed": True, "note": "no_face"}
    face_results = []
    for lm in results.multi_face_landmarks:
        left = _ear(lm.landmark, LEFT_EYE, w, h)
        right = _ear(lm.landmark, RIGHT_EYE, w, h)
        avg = (left + right) / 2
        face_results.append({
            "left_ear": round(left, 3),
            "right_ear": round(right, 3),
            "avg_ear": round(avg, 3),
            "eyes_open": avg >= BLINK_RATIO_MIN,
        })
    all_open = all(f["eyes_open"] for f in face_results)
    return {"faces": face_results, "all_eyes_open": all_open, "passed": all_open}
