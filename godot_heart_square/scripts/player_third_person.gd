extends CharacterBody3D
## Third-person walker — humanoid presence + bob + footsteps
## Creator: rachaelmuse23

const WALK_SPEED := 5.2
const SPRINT_SPEED := 8.0
const JUMP_VELOCITY := 4.2
const MOUSE_SENS := 0.0035

@onready var pivot: Node3D = $CameraPivot
@onready var camera: Camera3D = $CameraPivot/Camera3D
@onready var body_root: Node3D = $Body

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")
var yaw := 0.0
var _bob_t := 0.0
var _step_t := 0.0
var _anim_t := 0.0
var _foot: AudioStreamPlayer3D
var _cam_base := Vector3(0, 1.35, 4.8)
var chat_lock := false
var _leg_l: MeshInstance3D
var _leg_r: MeshInstance3D
var _torso: MeshInstance3D


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	_foot = AudioStreamPlayer3D.new()
	_foot.name = "Footsteps"
	_foot.max_distance = 18.0
	add_child(_foot)
	_foot.stream = _make_step_stream()
	_leg_l = body_root.get_node_or_null("LegL")
	_leg_r = body_root.get_node_or_null("LegR")
	_torso = body_root.get_node_or_null("Torso")


func _make_step_stream() -> AudioStreamWAV:
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = 22050
	stream.stereo = false
	var n := 1800
	var data := PackedByteArray()
	data.resize(n * 2)
	for i in range(n):
		var t := float(i) / 22050.0
		var env := exp(-14.0 * t)
		var sample := int(clamp(sin(2.0 * PI * 90.0 * t) * env * 12000.0, -32767, 32767))
		data[i * 2] = sample & 0xFF
		data[i * 2 + 1] = (sample >> 8) & 0xFF
	stream.data = data
	return stream


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		yaw -= event.relative.x * MOUSE_SENS
		pivot.rotation.y = yaw
		var pitch: float = pivot.rotation.x - event.relative.y * MOUSE_SENS
		pivot.rotation.x = clampf(pitch, deg_to_rad(-50.0), deg_to_rad(20.0))
	if event.is_action_pressed("ui_cancel"):
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity * delta

	if chat_lock:
		velocity.x = move_toward(velocity.x, 0.0, WALK_SPEED)
		velocity.z = move_toward(velocity.z, 0.0, WALK_SPEED)
		move_and_slide()
		return

	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	var sprinting := Input.is_key_pressed(KEY_SHIFT)
	var speed := SPRINT_SPEED if sprinting else WALK_SPEED

	var input_dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	var basis_y := Basis(Vector3.UP, yaw)
	var direction := (basis_y * Vector3(input_dir.x, 0.0, input_dir.y)).normalized()
	var moving := direction != Vector3.ZERO and is_on_floor()

	if direction != Vector3.ZERO:
		velocity.x = direction.x * speed
		velocity.z = direction.z * speed
		var target_yaw := atan2(direction.x, direction.z)
		body_root.rotation.y = lerp_angle(body_root.rotation.y, target_yaw, 10.0 * delta)
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed)
		velocity.z = move_toward(velocity.z, 0.0, speed)

	move_and_slide()

	if moving:
		var cadence := 10.0 if sprinting else 7.0
		_bob_t += delta * cadence
		_step_t += delta * cadence
		_anim_t += delta * cadence
		var bob := sin(_bob_t) * (0.07 if sprinting else 0.05)
		camera.position = _cam_base + Vector3(0.0, bob, 0.0)
		if _torso:
			_torso.position.y = 1.05 + absf(sin(_bob_t)) * 0.03
		# Simple walk cycle — legs swing opposite
		var swing := sin(_anim_t) * 0.55
		if _leg_l:
			_leg_l.rotation.x = swing
		if _leg_r:
			_leg_r.rotation.x = -swing
		if _step_t >= PI:
			_step_t = 0.0
			if _foot and _foot.stream:
				_foot.pitch_scale = randf_range(0.9, 1.1)
				_foot.play()
	else:
		_bob_t = 0.0
		_step_t = 0.0
		_anim_t = 0.0
		camera.position = camera.position.lerp(_cam_base, 8.0 * delta)
		if _leg_l:
			_leg_l.rotation.x = lerpf(_leg_l.rotation.x, 0.0, 8.0 * delta)
		if _leg_r:
			_leg_r.rotation.x = lerpf(_leg_r.rotation.x, 0.0, 8.0 * delta)
		if _torso:
			_torso.position.y = lerpf(_torso.position.y, 1.05, 8.0 * delta)
