import cv2
import numpy as np
from rembg import remove


def get_subject_mask(image_path: str) -> np.ndarray | None:
    with open(image_path, "rb") as f:
        inp = f.read()
    out = remove(inp)
    # rembg returns RGBA PNG — alpha channel is the mask
    import io
    from PIL import Image
    img_pil = Image.open(io.BytesIO(out)).convert("RGBA")
    alpha = np.array(img_pil)[:, :, 3]
    return alpha


def apply_subject_mask(image_path: str, output_path: str,
                        background_color: tuple = (255, 255, 255)) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    mask = get_subject_mask(image_path)
    if mask is None:
        return image_path
    # Resize mask to match image if needed
    if mask.shape != img.shape[:2]:
        mask = cv2.resize(mask, (img.shape[1], img.shape[0]))
    bg = np.full_like(img, background_color[::-1])
    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0
    result = (img.astype(np.float32) * mask_3ch +
              bg.astype(np.float32) * (1 - mask_3ch))
    cv2.imwrite(output_path, result.clip(0, 255).astype(np.uint8))
    return output_path
