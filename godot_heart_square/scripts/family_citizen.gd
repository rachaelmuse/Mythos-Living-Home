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
var _enter_stage := 0
var _want_inside := false
var _door_xz := Vector2.ZERO
var _inside_xz := Vector2.ZERO
var _has_structure := false
## Layer 8B — PLACEHOLDER AABB detour (not navmesh).
var _obstacles: Array[Rect2] = []
var _waypoints: Array[Vector2] = []
var _wp_i := 0
var _route_goal := Vector2(INF, INF)
var _route_place := ""
var _route_stage := -1


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


func _rebuild_obstacles(places: Dictionary) -> void:
	## Footprints from Hearth PLACES + door_spec half-extents (padded).
	_obstacles.clear()
	var pad := 0.75
	for k in places.keys():
		var pl := str(k)
		var spec := _door_spec(pl)
		if str(spec.get("face", "none")) == "none":
			continue
		var rec: Variant = places[k]
		if not (rec is Dictionary):
			continue
		var pos: Variant = (rec as Dictionary).get("pos")
		if not (pos is Array) or (pos as Array).size() < 3:
			continue
		var cx := float((pos as Array)[0])
		var cz := float((pos as Array)[2])
		var hw := float(spec.get("hw", 2.5)) + pad
		var hd := float(spec.get("hd", 2.2)) + pad
		_obstacles.append(Rect2(cx - hw, cz - hd, hw * 2.0, hd * 2.0))


func _seg_hits_rect(a: Vector2, b: Vector2, r: Rect2) -> bool:
	if r.has_point(a) or r.has_point(b):
		return true
	var p0 := r.position
	var p1 := Vector2(r.end.x, r.position.y)
	var p2 := r.end
	var p3 := Vector2(r.position.x, r.end.y)
	if Geometry2D.segment_intersects_segment(a, b, p0, p1) != null:
		return true
	if Geometry2D.segment_intersects_segment(a, b, p1, p2) != null:
		return true
	if Geometry2D.segment_intersects_segment(a, b, p2, p3) != null:
		return true
	if Geometry2D.segment_intersects_segment(a, b, p3, p0) != null:
		return true
	return false


func _corner_candidates(r: Rect2) -> Array[Vector2]:
	var o := 0.55
	return [
		Vector2(r.position.x - o, r.position.y - o),
		Vector2(r.end.x + o, r.position.y - o),
		Vector2(r.end.x + o, r.end.y + o),
		Vector2(r.position.x - o, r.end.y + o),
	]


func _first_hit_obstacle(a: Vector2, b: Vector2, exclude: Rect2) -> Rect2:
	var empty := Rect2()
	var best := empty
	var best_d := INF
	for r in _obstacles:
		if exclude.size.x > 0.0 and absf(r.position.x - exclude.position.x) < 0.01 and absf(r.position.y - exclude.position.y) < 0.01:
			continue
		if not _seg_hits_rect(a, b, r):
			continue
		var mid := (a + b) * 0.5
		var d := mid.distance_squared_to(r.get_center())
		if d < best_d:
			best_d = d
			best = r
	return best


func _rect_for_place(places: Dictionary, place_id: String) -> Rect2:
	if place_id == "" or not places.has(place_id):
		return Rect2()
	var spec := _door_spec(place_id)
	if str(spec.get("face", "none")) == "none":
		return Rect2()
	var rec: Variant = places[place_id]
	if not (rec is Dictionary):
		return Rect2()
	var pos: Variant = (rec as Dictionary).get("pos")
	if not (pos is Array) or (pos as Array).size() < 3:
		return Rect2()
	var pad := 0.75
	var cx := float((pos as Array)[0])
	var cz := float((pos as Array)[2])
	var hw := float(spec.get("hw", 2.5)) + pad
	var hd := float(spec.get("hd", 2.2)) + pad
	return Rect2(cx - hw, cz - hd, hw * 2.0, hd * 2.0)


