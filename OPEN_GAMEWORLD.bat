@echo off
setlocal EnableExtensions
REM Mythos Hearth — Living Gameworld server (:8888)
title Mythos Gameworld :8888
cd /d "D:\Mythos_Apex"

set "PYTHON_EXE=%~dp0..\Mythos_Apex\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=D:\Mythos_Apex\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

echo [Mythos] Living Gameworld → http://127.0.0.1:8888/
echo [Mythos] Console → http://127.0.0.1:8790/play/gameworld/
echo Keep this window open.

"%PYTHON_EXE%" "D:\Mythos_Apex\gameworld_server_live.py"
pause
