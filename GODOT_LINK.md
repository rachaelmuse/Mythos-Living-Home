# Godot ↔ Mythos Hearth

- **Playable web village (primary):** http://127.0.0.1:8790/ via `START_HEARTH.bat`
- **3D Godot project:** `D:\Mythos_Apex\godot_project` (Godot **4.7**, `scenes/main_world.tscn`)
- **Mirror:** `G:\Mythos_Codex\godot_project`
- **Portable editor (preferred):** `D:\Mythos_Hearth\tools\Godot_v4.7\Godot_v4.7-stable_win64.exe`
- **Open from Hearth:** Districts → **Godot Hearthbound** or `D:\Mythos_Hearth\OPEN_GODOT.bat`
- **Court notes:** `D:\Court\companion_room\projects\living_game\godot\`

`OPEN_GODOT.bat` prefers the portable 4.7 standard exe first, then common install paths, then opens the project folder if nothing is found. Verified: `--path D:\Mythos_Apex\godot_project --headless --quit` loads (`Living World initializing…`).

HTTP `:8888` = NPC/status mock only — not the canvas village (that's `:8790`).