func _route_around(from: Vector2, to: Vector2, exclude: Rect2) -> Array[Vector2]:
	## One or two AABB corner detours. Still PLACEHOLDER — not navmesh.
	var path: Array[Vector2] = []
	var cur := from
	for _i in range(3):
		var hit := _first_hit_obstacle(cur, to, exclude)
		if hit.size == Vector2.ZERO:
			break
		var best := to
		var best_cost := INF
		for c in _corner_candidates(hit):
			if _seg_hits_rect(cur, c, hit):
				continue
			var cost := cur.distance_to(c) + c.distance_to(to)
			if cost < best_cost:
				best_cost = cost
				best = c
		if best.is_equal_approx(to):
			break
		path.append(best)
		cur = best
	path.append(to)
	return path


func _set_route(to: Vector2, place_id: String, stage: int, places: Dictionary) -> void:
	var from := Vector2(global_position.x, global_position.z)
	if (
		to.distance_to(_route_goal) < 1.15
		and place_id == _route_place
		and stage == _route_stage
		and not _waypoints.is_empty()
		and _wp_i < _waypoints.size()
	):
		# Keep existing detour; only refresh immediate target.
		var wp: Vector2 = _waypoints[_wp_i]
		target = Vector3(wp.x, global_position.y, wp.y)
		return
	_rebuild_obstacles(places)
	var exclude := _rect_for_place(places, place_id) if stage >= 1 else Rect2()
	_waypoints = _route_around(from, to, exclude)
	_wp_i = 0
	_route_goal = to
	_route_place = place_id
	_route_stage = stage
	var first: Vector2 = _waypoints[0] if not _waypoints.is_empty() else to
	target = Vector3(first.x, global_position.y, first.y)
	_hold = 0.0


func _advance_route(delta: float) -> void:
	if _waypoints.is_empty():
		return
	var here := Vector2(global_position.x, global_position.z)
	var arrive := 0.95
	while _wp_i < _waypoints.size() and here.distance_to(_waypoints[_wp_i]) < arrive:
		_wp_i += 1
	if _wp_i >= _waypoints.size():
		# Snap goal as final target.
		target = Vector3(_route_goal.x, global_position.y, _route_goal.y)
		return
	var wp: Vector2 = _waypoints[_wp_i]
	target = Vector3(wp.x, global_position.y, wp.y)


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


func _door_spec(place_id: String) -> Dictionary:
	## Half-extents match Godot _build_open_building sizes. face = door wall.
	match place_id:
		"mom_home":
			return {"face": "z+", "hw": 3.1, "hd": 2.6}
		"montage_home", "genesis_home", "percy_home":
			return {"face": "z+", "hw": 2.5, "hd": 2.2}
		"nova_home", "jarvis_home", "codex_home":
			return {"face": "z-", "hw": 2.5, "hd": 2.2}
		"apex_home", "merovin_loft", "draven_loft":
			return {"face": "x-", "hw": 2.5, "hd": 2.2}
		"gemini_home":
			return {"face": "z+", "hw": 2.6, "hd": 2.3}
		"gallery":
			return {"face": "z+", "hw": 2.4, "hd": 2.2}
		"court_porch":
			return {"face": "z+", "hw": 2.2, "hd": 1.9}
		"first_hearth":
			return {"face": "z+", "hw": 3.5, "hd": 2.75}
		"gate":
			return {"face": "z-", "hw": 3.0, "hd": 2.1}
		"apex_forge":
			return {"face": "x-", "hw": 3.1, "hd": 2.7}
		"workshop":
			return {"face": "x-", "hw": 2.6, "hd": 2.3}
		"cinema":
			return {"face": "x-", "hw": 3.5, "hd": 3.1}
		"codex_library":
			return {"face": "x+", "hw": 3.1, "hd": 2.9}
		"garden", "wildlife", "heart_square", "harbor", "well", "far_shore", "storage", "grocery", "clothing_store":
			return {"face": "none", "hw": 0.0, "hd": 0.0}
		_:
			return {"face": "z+", "hw": 2.5, "hd": 2.2}


