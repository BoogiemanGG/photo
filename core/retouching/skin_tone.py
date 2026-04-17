import cv2
import numpy as np
import mediapipe as mp

_mesh = None
CHEEK_LEFT = [234, 93, 132, 58]
CHEEK_RIGHT = [454, 323, 361, 288]


def _get_mesh():
    global _mesh
    if _mesh is None:
        _mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1
        )
    return _mesh


def classify_skin_tone(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"tone": "unknown", "hex": None}
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _get_mesh().process(rgb)
    if not results.multi_face_landmarks:
        return {"tone": "unknown", "hex": None}
    lm = results.multi_face_landmarks[0].landmark
    sample_pts = CHEEK_LEFT + CHEEK_RIGHT
    pixels = []
    for idx in sample_pts:
        x = int(lm[idx].x * w)
        y = int(lm[idx].y * h)
        x = np.clip(x, 0, w - 1)
        y = np.clip(y, 0, h - 1)
        pixels.append(img[y, x])
    if not pixels:
        return {"tone": "unknown", "hex": None}
    avg = np.mean(pixels, axis=0).astype(int)
    b, g, r = int(avg[0]), int(avg[1]), int(avg[2])
    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
    brightness = (r + g + b) / 3
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
    return {"tone": tone, "hex": hex_color, "rgb": [r, g, b]}
