from core.culling.sharpness import score_sharpness
from core.culling.eye_detection import detect_eyes
from core.culling.exposure import analyze_exposure


def score_photo(image_path: str) -> float:
    sharpness = score_sharpness(image_path)
    exposure = analyze_exposure(image_path)
    eyes = detect_eyes(image_path)

    score = sharpness["score"] / 200.0  # normalize ~0-1
    if exposure["passed"]:
        score += 0.3
    eyes_result = eyes.get("all_eyes_open")
    if eyes_result is True:
        score += 0.4
    elif eyes_result is False:
        score -= 0.5
    return round(score, 4)


def pick_best_from_burst(image_paths: list[str]) -> dict:
    if not image_paths:
        return {"best": None, "rejected": [], "scores": {}}
    scores = {p: score_photo(p) for p in image_paths}
    best = max(scores, key=lambda p: scores[p])
    rejected = [p for p in image_paths if p != best]
    return {"best": best, "rejected": rejected, "scores": scores}


def process_burst_groups(groups: list[list[str]]) -> dict:
    results = {}
    for i, group in enumerate(groups):
        results[f"group_{i}"] = pick_best_from_burst(group)
    return results
