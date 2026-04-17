import cv2
import numpy as np


def correct_chromatic_aberration(image_path: str, output_path: str) -> str:
    try:
        import lensfunpy
        # lensfunpy correction when camera/lens metadata available
        img = cv2.imread(image_path)
        if img is None:
            return image_path
        # Fallback to channel-shift correction without lens profile
        return _channel_shift_correction(img, output_path)
    except ImportError:
        img = cv2.imread(image_path)
        if img is None:
            return image_path
        return _channel_shift_correction(img, output_path)


def _channel_shift_correction(img: np.ndarray, output_path: str) -> str:
    b, g, r = cv2.split(img)
    h, w = img.shape[:2]
    # Red channel slight shrink, blue slight expand (common CA pattern)
    def scale_channel(ch, factor):
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, factor)
        return cv2.warpAffine(ch, M, (w, h), flags=cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_REFLECT)
    r_corrected = scale_channel(r, 0.999)
    b_corrected = scale_channel(b, 1.001)
    result = cv2.merge([b_corrected, g, r_corrected])
    cv2.imwrite(output_path, result)
    return output_path
