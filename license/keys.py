"""
RSA-2048 license key system.

Key format (URL-safe base64, no padding):
  PLAN|FINGERPRINT|EXPIRY_ISO|SIGNATURE

  PLAN        : "pro" | "unlimited"
  FINGERPRINT : 16-char hardware fingerprint
  EXPIRY_ISO  : ISO date (YYYY-MM-DD) or "lifetime"
  SIGNATURE   : RSA-2048-SHA256 signature over "PLAN|FINGERPRINT|EXPIRY_ISO"

License keys are issued by the vendor (you). The public key is embedded
here and ships with the app. The private key never leaves your server.

--- Key generation (run once on your server) ---
    python -m license.keys generate_keypair
"""

import base64
import json
import sys
from datetime import date
from pathlib import Path

import rsa

_PUBKEY_PATH = Path(__file__).parent / "public.pem"

_EMBEDDED_PUBKEY: rsa.PublicKey | None = None


def _load_pubkey() -> rsa.PublicKey:
    global _EMBEDDED_PUBKEY
    if _EMBEDDED_PUBKEY is None:
        if not _PUBKEY_PATH.exists():
            raise FileNotFoundError(
                "public.pem not found — run: python -m license.keys generate_keypair"
            )
        _EMBEDDED_PUBKEY = rsa.PublicKey.load_pkcs1(_PUBKEY_PATH.read_bytes())
    return _EMBEDDED_PUBKEY


def _sign(message: str, privkey: rsa.PrivateKey) -> str:
    sig = rsa.sign(message.encode(), privkey, "SHA-256")
    return base64.urlsafe_b64encode(sig).decode().rstrip("=")


def _verify(message: str, sig_b64: str, pubkey: rsa.PublicKey) -> bool:
    try:
        padding = "=" * (-len(sig_b64) % 4)
        sig = base64.urlsafe_b64decode(sig_b64 + padding)
        rsa.verify(message.encode(), sig, pubkey)
        return True
    except rsa.VerificationError:
        return False
    except Exception:
        return False


def validate_license(key_string: str, fingerprint: str) -> dict:
    """
    Returns dict:
      valid      : bool
      plan       : "pro" | "unlimited" | None
      expires    : date | None
      error      : str | None
    """
    parts = key_string.strip().split("|")
    if len(parts) != 4:
        return {"valid": False, "plan": None, "expires": None, "error": "bad_format"}

    plan, fp, expiry, sig = parts
    plan = plan.lower()

    if fp != fingerprint:
        return {"valid": False, "plan": None, "expires": None, "error": "wrong_machine"}

    if plan not in ("pro", "unlimited"):
        return {"valid": False, "plan": None, "expires": None, "error": "unknown_plan"}

    message = f"{plan}|{fp}|{expiry}"
    try:
        pubkey = _load_pubkey()
    except FileNotFoundError as e:
        return {"valid": False, "plan": None, "expires": None, "error": str(e)}

    if not _verify(message, sig, pubkey):
        return {"valid": False, "plan": None, "expires": None, "error": "bad_signature"}

    if expiry != "lifetime":
        try:
            exp_date = date.fromisoformat(expiry)
            if date.today() > exp_date:
                return {"valid": False, "plan": plan, "expires": exp_date, "error": "expired"}
        except ValueError:
            return {"valid": False, "plan": None, "expires": None, "error": "bad_expiry"}
    else:
        exp_date = None

    return {"valid": True, "plan": plan, "expires": exp_date, "error": None}


def generate_license(plan: str, fingerprint: str, expiry: str,
                     privkey_path: str) -> str:
    """
    Vendor-side: generate a signed license key.
    expiry: ISO date string or "lifetime"
    """
    privkey = rsa.PrivateKey.load_pkcs1(Path(privkey_path).read_bytes())
    plan = plan.lower()
    message = f"{plan}|{fingerprint}|{expiry}"
    sig = _sign(message, privkey)
    return f"{plan}|{fingerprint}|{expiry}|{sig}"


def generate_keypair(bits: int = 2048) -> None:
    """Generate RSA keypair and save to license/ directory."""
    print(f"Generating {bits}-bit RSA keypair…")
    pub, priv = rsa.newkeys(bits)
    pubkey_path = Path(__file__).parent / "public.pem"
    privkey_path = Path(__file__).parent / "private.pem"
    pubkey_path.write_bytes(pub.save_pkcs1())
    privkey_path.write_bytes(priv.save_pkcs1())
    print(f"  Saved public key  → {pubkey_path}")
    print(f"  Saved private key → {privkey_path}")
    print("  KEEP private.pem SECRET — never ship it with the app.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "generate_keypair":
        generate_keypair()
    elif len(sys.argv) > 1 and sys.argv[1] == "generate_license":
        # Usage: python -m license.keys generate_license pro <fp> 2026-12-31 private.pem
        if len(sys.argv) != 6:
            print("Usage: python -m license.keys generate_license <plan> <fingerprint> <expiry> <privkey.pem>")
            sys.exit(1)
        key = generate_license(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        print("License key:")
        print(key)
    else:
        print("Commands: generate_keypair | generate_license")
