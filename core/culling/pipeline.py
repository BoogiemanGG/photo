from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tqdm import tqdm

from core.culling.sharpness import score_sharpness, score_subject_vs_background
from core.culling.exposure import analyze_exposure
from core.culling.noise import assess_noise
from core.culling.motion_blur import detect_motion_blur
from core.culling.face_detection import detect_faces
from core.culling.eye_detection import detect_eyes
from core.culling.expression import analyze_expression, analyze_age_gender
from core.culling.head_pose import estimate_head_pose
from core.culling.duplicates import group_duplicates
from core.culling.burst import process_burst_groups
from core.culling.timestamp import group_by_burst, group_by_event
from core.culling.gps import group_by_location
from config import BATCH_WORKERS


def analyze_single(image_path: str, include_faces: bool = True) -> dict:
    result = {
        "path": image_path,
        "sharpness": score_sharpness(image_path),
        "subject_sharpness": score_subject_vs_background(image_path),
        "exposure": analyze_exposure(image_path),
        "noise": assess_noise(image_path),
        "motion_blur": detect_motion_blur(image_path),
    }
    if include_faces:
        faces = detect_faces(image_path)
        result["faces"] = faces
        if faces["count"] > 0:
            result["eyes"] = detect_eyes(image_path)
            result["expression"] = analyze_expression(image_path)
            result["head_pose"] = estimate_head_pose(image_path)
            result["age_gender"] = analyze_age_gender(image_path)
        else:
            result["eyes"] = None
            result["expression"] = None
            result["head_pose"] = None
            result["age_gender"] = None
    result["passed"] = _compute_pass(result)
    result["score"] = _compute_score(result)
    return result


def _compute_pass(r: dict) -> bool:
    if not r["sharpness"]["passed"]:
        return False
    if not r["exposure"]["passed"]:
        return False
    if not r["noise"]["passed"]:
        return False
    if not r["motion_blur"]["passed"]:
        return False
    eyes = r.get("eyes")
    if eyes and eyes.get("all_eyes_open") is False:
        return False
    expr = r.get("expression")
    if expr and not expr.get("passed", True):
        return False
    return True


def _compute_score(r: dict) -> float:
    score = 0.0
    score += min(r["sharpness"]["score"] / 300.0, 1.0) * 30
    score += 20 if r["exposure"]["passed"] else 0
    score += 10 if r["noise"]["passed"] else 0
    score += 10 if r["motion_blur"]["passed"] else 0
    eyes = r.get("eyes")
    if eyes:
        score += 20 if eyes.get("all_eyes_open") else -20
    expr = r.get("expression")
    if expr and expr.get("faces"):
        score += 10 if expr["passed"] else -10
    pose = r.get("head_pose")
    if pose and pose.get("faces"):
        score += 10 if pose["passed"] else -5
    return round(score, 1)


def run_culling_pipeline(
    image_paths: list[str],
    include_faces: bool = True,
    workers: int = BATCH_WORKERS,
) -> dict:
    print(f"[PhotoStudioHub] Culling {len(image_paths)} photos...")

    # Step 1: duplicate grouping
    print("  → Grouping duplicates...")
    dup_groups = group_duplicates(image_paths)

    # Step 2: burst grouping by timestamp
    print("  → Grouping bursts by timestamp...")
    burst_groups = group_by_burst(image_paths)
    burst_results = process_burst_groups(burst_groups)

    # Step 3: per-photo analysis
    print("  → Analyzing photos...")
    results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(analyze_single, p, include_faces): p for p in image_paths}
        for future in tqdm(futures, total=len(futures)):
            results.append(future.result())

    # Step 4: sort by score
    results.sort(key=lambda r: r["score"], reverse=True)
    selects = [r for r in results if r["passed"]]
    rejects = [r for r in results if not r["passed"]]

    # Step 5: GPS grouping
    print("  → Grouping by GPS location...")
    location_groups = group_by_location(image_paths)

    # Step 6: event grouping
    event_groups = group_by_event(image_paths)

    print(f"  ✓ Done — {len(selects)} selects / {len(rejects)} rejects")
    return {
        "selects": selects,
        "rejects": rejects,
        "duplicate_groups": dup_groups,
        "burst_groups": burst_results,
        "location_groups": location_groups,
        "event_groups": event_groups,
        "total": len(image_paths),
        "select_count": len(selects),
        "reject_count": len(rejects),
    }
