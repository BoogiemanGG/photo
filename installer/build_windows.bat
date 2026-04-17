@echo off
REM ──────────────────────────────────────────────────────────────────
REM PhotoStudioHub — Windows build script
REM Run this from the project root directory.
REM Produces: dist\PhotoStudioHub-Setup-1.0.exe
REM ──────────────────────────────────────────────────────────────────

echo [1/3] Installing / updating dependencies...
pip install -r requirements.txt -q
pip install pyinstaller -q

echo [2/3] Building with PyInstaller...
pyinstaller PhotoStudioHub.spec --noconfirm --clean
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
