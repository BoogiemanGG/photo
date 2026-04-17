import exifread
from datetime import datetime
from collections import defaultdict


def get_timestamp(image_path: str) -> datetime | None:
    try:
        with open(image_path, "rb") as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
        dt_str = str(tags.get("EXIF DateTimeOriginal", ""))
        return datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S") if dt_str else None
    except Exception:
        return None


def group_by_event(image_paths: list[str], gap_minutes: int = 60) -> list[list[str]]:
    timed = []
    for p in image_paths:
        ts = get_timestamp(p)
        timed.append((p, ts))
    timed_valid = sorted([(p, t) for p, t in timed if t], key=lambda x: x[1])
    no_time = [p for p, t in timed if t is None]

    groups: list[list[str]] = []
    current: list[str] = []
    last_ts = None
    for path, ts in timed_valid:
        if last_ts is None or (ts - last_ts).total_seconds() / 60 > gap_minutes:
            if current:
                groups.append(current)
            current = [path]
        else:
            current.append(path)
        last_ts = ts
    if current:
        groups.append(current)
    if no_time:
        groups.append(no_time)
    return groups


def group_by_burst(image_paths: list[str], gap_seconds: int = 3) -> list[list[str]]:
    return group_by_event(image_paths, gap_minutes=gap_seconds / 60)
