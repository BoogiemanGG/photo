import cv2
import os
import threading

_local = threading.local()


def _get_cascade():
    if not hasattr(_local, "face"):
        _local.face = cv2.CascadeClassifier(
            os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        )
    return _local.face


def auto_crop_rule_of_thirds(image_path: str, output_path: str,
                              target_ratio: float = 2 / 3) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = _get_cascade().detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    if len(faces) > 0:
        x, y, fw, fh = faces[0]
        face_cx, face_cy = x + fw // 2, y + fh // 2
    else:
        face_cx, face_cy = w // 2, h // 3
    new_h = int(w * (1 / target_ratio))
    top = max(0, face_cy - h // 3)
    bottom = top + new_h
    if bottom > h:
        bottom = h
        top = max(0, bottom - new_h)
    cv2.imwrite(output_path, img[top:bottom, 0:w])
    return output_path


def portrait_crop_by_head_size(image_path: str, output_path: str,
                                head_fraction: float = 0.25) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = _get_cascade().detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    if not len(faces):
        return image_path
    x, y, fw, fh = faces[0]
    target_h = int(fh / head_fraction)
    top = max(0, y - int(fh * 0.3))
    bottom = min(h, top + target_h)
    cv2.imwrite(output_path, img[top:bottom, 0:w])
    return output_path
