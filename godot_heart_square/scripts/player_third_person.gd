extends CharacterBody3D
## Third-person walker — humanoid presence + bob + footsteps
## Creator: rachaelmuse23

const WALK_SPEED := 5.2
const SPRINT_SPEED := 8.0
const JUMP_VELOCITY := 4.2
const MOUSE_SENS := 0.0035
const ZOOM_MIN := 2.2
const ZOOM_MAX := 18.0

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
var _look_armed := true
var _reclaim_cd := 0.0


func _ready() -> void:
	_ensure_move_actions()
	_capture_mouse()
	_foot = AudioStreamPlayer3D.new()
	_foot.name = "Footsteps"
	_foot.max_distance = 18.0
	add_child(_foot)
	_foot.stream = _make_step_stream()
	_leg_l = body_root.get_node_or_null("LegL")
	_leg_r = body_root.get_node_or_null("LegR")
	_torso = body_root.get_node_or_null("Torso")
	get_viewport().size_changed.connect(_on_viewport_changed)
	if not get_window().focus_entered.is_connected(_on_focus_entered):
		get_window().focus_entered.connect(_on_focus_entered)
	call_deferred("_reclaim_look_burst")


func _ensure_move_actions() -> void:
	## ui_* are arrow keys only — map real WASD so Mom can walk.
	_bind_key("move_left", KEY_A)
	_bind_key("move_right", KEY_D)
	_bind_key("move_forward", KEY_W)
	_bind_key("move_back", KEY_S)
	_bind_key("move_left", KEY_LEFT)
	_bind_key("move_right", KEY_RIGHT)
	_bind_key("move_forward", KEY_UP)
	_bind_key("move_back", KEY_DOWN)


func _bind_key(action: String, keycode: Key) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	for ev in InputMap.action_get_events(action):
		if ev is InputEventKey and (ev as InputEventKey).physical_keycode == keycode:
			return
	var e := InputEventKey.new()
	e.physical_keycode = keycode
	InputMap.action_add_event(action, e)


func _capture_mouse() -> void:
	if chat_lock:
		return
	_look_armed = true
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _reclaim_look_burst() -> void:
	## Fullscreen / focus often drops capture on Windows — reclaim over a few frames.
	_capture_mouse()
	await get_tree().create_timer(0.05).timeout
	_capture_mouse()
	await get_tree().create_timer(0.2).timeout
	_capture_mouse()
	await get_tree().create_timer(0.5).timeout
	_capture_mouse()
	await get_tree().create_timer(1.0).timeout
	_capture_mouse()


func _on_viewport_changed() -> void:
	call_deferred("_capture_mouse")
	call_deferred("_reclaim_look_burst")


func _on_focus_entered() -> void:
	call_deferred("_capture_mouse")
	call_deferred("_reclaim_look_burst")


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


func _apply_look(relative: Vector2) -> void:
	if relative.length_squared() < 0.0001:
		return
	yaw -= relative.x * MOUSE_SENS
	if pivot:
		pivot.rotation.y = yaw
		var pitch: float = pivot.rotation.x - relative.y * MOUSE_SENS
		pivot.rotation.x = clampf(pitch, deg_to_rad(-78.0), deg_to_rad(55.0))


func _input(event: InputEvent) -> void:
	# Use _input (not only unhandled) so look still works over HUD labels.
	if chat_lock:
		return
	var looking := Input.mouse_mode == Input.MOUSE_MODE_CAPTURED
	var drag_look := (
		Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT)
		or Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)
	)
	if event is InputEventMouseMotion and (looking or drag_look):
		var motion := event as InputEventMouseMotion
		# Cancel stretch-mode scaling so look stays consistent fullscreen/windowed.
		var rel: Vector2 = motion.xformed_by(get_tree().root.get_final_transform()).relative
		_apply_look(rel)
		get_viewport().set_input_as_handled()
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_cam_base.z = clampf(_cam_base.z - 0.55, ZOOM_MIN, ZOOM_MAX)
			if camera:
				camera.position = _cam_base
			get_viewport().set_input_as_handled()
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_cam_base.z = clampf(_cam_base.z + 0.55, ZOOM_MIN, ZOOM_MAX)
			if camera:
				camera.position = _cam_base
			get_viewport().set_input_as_handled()
		elif event.button_index == MOUSE_BUTTON_LEFT or event.button_index == MOUSE_BUTTON_RIGHT:
			# Click / drag back into look mode after Esc / UI / fullscreen drop.
			_capture_mouse()
			get_viewport().set_input_as_handled()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		if chat_lock:
			return
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
			_look_armed = false
		else:
			_capture_mouse()
		get_viewport().set_input_as_handled()
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F11:
		_toggle_fullscreen()
		get_viewport().set_input_as_handled()


func _toggle_fullscreen() -> void:
	# Prefer borderless fullscreen — exclusive mode often kills mouse-look on Windows.
	var win := get_window()
	if win.mode == Window.MODE_FULLSCREEN or win.mode == Window.MODE_EXCLUSIVE_FULLSCREEN:
		win.mode = Window.MODE_MAXIMIZED
	else:
		win.mode = Window.MODE_FULLSCREEN
	call_deferred("_capture_mouse")
	call_deferred("_reclaim_look_burst")


func _move_vector() -> Vector2:
	## Prefer dedicated WASD actions; fall back to physical keys if map missing.
	var v := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	if v.length_squared() > 0.0001:
		return v
	var x := 0.0
	var y := 0.0
	if Input.is_physical_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
		x -= 1.0
	if Input.is_physical_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
		x += 1.0
	if Input.is_physical_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
		y -= 1.0
	if Input.is_physical_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
		y += 1.0
	return Vector2(x, y).normalized() if (x != 0.0 or y != 0.0) else Vector2.ZERO


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity * delta

	# Soft reclaim if capture dropped but Mom isn't typing / paused.
	_reclaim_cd = maxf(0.0, _reclaim_cd - delta)
	if not chat_lock and _look_armed and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED and _reclaim_cd <= 0.0:
		_capture_mouse()
		_reclaim_cd = 0.75

	if chat_lock:
		velocity.x = move_toward(velocity.x, 0.0, WALK_SPEED)
		velocity.z = move_toward(velocity.z, 0.0, WALK_SPEED)
		move_and_slide()
		return

	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	var sprinting := Input.is_key_pressed(KEY_SHIFT)
	var speed := SPRINT_SPEED if sprinting else WALK_SPEED

	var input_dir := _move_vector()
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
