import shutil
from pathlib import Path
from tqdm import tqdm


def export_selects(cull_result: dict, output_dir: str) -> list[str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    copied = []
    for r in tqdm(cull_result.get("selects", []), desc="Exporting selects"):
        src = Path(r["path"])
        dst = out / src.name
        shutil.copy2(src, dst)
        xmp_src = src.with_suffix(".xmp")
        if xmp_src.exists():
            shutil.copy2(xmp_src, out / xmp_src.name)
        copied.append(str(dst))
    return copied


def collect_images(input_dir: str, recursive: bool = True) -> list[str]:
    extensions = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp",
                  ".cr2", ".cr3", ".nef", ".arw", ".dng", ".orf", ".rw2"}
    p = Path(input_dir)
    if recursive:
        files = [f for f in p.rglob("*") if f.suffix.lower() in extensions]
    else:
        files = [f for f in p.iterdir() if f.suffix.lower() in extensions]
    return sorted(str(f) for f in files)
