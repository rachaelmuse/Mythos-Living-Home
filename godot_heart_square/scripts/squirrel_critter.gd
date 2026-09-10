extends CharacterBody3D
## Wildlife — roam the whole village. AUTONOMOUS. No LLM.

signal chattered(line: String)

@export var squirrel_id := "sq_1"
var dest := Vector3.ZERO
var player_near := false
var state := "forage"
var _t := 0.0
var _hold := 0.0
var _seed := 1
var _eat := false
var _climb_y := 0.0

const FOOD_SPOTS := [
	Vector3(-13.0, 0.2, 7.0),
	Vector3(4.0, 0.2, 4.0),
	Vector3(-6.0, 0.2, -20.0),
	Vector3(18.0, 0.2, -8.0),
	Vector3(0.0, 0.2, 18.0),
	Vector3(-24.0, 0.2, 2.0),
]
const TREES := [
	Vector3(-10.0, 0.2, 10.0),
	Vector3(-20.0, 0.2, 8.0),
	Vector3(8.0, 0.2, 10.0),
	Vector3(18.0, 0.2, -8.0),
	Vector3(0.0, 0.2, 28.0),
	Vector3(-22.0, 0.2, -12.0),
	Vector3(12.0, 0.2, 18.0),
]
const HIDE_SPOTS := [
	Vector3(-32.0, 0.2, 22.0),
	Vector3(28.0, 0.2, 4.0),
	Vector3(-14.0, 0.2, -30.0),
	Vector3(20.0, 0.2, 28.0),
]
const TOWN_STOPS := [
	Vector3(0.0, 0.2, 0.0),
	Vector3(0.0, 0.2, -16.0),
	Vector3(16.0, 0.2, -24.0),
	Vector3(-16.0, 0.2, -16.0),
	Vector3(-24.0, 0.2, -4.0),
	Vector3(22.0, 0.2, 0.0),
	Vector3(14.0, 0.2, 12.0),
	Vector3(0.0, 0.2, 22.0),
	Vector3(-18.0, 0.2, 12.0),
	Vector3(-6.0, 0.2, -24.0),
	Vector3(26.0, 0.2, 14.0),
	Vector3(20.0, 0.2, 30.0),
]
# Keep wildlife out of well footprints (xz Rect2: x,z,w,d).
const AVOID_RECTS := [
	Rect2(-10.2, 5.8, 3.6, 3.6),  # village well
]


func _ready() -> void:
	add_to_group("squirrel")
	collision_layer = 8
	collision_mask = 1
	_seed = absi(hash(squirrel_id)) + 17
	_pick("forage")
	set_physics_process(true)
	set_process(true)


func apply_kernel(rec: Dictionary) -> void:
	var st := str(rec.get("state") or rec.get("activity") or "")
	if st != "":
		state = st
	var tgt: Variant = rec.get("target")
	if tgt is Array and (tgt as Array).size() >= 3:
		var arr: Array = tgt
		dest = Vector3(float(arr[0]), 0.2, float(arr[2]))
		_clamp_town(dest)


func _rng() -> float:
	_seed = (_seed * 1103515245 + 12345) & 0x7fffffff
	return float(_seed % 10000) / 10000.0


func _in_avoid(p: Vector3) -> bool:
	var xz := Vector2(p.x, p.z)
	for r in AVOID_RECTS:
		if r.has_point(xz):
			return true
	return false


func _push_out_of_avoid(p: Vector3) -> Vector3:
	## Nudge goals/bodies out of the well so they don't path through it.
	var xz := Vector2(p.x, p.z)
	for r in AVOID_RECTS:
		if not r.has_point(xz):
			continue
		var cx: float = r.position.x + r.size.x * 0.5
		var cz: float = r.position.y + r.size.y * 0.5
		var dx: float = xz.x - cx
		var dz: float = xz.y - cz
		if absf(dx) < 0.05 and absf(dz) < 0.05:
			dx = 1.0
		var push := Vector2(dx, dz).normalized() * (maxf(r.size.x, r.size.y) * 0.55 + 0.8)
		p.x = cx + push.x
		p.z = cz + push.y
	return p


func _clamp_town(p: Vector3) -> Vector3:
	p.x = clampf(p.x, -34.0, 34.0)
	p.z = clampf(p.z, -34.0, 34.0)
	p.y = 0.2
	return _push_out_of_avoid(p)


