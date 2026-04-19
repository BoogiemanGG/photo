# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for PhotoStudioHub.
#
# Build command (Windows, from the project root):
#   pyinstaller PhotoStudioHub.spec --noconfirm
#
# Prerequisites:
#   pip install pyinstaller
#   pip install -r requirements.txt
#
# Output:
#   dist/PhotoStudioHub/PhotoStudioHub.exe  (folder mode — fastest startup)
#
# Wrap with Inno Setup (installer/setup.iss) to produce Setup.exe.

import sys
from pathlib import Path

ROOT = Path(SPECPATH)

block_cipher = None

# ── Hidden imports required by our dependencies ────────────────────
hidden_imports = [
    # DeepFace / TensorFlow
    "tensorflow",
    "tf_keras",
    "deepface",
    "deepface.detectors",
    "deepface.commons",
    # OpenCV
    "cv2",
    # rembg / onnxruntime
    "rembg",
    "onnxruntime",
    # imagehash / Pillow
    "imagehash",
    "PIL",
    "PIL.Image",
    # rawpy
    "rawpy",
    # Real-ESRGAN / basicsr
    "realesrgan",
    "basicsr",
    # colour-science / LUT
    "colour",
    # Pylette
    "pylette",
    # piexif / exifread
    "piexif",
    "exifread",
    # cryptography / rsa
    "cryptography",
    "rsa",
    # customtkinter + drag & drop
    "customtkinter",
    "tkinterdnd2",
    # project modules
    "i18n",
    "config",
    "user_settings",
    "license",
    "license.fingerprint",
    "license.trial",
    "license.keys",
    "license.manager",
    "core.culling.pipeline",
    "core.editing.pipeline",
    "core.editing.io_utils",
    "core.retouching.pipeline",
    "ui.theme",
    "ui.widgets",
    "ui.views.pipeline_view",
    "ui.views.cull_review_view",
    "ui.views.settings_view",
    "ui.views.activate_view",
]

# ── Data files to bundle ──────────────────────────────────────────
datas = [
    # Locale JSON files
    (str(ROOT / "locales"),         "locales"),
    # Preset profiles
    (str(ROOT / "profiles"),        "profiles"),
    # RSA public key (NEVER include private.pem here)
    (str(ROOT / "license" / "public.pem"), "license"),
    # CustomTkinter themes / assets
    ("customtkinter", "customtkinter"),
]

# ── Binaries (OpenCV Haar cascades ship inside cv2 package) ──────
binaries = []

# ── Analysis ──────────────────────────────────────────────────────
a = Analysis(
    [str(ROOT / "app.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude dev-only packages to shrink bundle
        "pytest",
        "matplotlib",
        "notebook",
        "IPython",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PhotoStudioHub",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "installer" / "icon.ico") if (ROOT / "installer" / "icon.ico").exists() else None,
    version=str(ROOT / "installer" / "version.txt") if (ROOT / "installer" / "version.txt").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PhotoStudioHub",
)
