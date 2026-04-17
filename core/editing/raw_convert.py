import rawpy
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
from config import OUTPUT_FORMAT, OUTPUT_QUALITY

RAW_EXTENSIONS = {".cr2", ".cr3", ".nef", ".arw", ".dng", ".orf", ".rw2",
                  ".pef", ".raf", ".srw", ".x3f", ".3fr"}


def convert_raw(image_path: str, output_path: str,
                fmt: str = OUTPUT_FORMAT) -> str:
    with rawpy.imread(image_path) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,
            output_bps=8,
            no_auto_bright=False,
        )
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    ext = ".jpg" if fmt == "JPEG" else f".{fmt.lower()}"
    out = Path(output_path).with_suffix(ext)
    params = [cv2.IMWRITE_JPEG_QUALITY, OUTPUT_QUALITY] if fmt == "JPEG" else []
    cv2.imwrite(str(out), bgr, params)
    return str(out)


def batch_convert_raw(input_dir: str, output_dir: str,
                       fmt: str = OUTPUT_FORMAT) -> list[str]:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    raw_files = [f for f in input_path.iterdir()
                 if f.suffix.lower() in RAW_EXTENSIONS]
    converted = []
    for f in tqdm(raw_files, desc="Converting RAW"):
        out = output_path / f.stem
        try:
            result = convert_raw(str(f), str(out), fmt)
            converted.append(result)
        except Exception as e:
            print(f"  ✗ {f.name}: {e}")
    return converted
