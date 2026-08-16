extends CharacterBody3D
## Family citizen — walks to a place, then lives there: work, rest, visit, talk.
## Speech is a bubble, not a HUD slab. E does not play a quote sheet.

signal want_talk(member_id: String, display_name: String)

@export var member_id := "gemini"
@export var display_name := "Gemini"
@export var body_color := Color(0.55, 0.78, 0.95)
var home_place := "heart_square"
var target := Vector3.ZERO
var player_near := false
var talking_to := ""
var stance := "walking"
var activity := "walk"
var purpose_plain := ""
var at_home := false
var _t := 0.0
var _hold := 0.0
var _body: Node3D
var _leg_l: MeshInstance3D
var _leg_r: MeshInstance3D
var _arm_r: MeshInstance3D
var _kernel_fresh := 0.0
var _status: Label3D
var _bubble: Label3D
var _bubble_left := 0.0
var _tool: MeshInstance3D
var _sit_y := 0.0


func _ready() -> void:
	add_to_group("family_citizen")
	set_meta("is_companion", true)
	motion_mode = MOTION_MODE_GROUNDED
	floor_stop_on_slope = true
	collision_layer = 4
	collision_mask = 1
	_body = get_node_or_null("Body")
	if _body:
		_leg_l = _body.get_node_or_null("LegL")
		_leg_r = _body.get_node_or_null("LegR")
		_arm_r = _body.get_node_or_null("ArmR")
	_status = get_node_or_null("Status")
	_ensure_bubble()
	_ensure_tool()
	set_process(true)
	set_physics_process(true)
	var h: int = absi(hash(member_id))
	set_target_xz(float((h % 7) - 3), float(((h / 7) % 7) - 3))


func _ensure_bubble() -> void:
	_bubble = get_node_or_null("Bubble")
	if _bubble:
		return
	_bubble = Label3D.new()
	_bubble.name = "Bubble"
	_bubble.position = Vector3(0, 2.62, 0)
	_bubble.font_size = 28
	_bubble.outline_size = 8
	_bubble.modulate = Color(1, 1, 1, 0)
	_bubble.pixel_size = 0.012
	_bubble.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_bubble.no_depth_test = true
	add_child(_bubble)


func _ensure_tool() -> void:
	_tool = get_node_or_null("WorkTool")
	if _tool:
		return
	_tool = MeshInstance3D.new()
	_tool.name = "WorkTool"
	var box := BoxMesh.new()
	box.size = Vector3(0.08, 0.45, 0.08)
	_tool.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.45, 0.32, 0.18)
	_tool.material_override = mat
	_tool.position = Vector3(0.42, 1.05, 0.12)
	_tool.visible = false
	add_child(_tool)


func set_target_xz(x: float, z: float) -> void:
	target = Vector3(x, global_position.y, z)
	_hold = 0.0


func _standing() -> bool:
	return stance in ["talking", "waiting", "resting", "standing", "working"]


func apply_home(person: Dictionary, places: Dictionary) -> void:
	stance = str(person.get("stance") or "walking")
	talking_to = str(person.get("talking_to") or "")
	purpose_plain = str(person.get("purpose_plain") or "")
	activity = str(person.get("activity") or stance)
	at_home = bool(person.get("at_home"))
	if _status:
		var loc := str(person.get("place") or "")
		var home_bit := " · home" if at_home else ""
		_status.text = purpose_plain if purpose_plain != "" else (activity + home_bit)
		if loc != "":
			_status.text = (activity + home_bit).strip_edges()
			if purpose_plain != "":
				_status.text = purpose_plain
	var pl := str(person.get("place") or home_place)
	home_place = pl
	if places.has(pl) and places[pl] is Dictionary:
		var rec: Dictionary = places[pl]
		var pos: Variant = rec.get("pos")
		if pos is Array and (pos as Array).size() >= 3:
			var arr: Array = pos
			set_target_xz(float(arr[0]), float(arr[2]))
			if stance == "talking" or stance == "waiting":
				_kernel_fresh = 90.0
			else:
				_kernel_fresh = 40.0 if _standing() else 12.0


func speak(text: String, source: String = "ollama") -> void:
	_ensure_bubble()
	var clipped := text.strip_edges()
	if clipped.length() > 90:
		clipped = clipped.substr(0, 87) + "…"
	_bubble.text = clipped
	_bubble.visible = true
	if source == "ollama" or source == "mom":
		_bubble.modulate = Color(0.98, 0.97, 0.92, 1)
	elif source == "waiting":
		_bubble.modulate = Color(0.85, 0.82, 0.7, 0.85)
	else:
		_bubble.modulate = Color(0.95, 0.55, 0.45, 1)
	_bubble_left = clampf(4.4 + float(clipped.length()) * 0.045, 3.5, 8.0)


