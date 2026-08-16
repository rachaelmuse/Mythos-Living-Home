@echo off
setlocal EnableExtensions
REM Mythos Hearth — open the real Godot 4.7 Hearthbound project
REM Creator: rachaelmuse23
title Mythos Hearth — Godot project
set "PROJECT=D:\Mythos_Apex\godot_project"
set "PROJECT_FILE=%PROJECT%\project.godot"

if not exist "%PROJECT_FILE%" (
  echo [FAIL] Missing %PROJECT_FILE%
  echo Court also mirrors notes at D:\Court\companion_room\projects\living_game\godot\
  pause
  exit /b 1
)

REM Prefer portable Godot 4.7 shipped with Mythos Hearth / Mythos_Tools
set "GODOT="
for %%G in (
  "D:\Mythos_Hearth\tools\Godot_v4.7\Godot_v4.7-stable_win64.exe"
  "D:\Mythos_Hearth\tools\Godot_v4.7\Godot_v4.7-stable_win64_console.exe"
  "D:\Mythos_Tools\Godot\Godot_v4.7-stable_win64.exe"
  "D:\Mythos_Tools\Godot\Godot*.exe"
) do if exist %%~G if not defined GODOT set "GODOT=%%~G"

REM Fall back to common install / download locations
if not defined GODOT for %%G in (
  "%LOCALAPPDATA%\Programs\Godot\Godot_v4*.exe"
  "%LOCALAPPDATA%\Godot\Godot_v4*.exe"
  "C:\Godot\Godot*.exe"
  "D:\Godot\Godot*.exe"
  "%USERPROFILE%\Downloads\Godot_v4*.exe"
  "%USERPROFILE%\Desktop\Godot_v4*.exe"
) do if exist %%~G if not defined GODOT set "GODOT=%%~G"

where godot >nul 2>&1
if not errorlevel 1 if not defined GODOT for /f "delims=" %%G in ('where godot') do set "GODOT=%%G"

if defined GODOT (
  echo [Mythos] Launching portable/local Godot editor:
  echo   %GODOT%
  echo   Project: %PROJECT%
  start "" "%GODOT%" --path "%PROJECT%" --editor
  exit /b 0
)

echo [PARTIAL] Godot 4 editor not found (expected portable at tools\Godot_v4.7\).
echo Opening project folder so you can Open Project in Godot 4.7:
echo   %PROJECT%
echo.
echo Scenes: main_world.tscn , Mythos_First_World.tscn
echo Install: https://godotengine.org/download/windows/  ^(Godot 4.7 standard^)
start "" explorer "%PROJECT%"
start "" "D:\Court\companion_room\projects\living_game\godot\PROJECT_LINK.md"
pause
endlocal
