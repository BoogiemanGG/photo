import piexif
from pathlib import Path


def read_exif(image_path: str) -> dict:
    try:
        exif = piexif.load(image_path)
        readable = {}
        for ifd in ("0th", "Exif", "GPS", "1st"):
            for tag, value in exif.get(ifd, {}).items():
                tag_name = piexif.TAGS.get(ifd, {}).get(tag, {}).get("name", str(tag))
                try:
                    readable[tag_name] = value.decode("utf-8") if isinstance(value, bytes) else value
                except Exception:
                    readable[tag_name] = str(value)
        return readable
    except Exception as e:
        return {"error": str(e)}


def strip_exif(image_path: str, output_path: str) -> str:
    from PIL import Image
    img = Image.open(image_path)
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    clean.save(output_path)
    return output_path


def copy_exif(source_path: str, target_path: str) -> str:
    try:
        exif_bytes = piexif.dump(piexif.load(source_path))
        piexif.insert(exif_bytes, target_path)
    except Exception:
        pass
    return target_path


def batch_rename_with_exif(image_paths: list[str], pattern: str = "{date}_{time}_{seq}") -> dict:
    import exifread
    from datetime import datetime
    renamed = {}
    for i, path in enumerate(sorted(image_paths)):
        p = Path(path)
        try:
            with open(path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            dt_str = str(tags.get("EXIF DateTimeOriginal", ""))
            dt = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S") if dt_str else None
        except Exception:
            dt = None
        date = dt.strftime("%Y%m%d") if dt else "nodate"
        time_ = dt.strftime("%H%M%S") if dt else "000000"
        new_name = pattern.format(date=date, time=time_, seq=str(i + 1).zfill(4))
        new_path = p.parent / f"{new_name}{p.suffix}"
        renamed[path] = str(new_path)
    return renamed
