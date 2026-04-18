import json
import cv2
import numpy as np
from pathlib import Path
from config import PROFILES_DIR
from core.editing.io_utils import imwrite


def load_profile(profile_name: str) -> dict:
    path = PROFILES_DIR / f"{profile_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Profile '{profile_name}' not found in {PROFILES_DIR}")
    return json.loads(path.read_text())


def apply_profile(image_path: str, output_path: str, profile_name: str) -> str:
    profile = load_profile(profile_name)
    img = cv2.imread(image_path)
    if img is None:
        return image_path

    # Exposure
    exposure = profile.get("exposure", 1.0)
    if exposure != 1.0:
        img = np.clip(img.astype(np.float32) * exposure, 0, 255).astype(np.uint8)

    # Contrast
    contrast = profile.get("contrast", 1.0)
    if contrast != 1.0:
        img = np.clip(128 + (img.astype(np.float32) - 128) * contrast, 0, 255).astype(np.uint8)

    # Saturation
    saturation = profile.get("saturation", 1.0)
    if saturation != 1.0:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255)
        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # Color temperature shift (warm/cool)
    temp = profile.get("temperature", 0)
    if temp != 0:
        img = img.astype(np.float32)
        img[:, :, 2] = np.clip(img[:, :, 2] + temp, 0, 255)  # R
        img[:, :, 0] = np.clip(img[:, :, 0] - temp, 0, 255)  # B
        img = img.astype(np.uint8)

    # Tone curve (simple gamma)
    gamma = profile.get("gamma", 1.0)
    if gamma != 1.0:
        table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255
                           for i in range(256)], dtype=np.uint8)
        img = cv2.LUT(img, table)

    imwrite(output_path, img)
    return output_path


def list_profiles() -> list[str]:
    return [p.stem for p in PROFILES_DIR.glob("*.json")]
