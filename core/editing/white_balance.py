import cv2
import numpy as np
from config import WB_ALGORITHM


def gray_world(img: np.ndarray) -> np.ndarray:
    b, g, r = cv2.split(img.astype(np.float32))
    mean_b, mean_g, mean_r = b.mean(), g.mean(), r.mean()
    mean_gray = (mean_b + mean_g + mean_r) / 3
    img_out = cv2.merge([
        np.clip(b * (mean_gray / (mean_b + 1e-6)), 0, 255),
        np.clip(g * (mean_gray / (mean_g + 1e-6)), 0, 255),
        np.clip(r * (mean_gray / (mean_r + 1e-6)), 0, 255),
    ])
    return img_out.astype(np.uint8)


def white_patch(img: np.ndarray) -> np.ndarray:
    b, g, r = cv2.split(img.astype(np.float32))
    img_out = cv2.merge([
        np.clip(b * (255.0 / (b.max() + 1e-6)), 0, 255),
        np.clip(g * (255.0 / (g.max() + 1e-6)), 0, 255),
        np.clip(r * (255.0 / (r.max() + 1e-6)), 0, 255),
    ])
    return img_out.astype(np.uint8)


def auto_white_balance(image_path: str, output_path: str,
                        algorithm: str = WB_ALGORITHM) -> str:
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    result = gray_world(img) if algorithm == "gray_world" else white_patch(img)
    cv2.imwrite(output_path, result)
    return output_path
