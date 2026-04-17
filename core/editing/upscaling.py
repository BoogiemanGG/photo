import cv2
import numpy as np
from pathlib import Path
from config import UPSCALE_FACTOR


def upscale(image_path: str, output_path: str, scale: int = UPSCALE_FACTOR) -> str:
    try:
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                        num_block=23, num_grow_ch=32, scale=scale)
        upsampler = RealESRGANer(
            scale=scale,
            model_path=f"https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x{scale}plus.pth",
            model=model,
            tile=400,
            tile_pad=10,
            pre_pad=0,
            half=False,
        )
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        output, _ = upsampler.enhance(img, outscale=scale)
        cv2.imwrite(output_path, output)
        return output_path
    except Exception:
        # Fallback: bicubic upscaling
        img = cv2.imread(image_path)
        if img is None:
            return image_path
        h, w = img.shape[:2]
        resized = cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(output_path, resized)
        return output_path