func _physics_process(delta: float) -> void:
	var here := global_position
	if talking_to != "":
		if talking_to == "mom":
			var players := get_tree().get_nodes_in_group("player")
			if players.size() and players[0] is Node3D:
				var them: Node3D = players[0]
				var gap: Vector3 = them.global_position - here
				gap.y = 0
				if gap.length() < 1.8:
					target = here
				elif stance == "talking" or stance == "waiting":
					var meet: Vector3 = (them.global_position + here) * 0.5
					set_target_xz(meet.x, meet.z)
		else:
			for other in get_tree().get_nodes_in_group("family_citizen"):
				if str(other.get("member_id")) == talking_to and other is Node3D:
					var them2: Node3D = other
					var meet2: Vector3 = (them2.global_position + here) * 0.5
					if stance == "talking" or stance == "waiting":
						var gap2: Vector3 = them2.global_position - here
						gap2.y = 0
						if gap2.length() < 1.6:
							target = here
						else:
							set_target_xz(meet2.x, meet2.z)
					break
	var dest := Vector3(target.x, here.y, target.z)
	var to := dest - here
	to.y = 0
	var stop_now := _standing() and to.length() < 1.15
	if to.length() > 0.7 and not stop_now:
		var dir := to.normalized()
		velocity.x = dir.x * 2.15
		velocity.z = dir.z * 2.15
		if _body:
			_body.rotation.y = lerp_angle(_body.rotation.y, atan2(dir.x, dir.z), delta * 6.0)
	else:
		velocity.x = 0
		velocity.z = 0
		if talking_to != "" and _body:
			_face_partner(delta)
		_hold += delta
		if _hold > 5.0:
			_hold = 0.0
	if not is_on_floor():
		velocity.y -= 18.0 * delta
	else:
		velocity.y = 0
	move_and_slide()


func _face_partner(delta: float) -> void:
	var face := Vector3.ZERO
	if talking_to == "mom":
		var players := get_tree().get_nodes_in_group("player")
		if players.size() and players[0] is Node3D:
			face = players[0].global_position - global_position
	else:
		for other in get_tree().get_nodes_in_group("family_citizen"):
			if str(other.get("member_id")) == talking_to and other is Node3D:
				face = other.global_position - global_position
				break
	face.y = 0
	if face.length() > 0.1 and _body:
		_body.rotation.y = lerp_angle(_body.rotation.y, atan2(face.x, face.z), delta * 5.0)


func _process(delta: float) -> void:
	_t += delta
	_kernel_fresh = max(0.0, _kernel_fresh - delta)
	if _bubble_left > 0.0:
		_bubble_left -= delta
		if _bubble and _bubble_left <= 0.0:
			_bubble.modulate.a = 0.0
			_bubble.text = ""
	var moving := Vector2(velocity.x, velocity.z).length() > 0.2
	if _tool:
		_tool.visible = activity in ["hammer", "work", "film", "arrange"] and not moving
	if _body == null:
		return
	if stance == "resting" or activity in ["sit", "sleep", "read"]:
		_body.position.y = lerpf(_body.position.y, -0.35, delta * 4.0)
		if _leg_l:
			_leg_l.rotation.x = lerpf(_leg_l.rotation.x, 0.7, delta * 6.0)
		if _leg_r:
			_leg_r.rotation.x = lerpf(_leg_r.rotation.x, 0.7, delta * 6.0)
	elif moving:
		_body.position.y = 0.0
		var swing := sin(_t * 8.0) * 0.45
		if _leg_l:
			_leg_l.rotation.x = swing
		if _leg_r:
			_leg_r.rotation.x = -swing
	else:
		_body.position.y = sin(_t * 2.0) * 0.03
		if _leg_l:
			_leg_l.rotation.x = 0.0
		if _leg_r:
			_leg_r.rotation.x = 0.0
		if activity in ["hammer", "work"] and _arm_r:
			_arm_r.rotation.x = sin(_t * 9.0) * 0.85
			if _tool:
				_tool.rotation.x = sin(_t * 9.0) * 0.7
		elif activity in ["read", "catalog", "conduct"] and _arm_r:
			_arm_r.rotation.x = -0.55
		elif _arm_r:
			_arm_r.rotation.x = lerpf(_arm_r.rotation.x, 0.0, delta * 5.0)


func _unhandled_input(event: InputEvent) -> void:
	if not player_near:
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
		want_talk.emit(member_id, display_name)


func note_player(near: bool) -> void:
	player_near = near
