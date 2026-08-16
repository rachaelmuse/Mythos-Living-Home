extends CharacterBody3D
## Wildlife — bounded choices: forage, eat, climb, follow, flee, hide, rest.
## AUTONOMOUS. No LLM. Not a left-right patrol script.

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

const FOOD := Vector3(-13.0, 0.2, 7.0)
const TREES := [
	Vector3(-10.0, 0.2, 10.0),
	Vector3(-18.0, 0.2, 8.0),
	Vector3(-6.0, 0.2, 12.0),
]
const HIDE := Vector3(-20.5, 0.2, 12.8)


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


func _rng() -> float:
	_seed = (_seed * 1103515245 + 12345) & 0x7fffffff
	return float(_seed % 10000) / 10000.0


func _pick(kind: String = "") -> void:
	if kind == "":
		var roll := _rng()
		if player_near:
			kind = "flee" if roll < 0.7 else "hide"
		elif roll < 0.22:
			kind = "eat"
		elif roll < 0.40:
			kind = "forage"
		elif roll < 0.52:
			kind = "climb"
		elif roll < 0.64:
			kind = "investigate"
		elif roll < 0.78:
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
			dest = FOOD + Vector3((_rng() - 0.5) * 1.6, 0, (_rng() - 0.5) * 1.6)
		"forage":
			dest = FOOD + Vector3((_rng() - 0.5) * 6.0, 0, (_rng() - 0.5) * 5.0)
		"climb":
			dest = TREES[int(_rng() * TREES.size()) % TREES.size()]
		"hide", "flee":
			dest = HIDE + Vector3((_rng() - 0.5) * 1.2, 0, (_rng() - 0.5) * 1.0)
		"follow":
			var pack := get_tree().get_nodes_in_group("squirrel")
			if pack.size() > 1:
				var other: Node = pack[int(_rng() * pack.size()) % pack.size()]
				if other != self and other is Node3D:
					dest = other.global_position + Vector3(0.7, 0, 0.4)
				else:
					dest = Vector3(-16, 0.2, 10)
			else:
				dest = Vector3(-16, 0.2, 10)
		"investigate":
			dest = Vector3(-14.0 + (_rng() - 0.5) * 8.0, 0.2, 8.0 + (_rng() - 0.5) * 6.0)
		_:
			dest = global_position
	dest.x = clampf(dest.x, -22.0, -6.0)
	dest.z = clampf(dest.z, 3.0, 14.0)


func _physics_process(delta: float) -> void:
	_t += delta
	_hold += delta
	var here := global_position
	var to := dest - here
	to.y = 0
	var speed := 2.35
	if state == "flee":
		speed = 3.9
	elif state == "rest" or state == "eat":
		speed = 0.0 if to.length() < 0.55 else 1.1
	if to.length() < 0.45 or _hold > (2.8 if state == "eat" else 6.5):
		_pick("")
		to = dest - here
		to.y = 0
	if to.length() > 0.2 and speed > 0.05:
		var d := to.normalized()
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
	# Honest: wildlife has no language model. Chirps are PLACEHOLDER sound-stand-ins.
	var s := "*chip*  (wildlife — autonomous, not speech)"
	chattered.emit(s)
	return s


func _unhandled_input(event: InputEvent) -> void:
	if not player_near:
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
		chatter()
