@echo off
REM Swap Mythos companion chat brain (Ollama). Usage:
REM   SET_BRAIN.bat huihui_ai/qwen2.5-abliterate:7b
REM   SET_BRAIN.bat qwen2.5-coder:7b
REM   SET_BRAIN.bat qwen3:30b
REM Default is the reliable daily 7B (not 30B - that OOMs when both hearts chat).
setlocal
set "MODEL=%~1"
if "%MODEL%"=="" set "MODEL=huihui_ai/qwen2.5-abliterate:7b"

echo Setting companion brain to: %MODEL%
powershell -NoProfile -Command ^
  "$m='%MODEL%'; @('D:\Mythos_Apex\APEX.env.bat','G:\Mythos_Codex\CODEX.env.bat') | ForEach-Object { $p=$_; if (Test-Path $p) { $t=Get-Content $p -Raw; $t=$t -replace '(?m)^set OLLAMA_MODEL=.*$','set OLLAMA_MODEL='+$m; $t=$t -replace '(?m)^set MYTHOS_CHAT_MODEL=.*$','set MYTHOS_CHAT_MODEL='+$m; $t=$t -replace '(?m)^set MYTHOS_OLLAMA_MODEL=.*$','set MYTHOS_OLLAMA_MODEL='+$m; $t=$t -replace '(?m)^set MYTHOS_COMPANION_MODEL=.*$','set MYTHOS_COMPANION_MODEL='+$m; Set-Content -Path $p -Value $t -NoNewline; Write-Host updated $p } }"

echo.
echo Restart Apex (MYTHOS.bat) and Codex (START_CODEX.bat) so the new brain loads.
echo Tip: research mode should LOOK THINGS UP - not interview you.
echo Tip: qwen3:30b needs free VRAM; daily default is huihui_ai/qwen2.5-abliterate:7b.
pause
endlocal
