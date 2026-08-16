@echo off
setlocal EnableExtensions
REM Mythos Hearth — immersive 3D Heart Square (walk / look / talk)
REM Creator: rachaelmuse23
title Mythos Hearth — Enter Immersive World
set "PROJECT=D:\Mythos_Apex\godot_project"
set "SCENE=res://scenes/heart_square_immersive.tscn"
set "PROJECT_FILE=%PROJECT%\project.godot"

if not exist "%PROJECT_FILE%" (
  echo [FAIL] Missing %PROJECT_FILE%
  pause
  exit /b 1
)

set "GODOT="
for %%G in (
  "D:\Mythos_Hearth\tools\Godot_v4.7\Godot_v4.7-stable_win64.exe"
  "D:\Mythos_Hearth\tools\Godot_v4.7\Godot_v4.7-stable_win64_console.exe"
  "D:\Mythos_Tools\Godot\Godot_v4.7-stable_win64.exe"
) do if exist %%~G if not defined GODOT set "GODOT=%%~G"

if not defined GODOT (
  echo [FAIL] Portable Godot not found.
  pause
  exit /b 1
)

echo [Mythos] Immersive Heart Square
echo   Start Hearth :8790 first so the family clock/gifts persist.
echo   WASD walk · Mouse look · Esc free cursor · E talk · F1 debug
echo   %GODOT% --path "%PROJECT%" "%SCENE%"
start "" "%GODOT%" --path "%PROJECT%" "%SCENE%"
exit /b 0
