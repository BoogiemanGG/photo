import cv2
import numpy as np
import io
from rembg import remove
from PIL import Image
from config import BOKEH_BLUR_RADIUS

from core.editing.io_utils import imwrite


def portrait_bokeh(image_path: str, output_path: str,
                   blur_radius: int = BOKEH_BLUR_RADIUS) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    with open(image_path, "rb") as f:
        inp = f.read()
    out_bytes = remove(inp)
    img_pil = Image.open(io.BytesIO(out_bytes)).convert("RGBA")
    alpha = np.array(img_pil)[:, :, 3]
    if alpha.shape != img.shape[:2]:
        alpha = cv2.resize(alpha, (img.shape[1], img.shape[0]))
    radius = blur_radius if blur_radius % 2 == 1 else blur_radius + 1
    blurred_bg = cv2.GaussianBlur(img, (radius, radius), 0)
    mask_f = cv2.GaussianBlur(alpha.astype(np.float32), (21, 21), 0) / 255.0
    mask_3ch = np.stack([mask_f] * 3, axis=2)
    result = (img.astype(np.float32) * mask_3ch +
              blurred_bg.astype(np.float32) * (1 - mask_3ch))
    imwrite(output_path, result.clip(0, 255).astype(np.uint8))
    return output_path
