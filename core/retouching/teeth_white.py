import cv2
import numpy as np
import mediapipe as mp
from config import TEETH_WHITEN_AMOUNT

_mesh = None
LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
              375, 321, 405, 314, 17, 84, 181, 91, 146]


def _get_mesh():
    global _mesh
    if _mesh is None:
        _mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=5, refine_landmarks=True
        )
    return _mesh


def whiten_teeth(image_path: str, output_path: str,
                 amount: int = TEETH_WHITEN_AMOUNT) -> str:
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
        pts = np.array([[int(face.landmark[i].x * w),
                         int(face.landmark[i].y * h)] for i in LIPS_OUTER])
        mouth_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mouth_mask, [pts], 255)
        # Only whiten bright pixels (actual teeth, not lips)
        bright_mask = (hsv[:, :, 2] > 120).astype(np.uint8) * 255
        teeth_mask = cv2.bitwise_and(mouth_mask, bright_mask)
        # Reduce saturation (removes yellow) and boost value
        hsv[:, :, 1] = np.where(teeth_mask > 0,
                                  np.clip(hsv[:, :, 1] - amount, 0, 255),
                                  hsv[:, :, 1])
        hsv[:, :, 2] = np.where(teeth_mask > 0,
                                  np.clip(hsv[:, :, 2] + amount // 2, 0, 255),
                                  hsv[:, :, 2])
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, result)
    return output_path
