@echo off
REM Shared Ollama door for Homecoming and Covert. Do not unpack Sentinel.
curl.exe -s --max-time 3 http://127.0.0.1:11434/api/tags >nul 2>&1
if not errorlevel 1 (
    echo [BRAIN] Ollama answering on :11434.
    exit /b 0
)
echo [BRAIN] Ollama not answering on :11434. Starting ollama...
start "" /B ollama serve
timeout /t 4 /nobreak >nul
curl.exe -s --max-time 8 http://127.0.0.1:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [BRAIN] Still down. Sentinel will try once more, then ask will fail honestly.
    exit /b 1
)
echo [BRAIN] Ollama is up.
exit /b 0
