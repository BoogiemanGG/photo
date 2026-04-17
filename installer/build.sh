#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
# PhotoStudioHub — Linux / macOS build script
# Produces: dist/PhotoStudioHub/  (folder with executable)
#
# Note: PyInstaller on Linux produces a Linux binary.
#       For the Windows Setup.exe run installer\build_windows.bat
#       on a Windows machine.
# ──────────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")/.."

echo "[1/3] Installing / updating dependencies..."
pip install -r requirements.txt -q
pip install pyinstaller -q

echo "[2/3] Building with PyInstaller..."
pyinstaller PhotoStudioHub.spec --noconfirm --clean

echo "[3/3] Done."
echo ""
echo "  Binary:  dist/PhotoStudioHub/PhotoStudioHub"
echo "  Run:     ./dist/PhotoStudioHub/PhotoStudioHub"
