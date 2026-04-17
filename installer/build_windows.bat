@echo off
REM ──────────────────────────────────────────────────────────────────
REM PhotoStudioHub — Windows build script
REM Double-click this file from anywhere — it finds its own location.
REM Produces: dist\PhotoStudioHub-Setup-1.0.exe

REM Always run from the project root (one folder above installer\)
cd /d "%~dp0.."
echo Running from: %CD%
REM
REM Finds Python 3.11 automatically via three methods:
REM   1. py -3.11 launcher (recommended)
REM   2. Known user-install path (Microsoft Store / winget)
REM   3. Known system-install path (python.org installer)
REM ──────────────────────────────────────────────────────────────────

set PY311=

REM Method 1 — py launcher
py -3.11 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PY311=py -3.11
    goto :found
)

REM Method 2 — user-level install (Microsoft Store / winget)
set CANDIDATE=%LOCALAPPDATA%\Python\pythoncore-3.11-64\python.exe
if exist "%CANDIDATE%" (
    "%CANDIDATE%" --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PY311="%CANDIDATE%"
        goto :found
    )
)

REM Method 3 — system-level install (python.org)
set CANDIDATE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
if exist "%CANDIDATE%" (
    "%CANDIDATE%" --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PY311="%CANDIDATE%"
        goto :found
    )
)

echo ERROR: Python 3.11 not found. Tried:
echo   1. py -3.11 launcher
echo   2. %LOCALAPPDATA%\Python\pythoncore-3.11-64\python.exe
echo   3. %LOCALAPPDATA%\Programs\Python\Python311\python.exe
echo.
echo Install Python 3.11.15 from https://python.org/downloads/
pause
exit /b 1

:found
echo Found Python 3.11: %PY311%
%PY311% --version
echo.

echo [1/3] Installing / updating dependencies...
%PY311% -m pip install -r requirements.txt -q
%PY311% -m pip install pyinstaller -q

echo [2/3] Building with PyInstaller...
%PY311% -m PyInstaller PhotoStudioHub.spec --noconfirm --clean
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
