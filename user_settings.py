"""Persistent user settings — load/save/apply to config + i18n at runtime.

Lives at ~/.photostudiohub/user_settings.json. Sliders are stored on a
normalized 0-100 scale and mapped to real config ranges in apply().
"""

import json
from pathlib import Path

import config
from i18n import set_lang

SETTINGS_FILE = Path.home() / ".photostudiohub" / "user_settings.json"

DEFAULTS = {
    "lang": "en",
    "theme": "dark",
    "output_format": config.OUTPUT_FORMAT,
    "output_quality": config.OUTPUT_QUALITY,
    # Thresholds are 0-100 sliders; mapped to real ranges in apply().
    "thresholds.sharpness_min": 27,
    "thresholds.noise_max": 45,
    "thresholds.exposure_low": 23,
    "thresholds.exposure_high": 88,
    "thresholds.duplicate_threshold": 33,
    "thresholds.motion_blur_threshold": 10,
}

# slider-key -> (config attr, real-range low, real-range high)
THRESHOLD_RANGES = {
    "thresholds.sharpness_min":         ("SHARPNESS_MIN",         0, 300),
    "thresholds.noise_max":             ("NOISE_MAX",             0, 100),
    "thresholds.exposure_low":          ("EXPOSURE_LOW",          0, 128),
    "thresholds.exposure_high":         ("EXPOSURE_HIGH",         128, 255),
    "thresholds.duplicate_threshold":   ("DUPLICATE_THRESHOLD",   0, 30),
    "thresholds.motion_blur_threshold": ("MOTION_BLUR_THRESHOLD", 0, 50),
}


def load() -> dict:
    try:
        return {**DEFAULTS, **json.loads(SETTINGS_FILE.read_text())}
    except Exception:
        return {**DEFAULTS}


def save(data: dict) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, indent=2))


def apply(data: dict | None = None) -> dict:
    """Push persisted settings into config + i18n. Returns the resolved dict."""
    s = data if data is not None else load()

    config.OUTPUT_FORMAT = s.get("output_format", config.OUTPUT_FORMAT)
    config.OUTPUT_QUALITY = int(s.get("output_quality", config.OUTPUT_QUALITY))

    for slider_key, (attr, lo, hi) in THRESHOLD_RANGES.items():
        slider = float(s.get(slider_key, DEFAULTS[slider_key]))
        real = lo + (hi - lo) * max(0.0, min(100.0, slider)) / 100.0
        setattr(config, attr, real)

    lang = s.get("lang", DEFAULTS["lang"])
    set_lang(lang)

    return s
