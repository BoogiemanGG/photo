import cv2
import mediapipe as mp

_detector = None


def _get_detector():
    global _detector
    if _detector is None:
        _detector = mp.solutions.face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
    return _detector


def auto_crop_rule_of_thirds(image_path: str, output_path: str,
                              target_ratio: float = 2 / 3) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _get_detector().process(rgb)

    if results.detections:
        det = results.detections[0]
        bb = det.location_data.relative_bounding_box
        face_cx = int((bb.xmin + bb.width / 2) * w)
        face_cy = int((bb.ymin + bb.height / 2) * h)
    else:
        face_cx, face_cy = w // 2, h // 2

    # Place face at upper third
    third_y = h // 3
    new_h = int(w * (1 / target_ratio))
    top = max(0, face_cy - third_y)
    bottom = top + new_h
    if bottom > h:
        bottom = h
        top = max(0, bottom - new_h)
    cropped = img[top:bottom, 0:w]
    cv2.imwrite(output_path, cropped)
    return output_path


def portrait_crop_by_head_size(image_path: str, output_path: str,
                                head_fraction: float = 0.25) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _get_detector().process(rgb)
    if not results.detections:
        return image_path
    bb = results.detections[0].location_data.relative_bounding_box
    face_h = bb.height * h
    target_h = int(face_h / head_fraction)
    face_top = int(bb.ymin * h)
    padding_top = int(face_h * 0.3)
    top = max(0, face_top - padding_top)
    bottom = min(h, top + target_h)
    cropped = img[top:bottom, 0:w]
    cv2.imwrite(output_path, cropped)
    return output_path
