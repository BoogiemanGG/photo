import cv2
import numpy as np
import mediapipe as mp
from config import DARK_CIRCLE_BRIGHTEN

_mesh = None
LEFT_UNDER_EYE = [145, 153, 154, 155, 133, 7, 163, 144]
RIGHT_UNDER_EYE = [374, 380, 381, 382, 362, 249, 390, 373]


def _get_mesh():
    global _mesh
    if _mesh is None:
        _mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=5, refine_landmarks=True
        )
    return _mesh


def reduce_dark_circles(image_path: str, output_path: str,
                         amount: int = DARK_CIRCLE_BRIGHTEN) -> str:
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
        for indices in (LEFT_UNDER_EYE, RIGHT_UNDER_EYE):
            pts = np.array([[int(face.landmark[i].x * w),
                              int(face.landmark[i].y * h)] for i in indices])
            # Expand region slightly downward
            pts[:, 1] = np.clip(pts[:, 1] + 8, 0, h - 1)
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(mask, [pts], 255)
            # Blur mask edges for natural look
            mask_blur = cv2.GaussianBlur(mask.astype(np.float32), (15, 15), 0) / 255.0
            hsv[:, :, 2] = np.clip(
                hsv[:, :, 2] + (mask_blur * amount).astype(np.int32), 0, 255
            )
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, result)
    return output_path
