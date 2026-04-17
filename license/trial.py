"""
14-day hardware-bound trial system.

Trial start date is AES-GCM encrypted with a key derived from the
hardware fingerprint. Stored in ~/.photostudiohub/trial.dat
Tampering (deleting the file, changing hardware) restarts the trial
from the new detected install date — not the original.
"""

import base64
import json
import os
from datetime import date, timedelta
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .fingerprint import get_fingerprint

TRIAL_DAYS = 14
_DATA_DIR = Path.home() / ".photostudiohub"
_TRIAL_FILE = _DATA_DIR / "trial.dat"
_SALT = b"photostudiohub_trial_salt_v1"


def _derive_key(fingerprint: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_SALT,
        iterations=100_000,
    )
    return kdf.derive(fingerprint.encode())


def _encrypt(payload: dict, key: bytes) -> str:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    data = json.dumps(payload).encode()
    ct = aesgcm.encrypt(nonce, data, None)
    return base64.b64encode(nonce + ct).decode()


def _decrypt(token: str, key: bytes) -> dict | None:
    try:
        raw = base64.b64decode(token.encode())
        nonce, ct = raw[:12], raw[12:]
        aesgcm = AESGCM(key)
        data = aesgcm.decrypt(nonce, ct, None)
        return json.loads(data)
    except Exception:
        return None


def _load_or_create(fp: str) -> dict:
    key = _derive_key(fp)
    _DATA_DIR.mkdir(parents=True, exist_ok=True)

    if _TRIAL_FILE.exists():
        try:
            token = _TRIAL_FILE.read_text().strip()
            payload = _decrypt(token, key)
            if payload and payload.get("fingerprint") == fp:
                return payload
        except Exception:
            pass

    # New trial
    payload = {
        "fingerprint": fp,
        "start": date.today().isoformat(),
        "version": 1,
    }
    _TRIAL_FILE.write_text(_encrypt(payload, key))
    return payload


def get_trial_status() -> dict:
    fp = get_fingerprint()
    payload = _load_or_create(fp)
    start = date.fromisoformat(payload["start"])
    today = date.today()
    elapsed = (today - start).days
    days_left = max(0, TRIAL_DAYS - elapsed)
    expired = days_left == 0
    return {
        "active": not expired,
        "expired": expired,
        "days_left": days_left,
        "start_date": payload["start"],
        "fingerprint": fp,
    }
