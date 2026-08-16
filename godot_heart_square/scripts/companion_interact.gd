extends Area3D
## Walk-up companion — humanoid idle + dialogue cycle + optional voice
## Creator: rachaelmuse23

@export var companion_id := "apex"
@export var display_name := "Apex"
@export var line := "I'm here — in the world with you, not only on a screen."
@export var body_color := Color(0.35, 0.85, 0.95)
@export var lines: PackedStringArray = PackedStringArray()
@export var voice_rate := 0  ## -10..10 for Windows SAPI

signal interacted(companion_id: String, display_name: String, line: String)

var player_near := false
var _body: Node3D
var _t := 0.0
var _line_i := 0


func _ready() -> void:
	body_entered.connect(_on_enter)
	body_exited.connect(_on_exit)
	monitoring = true
	monitorable = false
	collision_layer = 0
	collision_mask = 1
	_body = get_node_or_null("Body")
	_tint_body()
	if lines.is_empty():
		lines = PackedStringArray([line])
	set_process(true)


func _tint_body() -> void:
	if _body == null:
		return
	for child in _body.get_children():
		if child is MeshInstance3D:
			var mat := StandardMaterial3D.new()
			mat.albedo_color = body_color
			mat.roughness = 0.45
			mat.emission_enabled = true
			mat.emission = body_color * 0.12
			mat.emission_energy_multiplier = 0.4
			child.material_override = mat


func _process(delta: float) -> void:
	_t += delta
	if _body:
		_body.position.y = sin(_t * 2.1) * 0.04
		_body.rotation.y = sin(_t * 0.65) * 0.2
		var leg_l: MeshInstance3D = _body.get_node_or_null("LegL")
		var leg_r: MeshInstance3D = _body.get_node_or_null("LegR")
		if leg_l and leg_r:
			# Soft weight-shift idle
			leg_l.rotation.x = sin(_t * 1.3) * 0.08
			leg_r.rotation.x = -sin(_t * 1.3) * 0.08


func _on_enter(body: Node3D) -> void:
	if body.is_in_group("player"):
		player_near = true


func _on_exit(body: Node3D) -> void:
	if body.is_in_group("player"):
		player_near = false


func _unhandled_input(event: InputEvent) -> void:
	if not player_near:
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
		var spoken := line
		if lines.size() > 0:
			spoken = lines[_line_i % lines.size()]
			_line_i += 1
		interacted.emit(companion_id, display_name, spoken)
		_speak(spoken)
		get_viewport().set_input_as_handled()


func _speak(text: String) -> void:
	## Detached Windows SAPI — voice in the world without freezing the game
	var safe := text.replace("'", "").replace('"', "").replace("\n", " ")
	if safe.length() > 180:
		safe = safe.substr(0, 180)
	var rate := clampi(voice_rate, -6, 6)
	var ps := (
		"Add-Type -AssemblyName System.Speech; "
		+ "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
		+ "$s.Rate=%d; $s.Speak('%s')" % [rate, safe]
	)
	OS.create_process("powershell", ["-NoProfile", "-WindowStyle", "Hidden", "-Command", ps])
