import cv2
import numpy as np
from core.retouching._face_regions import get_face_regions


def classify_skin_tone(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"tone": "unknown", "hex": None}
    regions = get_face_regions(img)
    if not regions:
        return {"tone": "unknown", "hex": None}
    r = regions[0]
    pixels = []
    for key in ("left_cheek", "right_cheek"):
        x, y, w, h = r[key]
        x, y = max(0, x), max(0, y)
        w = min(w, img.shape[1] - x)
        h = min(h, img.shape[0] - y)
        if w > 0 and h > 0:
            roi = img[y:y + h, x:x + w]
            pixels.append(roi.mean(axis=(0, 1)))
    if not pixels:
        return {"tone": "unknown", "hex": None}
    avg = np.mean(pixels, axis=0).astype(int)
    b, g, rv = int(avg[0]), int(avg[1]), int(avg[2])
    hex_color = "#{:02x}{:02x}{:02x}".format(rv, g, b)
    brightness = (rv + g + b) / 3
    if brightness > 200:
        tone = "very_light"
    elif brightness > 160:
        tone = "light"
    elif brightness > 120:
        tone = "medium"
    elif brightness > 80:
        tone = "tan"
    elif brightness > 50:
        tone = "dark"
    else:
        tone = "very_dark"
    return {"tone": tone, "hex": hex_color, "rgb": [rv, g, b]}
