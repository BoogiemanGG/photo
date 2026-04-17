from deepface import DeepFace
from config import EXPRESSION_MIN_SCORE

GOOD_EXPRESSIONS = {"happy", "neutral", "surprise"}
BAD_EXPRESSIONS = {"angry", "disgust", "fear", "sad"}


def analyze_expression(image_path: str) -> dict:
    try:
        results = DeepFace.analyze(
            img_path=image_path,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )
        if not isinstance(results, list):
            results = [results]
        faces = []
        for r in results:
            dominant = r.get("dominant_emotion", "unknown")
            emotions = r.get("emotion", {})
            confidence = emotions.get(dominant, 0) / 100.0
            is_good = dominant in GOOD_EXPRESSIONS and confidence >= EXPRESSION_MIN_SCORE
            faces.append({
                "dominant_emotion": dominant,
                "confidence": round(confidence, 3),
                "emotions": {k: round(v / 100, 3) for k, v in emotions.items()},
                "passed": is_good,
            })
        return {"faces": faces, "passed": all(f["passed"] for f in faces)}
    except Exception as e:
        return {"faces": [], "passed": False, "error": str(e)}


def analyze_age_gender(image_path: str) -> dict:
    try:
        results = DeepFace.analyze(
            img_path=image_path,
            actions=["age", "gender"],
            enforce_detection=False,
            silent=True,
        )
        if not isinstance(results, list):
            results = [results]
        return {
            "faces": [
                {"age": r.get("age"), "gender": r.get("dominant_gender")}
                for r in results
            ]
        }
    except Exception as e:
        return {"faces": [], "error": str(e)}
