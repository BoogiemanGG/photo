import cv2
import numpy as np
import mediapipe as mp
from config import EYE_BRIGHTEN_AMOUNT

_mesh = None
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
LEFT_SCLERA = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_SCLERA = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]


def _get_mesh():
    global _mesh
    if _mesh is None:
        _mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=5, refine_landmarks=True
        )
    return _mesh


def _landmark_pts(landmarks, indices, w, h):
    return np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in indices])


def brighten_eyes(image_path: str, output_path: str,
                  amount: int = EYE_BRIGHTEN_AMOUNT) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _get_mesh().process(rgb)
    if not results.multi_face_landmarks:
        cv2.imwrite(output_path, img)
        return output_path
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int32)
    for face in results.multi_face_landmarks:
        for indices in (LEFT_SCLERA, RIGHT_SCLERA):
            pts = _landmark_pts(face.landmark, indices, w, h)
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(mask, [pts], 255)
            hsv[:, :, 2] = np.where(mask > 0,
                                     np.clip(hsv[:, :, 2] + amount, 0, 255),
                                     hsv[:, :, 2])
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, result)
    return output_path
