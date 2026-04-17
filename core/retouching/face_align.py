import cv2
import numpy as np
import os
import threading

_local = threading.local()


def _load():
    if not hasattr(_local, "face"):
        data = cv2.data.haarcascades
        _local.face = cv2.CascadeClassifier(
            os.path.join(data, "haarcascade_frontalface_default.xml")
        )
        _local.eye = cv2.CascadeClassifier(
            os.path.join(data, "haarcascade_eye_tree_eyeglasses.xml")
        )
    return _local.face, _local.eye


def align_face(image_path: str, output_path: str,
               target_size: tuple = (512, 512)) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_c, eye_c = _load()
    faces = face_c.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))
    if not len(faces):
        return image_path
    fx, fy, fw, fh = faces[0]
    roi_gray = gray[fy:fy + fh // 2, fx:fx + fw]
    eyes = eye_c.detectMultiScale(roi_gray, 1.1, 5, minSize=(10, 10))
    if len(eyes) < 2:
        return image_path
    # Sort eyes left to right
    eyes = sorted(eyes, key=lambda e: e[0])
    left_eye = (fx + eyes[0][0] + eyes[0][2] // 2, fy + eyes[0][1] + eyes[0][3] // 2)
    right_eye = (fx + eyes[1][0] + eyes[1][2] // 2, fy + eyes[1][1] + eyes[1][3] // 2)
    dx = right_eye[0] - left_eye[0]
    dy = right_eye[1] - left_eye[1]
    angle = np.degrees(np.arctan2(dy, dx))
    eye_center = ((left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2)
    M = cv2.getRotationMatrix2D(eye_center, angle, 1.0)
    aligned = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT)
    cv2.imwrite(output_path, aligned)
    return output_path
