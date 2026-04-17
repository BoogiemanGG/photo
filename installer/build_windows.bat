@echo off
REM ──────────────────────────────────────────────────────────────────
REM PhotoStudioHub — Windows build script
REM Run this from the project root directory.
REM Produces: dist\PhotoStudioHub-Setup-1.0.exe
REM
REM Requires Python 3.11.x — uses "py -3.11" launcher so it works
REM even if Python 3.14 (or any other version) is the system default.
REM ──────────────────────────────────────────────────────────────────

REM Verify Python 3.11 is available via the py launcher
py -3.11 --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python 3.11 not found via the py launcher.
    echo Install Python 3.11.15 from https://python.org/downloads/
    echo Make sure "py.exe launcher" is checked during install.
    pause
    exit /b 1
)

echo Using: && py -3.11 --version

echo [1/3] Installing / updating dependencies...
py -3.11 -m pip install -r requirements.txt -q
py -3.11 -m pip install pyinstaller -q

echo [2/3] Building with PyInstaller...
py -3.11 -m PyInstaller PhotoStudioHub.spec --noconfirm --clean
if %ERRORLEVEL% neq 0 (
    echo PyInstaller failed. Check output above.
    pause
    exit /b 1
)

echo [3/3] Creating installer with Inno Setup...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo Inno Setup not found at %ISCC%
    echo Download from: https://jrsoftware.org/isinfo.php
    echo Skipping installer creation.
    echo.
    echo PyInstaller build is at: dist\PhotoStudioHub\
    pause
    exit /b 0
)

%ISCC% installer\setup.iss
if %ERRORLEVEL% neq 0 (
    echo Inno Setup failed.
    pause
    exit /b 1
)

echo.
echo ✓ Build complete: dist\PhotoStudioHub-Setup-1.0.exe
pause
