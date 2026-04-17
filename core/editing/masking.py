import cv2
import numpy as np
import mediapipe as mp

_segmenter = None


def _get_segmenter():
    global _segmenter
    if _segmenter is None:
        _segmenter = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)
    return _segmenter


def get_subject_mask(image_path: str) -> np.ndarray | None:
    img = cv2.imread(image_path)
    if img is None:
        return None
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _get_segmenter().process(rgb)
    if results.segmentation_mask is None:
        return None
    mask = (results.segmentation_mask > 0.5).astype(np.uint8) * 255
    return mask


def apply_subject_mask(image_path: str, output_path: str,
                        background_color: tuple = (255, 255, 255)) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    mask = get_subject_mask(image_path)
    if mask is None:
        return image_path
    bg = np.full_like(img, background_color[::-1])
    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    result = np.where(mask_3ch > 127, img, bg)
    cv2.imwrite(output_path, result)
    return output_path
