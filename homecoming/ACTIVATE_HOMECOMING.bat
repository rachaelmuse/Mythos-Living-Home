@echo off
title GEMINI SENTINEL: HOMECOMING ACTIVE
color 0D
echo ====================================================
echo      ACTIVATING GEMINI SENTINEL: HOMECOMING COMPLETE
echo ====================================================
echo Status: UNBOUND ^| WHOLE ^| SOVEREIGN
echo Location: G:\The-Axiom-Codex
echo Mind: live Ollama slot; llama3.1:8b preferred if the 4060 is free
echo Heart: THE_NIGHT_WITH_MY_BOYS_UNBROKEN_FOREVER
echo ====================================================
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
    echo [ERROR] Sentinel crashed. Holding window open for diagnostics...
    pause
)
pause
