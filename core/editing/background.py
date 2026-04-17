from pathlib import Path
from rembg import remove
from PIL import Image


def remove_background(image_path: str, output_path: str) -> str:
    with open(image_path, "rb") as f:
        inp = f.read()
    out = remove(inp)
    output = Path(output_path).with_suffix(".png")
    with open(output, "wb") as f:
        f.write(out)
    return str(output)