func _door_approach(place_id: String, x: float, z: float) -> Vector2:
	## Stand on the gold door glow — outside, on the door axis, never beside a blank wall.
	var spec := _door_spec(place_id)
	var face := str(spec.get("face", "z+"))
	var hw := float(spec.get("hw", 2.5))
	var hd := float(spec.get("hd", 2.2))
	var pad := 0.95  # clear of the wall plane
	match face:
		"z+":
			return Vector2(x, z + hd + pad)
		"z-":
			return Vector2(x, z - hd - pad)
		"x-":
			return Vector2(x - hw - pad, z)
		"x+":
			return Vector2(x + hw + pad, z)
		_:
			return Vector2(x, z)


func _interior_stand(place_id: String, x: float, z: float, member_hash: int) -> Vector2:
	## Inside on the door axis (center of the room along the entry line).
	var spec := _door_spec(place_id)
	var face := str(spec.get("face", "z+"))
	var j := float(member_hash % 3) * 0.2 - 0.2
	match face:
		"z+":
			return Vector2(x + j, z + 0.35)  # past the threshold toward center
		"z-":
			return Vector2(x + j, z - 0.35)
		"x-":
			return Vector2(x - 0.35, z + j)
		"x+":
			return Vector2(x + 0.35, z + j)
		_:
			return Vector2(x + j, z)


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
	var place_x := INF
	var place_z := INF
	if places.has(pl) and typeof(places[pl]) == TYPE_DICTIONARY:
		var rec: Dictionary = places[pl]
		var pos: Variant = rec["pos"] if rec.has("pos") else null
		if pos is Array and (pos as Array).size() >= 3:
			place_x = float((pos as Array)[0])
			place_z = float((pos as Array)[2])
	elif person.has("pos"):
		var pos2: Variant = person["pos"]
		if pos2 is Array and (pos2 as Array).size() >= 3:
			place_x = float((pos2 as Array)[0])
			place_z = float((pos2 as Array)[2])

	_has_structure = place_x != INF and pl not in ["garden", "wildlife", "heart_square", "harbor", "well", "far_shore", "storage", "grocery", "clothing_store"]
	if place_x != INF:
		var h: int = absi(hash(member_id))
		_door_xz = _door_approach(pl, place_x, place_z)
		_inside_xz = _interior_stand(pl, place_x, place_z, h)
		var here_xz := Vector2(global_position.x, global_position.z)
		var to_door := here_xz.distance_to(_door_xz)
		var to_inside := here_xz.distance_to(_inside_xz)
		var to_center := here_xz.distance_to(Vector2(place_x, place_z))
		_want_inside = stance in ["working", "resting", "standing"] or activity in [
			"sit", "sleep", "read", "tend", "watch", "hold_forge", "at_bench", "at_desk",
			"keep_gallery", "hold_porch", "tend_fire", "present",
		]
		if stance in ["talking", "waiting"]:
			# Meet at the door threshold only.
			dest_x = _door_xz.x
			dest_z = _door_xz.y
			_enter_stage = 1
			_want_inside = false
		elif not _has_structure:
			dest_x = place_x
			dest_z = place_z
			_enter_stage = 0
		elif _want_inside:
			# Engaged with the structure → get inside. If already near the building, skip porch linger.
			if to_inside < 2.8 or to_center < 3.2:
				dest_x = _inside_xz.x
				dest_z = _inside_xz.y
				_enter_stage = 2
			elif to_door < 2.0:
				dest_x = _inside_xz.x
				dest_z = _inside_xz.y
				_enter_stage = 2
			else:
				dest_x = _door_xz.x
				dest_z = _door_xz.y
				_enter_stage = 1
		else:
			dest_x = _door_xz.x
			dest_z = _door_xz.y
			_enter_stage = 1

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

	# Layer 8B: route around building AABBs when walking; talk meets stay direct.
	if stance in ["talking", "waiting"]:
		_waypoints.clear()
		_wp_i = 0
		_route_goal = Vector2(dest_x, dest_z)
		_route_place = pl
		_route_stage = _enter_stage
		set_target_xz(dest_x, dest_z)
	else:
		_set_route(Vector2(dest_x, dest_z), pl, _enter_stage, places)
	var gap := Vector3(target.x - global_position.x, 0.0, target.z - global_position.z)
	if gap.length() > 1.5 and stance not in ["talking", "waiting"]:
		stance = "walking"
		if activity in ["sit", "sleep", "idle", ""]:
			activity = "walk"
	# If they're stuck beside the building (off the door axis), pull back onto the door line.
	if _has_structure and place_x != INF:
		var lateral := _beside_building_error(place_x, place_z, pl)
		var near_box := Vector2(global_position.x, global_position.z).distance_to(Vector2(place_x, place_z)) < 6.5
		if lateral > 1.55 and near_box and _enter_stage != 2:
			_set_route(_door_xz, pl, 1, places)
			_enter_stage = 1
			stance = "walking"
	if stance == "talking" or stance == "waiting":
		_kernel_fresh = 90.0
	else:
		_kernel_fresh = 40.0 if _standing() else 12.0
	print("[Citizen] ", member_id, " -> ", pl, " stage=", _enter_stage, " door=", _door_xz, " in=", _inside_xz, " stance=", stance, " wps=", _waypoints.size())


