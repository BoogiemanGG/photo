"""Write helper — picks JPEG/PNG/TIFF params from config at call time."""

import cv2

import config


def imwrite(path: str, img) -> bool:
    ext = str(path).rsplit(".", 1)[-1].lower()
    params: list[int] = []
    if ext in ("jpg", "jpeg"):
        params = [cv2.IMWRITE_JPEG_QUALITY, int(config.OUTPUT_QUALITY)]
    elif ext == "png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, 3]
    return bool(cv2.imwrite(path, img, params))
