import cv2
import numpy as np

from core.editing.io_utils import imwrite


def adjust_exposure(image_path: str, output_path: str, target_mean: float = 128.0) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    current_mean = float(np.mean(gray))
    if current_mean < 1:
        return image_path
    scale = target_mean / current_mean
    adjusted = np.clip(img.astype(np.float32) * scale, 0, 255).astype(np.uint8)
    imwrite(output_path, adjusted)
    return output_path


def shadows_highlights(image_path: str, output_path: str,
                        shadow_boost: float = 1.3,
                        highlight_reduce: float = 0.85) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    l_channel = lab[:, :, 0]
    shadow_mask = l_channel < 80
    highlight_mask = l_channel > 180
    l_channel[shadow_mask] = np.clip(l_channel[shadow_mask] * shadow_boost, 0, 255)
    l_channel[highlight_mask] = np.clip(l_channel[highlight_mask] * highlight_reduce, 0, 255)
    lab[:, :, 0] = l_channel
    result = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    imwrite(output_path, result)
    return output_path
