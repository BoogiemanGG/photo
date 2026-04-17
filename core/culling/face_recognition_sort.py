import face_recognition
import numpy as np
from pathlib import Path


def encode_faces(image_paths: list[str]) -> list[dict]:
    encodings = []
    for path in image_paths:
        try:
            img = face_recognition.load_image_file(path)
            encs = face_recognition.face_encodings(img)
            encodings.append({"path": path, "encodings": encs})
        except Exception:
            encodings.append({"path": path, "encodings": []})
    return encodings


def group_by_person(image_paths: list[str], tolerance: float = 0.6) -> dict[str, list[str]]:
    all_encodings = encode_faces(image_paths)
    groups: dict[int, list[str]] = {}
    known_encs: list[np.ndarray] = []
    known_ids: list[int] = []
    person_id = 0

    for item in all_encodings:
        for enc in item["encodings"]:
            if not known_encs:
                groups[person_id] = [item["path"]]
                known_encs.append(enc)
                known_ids.append(person_id)
                person_id += 1
                continue
            matches = face_recognition.compare_faces(known_encs, enc, tolerance=tolerance)
            if any(matches):
                matched_id = known_ids[matches.index(True)]
                if item["path"] not in groups[matched_id]:
                    groups[matched_id].append(item["path"])
            else:
                groups[person_id] = [item["path"]]
                known_encs.append(enc)
                known_ids.append(person_id)
                person_id += 1

    return {f"person_{pid}": paths for pid, paths in groups.items()}
