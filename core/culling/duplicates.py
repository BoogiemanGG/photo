from PIL import Image
import imagehash
import config


def compute_hash(image_path: str) -> imagehash.ImageHash:
    return imagehash.phash(Image.open(image_path))


def group_duplicates(image_paths: list[str]) -> list[list[str]]:
    hashes = []
    for path in image_paths:
        try:
            h = compute_hash(path)
            hashes.append((path, h))
        except Exception:
            hashes.append((path, None))

    groups = []
    used = set()
    for i, (path_a, hash_a) in enumerate(hashes):
        if i in used or hash_a is None:
            continue
        group = [path_a]
        used.add(i)
        for j, (path_b, hash_b) in enumerate(hashes):
            if j in used or j == i or hash_b is None:
                continue
            if hash_a - hash_b <= config.DUPLICATE_THRESHOLD:
                group.append(path_b)
                used.add(j)
        if len(group) > 1:
            groups.append(group)
    return groups
