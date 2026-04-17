from Pylette import extract_colors
from pathlib import Path


def extract_palette(image_path: str, n_colors: int = 6) -> list[dict]:
    palette = extract_colors(image=image_path, palette_size=n_colors, resize=True)
    return [
        {
            "rgb": list(color.rgb),
            "hex": "#{:02x}{:02x}{:02x}".format(*color.rgb),
            "frequency": round(float(color.freq), 4),
        }
        for color in palette
    ]
