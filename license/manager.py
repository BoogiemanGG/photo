"""
LicenseManager — single source of truth for app access control.

Usage:
    from license.manager import LicenseManager
    lm = LicenseManager()
    if lm.can_run():
        ...
    print(lm.status_line())   # "Trial: 9 days remaining"
"""

from pathlib import Path
from datetime import date
import json

from .fingerprint import get_fingerprint
from .trial import get_trial_status
from .keys import validate_license

_DATA_DIR = Path.home() / ".photostudiohub"
_LICENSE_FILE = _DATA_DIR / "license.key"


class LicenseManager:
    def __init__(self):
        self._fp = get_fingerprint()
        self._trial = get_trial_status()
        self._license: dict | None = self._load_license()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def can_run(self) -> bool:
        """True if the user is either in active trial or has a valid license."""
        if self._license and self._license["valid"]:
            return True
        return self._trial["active"]

    def is_licensed(self) -> bool:
        return bool(self._license and self._license["valid"])

    def plan(self) -> str | None:
        """Returns 'pro', 'unlimited', 'trial', or None (expired)."""
        if self._license and self._license["valid"]:
            return self._license["plan"]
        if self._trial["active"]:
            return "trial"
        return None

    def days_left_trial(self) -> int:
        return self._trial["days_left"]

    def fingerprint(self) -> str:
        return self._fp

    def activate(self, key_string: str) -> dict:
        """
        Try to activate a license key.
        Returns validation result dict with 'valid', 'plan', 'error'.
        """
        result = validate_license(key_string, self._fp)
        if result["valid"]:
            _DATA_DIR.mkdir(parents=True, exist_ok=True)
            _LICENSE_FILE.write_text(key_string.strip())
            self._license = result
        return result

    def status_line(self, lang: str = "en") -> str:
        from i18n import t
        if self._license and self._license["valid"]:
            tier = (self._license["plan"] or "pro").capitalize()
            return t("trial.full_access", lang=lang, tier=tier)
        if self._trial["active"]:
            return t("trial.days_remaining", lang=lang, n=self._trial["days_left"])
        return t("trial.expired", lang=lang)

    def pro_photo_limit(self) -> int | None:
        """Returns monthly photo cap for Pro plan, None for unlimited/trial."""
        if self.plan() == "pro":
            from config import TIER_PRO_MONTHLY_PHOTOS
            return TIER_PRO_MONTHLY_PHOTOS
        return None

    # ------------------------------------------------------------------ #
    # Internal                                                             #
    # ------------------------------------------------------------------ #

    def _load_license(self) -> dict | None:
        if not _LICENSE_FILE.exists():
            return None
        try:
            key_string = _LICENSE_FILE.read_text().strip()
            result = validate_license(key_string, self._fp)
            return result if result["valid"] else None
        except Exception:
            return None
