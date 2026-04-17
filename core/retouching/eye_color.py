import cv2
import numpy as np
import mediapipe as mp

_mesh = None
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]


def _get_mesh():
    global _mesh
    if _mesh is None:
        _mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=5, refine_landmarks=True
        )
    return _mesh


def change_eye_color(image_path: str, output_path: str,
                     target_hue: int = 120) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _get_mesh().process(rgb)
    if not results.multi_face_landmarks:
        cv2.imwrite(output_path, img)
        return output_path
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).copy()
    for face in results.multi_face_landmarks:
        for indices in (LEFT_IRIS, RIGHT_IRIS):
            pts = np.array([[int(face.landmark[i].x * w),
                              int(face.landmark[i].y * h)] for i in indices])
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillConvexPoly(mask, pts, 255)
            mask = cv2.dilate(mask, np.ones((3, 3), dtype=np.uint8), iterations=2)
            hsv[:, :, 0] = np.where(mask > 0, target_hue // 2, hsv[:, :, 0])
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    cv2.imwrite(output_path, result)
    return output_path
