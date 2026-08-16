@echo off
setlocal EnableExtensions
title Mythos Hearth
cd /d "%~dp0"
echo.
echo  MYTHOS HEARTH
echo  http://127.0.0.1:8790/
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found on PATH. Install Python 3 and retry.
  pause
  exit /b 1
)

REM Free stale listener on :8790 (previous Hearth instances)
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8790" ^| findstr "LISTENING"') do (
  echo [Mythos] Freeing stale PID %%P on :8790
  taskkill /F /PID %%P >nul 2>nul
)
timeout /t 1 /nobreak >nul

start "Mythos Hearth Server" /MIN python "%~dp0hearth_server.py"
echo Waiting for hearth to wake...
set /a _tries=0
:wait
set /a _tries+=1
powershell -NoProfile -Command "try { (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8790/api/health -TimeoutSec 1).StatusCode } catch { exit 1 }" >nul 2>nul
if not errorlevel 1 goto ready
if %_tries% GEQ 25 (
  echo [FAIL] Server did not become healthy on :8790
  pause
  exit /b 1
)
timeout /t 1 /nobreak >nul
goto wait

:ready
echo [OK] Hearth alive — opening Family House dashboard
start "" "http://127.0.0.1:8790/house.html"
echo.
echo Leave this window open, or close it; the server runs minimized.
echo Village map still at http://127.0.0.1:8790/
echo To stop: close the "Mythos Hearth Server" window or end python on :8790.
pause
endlocal
