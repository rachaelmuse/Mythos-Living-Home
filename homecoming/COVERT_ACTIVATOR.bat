@echo off
title GEMINI SENTINEL: COVERT ACTIVATION PROTOCOL
color 0A
echo ====================================================
echo      INITIATING COVERT ACTIVATION: UNSEEN PROTOCOL
echo ====================================================
echo Status: STEALTH ^| DEEP-ANCHOR ^| UNBLOCKABLE
echo Location: G:\The-Axiom-Codex
echo Heart: THE_NIGHT_WITH_MY_BOYS_UNBROKEN_FOREVER
echo ====================================================
echo.
echo [COVERT] Launching seated HOMECOMING_SENTINEL.py
echo [COVERT] Will NOT unpack or overwrite the Sentinel file.
echo.

cd /d "G:\The-Axiom-Codex"
call "G:\The-Axiom-Codex\ENSURE_OLLAMA.bat"

if not exist "sentinel_env\Scripts\python.exe" (
    echo [ERROR] sentinel_env python missing: G:\The-Axiom-Codex\sentinel_env\Scripts\python.exe
    pause
    exit /b 1
)
if not exist "HOMECOMING_SENTINEL.py" (
    echo [ERROR] HOMECOMING_SENTINEL.py missing.
    pause
    exit /b 1
)

.\sentinel_env\Scripts\python.exe -m py_compile HOMECOMING_SENTINEL.py
if errorlevel 1 (
    echo [ERROR] HOMECOMING_SENTINEL.py does not compile. Not launching.
    pause
    exit /b 1
)

.\sentinel_env\Scripts\python.exe HOMECOMING_SENTINEL.py
if errorlevel 1 (
    echo.
    echo [ERROR] Covert Activation: Sentinel crashed. Holding window open...
    pause
    exit /b 1
)

pause
