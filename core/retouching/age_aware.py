from deepface import DeepFace


def get_retouch_intensity(image_path: str,
                           base_intensity: float = 1.0) -> float:
    try:
        result = DeepFace.analyze(
            img_path=image_path,
            actions=["age"],
            enforce_detection=False,
            silent=True,
        )
        if isinstance(result, list):
            result = result[0]
        age = result.get("age", 30)
        # Younger = lighter retouch, older = heavier
        if age < 20:
            return round(base_intensity * 0.5, 2)
        elif age < 35:
            return round(base_intensity * 0.75, 2)
        elif age < 50:
            return round(base_intensity * 1.0, 2)
        else:
            return round(base_intensity * 1.3, 2)
    except Exception:
        return base_intensity