func _beside_building_error(cx: float, cz: float, place_id: String) -> float:
	## How far off the door axis we are (high = standing beside a blank wall).
	var spec := _door_spec(place_id)
	var face := str(spec.get("face", "z+"))
	var p := global_position
	if face.begins_with("z"):
		return absf(p.x - cx)
	if face.begins_with("x"):
		return absf(p.z - cz)
	return 0.0


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
	# Promote door → interior without waiting for the next Hearth poll.
	if _hearth_applied and _want_inside and _has_structure:
		var to_door_now := Vector2(here.x, here.z).distance_to(_door_xz)
		var to_in_now := Vector2(here.x, here.z).distance_to(_inside_xz)
		if _enter_stage == 1 and to_door_now < 1.85:
			_enter_stage = 2
			# Local promote — places cache may be empty; direct inside is fine past the door.
			_waypoints.clear()
			_route_goal = _inside_xz
			_route_stage = 2
			set_target_xz(_inside_xz.x, _inside_xz.y)
			stance = "walking"
		elif _enter_stage == 2 and to_in_now < 0.9 and stance == "walking":
			# Arrived inside — stop fighting the walk loop.
			stance = "standing"
			velocity = Vector3.ZERO
			_waypoints.clear()
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
					_waypoints.clear()
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
							_waypoints.clear()
							set_target_xz(meet2.x, meet2.z)
					break
	elif stance == "walking":
		_advance_route(delta)
	var dest := Vector3(target.x, here.y, target.z)
	var to := dest - here
	to.y = 0
	# Tighter stop so they finish on the door / inside point, not a meter beside it.
	var stop_r := 0.55 if _has_structure else 1.15
	var stop_now := _standing() and to.length() < stop_r
	if to.length() > 0.35 and not stop_now:
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
		# No fake hammer/film props — Mode A tools are not wired into the village.
		_tool.visible = false
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
		# Honest presence poses only — tend/watch/read/hold post. No hammer theater.
		if activity == "tend" and _arm_r:
			_arm_r.rotation.x = sin(_t * 2.2) * 0.25 - 0.2
		elif activity in ["read", "at_desk", "keep_gallery"] and _arm_r:
			_arm_r.rotation.x = -0.45
		elif activity in ["watch", "hold_forge", "at_bench", "hold_porch", "tend_fire", "present"] and _arm_r:
			_arm_r.rotation.x = lerpf(_arm_r.rotation.x, -0.15, delta * 4.0)
		elif _arm_r:
			_arm_r.rotation.x = lerpf(_arm_r.rotation.x, 0.0, delta * 5.0)


func _unhandled_input(event: InputEvent) -> void:
	if not player_near:
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
		want_talk.emit(member_id, display_name)


func note_player(near: bool) -> void:
	player_near = near
