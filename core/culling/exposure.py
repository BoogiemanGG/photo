import cv2
import numpy as np
import config


def analyze_exposure(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"mean_brightness": 0, "passed": False, "issue": "Cannot read image"}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean = float(np.mean(gray))
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    total = gray.size
    clipped_low = float(np.sum(hist[:5]) / total)
    clipped_high = float(np.sum(hist[250:]) / total)
    issue = None
    if mean < config.EXPOSURE_LOW:
        issue = "underexposed"
    elif mean > config.EXPOSURE_HIGH:
        issue = "overexposed"
    elif clipped_low > 0.02:
        issue = "clipped_shadows"
    elif clipped_high > 0.02:
        issue = "clipped_highlights"
    return {
        "mean_brightness": round(mean, 1),
        "clipped_shadows_pct": round(clipped_low * 100, 2),
        "clipped_highlights_pct": round(clipped_high * 100, 2),
        "issue": issue,
        "passed": issue is None,
    }
