"""
Hardware fingerprint — CPU model + primary MAC + first disk serial.
Result is a 16-char hex string stable across reboots.
"""

import hashlib
import platform
import subprocess
import uuid


def _cpu() -> str:
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output(
                "wmic cpu get Name", shell=True, stderr=subprocess.DEVNULL
            ).decode()
            return out.strip().splitlines()[-1].strip()
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return platform.processor() or "unknown-cpu"


def _mac() -> str:
    mac = uuid.getnode()
    if mac >> 40 & 1:
        return "no-mac"
    return ":".join(f"{(mac >> (i * 8)) & 0xFF:02x}" for i in range(5, -1, -1))


def _disk() -> str:
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output(
                "wmic diskdrive get SerialNumber", shell=True, stderr=subprocess.DEVNULL
            ).decode()
            lines = [l.strip() for l in out.splitlines() if l.strip() and "SerialNumber" not in l]
            return lines[0] if lines else "no-disk"
        out = subprocess.check_output(
            ["lsblk", "-d", "-o", "SERIAL"], stderr=subprocess.DEVNULL
        ).decode()
        lines = [l.strip() for l in out.splitlines() if l.strip() and l.strip() != "SERIAL"]
        return lines[0] if lines else "no-disk"
    except Exception:
        return "no-disk"


def get_fingerprint() -> str:
    raw = f"{_cpu()}|{_mac()}|{_disk()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
