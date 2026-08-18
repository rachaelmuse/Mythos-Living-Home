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
var _hearth_applied := false


func _ready() -> void:
	print("[Citizen] ready: ", member_id, " (", display_name, ")")
	add_to_group("family_citizen")
	set_meta("is_companion", true)
	if str(member_id) != "" and not has_meta("family_id"):
		set_meta("family_id", str(member_id))
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
	# Hold spawn until Hearth apply_home — do NOT walk to plaza (0,0) while offline.
	call_deferred("_hold_spawn_target")


func _hold_spawn_target() -> void:
	# Race guard: if Hearth already applied, never wipe their place target.
	if _hearth_applied:
		return
	set_target_xz(global_position.x, global_position.z)
	stance = "standing"
	activity = "idle"
	if _status:
		_status.text = "Waiting for Hearth…"


func _ensure_bubble() -> void:
	_bubble = get_node_or_null("Bubble")
	if _bubble:
		return
	_bubble = Label3D.new()
	_bubble.name = "Bubble"
	_bubble.position = Vector3(0, 2.62, 0)
	_bubble.font_size = 42
	_bubble.outline_size = 12
	_bubble.modulate = Color(1, 1, 1, 0)
	_bubble.pixel_size = 0.018
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
	if stance in ["talking", "waiting"]:
		var near := Vector3(target.x - global_position.x, 0, target.z - global_position.z)
		return near.length() < 1.35
	if stance in ["resting", "standing", "working"]:
		var near2 := Vector3(target.x - global_position.x, 0, target.z - global_position.z)
		return near2.length() < 1.2
	return false


func _field_str(d: Dictionary, key: String, fallback: String = "") -> String:
	if not d.has(key):
		return fallback
	var v: Variant = d[key]
	# Reject bools — Object/JSON mixups have shown up as true/false here before.
	if typeof(v) == TYPE_BOOL:
		return fallback
	if typeof(v) == TYPE_STRING:
		var s := str(v)
		if s == "" or s == "true" or s == "false":
			return fallback
		return s
	if typeof(v) == TYPE_NIL:
		return fallback
	return str(v)


func _door_approach(place_id: String, x: float, z: float) -> Vector2:
	## Outdoor point in front of the door (matches heart_square building door faces).
	## Vector2 = (x, z). Walkers use this so they leave interiors and cross the plaza.
	match place_id:
		"mom_home":
			return Vector2(x, z + 3.8)  # door z+
		"first_hearth":
			return Vector2(x, z + 3.6)
		"gemini_home", "gallery", "court_porch":
			return Vector2(x, z + 3.2)
		"gate":
			return Vector2(x, z - 3.4)  # door z-
		"apex_forge", "workshop", "cinema":
			return Vector2(x - 3.6, z)  # door x-
		"codex_library":
			return Vector2(x + 3.6, z)  # door x+
		"garden", "wildlife", "heart_square":
			return Vector2(x, z)
		_:
			return Vector2(x, z + 2.5)


func apply_home(person: Dictionary, places: Dictionary) -> void:
	_hearth_applied = true
	stance = _field_str(person, "stance", "walking")
	talking_to = _field_str(person, "talking_to", "")
	purpose_plain = _field_str(person, "purpose_plain", "")
	activity = _field_str(person, "activity", stance)
	at_home = bool(person["at_home"]) if person.has("at_home") and typeof(person["at_home"]) == TYPE_BOOL else false
	var pl := _field_str(person, "place", "")
	if pl == "":
		pl = _field_str(person, "home", home_place)
	if pl == "":
		pl = "heart_square"
	home_place = pl
	if _status:
		var home_bit := " · home" if at_home else ""
		_status.text = purpose_plain if purpose_plain != "" else (activity + home_bit)

	var dest_x := INF
	var dest_z := INF
	var raw_place: Variant = person["place"] if person.has("place") else null
	# 1) places dictionary — walkers aim at the DOOR outside so they cross the square
	if places.has(pl) and typeof(places[pl]) == TYPE_DICTIONARY:
		var rec: Dictionary = places[pl]
		var pos: Variant = rec["pos"] if rec.has("pos") else null
		if pos is Array and (pos as Array).size() >= 3:
			var arr: Array = pos
			var door := _door_approach(pl, float(arr[0]), float(arr[2]))
			var h: int = absi(hash(member_id))
			var jx := float(h % 9) * 0.35 - 1.4
			var jz := float((h / 9) % 9) * 0.35 - 1.4
			if stance == "walking" or stance == "talking" or stance == "waiting":
				dest_x = door.x + jx * 0.35
				dest_z = door.y + jz * 0.35
			else:
				# Arrived / working / resting — stand inside near center
				dest_x = float(arr[0]) + jx * 0.5
				dest_z = float(arr[2]) + jz * 0.5
	# 2) fallback — snapshot row already carries world pos
	if dest_x == INF and person.has("pos"):
		var pos2: Variant = person["pos"]
		if pos2 is Array and (pos2 as Array).size() >= 3:
			var arr2: Array = pos2
			var door2 := _door_approach(pl, float(arr2[0]), float(arr2[2]))
			if stance == "walking":
				dest_x = door2.x
				dest_z = door2.y
			else:
				dest_x = float(arr2[0])
				dest_z = float(arr2[2])

	if dest_x == INF:
		print(
			"[Citizen] ",
			member_id,
			" cannot resolve place pl=",
			pl,
			" raw_place=",
			raw_place,
			" typeof=",
			typeof(raw_place),
			" places_has=",
			places.has(pl)
		)
		return

	set_target_xz(dest_x, dest_z)
	# Must walk to place before posing as resting/working in place.
	var gap := Vector3(target.x - global_position.x, 0.0, target.z - global_position.z)
	if gap.length() > 1.8 and stance not in ["talking", "waiting"]:
		stance = "walking"
		if activity in ["sit", "sleep", "idle", ""]:
			activity = "walk"
	if stance == "talking" or stance == "waiting":
		_kernel_fresh = 90.0
	else:
		_kernel_fresh = 40.0 if _standing() else 12.0
	print("[Citizen] ", member_id, " -> ", pl, " target=", dest_x, ",", dest_z, " stance=", stance)


func test_walk_to_heart_square() -> void:
	print("[Citizen] TEST walk to heart_square: ", member_id)
	_hearth_applied = true
	set_target_xz(0.0, 0.0)
	stance = "walking"
	activity = "walk"
	if _status:
		_status.text = "TEST: walking to Heart Square"


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
				if str(other.member_id) == talking_to and other is Node3D:
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
		velocity.x = dir.x * 3.4
		velocity.z = dir.z * 3.4
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
			if str(other.member_id) == talking_to and other is Node3D:
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
