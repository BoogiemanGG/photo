import cv2
import numpy as np
from core.editing.masking import get_subject_mask
from config import BOKEH_BLUR_RADIUS


def portrait_bokeh(image_path: str, output_path: str,
                   blur_radius: int = BOKEH_BLUR_RADIUS) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    mask = get_subject_mask(image_path)
    if mask is None:
        return image_path
    radius = blur_radius if blur_radius % 2 == 1 else blur_radius + 1
    blurred_bg = cv2.GaussianBlur(img, (radius, radius), 0)
    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0
    # Smooth mask edge to avoid hard cutout look
    mask_3ch = cv2.GaussianBlur(mask_3ch, (15, 15), 0)
    result = (img.astype(np.float32) * mask_3ch +
              blurred_bg.astype(np.float32) * (1 - mask_3ch))
    cv2.imwrite(output_path, result.clip(0, 255).astype(np.uint8))
    return output_path
