"""
PhotoStudioHub — Installation Check
Run this on your Windows machine:

    py -3.11 check_install.py

or double-click check_install.py if Python 3.11 is the default.
Prints PASS / FAIL for every dependency and core module.
"""

import sys
import importlib

# ── Colour codes (Windows 10+ supports ANSI in CMD) ──
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

def ok(msg):  print(f"  {GREEN}PASS{RESET}  {msg}")
def fail(msg): print(f"  {RED}FAIL{RESET}  {msg}")
def warn(msg): print(f"  {YELLOW}WARN{RESET}  {msg}")

passed = failed = 0

def check(import_name, friendly=None, optional=False):
    global passed, failed
    label = friendly or import_name
    try:
        mod = importlib.import_module(import_name)
        ver = getattr(mod, "__version__", "")
        ok(f"{label}  {ver}")
        passed += 1
    except ImportError as e:
        if optional:
            warn(f"{label}  (optional — {e})")
        else:
            fail(f"{label}  — {e}")
            failed += 1

# ─────────────────────────────────────────────────────
print("\n=== PhotoStudioHub Installation Check ===\n")

# Python version
v = sys.version_info
label = f"Python {v.major}.{v.minor}.{v.micro}"
if v >= (3, 11, 3):
    ok(label)
    passed += 1
else:
    fail(f"{label}  — need 3.11.3 or later")
    failed += 1

print()
print("── Core dependencies ──")
check("cv2",          "OpenCV")
check("numpy",        "NumPy")
check("PIL",          "Pillow")
check("rawpy",        "rawpy (RAW files)")
check("imagehash",    "imagehash (pHash duplicates)")
check("piexif",       "piexif (EXIF write)")
check("exifread",     "exifread (EXIF read)")

print()
print("── AI / ML ──")
check("deepface",     "DeepFace (expression/age/gender)")
check("tf_keras",     "tf-keras (required by DeepFace)")
check("tensorflow",   "TensorFlow", optional=True)
check("ultralytics",  "YOLOv8 (scene detection)", optional=True)

print()
print("── Editing ──")
check("rembg",        "rembg (background removal)")
check("onnxruntime",  "onnxruntime (rembg backend)")
check("basicsr",      "basicsr (Real-ESRGAN base)")
check("realesrgan",   "Real-ESRGAN (upscaling)", optional=True)
check("colour",       "colour-science (LUT grading)")
check("Pylette",      "Pylette (palette extraction)")

print()
print("── GUI ──")
check("customtkinter","CustomTkinter")
check("tkinter",      "tkinter")

print()
print("── License / security ──")
check("cryptography", "cryptography (trial encryption)")
check("rsa",          "rsa (license keys)")

print()
print("── Project modules ──")
check("config",       "config.py")
check("i18n",         "i18n.py")
check("license.fingerprint", "license.fingerprint")
check("license.trial",       "license.trial")
check("license.manager",     "license.manager")

print()
print("─" * 42)
total = passed + failed
print(f"  Result: {passed}/{total} passed", end="")
if failed == 0:
    print(f"  {GREEN}— all good, ready to run!{RESET}")
else:
    print(f"  {RED}— fix the FAIL items above{RESET}")
    print()
    print("  Install missing packages:")
    print("    py -3.11 -m pip install -r requirements.txt")
print()
input("Press Enter to close...")
