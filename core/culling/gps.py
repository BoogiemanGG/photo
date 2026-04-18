import exifread
from pathlib import Path


def _dms_to_decimal(values, ref: str) -> float | None:
    try:
        d = float(values[0].num) / float(values[0].den)
        m = float(values[1].num) / float(values[1].den)
        s = float(values[2].num) / float(values[2].den)
        decimal = d + m / 60 + s / 3600
        if ref in ("S", "W"):
            decimal = -decimal
        return round(decimal, 6)
    except Exception:
        return None


def get_gps(image_path: str) -> dict:
    try:
        f_handle = open(image_path, "rb")
    except OSError:
        return {"lat": None, "lon": None, "has_gps": False}
    with f_handle as f:
        tags = exifread.process_file(f, stop_tag="GPS GPSLongitude", details=False)
    lat = _dms_to_decimal(
        tags.get("GPS GPSLatitude", type("", (), {"values": None})()).values,
        str(tags.get("GPS GPSLatitudeRef", "N")),
    ) if "GPS GPSLatitude" in tags else None
    lon = _dms_to_decimal(
        tags.get("GPS GPSLongitude", type("", (), {"values": None})()).values,
        str(tags.get("GPS GPSLongitudeRef", "E")),
    ) if "GPS GPSLongitude" in tags else None
    return {"lat": lat, "lon": lon, "has_gps": lat is not None and lon is not None}


def group_by_location(image_paths: list[str], radius_km: float = 0.5) -> list[list[str]]:
    import math
    coords = [(p, get_gps(p)) for p in image_paths]
    groups = []
    used = set()
    for i, (path_a, gps_a) in enumerate(coords):
        if i in used or not gps_a["has_gps"]:
            continue
        group = [path_a]
        used.add(i)
        for j, (path_b, gps_b) in enumerate(coords):
            if j in used or not gps_b["has_gps"]:
                continue
            dlat = math.radians(gps_b["lat"] - gps_a["lat"])
            dlon = math.radians(gps_b["lon"] - gps_a["lon"])
            a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(gps_a["lat"])) * \
                math.cos(math.radians(gps_b["lat"])) * math.sin(dlon / 2) ** 2
            dist = 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            if dist <= radius_km:
                group.append(path_b)
                used.add(j)
        if len(group) > 1:
            groups.append(group)
    return groups
