import cv2
import mediapipe as mp
import numpy as np
from config import HEAD_POSE_YAW_MAX

_mesh = None


def _get_mesh():
    global _mesh
    if _mesh is None:
        _mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=10,
            refine_landmarks=True, min_detection_confidence=0.5
        )
    return _mesh


def estimate_head_pose(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"faces": [], "passed": False}
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _get_mesh().process(rgb)
    if not results.multi_face_landmarks:
        return {"faces": [], "passed": True, "note": "no_face"}

    model_pts = np.array([
        [0, 0, 0], [0, -330, -65], [-225, 170, -135],
        [225, 170, -135], [-150, -150, -125], [150, -150, -125]
    ], dtype=np.float64)
    cam = np.array([[w, 0, w / 2], [0, w, h / 2], [0, 0, 1]], dtype=np.float64)
    dist = np.zeros((4, 1))

    faces = []
    for lm in results.multi_face_landmarks:
        img_pts = np.array([
            [lm.landmark[1].x * w, lm.landmark[1].y * h],
            [lm.landmark[152].x * w, lm.landmark[152].y * h],
            [lm.landmark[226].x * w, lm.landmark[226].y * h],
            [lm.landmark[446].x * w, lm.landmark[446].y * h],
            [lm.landmark[57].x * w, lm.landmark[57].y * h],
            [lm.landmark[287].x * w, lm.landmark[287].y * h],
        ], dtype=np.float64)
        _, rvec, _ = cv2.solvePnP(model_pts, img_pts, cam, dist)
        rmat, _ = cv2.Rodrigues(rvec)
        angles = cv2.RQDecomp3x3(rmat)[0]
        yaw = angles[1]
        faces.append({"yaw": round(yaw, 1), "looking_at_camera": abs(yaw) <= HEAD_POSE_YAW_MAX})
    all_looking = all(f["looking_at_camera"] for f in faces)
    return {"faces": faces, "passed": all_looking}
