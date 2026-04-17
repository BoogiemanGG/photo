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


def detect_faces(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"count": 0, "faces": [], "passed": False}
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _get_detector().process(rgb)
    if not results.detections:
        return {"count": 0, "faces": [], "passed": False}
    h, w = img.shape[:2]
    faces = []
    for det in results.detections:
        bb = det.location_data.relative_bounding_box
        faces.append({
            "x": round(bb.xmin * w),
            "y": round(bb.ymin * h),
            "w": round(bb.width * w),
            "h": round(bb.height * h),
            "confidence": round(det.score[0], 3),
        })
    return {"count": len(faces), "faces": faces, "passed": len(faces) > 0}
