from ultralytics import YOLO
from pathlib import Path

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = YOLO("yolov8n.pt")  # downloads once (~6MB), runs offline after
    return _model


def detect_objects(image_path: str, confidence: float = 0.4) -> dict:
    results = _get_model().predict(
        source=image_path,
        conf=confidence,
        verbose=False,
    )
    objects = []
    for r in results:
        for box in r.boxes:
            objects.append({
                "label": r.names[int(box.cls)],
                "confidence": round(float(box.conf), 3),
                "bbox": [round(float(x), 1) for x in box.xyxy[0].tolist()],
            })
    labels = list({obj["label"] for obj in objects})
    return {"objects": objects, "labels": labels, "count": len(objects)}