func _jitter(base: Vector3, span: float) -> Vector3:
	return _clamp_town(base + Vector3((_rng() - 0.5) * span, 0, (_rng() - 0.5) * span))


func _pick(kind: String = "") -> void:
	if kind == "":
		var roll := _rng()
		if player_near:
			kind = "flee" if roll < 0.7 else "hide"
		elif roll < 0.18:
			kind = "eat"
		elif roll < 0.40:
			kind = "forage"
		elif roll < 0.52:
			kind = "climb"
		elif roll < 0.68:
			kind = "wander"
		elif roll < 0.80:
			kind = "follow"
		elif roll < 0.90:
			kind = "rest"
		else:
			kind = "hide"
	state = kind
	_eat = kind == "eat"
	_hold = 0.0
	_t = 0.0
	match kind:
		"eat":
			dest = _jitter(FOOD_SPOTS[int(_rng() * FOOD_SPOTS.size()) % FOOD_SPOTS.size()], 2.4)
		"forage", "wander", "investigate":
			dest = _jitter(TOWN_STOPS[int(_rng() * TOWN_STOPS.size()) % TOWN_STOPS.size()], 6.0)
		"climb":
			dest = TREES[int(_rng() * TREES.size()) % TREES.size()]
		"hide", "flee":
			dest = _jitter(HIDE_SPOTS[int(_rng() * HIDE_SPOTS.size()) % HIDE_SPOTS.size()], 2.0)
		"follow":
			var pack := get_tree().get_nodes_in_group("squirrel")
			if pack.size() > 1:
				var other: Node = pack[int(_rng() * pack.size()) % pack.size()]
				if other != self and other is Node3D:
					dest = _clamp_town((other as Node3D).global_position + Vector3(0.7, 0, 0.4))
				else:
					dest = _jitter(TOWN_STOPS[0], 4.0)
			else:
				dest = _jitter(TOWN_STOPS[0], 4.0)
		_:
			dest = global_position
	dest = _clamp_town(dest)


func _physics_process(delta: float) -> void:
	_t += delta
	_hold += delta
	var here := global_position
	var to := dest - here
	to.y = 0
	var speed := 2.8
	if state == "flee":
		speed = 4.2
	elif state == "wander" or state == "forage":
		speed = 3.1
	elif state == "rest" or state == "eat":
		speed = 0.0 if to.length() < 0.55 else 1.2
	# Reach farther goals before re-picking so they cross the village.
	var patience := 11.0 if state in ["wander", "forage", "investigate"] else (3.2 if state == "eat" else 7.0)
	if to.length() < 0.55 or _hold > patience:
		_pick("")
		to = dest - here
		to.y = 0
	if to.length() > 0.2 and speed > 0.05:
		var d := to.normalized()
		# Soft steer around well before physics hits the rim.
		var look := here + d * 1.4
		if _in_avoid(look) or _in_avoid(here):
			var cleared := _push_out_of_avoid(look)
			d = (cleared - here)
			d.y = 0
			if d.length() > 0.05:
				d = d.normalized()
			else:
				d = Vector3(1, 0, 0)
		velocity.x = d.x * speed
		velocity.z = d.z * speed
		rotation.y = atan2(d.x, d.z)
	else:
		velocity.x = 0
		velocity.z = 0
	if state == "climb" and to.length() < 0.8:
		_climb_y = min(0.85, _climb_y + delta * 0.7)
	else:
		_climb_y = max(0.0, _climb_y - delta)
	if not is_on_floor():
		velocity.y -= 16.0 * delta
	else:
		velocity.y = 0
	var players := get_tree().get_nodes_in_group("player")
	if players.size():
		var p: Node3D = players[0]
		var dist := p.global_position.distance_to(global_position)
		player_near = dist < 2.6
		if dist < 2.2:
			state = "flee"
			var away := (global_position - p.global_position)
			away.y = 0
			if away.length() > 0.01:
				away = away.normalized()
				velocity.x = away.x * 3.8
				velocity.z = away.z * 3.8
	move_and_slide()
	if _climb_y > 0.05:
		global_position.y = 0.15 + _climb_y


func _process(_delta: float) -> void:
	pass


func chatter() -> String:
	var s := "*chip*  (wildlife — autonomous, not speech)"
	chattered.emit(s)
	return s


func _unhandled_input(event: InputEvent) -> void:
	if not player_near:
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
		chatter()
