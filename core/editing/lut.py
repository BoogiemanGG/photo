import cv2
import numpy as np
from pathlib import Path

from core.editing.io_utils import imwrite


def apply_lut(image_path: str, output_path: str, lut_path: str) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    lut_data = np.load(lut_path) if lut_path.endswith(".npy") else _load_cube_lut(lut_path)
    if lut_data is None:
        return image_path
    b, g, r = cv2.split(img)
    result = cv2.LUT(img, lut_data) if lut_data.ndim == 1 else _apply_3d_lut(img, lut_data)
    imwrite(output_path, result)
    return output_path


def _load_cube_lut(cube_path: str) -> np.ndarray | None:
    try:
        lines = Path(cube_path).read_text().splitlines()
        size = 33
        data = []
        for line in lines:
            line = line.strip()
            if line.startswith("LUT_3D_SIZE"):
                size = int(line.split()[-1])
            elif line and not line.startswith("#") and not line.startswith("LUT"):
                vals = list(map(float, line.split()))
                if len(vals) == 3:
                    data.append(vals)
        lut = np.array(data, dtype=np.float32).reshape(size, size, size, 3)
        return (lut * 255).astype(np.uint8)
    except Exception:
        return None


def _apply_3d_lut(img: np.ndarray, lut: np.ndarray) -> np.ndarray:
    size = lut.shape[0]
    scale = (size - 1) / 255.0
    b, g, r = cv2.split(img)
    bi = (b * scale).astype(np.int32).clip(0, size - 1)
    gi = (g * scale).astype(np.int32).clip(0, size - 1)
    ri = (r * scale).astype(np.int32).clip(0, size - 1)
    mapped = lut[bi, gi, ri]
    return mapped.astype(np.uint8)
