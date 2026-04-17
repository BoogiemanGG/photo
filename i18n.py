"""
i18n loader for PhotoStudioHub.

Usage:
    from i18n import t, set_lang, available_langs

    set_lang("hr")
    print(t("nav.cull"))                          # "Selekcija"
    print(t("trial.days_remaining", n=7))         # "Probna verzija: još 7 dana"
    print(t("pricing.pro_monthly", price=49))     # "€49 / mjesec"
"""

import json
import re
from pathlib import Path

_LOCALES_DIR = Path(__file__).parent / "locales"
_DEFAULT_LANG = "en"
_current_lang = "en"

_cache: dict[str, dict] = {}


def _load(lang: str) -> dict:
    if lang not in _cache:
        path = _LOCALES_DIR / f"{lang}.json"
        if not path.exists():
            return {}
        with open(path, encoding="utf-8") as f:
            _cache[lang] = json.load(f)
    return _cache[lang]


def _get_nested(data: dict, key: str):
    parts = key.split(".")
    node = data
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None


def t(key: str, lang: str | None = None, **kwargs) -> str:
    """
    Translate a dot-separated key with optional format kwargs.
    Falls back to English if the key is missing in the requested language.
    Falls back to the raw key if not found in English either.
    """
    active = lang or _current_lang

    value = _get_nested(_load(active), key)
    if value is None and active != _DEFAULT_LANG:
        value = _get_nested(_load(_DEFAULT_LANG), key)
    if value is None:
        return key

    if kwargs:
        # Replace {n}, {price}, {msg}, {t}, {tier}, {total} etc.
        for k, v in kwargs.items():
            value = value.replace("{" + k + "}", str(v))
    return value


def set_lang(lang: str) -> None:
    global _current_lang
    if lang in available_langs():
        _current_lang = lang


def get_lang() -> str:
    return _current_lang


def available_langs() -> list[str]:
    return sorted(
        p.stem for p in _LOCALES_DIR.glob("*.json")
        if not p.stem.startswith("_")
    )


def lang_display_name(lang: str) -> str:
    data = _load(lang)
    return _get_nested(data, "_meta.language") or lang.upper()


def all_lang_options() -> list[tuple[str, str]]:
    """Returns list of (code, display_name) for all available languages."""
    return [(code, lang_display_name(code)) for code in available_langs()]


def reload_all() -> None:
    """Force reload locale files from disk (useful during development)."""
    _cache.clear()
