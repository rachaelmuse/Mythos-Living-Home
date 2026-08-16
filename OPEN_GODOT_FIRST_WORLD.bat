@echo off
setlocal EnableExtensions
REM Mythos Hearth — run Mythos_First_World.tscn (AvatarAnchor scene)
REM Creator: rachaelmuse23
title Mythos Hearth — First World
set "PROJECT=D:\Mythos_Apex\godot_project"
set "SCENE=res://scenes/Mythos_First_World.tscn"
set "PROJECT_FILE=%PROJECT%\project.godot"
set "SCENE_FILE=%PROJECT%\scenes\Mythos_First_World.tscn"

if not exist "%PROJECT_FILE%" (
  echo [FAIL] Missing %PROJECT_FILE%
  pause
  exit /b 1
)
if not exist "%SCENE_FILE%" (
  echo [FAIL] Missing %SCENE_FILE%
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
  echo [FAIL] Portable Godot not found. Try OPEN_GODOT.bat
  pause
  exit /b 1
)

echo [Mythos] First World:
echo   %GODOT% --path "%PROJECT%" "%SCENE%"
start "" "%GODOT%" --path "%PROJECT%" "%SCENE%"
exit /b 0
