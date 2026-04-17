import cv2
import numpy as np
import mediapipe as mp

_mesh = None
LEFT_EYE_CENTER = 468
RIGHT_EYE_CENTER = 473


def _get_mesh():
    global _mesh
    if _mesh is None:
        _mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1, refine_landmarks=True
        )
    return _mesh


def align_face(image_path: str, output_path: str,
               target_size: tuple = (512, 512)) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _get_mesh().process(rgb)
    if not results.multi_face_landmarks:
        return image_path
    lm = results.multi_face_landmarks[0].landmark
    left_eye = (int(lm[LEFT_EYE_CENTER].x * w), int(lm[LEFT_EYE_CENTER].y * h))
    right_eye = (int(lm[RIGHT_EYE_CENTER].x * w), int(lm[RIGHT_EYE_CENTER].y * h))
    dx = right_eye[0] - left_eye[0]
    dy = right_eye[1] - left_eye[1]
    angle = np.degrees(np.arctan2(dy, dx))
    eye_center = ((left_eye[0] + right_eye[0]) // 2,
                  (left_eye[1] + right_eye[1]) // 2)
    M = cv2.getRotationMatrix2D(eye_center, angle, 1.0)
    aligned = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT)
    cv2.imwrite(output_path, aligned)
    return output_path
