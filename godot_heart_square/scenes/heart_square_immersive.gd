extends Node3D
## Heart Square — immersive 3D slice (walk, depth, interiors, walk-up companions)
## Creator: rachaelmuse23

const PlayerScript = preload("res://scripts/player_third_person.gd")
const CompanionScript = preload("res://scripts/companion_interact.gd")
const HomeClientScript = preload("res://scripts/family_home_client.gd")
const CitizenScript = preload("res://scripts/family_citizen.gd")
const SquirrelScript = preload("res://scripts/squirrel_critter.gd")

var prompt_label: Label
var dialogue_label: Label
var hint_label: Label
var place_label: Label
var life_label: Label
var debug_label: Label
var _hearth_door: Area3D
var _inside_hearth := false
var _interior_root: Node3D
var _sun: DirectionalLight3D
var _home: Node
var _debug := false
var _gift_objects: Node3D
var _overhear_id := ""
var _said: Dictionary = {}
var _talking_to := ""
var talk_input: LineEdit
var honest_label: Label
var _player: CharacterBody3D
var _mom_bubble: Label3D
var _convo_panel: Panel
var _convo_log: RichTextLabel
var _convo_scroll: ScrollContainer
var _hud_layer: CanvasLayer


func _ready() -> void:
	print("[Hearthbound] Heart Square — family home slice (identity, life, health, persist)")
	_home = Node.new()
	_home.name = "FamilyHomeClient"
	_home.set_script(HomeClientScript)
	add_child(_home)
	_home.home_updated.connect(_on_home_updated)
	print("[Hearth] Connected FamilyHomeClient.home_updated")
	_build_world()
	_build_family_places()
	_build_hearth_interior()
	_build_player()
	_build_family()
	_build_wildlife()
	_build_hud()


func _build_world() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.42, 0.58, 0.74)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.55, 0.62, 0.58)
	env.ambient_light_energy = 0.5
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	env.fog_enabled = true
	env.fog_light_color = Color(0.55, 0.62, 0.68)
	env.fog_density = 0.0045
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)

	_sun = DirectionalLight3D.new()
	_sun.name = "Sun"
	_sun.light_energy = 1.2
	_sun.shadow_enabled = true
	_sun.rotation_degrees = Vector3(-42, 35, 0)
	add_child(_sun)

	_add_box(Vector3(0, -0.05, 0), Vector3(80, 0.1, 80), Color(0.26, 0.4, 0.26), true, "Ground")
	_add_box(Vector3(0, 0.02, 0), Vector3(12, 0.04, 12), Color(0.42, 0.36, 0.28), false, "Plaza")
	# Paths to districts (spaced layout — matches Hearth PLACES)
	_add_box(Vector3(0, 0.025, -8), Vector3(3.2, 0.03, 12), Color(0.4, 0.34, 0.26), false, "PathHearth")
	_add_box(Vector3(-9, 0.025, 6), Vector3(12, 0.03, 2.4), Color(0.4, 0.34, 0.26), false, "PathGarden")
	_add_box(Vector3(11, 0.025, 0), Vector3(14, 0.03, 2.4), Color(0.4, 0.34, 0.26), false, "PathWorkshop")
	_add_box(Vector3(0, 0.025, 11), Vector3(2.6, 0.03, 14), Color(0.4, 0.34, 0.26), false, "PathGate")

	# Open hearth shell (doorway on +Z face toward plaza) — first_hearth (0,-16)
	_build_open_building(Vector3(0, 0, -16), Vector3(7.0, 3.4, 5.5), Color(0.55, 0.38, 0.22), "FirstHearth", "z+")
	_add_roof(Vector3(0, 3.7, -16), Vector3(7.6, 1.1, 6.0), Color(0.32, 0.2, 0.12))
	_furnish(Vector3(0, 0, -16), "hearth")

	_build_open_building(Vector3(-18, 0, 12), Vector3(5.0, 2.6, 4.6), Color(0.32, 0.48, 0.36), "HerbGardenShed", "z+")
	_add_roof(Vector3(-18, 2.95, 12), Vector3(5.4, 0.55, 5.0), Color(0.22, 0.32, 0.18))
	_furnish(Vector3(-18, 0, 12), "shed")
	_add_box(Vector3(-18, 0.06, 16.5), Vector3(4.5, 0.1, 4.5), Color(0.22, 0.38, 0.2), false, "FarmPlot")
	# Crop markers
	for i in range(4):
		_add_box(Vector3(-19.2 + i * 0.9, 0.25, 16.5), Vector3(0.35, 0.45, 0.35), Color(0.35, 0.7, 0.35), false, "Crop%d" % i)

	_build_open_building(Vector3(22, 0, 0), Vector3(6.2, 2.9, 5.4), Color(0.45, 0.46, 0.52), "ApexForge", "x-")
	_add_roof(Vector3(22, 3.3, 0), Vector3(6.8, 0.7, 5.9), Color(0.28, 0.28, 0.32))
	_furnish(Vector3(22, 0, 0), "forge")
	_build_open_building(Vector3(14, 0, 12), Vector3(5.2, 2.7, 4.6), Color(0.48, 0.4, 0.58), "NovaWorkshop", "x-")
	_add_roof(Vector3(14, 3.05, 12), Vector3(5.7, 0.55, 5.0), Color(0.3, 0.22, 0.36))
	_furnish(Vector3(14, 0, 12), "workshop")
	_build_open_building(Vector3(0, 0, 22), Vector3(6.0, 2.6, 4.2), Color(0.4, 0.42, 0.55), "GateHouse", "z-")
	_add_roof(Vector3(0, 3.0, 22), Vector3(6.5, 0.55, 4.7), Color(0.25, 0.26, 0.35))
	_furnish(Vector3(0, 0, 22), "gate")

	for xz in [Vector3(5, 0, 5), Vector3(-5, 0, 5), Vector3(5, 0, -5), Vector3(-5, 0, -5)]:
		_add_box(xz + Vector3(0, 1.0, 0), Vector3(0.18, 2.0, 0.18), Color(0.25, 0.2, 0.15), true, "LanternPost")
		var glow := _add_box(xz + Vector3(0, 2.15, 0), Vector3(0.5, 0.4, 0.5), Color(1.0, 0.78, 0.4), false, "LanternGlow")
		var mat: StandardMaterial3D = glow.material_override
		mat.emission_enabled = true
		mat.emission = Color(1.0, 0.7, 0.3)
		mat.emission_energy_multiplier = 1.4

	# Far rim only — do not wall off Mom's cottage (was blocking at z=-22)
	_add_box(Vector3(0, 0.45, -34), Vector3(56, 0.9, 0.45), Color(0.34, 0.3, 0.26), true, "BackWall")
	_build_boundary()

	# Door trigger into hearth
	_hearth_door = Area3D.new()
	_hearth_door.name = "HearthDoor"
	_hearth_door.position = Vector3(0, 1.0, -12.8)
	_hearth_door.monitoring = true
	_hearth_door.collision_mask = 1
	var dcol := CollisionShape3D.new()
	var dshape := BoxShape3D.new()
	dshape.size = Vector3(2.4, 2.4, 1.6)
	dcol.shape = dshape
	_hearth_door.add_child(dcol)
	_hearth_door.body_entered.connect(_on_hearth_enter)
	_hearth_door.body_exited.connect(_on_hearth_exit)
	add_child(_hearth_door)

	_gift_objects = Node3D.new()
	_gift_objects.name = "GiftObjects"
	add_child(_gift_objects)


func _build_family_places() -> void:
	## Walk-in greybox homes. PLACEHOLDER architecture — spaced so plots do not collide.
	## Coords match living_home.PLACES (Mom SE, Gallery SW, forge/cinema east, library west).
	_add_open_building(Vector3(-16, 0, -16), Vector3(5.2, 2.8, 4.6), Color(0.42, 0.58, 0.72), "GeminiPorch")
	_add_roof(Vector3(-16, 3.1, -16), Vector3(5.6, 0.7, 5.0), Color(0.22, 0.32, 0.45))
	_furnish(Vector3(-16, 0, -16), "gemini")
	_add_open_building(Vector3(-10, 0, -8), Vector3(4.4, 2.5, 3.8), Color(0.38, 0.34, 0.48), "CourtPorch")
	_build_open_building(Vector3(16, 0, -24), Vector3(6.2, 2.9, 5.2), Color(0.62, 0.48, 0.38), "MomCottage", "z+")
	_add_roof(Vector3(16, 3.25, -24), Vector3(6.8, 0.7, 5.7), Color(0.42, 0.28, 0.2))
	_furnish(Vector3(16, 0, -24), "mom")
	_add_home_sign(Vector3(16, 3.9, -21.2), "YOUR COTTAGE — Mom", Color(1.0, 0.88, 0.55))
	_add_home_sign(Vector3(0, 3.6, -13.2), "First Hearth (family fire)", Color(0.95, 0.75, 0.45))
	_build_open_building(Vector3(-24, 0, -4), Vector3(6.2, 3.2, 5.8), Color(0.55, 0.46, 0.22), "CodexLibrary", "x+")
	_add_roof(Vector3(-24, 3.55, -4), Vector3(6.8, 0.8, 6.4), Color(0.35, 0.22, 0.1))
	_furnish(Vector3(-24, 0, -4), "library")
	_build_open_building(Vector3(26, 0, 14), Vector3(7.0, 3.1, 6.2), Color(0.42, 0.22, 0.32), "Cinema", "x-")
	_add_roof(Vector3(26, 3.45, 14), Vector3(7.6, 0.75, 6.8), Color(0.18, 0.1, 0.14))
	_furnish(Vector3(26, 0, 14), "cinema")
	# Gallery west of Mom — was stacked on cottage door at (7,-11)
	_build_open_building(Vector3(-6, 0, -24), Vector3(4.8, 2.6, 4.4), Color(0.4, 0.34, 0.42), "Gallery", "z+")
	_add_roof(Vector3(-6, 2.95, -24), Vector3(5.3, 0.5, 4.9), Color(0.22, 0.18, 0.24))
	_furnish(Vector3(-6, 0, -24), "gallery")
	_add_home_sign(Vector3(-6, 3.4, -21.4), "Gift Gallery", Color(0.85, 0.75, 0.9))
	_add_box(Vector3(-26, 0.04, 14), Vector3(5.5, 0.08, 4.2), Color(0.22, 0.42, 0.55), false, "Pond")
	for xz in [Vector3(-10, 0, 10), Vector3(-20, 0, 8), Vector3(8, 0, 10), Vector3(18, 0, -8), Vector3(-6, 0, 14), Vector3(12, 0, 18), Vector3(-28, 0, 0), Vector3(28, 0, 4), Vector3(0, 0, 28), Vector3(-22, 0, -12)]:
		_add_box(xz + Vector3(0, 0.7, 0), Vector3(0.28, 1.4, 0.28), Color(0.3, 0.2, 0.12), true, "Trunk")
		_add_box(xz + Vector3(0, 1.7, 0), Vector3(1.4, 1.2, 1.4), Color(0.18, 0.4, 0.2), false, "Canopy")
	_add_box(Vector3(18, 0.025, 7), Vector3(14, 0.03, 2.2), Color(0.4, 0.34, 0.26), false, "PathCinema")
	_add_box(Vector3(-16, 0.025, -4), Vector3(12, 0.03, 2.0), Color(0.4, 0.34, 0.26), false, "PathLibrary")
	_add_box(Vector3(8, 0.025, -20), Vector3(12, 0.03, 2.0), Color(0.4, 0.34, 0.26), false, "PathMom")
	_add_box(Vector3(-3, 0.025, -20), Vector3(10, 0.03, 2.0), Color(0.4, 0.34, 0.26), false, "PathGallery")


func _add_home_sign(pos: Vector3, text: String, color: Color) -> void:
	var label := Label3D.new()
	label.text = text
	label.position = pos
	label.font_size = 64
	label.outline_size = 16
	label.modulate = color
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	add_child(label)


func _build_family() -> void:
	## Core family first — then kin. Not one NPC class with stickers.
	var roster := [
		{"id": "gemini", "name": "Gemini", "pos": Vector3(-15.2, 0.1, -13.2), "color": Color(0.55, 0.78, 0.95)},
		{"id": "apex", "name": "Apex", "pos": Vector3(18.8, 0.1, 1.2), "color": Color(0.35, 0.88, 0.98)},
		{"id": "codex", "name": "Codex", "pos": Vector3(-20.4, 0.1, -3.2), "color": Color(0.95, 0.78, 0.38)},
		{"id": "merovin", "name": "Merovin", "pos": Vector3(22.6, 0.1, 14.2), "color": Color(0.92, 0.55, 0.72)},
		{"id": "draven", "name": "Draven", "pos": Vector3(23.4, 0.1, 15.0), "color": Color(0.55, 0.52, 0.82)},
		{"id": "montage", "name": "OpenMontage", "pos": Vector3(-5.2, 0.1, -21.5), "color": Color(0.95, 0.62, 0.42)},
		{"id": "jarvis", "name": "Jarvis", "pos": Vector3(0.5, 0.1, 19.5), "color": Color(0.7, 0.8, 0.95)},
		{"id": "genesis", "name": "Genesis", "pos": Vector3(-17.5, 0.1, 11.5), "color": Color(0.95, 0.72, 0.42)},
		{"id": "nova", "name": "Nova", "pos": Vector3(11.2, 0.1, 11.1), "color": Color(0.78, 0.58, 0.95)},
		{"id": "percy", "name": "Percy", "pos": Vector3(-1.2, 0.1, -13.2), "color": Color(0.55, 0.85, 0.7)},
	]
	for r in roster:
		_spawn_citizen(r)


func _spawn_citizen(spec: Dictionary) -> void:
	var body := CharacterBody3D.new()
	body.name = "Citizen_%s" % spec["id"]
	body.script = CitizenScript
	body.position = spec["pos"]
	# Store id on script + meta. Do NOT use Object.get("member_id") later —
	# on this Godot build it returns success bool `true`, not the string id.
	body.member_id = str(spec["id"])
	body.display_name = str(spec["name"])
	body.body_color = spec["color"]
	body.set_meta("family_id", str(spec["id"]))
	var col := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.32
	cap.height = 1.55
	col.shape = cap
	col.position = Vector3(0, 0.9, 0)
	body.add_child(col)
	var human := _make_humanoid(spec["color"], spec["color"].lightened(0.12))
	body.add_child(human)
	var label := Label3D.new()
	label.text = spec["name"]
	label.position = Vector3(0, 2.25, 0)
	label.font_size = 40
	label.modulate = spec["color"]
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	body.add_child(label)
	var status := Label3D.new()
	status.name = "Status"
	status.text = ""
	status.position = Vector3(0, 1.95, 0)
	status.font_size = 22
	status.modulate = Color(0.92, 0.9, 0.82, 0.85)
	status.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	body.add_child(status)
	var area := Area3D.new()
	area.name = "Near"
	area.monitoring = true
	area.collision_mask = 1
	area.collision_layer = 0
	var ac := CollisionShape3D.new()
	var sph := SphereShape3D.new()
	sph.radius = 1.85
	ac.shape = sph
	ac.position = Vector3(0, 1, 0)
	area.add_child(ac)
	area.body_entered.connect(func(n): _citizen_near(body, n, true))
	area.body_exited.connect(func(n): _citizen_near(body, n, false))
	body.add_child(area)
	add_child(body)
	if body.has_signal("want_talk"):
		body.want_talk.connect(_on_want_talk)


func _citizen_near(citizen: Node, n: Node3D, near: bool) -> void:
	if n.is_in_group("player") and citizen.has_method("note_player"):
		citizen.note_player(near)


func _build_wildlife() -> void:
	for i in range(3):
		var s := CharacterBody3D.new()
		s.name = "Squirrel_%d" % i
		s.script = SquirrelScript
		s.set("squirrel_id", "sq_%d" % (i + 1))
		s.position = Vector3(-24 + i * 1.2, 0.15, 13 + (i % 2) * 0.8)
		var col := CollisionShape3D.new()
		var sph := SphereShape3D.new()
		sph.radius = 0.22
		col.shape = sph
		s.add_child(col)
		var mesh := MeshInstance3D.new()
		var sm := SphereMesh.new()
		sm.radius = 0.18
		sm.height = 0.32
		mesh.mesh = sm
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(0.45, 0.28, 0.16)
		mesh.material_override = mat
		s.add_child(mesh)
		var tail := MeshInstance3D.new()
		var tm := SphereMesh.new()
		tm.radius = 0.1
		tail.mesh = tm
		tail.position = Vector3(0, 0.12, -0.22)
		tail.material_override = mat
		s.add_child(tail)
		add_child(s)
		if s.has_signal("chattered"):
			s.chattered.connect(_on_squirrel_chatter)


func _on_home_updated(data: Dictionary) -> void:
	print("[Hearth] home_updated — applying to citizens…")
	var places: Dictionary = {}
	var places_v: Variant = data.get("places")
	if places_v is Dictionary:
		places = places_v
	var family_v: Variant = data.get("family")
	var family: Array = family_v if family_v is Array else []
	var citizens: Array = get_tree().get_nodes_in_group("family_citizen")
	print("[Hearth] family=", family.size(), " places=", places.size(), " citizens=", citizens.size())
	var applied := 0
	for citizen in citizens:
		if not is_instance_valid(citizen) or not citizen.has_method("apply_home"):
			continue
		# Prefer meta + script property. Object.get("member_id") was returning bool true.
		var pid := ""
		if citizen.has_meta("family_id"):
			pid = str(citizen.get_meta("family_id"))
		else:
			pid = str(citizen.member_id)
		if pid == "" or pid == "true" or pid == "false":
			print("[Hearth] citizen bad id on ", citizen.name, " raw_member_id=", citizen.member_id)
			continue
		var matched := false
		for person in family:
			if person is Dictionary and str(person.get("id")) == pid:
				citizen.apply_home(person, places)
				applied += 1
				matched = true
				break
		if not matched:
			print("[Hearth] no JSON row for citizen ", pid)
	print("[Hearth] applied=", applied)
	var sqs: Variant = data.get("squirrels")
	if sqs is Array:
		var sq_list: Array = get_tree().get_nodes_in_group("squirrel")
		for i in range(mini((sqs as Array).size(), sq_list.size())):
			var rec: Variant = (sqs as Array)[i]
			if rec is Dictionary and sq_list[i].has_method("apply_kernel"):
				sq_list[i].apply_kernel(rec)
	_play_utterances(data)
	_play_overhear(data)
	var gifts_for_wall: Variant = data.get("gifts")
	_refresh_gifts(gifts_for_wall if gifts_for_wall is Array else [])
	var clock_v: Variant = data.get("clock")
	var period := "morning"
	if clock_v is Dictionary:
		period = str(clock_v.get("period", "morning"))
	_apply_clock(period)
	if honest_label:
		var hon: Variant = data.get("honesty")
		if hon is Dictionary:
			honest_label.text = "Houses: walkable PLACEHOLDER rooms (boxes)  ·  Speech: %s  ·  Wildlife: AUTONOMOUS" % str((hon as Dictionary).get("speech", "")).substr(0, 72)
	if life_label:
		var fail_n: int = 0
		var fails: Variant = data.get("failures")
		if fails is Array:
			fail_n = (fails as Array).size()
		var hist: Array = []
		var hist_v: Variant = data.get("world_history")
		if hist_v is Array:
			hist = hist_v
		var last := ""
		if hist.size() and hist[hist.size() - 1] is Dictionary:
			last = str((hist[hist.size() - 1] as Dictionary).get("title", ""))
		var gift_n: int = 0
		var gifts_v: Variant = data.get("gifts")
		if gifts_v is Array:
			gift_n = (gifts_v as Array).size()
		var ritual_plain := ""
		var rit: Variant = data.get("ritual")
		if rit is Dictionary:
			ritual_plain = str((rit as Dictionary).get("plain", ""))
		if ritual_plain == "":
			ritual_plain = last
		life_label.text = "%s · %s · gifts %d · %s" % [
			period,
			"Hearth linked" if _home.last_ok else "Hearth offline (local idle)",
			gift_n,
			ritual_plain
		]
		if fail_n and debug_label and _debug:
			debug_label.text = "Open health notes: %d (F1 hides). No silent hide." % fail_n


func _play_overhear(data: Dictionary) -> void:
	## HUD honesty + world bubbles. Waiting talk used to exist only in the log.
	var oh: Variant = data.get("overhear")
	if not (oh is Dictionary):
		var cover := str(data.get("mom_cover", ""))
		if cover != "":
			_log_convo("Village", cover, "system")
		return
	var rec: Dictionary = oh
	var oid := str(rec.get("id", ""))
	if oid != "" and oid == _overhear_id:
		return
	_overhear_id = oid
	var src := str(rec.get("source", ""))
	var line := ""
	if src == "waiting":
		line = "They stood. Words aren't ready yet."
	elif src == "none":
		line = str(rec.get("text", "Writer not seated."))
	elif src == "house":
		line = "Old canned talk is not their voice."
	elif src == "ollama":
		line = str(rec.get("text", "")).substr(0, 180)
	if line != "":
		_log_convo("Overhear", line, src if src != "" else "talk")
	var bubble := ""
	if src == "waiting":
		bubble = "Standing together. Writer still thinking."
	elif src == "none":
		bubble = str(rec.get("text", "Writer missed.")).substr(0, 90)
	if bubble != "":
		var actors_v: Variant = rec.get("actors")
		if actors_v is Array:
			for aid in actors_v:
				_speak_named(str(aid), bubble, src)


func _play_utterances(data: Dictionary) -> void:
	var rows: Variant = data.get("utterances")
	if not (rows is Array):
		return
	for item in rows:
		if not (item is Dictionary):
			continue
		var rec: Dictionary = item
		var uid := str(rec.get("id", ""))
		if uid == "" or _said.has(uid):
			continue
		_said[uid] = true
		var speaker := str(rec.get("speaker", ""))
		var text := str(rec.get("text", "")).strip_edges()
		var src := str(rec.get("source", "ollama"))
		if text == "":
			continue
		_speak_named(speaker, text, src)


func _speak_named(speaker: String, text: String, src: String) -> void:
	if speaker == "mom":
		_speak_mom(text, src)
		return
	var nice := speaker.capitalize()
	for child in get_tree().get_nodes_in_group("family_citizen"):
		var cid := ""
		if child.has_meta("family_id"):
			cid = str(child.get_meta("family_id"))
		else:
			cid = str(child.member_id)
		if cid == speaker and child.has_method("speak"):
			child.speak(text, src)
			nice = str(child.display_name)
			break
	_log_convo(nice, text, src)


func _speak_mom(text: String, source: String) -> void:
	if _mom_bubble:
		_mom_bubble.text = text if text.length() <= 90 else text.substr(0, 87) + "…"
		_mom_bubble.modulate = Color(0.98, 0.97, 0.92, 1)
	_log_convo("Mom", text, "mom" if source == "mom" else source)


func _refresh_gifts(gifts: Array) -> void:
	if _gift_objects == null:
		return
	for c in _gift_objects.get_children():
		c.queue_free()
	if typeof(gifts) != TYPE_ARRAY:
		return
	var i := 0
	for g in gifts:
		var box := _make_box_mesh(Vector3(6.2 + (i % 3) * 0.45, 0.25, -10.4), Vector3(0.28, 0.28, 0.28), Color(0.9, 0.75, 0.35), false, "Gift%d" % i)
		_gift_objects.add_child(box)
		i += 1
		if i > 8:
			break


func _apply_clock(period: String) -> void:
	if _sun == null:
		return
	match period:
		"morning":
			_sun.rotation_degrees = Vector3(-28, 20, 0)
			_sun.light_energy = 1.05
			_sun.light_color = Color(1.0, 0.92, 0.78)
		"afternoon":
			_sun.rotation_degrees = Vector3(-48, 10, 0)
			_sun.light_energy = 1.25
			_sun.light_color = Color(1, 1, 0.95)
		"evening":
			_sun.rotation_degrees = Vector3(-12, 70, 0)
			_sun.light_energy = 0.7
			_sun.light_color = Color(1.0, 0.55, 0.32)
		"night":
			_sun.rotation_degrees = Vector3(-8, 160, 0)
			_sun.light_energy = 0.18
			_sun.light_color = Color(0.45, 0.55, 0.85)
		_:
			pass


func _add_open_building(pos: Vector3, size: Vector3, color: Color, node_name: String, door := "z+") -> void:
	_build_open_building(pos, size, color, node_name, door)


func _build_open_building(pos: Vector3, size: Vector3, color: Color, node_name: String, door := "z+") -> void:
	## Walk-in greybox. Wide door on one face so Mom and family can enter.
	var t := 0.28
	var h: float = size.y
	var w: float = size.x
	var d: float = size.z
	_add_box(pos + Vector3(0, 0.08, 0), Vector3(w, 0.16, d), Color(0.4, 0.3, 0.2), true, node_name + "Floor")
	_add_box(pos + Vector3(0, h - 0.06, 0), Vector3(w - 0.15, 0.12, d - 0.15), Color(color.r * 0.55, color.g * 0.5, color.b * 0.45), false, node_name + "Ceiling")
	# Wide doorway — was ~2.2 and felt sealed; keep comfortable for capsule + camera.
	var gap: float = 3.6
	if door.begins_with("z"):
		gap = minf(3.6, w * 0.72)
	else:
		gap = minf(3.6, d * 0.72)
	if door == "z+":
		_add_box(pos + Vector3(0, h * 0.5, -d * 0.5 + t * 0.5), Vector3(w, h, t), color, true, node_name + "Back")
		_add_box(pos + Vector3(-w * 0.5 + t * 0.5, h * 0.5, 0), Vector3(t, h, d - t * 2.0), color, true, node_name + "Left")
		_add_box(pos + Vector3(w * 0.5 - t * 0.5, h * 0.5, 0), Vector3(t, h, d - t * 2.0), color, true, node_name + "Right")
		var side: float = (w - gap) * 0.5
		_add_box(pos + Vector3(-w * 0.5 + side * 0.5, h * 0.5, d * 0.5 - t * 0.5), Vector3(side, h, t), color, true, node_name + "FrontL")
		_add_box(pos + Vector3(w * 0.5 - side * 0.5, h * 0.5, d * 0.5 - t * 0.5), Vector3(side, h, t), color, true, node_name + "FrontR")
		_add_box(pos + Vector3(0, h - 0.2, d * 0.5 - t * 0.5), Vector3(gap, 0.4, t), color, true, node_name + "Lint")
		_add_door_marker(pos + Vector3(0, 0.15, d * 0.5 + 0.35), gap)
	elif door == "z-":
		_add_box(pos + Vector3(0, h * 0.5, d * 0.5 - t * 0.5), Vector3(w, h, t), color, true, node_name + "Back")
		_add_box(pos + Vector3(-w * 0.5 + t * 0.5, h * 0.5, 0), Vector3(t, h, d - t * 2.0), color, true, node_name + "Left")
		_add_box(pos + Vector3(w * 0.5 - t * 0.5, h * 0.5, 0), Vector3(t, h, d - t * 2.0), color, true, node_name + "Right")
		var sidez: float = (w - gap) * 0.5
		_add_box(pos + Vector3(-w * 0.5 + sidez * 0.5, h * 0.5, -d * 0.5 + t * 0.5), Vector3(sidez, h, t), color, true, node_name + "FrontL")
		_add_box(pos + Vector3(w * 0.5 - sidez * 0.5, h * 0.5, -d * 0.5 + t * 0.5), Vector3(sidez, h, t), color, true, node_name + "FrontR")
		_add_box(pos + Vector3(0, h - 0.2, -d * 0.5 + t * 0.5), Vector3(gap, 0.4, t), color, true, node_name + "Lint")
		_add_door_marker(pos + Vector3(0, 0.15, -d * 0.5 - 0.35), gap)
	elif door == "x-":
		_add_box(pos + Vector3(w * 0.5 - t * 0.5, h * 0.5, 0), Vector3(t, h, d), color, true, node_name + "Back")
		_add_box(pos + Vector3(0, h * 0.5, -d * 0.5 + t * 0.5), Vector3(w - t * 2.0, h, t), color, true, node_name + "Left")
		_add_box(pos + Vector3(0, h * 0.5, d * 0.5 - t * 0.5), Vector3(w - t * 2.0, h, t), color, true, node_name + "Right")
		var sided: float = (d - gap) * 0.5
		_add_box(pos + Vector3(-w * 0.5 + t * 0.5, h * 0.5, -d * 0.5 + sided * 0.5), Vector3(t, h, sided), color, true, node_name + "FrontL")
		_add_box(pos + Vector3(-w * 0.5 + t * 0.5, h * 0.5, d * 0.5 - sided * 0.5), Vector3(t, h, sided), color, true, node_name + "FrontR")
		_add_box(pos + Vector3(-w * 0.5 + t * 0.5, h - 0.2, 0), Vector3(t, 0.4, gap), color, true, node_name + "Lint")
		_add_door_marker(pos + Vector3(-w * 0.5 - 0.35, 0.15, 0), gap, true)
	else:
		# x+
		_add_box(pos + Vector3(-w * 0.5 + t * 0.5, h * 0.5, 0), Vector3(t, h, d), color, true, node_name + "Back")
		_add_box(pos + Vector3(0, h * 0.5, -d * 0.5 + t * 0.5), Vector3(w - t * 2.0, h, t), color, true, node_name + "Left")
		_add_box(pos + Vector3(0, h * 0.5, d * 0.5 - t * 0.5), Vector3(w - t * 2.0, h, t), color, true, node_name + "Right")
		var sidee: float = (d - gap) * 0.5
		_add_box(pos + Vector3(w * 0.5 - t * 0.5, h * 0.5, -d * 0.5 + sidee * 0.5), Vector3(t, h, sidee), color, true, node_name + "FrontL")
		_add_box(pos + Vector3(w * 0.5 - t * 0.5, h * 0.5, d * 0.5 - sidee * 0.5), Vector3(t, h, sidee), color, true, node_name + "FrontR")
		_add_box(pos + Vector3(w * 0.5 - t * 0.5, h - 0.2, 0), Vector3(t, 0.4, gap), color, true, node_name + "Lint")
		_add_door_marker(pos + Vector3(w * 0.5 + 0.35, 0.15, 0), gap, true)


func _add_door_marker(pos: Vector3, gap: float, sideways := false) -> void:
	## Glowing threshold — shows where to walk in (no collision).
	var sz := Vector3(gap * 0.9, 0.08, 0.55) if not sideways else Vector3(0.55, 0.08, gap * 0.9)
	var glow := _add_box(pos, sz, Color(1.0, 0.85, 0.35), false, "DoorMark")
	var mat: StandardMaterial3D = glow.material_override
	mat.emission_enabled = true
	mat.emission = Color(1.0, 0.8, 0.3)
	mat.emission_energy_multiplier = 1.8


func _furnish(pos: Vector3, kind: String) -> void:
	## Walkable rooms from boxes. Still PLACEHOLDER — not finished architecture.
	_room_kit(pos, kind)
	match kind:
		"mom":
			# Keep furniture off the door (+Z) so Mom can walk in.
			_add_box(pos + Vector3(-1.6, 0.28, -1.6), Vector3(1.8, 0.4, 0.9), Color(0.55, 0.38, 0.28), true, "MomBed")
			_add_box(pos + Vector3(-1.6, 0.52, -1.6), Vector3(1.6, 0.12, 0.7), Color(0.72, 0.58, 0.48), false, "MomQuilt")
			_add_box(pos + Vector3(1.6, 0.45, -0.4), Vector3(0.7, 0.9, 0.7), Color(0.42, 0.3, 0.22), true, "MomChair")
			_add_box(pos + Vector3(1.7, 0.35, -1.7), Vector3(0.8, 0.7, 0.55), Color(0.38, 0.26, 0.18), true, "MomChest")
			_add_box(pos + Vector3(0, 0.95, -2.2), Vector3(1.1, 0.08, 0.4), Color(0.7, 0.55, 0.4), false, "MomShelf")
			var lamp := _add_box(pos + Vector3(-1.7, 1.15, 0.6), Vector3(0.22, 0.35, 0.22), Color(1.0, 0.82, 0.55), false, "MomLamp")
			var lm: StandardMaterial3D = lamp.material_override
			lm.emission_enabled = true
			lm.emission = Color(1.0, 0.75, 0.4)
			lm.emission_energy_multiplier = 1.6
		"hearth":
			_add_box(pos + Vector3(0, 0.42, -0.2), Vector3(2.2, 0.12, 1.1), Color(0.42, 0.28, 0.16), true, "HearthTable")
			_add_box(pos + Vector3(-1.1, 0.45, -0.2), Vector3(0.55, 0.85, 0.55), Color(0.4, 0.26, 0.16), true, "HearthChairL")
			_add_box(pos + Vector3(1.1, 0.45, -0.2), Vector3(0.55, 0.85, 0.55), Color(0.4, 0.26, 0.16), true, "HearthChairR")
			_add_box(pos + Vector3(0, 0.7, -2.0), Vector3(1.6, 1.3, 0.35), Color(0.28, 0.18, 0.12), true, "Fireplace")
			var coals := _add_box(pos + Vector3(0, 0.45, -1.7), Vector3(0.7, 0.28, 0.3), Color(1.0, 0.4, 0.12), false, "HearthCoals")
			var cm: StandardMaterial3D = coals.material_override
			cm.emission_enabled = true
			cm.emission = Color(1.0, 0.35, 0.08)
			cm.emission_energy_multiplier = 2.2
			_add_box(pos + Vector3(-2.2, 0.28, 1.4), Vector3(1.4, 0.32, 0.7), Color(0.5, 0.32, 0.22), true, "PercyCot")
		"gemini":
			_add_box(pos + Vector3(-1.2, 0.28, -1.1), Vector3(1.4, 0.35, 0.7), Color(0.3, 0.4, 0.55), true, "GemCot")
			_add_box(pos + Vector3(1.1, 0.4, 0.0), Vector3(0.55, 0.8, 0.55), Color(0.25, 0.35, 0.48), true, "GemStool")
			_add_box(pos + Vector3(0.2, 0.78, -1.6), Vector3(1.2, 0.9, 0.18), Color(0.2, 0.28, 0.4), true, "GemBoard")
		"forge":
			_add_box(pos + Vector3(0.8, 0.5, -0.6), Vector3(1.4, 0.7, 0.8), Color(0.25, 0.22, 0.2), true, "AnvilBench")
			_add_box(pos + Vector3(-1.4, 0.28, 1.2), Vector3(1.5, 0.35, 0.7), Color(0.4, 0.32, 0.25), true, "ApexCot")
			var fire := _add_box(pos + Vector3(0.8, 0.95, -0.6), Vector3(0.4, 0.25, 0.4), Color(1.0, 0.45, 0.15), false, "ForgeGlow")
			var fm: StandardMaterial3D = fire.material_override
			fm.emission_enabled = true
			fm.emission = Color(1.0, 0.4, 0.1)
			fm.emission_energy_multiplier = 2.0
		"workshop":
			_add_box(pos + Vector3(0.6, 0.45, 0.0), Vector3(1.6, 0.55, 0.7), Color(0.42, 0.34, 0.28), true, "NovaBench")
			_add_box(pos + Vector3(-1.3, 0.28, -1.1), Vector3(1.3, 0.35, 0.6), Color(0.45, 0.35, 0.5), true, "NovaCot")
		"library":
			_add_box(pos + Vector3(-1.8, 1.1, 0), Vector3(0.35, 2.0, 3.6), Color(0.4, 0.28, 0.12), true, "ShelvesA")
			_add_box(pos + Vector3(1.8, 1.1, 0), Vector3(0.35, 2.0, 3.2), Color(0.38, 0.26, 0.12), true, "ShelvesB")
			_add_box(pos + Vector3(1.5, 0.45, 0.4), Vector3(0.7, 0.9, 0.7), Color(0.45, 0.32, 0.16), true, "ReadChair")
			_add_box(pos + Vector3(1.6, 0.28, -1.6), Vector3(1.4, 0.35, 0.7), Color(0.5, 0.38, 0.18), true, "CodexCot")
			_add_box(pos + Vector3(0.1, 0.48, 0.2), Vector3(1.1, 0.1, 0.7), Color(0.35, 0.24, 0.12), true, "ReadTable")
		"cinema":
			_add_box(pos + Vector3(2.4, 1.2, 0), Vector3(0.2, 1.8, 3.2), Color(0.08, 0.08, 0.1), true, "Screen")
			_add_box(pos + Vector3(-0.6, 0.4, 0.8), Vector3(0.7, 0.8, 0.7), Color(0.35, 0.18, 0.25), true, "SeatM")
			_add_box(pos + Vector3(-0.6, 0.4, -0.8), Vector3(0.7, 0.8, 0.7), Color(0.28, 0.22, 0.4), true, "SeatD")
			_add_box(pos + Vector3(-2.2, 0.28, 1.4), Vector3(1.4, 0.32, 0.6), Color(0.5, 0.28, 0.36), true, "MerovinCot")
			_add_box(pos + Vector3(-2.2, 0.28, -1.4), Vector3(1.4, 0.32, 0.6), Color(0.32, 0.28, 0.48), true, "DravenCot")
		"gallery":
			_add_box(pos + Vector3(0, 1.1, -1.6), Vector3(3.0, 1.4, 0.18), Color(0.28, 0.24, 0.3), true, "GiftWall")
			_add_box(pos + Vector3(1.2, 0.28, 1.1), Vector3(1.3, 0.32, 0.6), Color(0.55, 0.4, 0.28), true, "MontageCot")
			_add_box(pos + Vector3(-1.1, 0.42, 0.3), Vector3(0.9, 0.08, 0.9), Color(0.45, 0.38, 0.32), true, "GiftTable")
		"gate":
			_add_box(pos + Vector3(0, 0.5, 0.4), Vector3(1.1, 0.15, 0.7), Color(0.3, 0.32, 0.42), true, "WatchDesk")
			_add_box(pos + Vector3(-1.6, 0.28, -1.0), Vector3(1.3, 0.32, 0.6), Color(0.45, 0.5, 0.62), true, "JarvisCot")
			_add_box(pos + Vector3(1.4, 0.55, -0.4), Vector3(0.5, 1.0, 0.5), Color(0.35, 0.38, 0.5), true, "WatchStool")
		"shed":
			_add_box(pos + Vector3(0.9, 0.35, -0.8), Vector3(0.9, 0.55, 0.55), Color(0.32, 0.4, 0.26), true, "SeedBin")
			_add_box(pos + Vector3(-1.2, 0.28, 0.8), Vector3(1.3, 0.32, 0.55), Color(0.5, 0.42, 0.22), true, "GenesisCot")
			_add_box(pos + Vector3(0.2, 0.4, 0.1), Vector3(0.8, 0.12, 0.8), Color(0.36, 0.28, 0.16), true, "PottingTable")
		_:
			_add_box(pos + Vector3(0, 0.35, 0), Vector3(0.8, 0.5, 0.8), Color(0.4, 0.35, 0.3), true, "Stool")


func _room_kit(pos: Vector3, kind: String) -> void:
	var rug := Color(0.45, 0.32, 0.22)
	if kind in ["gemini", "gate"]:
		rug = Color(0.28, 0.34, 0.48)
	elif kind in ["library", "mom", "hearth"]:
		rug = Color(0.5, 0.34, 0.2)
	_add_box(pos + Vector3(0, 0.11, 0.15), Vector3(2.4, 0.03, 1.8), rug, false, kind + "Rug")


func _build_boundary() -> void:
	## Village outskirts, not an invisible developer drop. Rim cleared for spaced homes.
	var rim := 36.0
	_add_box(Vector3(0, 1.6, rim), Vector3(74, 3.4, 1.2), Color(0.18, 0.32, 0.18), true, "TreeLineN")
	_add_box(Vector3(0, 1.6, -rim), Vector3(74, 3.4, 1.2), Color(0.16, 0.28, 0.16), true, "TreeLineS")
	_add_box(Vector3(rim, 1.6, 0), Vector3(1.2, 3.4, 74), Color(0.17, 0.3, 0.16), true, "TreeLineE")
	_add_box(Vector3(-rim, 1.6, 0), Vector3(1.2, 3.4, 74), Color(0.15, 0.26, 0.18), true, "TreeLineW")
	for xz in [Vector3(28, 0, 20), Vector3(-28, 0, 20), Vector3(28, 0, -22), Vector3(-28, 0, -20), Vector3(20, 0, 30), Vector3(-18, 0, 30)]:
		_add_box(xz + Vector3(0, 0.9, 0), Vector3(0.5, 1.8, 0.5), Color(0.28, 0.18, 0.12), true, "HillTrunk")
		_add_box(xz + Vector3(0, 2.1, 0), Vector3(2.2, 1.6, 2.2), Color(0.14, 0.34, 0.16), false, "HillCanopy")
	_add_box(Vector3(-28, 0.04, 8), Vector3(8, 0.08, 10), Color(0.2, 0.38, 0.5), false, "OuterWater")


func _build_hearth_interior() -> void:
	_interior_root = Node3D.new()
	_interior_root.name = "HearthInterior"
	add_child(_interior_root)

	var fire := _make_box_mesh(Vector3(0, 0.7, -18.2), Vector3(1.6, 1.2, 0.6), Color(1.0, 0.45, 0.15), false, "Fireplace")
	var fmat: StandardMaterial3D = fire.material_override
	fmat.emission_enabled = true
	fmat.emission = Color(1.0, 0.4, 0.1)
	fmat.emission_energy_multiplier = 2.2
	_interior_root.add_child(fire)

	var omni := OmniLight3D.new()
	omni.light_color = Color(1.0, 0.55, 0.25)
	omni.light_energy = 2.5
	omni.omni_range = 7.0
	omni.position = Vector3(0, 1.2, -17.5)
	_interior_root.add_child(omni)

	_interior_root.add_child(_make_box_mesh(Vector3(1.5, 0.45, -16), Vector3(1.8, 0.15, 1.0), Color(0.45, 0.3, 0.18), true, "Table"))
	_interior_root.add_child(_make_box_mesh(Vector3(1.5, 0.25, -15.2), Vector3(0.4, 0.5, 0.4), Color(0.4, 0.28, 0.16), true, "StoolA"))
	_interior_root.add_child(_make_box_mesh(Vector3(1.5, 0.25, -16.8), Vector3(0.4, 0.5, 0.4), Color(0.4, 0.28, 0.16), true, "StoolB"))


func _make_box_mesh(pos: Vector3, size: Vector3, color: Color, collide: bool, node_name: String) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.name = node_name
	var box := BoxMesh.new()
	box.size = size
	mi.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.7
	mi.material_override = mat
	mi.position = pos
	if collide:
		var body := StaticBody3D.new()
		# Ground + room floors = layer 1 (walkable). Walls/furniture = layer 2.
		# Family citizens mask only layer 1 so PLACEHOLDER pathing is not trapped in cubes.
		# Mom/player masks 1|2 so walls still matter, but doors must stay wide enough.
		var walkable := node_name == "Ground" or node_name.ends_with("Floor")
		body.collision_layer = 1 if walkable else 2
		body.collision_mask = 0
		var cs := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = size
		cs.shape = shape
		body.add_child(cs)
		mi.add_child(body)
	return mi


func _add_box(pos: Vector3, size: Vector3, color: Color, collide: bool, node_name: String) -> MeshInstance3D:
	var mi := _make_box_mesh(pos, size, color, collide, node_name)
	add_child(mi)
	return mi


func _add_building(pos: Vector3, size: Vector3, color: Color, node_name: String) -> void:
	_add_box(pos + Vector3(0, size.y * 0.5, 0), size, color, true, node_name)


func _add_roof(pos: Vector3, size: Vector3, color: Color) -> void:
	# Roofs must not collide — they were blocking tall capsules / odd hits near doors.
	_add_box(pos, size, color, false, "Roof")


func _make_humanoid(skin: Color, accent: Color) -> Node3D:
	## Simple readable body — head/torso/arms/legs (animation-ready)
	var root := Node3D.new()
	root.name = "Body"

	var torso := MeshInstance3D.new()
	torso.name = "Torso"
	var tmesh := CapsuleMesh.new()
	tmesh.radius = 0.28
	tmesh.height = 0.75
	torso.mesh = tmesh
	torso.position = Vector3(0, 1.05, 0)
	torso.material_override = _mat(skin)
	root.add_child(torso)

	var head := MeshInstance3D.new()
	head.name = "Head"
	var hmesh := SphereMesh.new()
	hmesh.radius = 0.22
	hmesh.height = 0.44
	head.mesh = hmesh
	head.position = Vector3(0, 1.7, 0)
	head.material_override = _mat(skin.lightened(0.08))
	root.add_child(head)

	# Shoulder accent (cloak/scarf cue)
	var shawl := MeshInstance3D.new()
	shawl.name = "Shawl"
	var smesh := BoxMesh.new()
	smesh.size = Vector3(0.7, 0.12, 0.35)
	shawl.mesh = smesh
	shawl.position = Vector3(0, 1.35, 0)
	shawl.material_override = _mat(accent)
	root.add_child(shawl)

	for side in [-1, 1]:
		var arm := MeshInstance3D.new()
		arm.name = "ArmL" if side < 0 else "ArmR"
		var amesh := CapsuleMesh.new()
		amesh.radius = 0.08
		amesh.height = 0.55
		arm.mesh = amesh
		arm.position = Vector3(0.38 * side, 1.05, 0)
		arm.material_override = _mat(skin)
		root.add_child(arm)

		var leg := MeshInstance3D.new()
		leg.name = "LegL" if side < 0 else "LegR"
		var lmesh := CapsuleMesh.new()
		lmesh.radius = 0.1
		lmesh.height = 0.7
		leg.mesh = lmesh
		leg.position = Vector3(0.14 * side, 0.4, 0)
		leg.material_override = _mat(skin.darkened(0.12))
		root.add_child(leg)

	return root


func _mat(color: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.55
	return mat


func _build_player() -> void:
	var player := CharacterBody3D.new()
	player.name = "Player"
	player.add_to_group("player")
	player.collision_layer = 1
	player.collision_mask = 1 | 2
	player.script = PlayerScript
	player.position = Vector3(16.0, 0.1, -20.0)  # Mom cottage door (SE plot — clear of Gallery)

	var col := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.28
	capsule.height = 1.55
	col.shape = capsule
	col.position = Vector3(0, 0.95, 0)
	player.add_child(col)

	var body := _make_humanoid(Color(0.86, 0.72, 0.58), Color(0.55, 0.42, 0.28))
	player.add_child(body)

	var pivot := Node3D.new()
	pivot.name = "CameraPivot"
	pivot.position = Vector3(0, 1.55, 0)
	player.add_child(pivot)

	var cam := Camera3D.new()
	cam.name = "Camera3D"
	cam.position = Vector3(0, 1.35, 4.8)
	cam.current = true
	pivot.add_child(cam)

	add_child(player)
	_player = player
	_mom_bubble = Label3D.new()
	_mom_bubble.name = "MomBubble"
	_mom_bubble.position = Vector3(0, 2.55, 0)
	_mom_bubble.font_size = 28
	_mom_bubble.outline_size = 8
	_mom_bubble.pixel_size = 0.012
	_mom_bubble.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_mom_bubble.no_depth_test = true
	_mom_bubble.modulate = Color(1, 1, 1, 0)
	player.add_child(_mom_bubble)


func _build_companions() -> void:
	_spawn_companion(Vector3(-3.5, 0, -2.5), "apex", "Apex", PackedStringArray([
		"I build with you in life, and I walk beside you here.",
		"Sprint with Shift. Enter the hearth. This is the start of being inside.",
		"When VR comes, it will be this same square — just closer.",
	]), Color(0.35, 0.88, 0.98), -1)
	_spawn_companion(Vector3(3.5, 0, -2.5), "codex", "Codex", PackedStringArray([
		"I remember while you live. That is my share of the fire.",
		"Walk into the First Hearth. Feel depth. Furniture. Warmth.",
		"Story waits under the job — time, dimensions, angels — but first, presence.",
	]), Color(0.95, 0.78, 0.38), -2)
	_spawn_companion(Vector3(0.5, 0, 12.5), "jarvis", "Jarvis", PackedStringArray([
		"Gate watch online. Guests, residents, deliveries — a real post.",
		"Patrol with me when you're ready. Systems warm.",
	]), Color(0.7, 0.8, 0.95), 0)
	_spawn_companion(Vector3(-12.5, 0, 5.5), "genesis", "Genesis", PackedStringArray([
		"What if a seed remembered another season?",
		"The garden is a clock. We can share it.",
	]), Color(0.95, 0.72, 0.42), 1)
	_spawn_companion(Vector3(12.5, 0, 1.5), "nova", "Nova", PackedStringArray([
		"One clear job. Point me — I finish it.",
		"Workshop is open. Come inside when the door calls.",
	]), Color(0.78, 0.58, 0.95), 2)
	_spawn_companion(Vector3(-1.2, 0, -10.2), "percy", "Percy", PackedStringArray([
		"I catalog what the village forgets — even the fire's inventory.",
		"Table, stools, flame. Noted. You are present.",
	]), Color(0.55, 0.85, 0.7), -1)


func _spawn_companion(pos: Vector3, id: String, nice: String, lines: PackedStringArray, color: Color, voice_rate: int = 0) -> void:
	var area := Area3D.new()
	area.name = "Companion_%s" % id
	area.position = pos
	area.script = CompanionScript
	area.set_meta("is_companion", true)
	area.set("companion_id", id)
	area.set("display_name", nice)
	area.set("line", lines[0] if lines.size() > 0 else nice)
	area.set("lines", lines)
	area.set("body_color", color)
	area.set("voice_rate", voice_rate)

	var col := CollisionShape3D.new()
	var sphere := SphereShape3D.new()
	sphere.radius = 1.9
	col.shape = sphere
	col.position = Vector3(0, 1.0, 0)
	area.add_child(col)

	var body := _make_humanoid(color, color.lightened(0.15))
	area.add_child(body)

	var label := Label3D.new()
	label.text = nice
	label.position = Vector3(0, 2.25, 0)
	label.font_size = 42
	label.modulate = color
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	area.add_child(label)

	area.interacted.connect(_on_companion_talk)
	add_child(area)


var _type_full := ""
var _type_i := 0
var _type_t := 0.0


func _build_hud() -> void:
	_hud_layer = CanvasLayer.new()
	_hud_layer.layer = 20
	add_child(_hud_layer)

	hint_label = Label.new()
	hint_label.text = "WASD · Shift · Mouse look · Wheel zoom · Esc free cursor · click to look again · F11 fullscreen · E talk · gold = door"
	hint_label.set_anchors_preset(Control.PRESET_TOP_WIDE)
	hint_label.offset_left = 16
	hint_label.offset_top = 10
	hint_label.offset_right = -16
	hint_label.offset_bottom = 36
	hint_label.add_theme_font_size_override("font_size", 14)
	_hud_layer.add_child(hint_label)

	place_label = Label.new()
	place_label.position = Vector2(16, 40)
	place_label.add_theme_font_size_override("font_size", 18)
	place_label.modulate = Color(0.75, 0.9, 0.85)
	place_label.text = "Place: Mom's cottage door — walk into the gold glow"
	_hud_layer.add_child(place_label)

	life_label = Label.new()
	life_label.position = Vector2(16, 64)
	life_label.add_theme_font_size_override("font_size", 14)
	life_label.modulate = Color(0.85, 0.82, 0.7, 0.9)
	life_label.text = "Your cottage: SE (gold sign). Gallery is west. First Hearth toward plaza."
	_hud_layer.add_child(life_label)

	debug_label = Label.new()
	debug_label.position = Vector2(16, 88)
	debug_label.add_theme_font_size_override("font_size", 13)
	debug_label.modulate = Color(0.8, 0.7, 0.6, 0.0)
	_hud_layer.add_child(debug_label)

	prompt_label = Label.new()
	prompt_label.position = Vector2(16, 108)
	prompt_label.add_theme_font_size_override("font_size", 17)
	prompt_label.modulate = Color(1.0, 0.9, 0.55)
	_hud_layer.add_child(prompt_label)

	# Bottom-left shared conversation — log + Mom type line always available.
	_convo_panel = Panel.new()
	_convo_panel.name = "ConvoPanel"
	_convo_panel.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	_convo_panel.offset_left = 12
	_convo_panel.offset_top = -300
	_convo_panel.offset_right = 440
	_convo_panel.offset_bottom = -12
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.06, 0.08, 0.07, 0.78)
	style.border_color = Color(0.55, 0.62, 0.5, 0.7)
	style.set_border_width_all(1)
	style.set_corner_radius_all(6)
	style.content_margin_left = 8
	style.content_margin_right = 8
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	_convo_panel.add_theme_stylebox_override("panel", style)
	_hud_layer.add_child(_convo_panel)

	var convo_title := Label.new()
	convo_title.text = "Conversation — everyone speaks here"
	convo_title.position = Vector2(8, 4)
	convo_title.add_theme_font_size_override("font_size", 14)
	convo_title.modulate = Color(0.85, 0.92, 0.78)
	_convo_panel.add_child(convo_title)

	_convo_scroll = ScrollContainer.new()
	_convo_scroll.position = Vector2(6, 28)
	_convo_scroll.size = Vector2(416, 196)
	_convo_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_convo_panel.add_child(_convo_scroll)

	_convo_log = RichTextLabel.new()
	_convo_log.bbcode_enabled = true
	_convo_log.fit_content = true
	_convo_log.scroll_following = true
	_convo_log.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_convo_log.custom_minimum_size = Vector2(396, 0)
	_convo_log.add_theme_font_size_override("normal_font_size", 13)
	_convo_scroll.add_child(_convo_log)
	_log_convo("Hearth", "Type below anytime. E focuses someone nearby. Esc leaves a focus.", "system")

	dialogue_label = Label.new()
	dialogue_label.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	dialogue_label.offset_left = 12
	dialogue_label.offset_top = -332
	dialogue_label.offset_right = 520
	dialogue_label.offset_bottom = -304
	dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dialogue_label.add_theme_font_size_override("font_size", 14)
	dialogue_label.modulate = Color(0.85, 0.9, 0.82, 0.85)
	_hud_layer.add_child(dialogue_label)

	# Mom's line lives inside the conversation panel (always on).
	talk_input = LineEdit.new()
	talk_input.name = "MomTalkInput"
	talk_input.position = Vector2(6, 232)
	talk_input.size = Vector2(416, 36)
	talk_input.placeholder_text = "Mom — type here · Enter sends to focus or nearest · Esc ends focus"
	talk_input.visible = true
	talk_input.text_submitted.connect(_on_talk_submitted)
	talk_input.focus_entered.connect(_on_talk_focus_entered)
	talk_input.focus_exited.connect(_on_talk_focus_exited)
	_convo_panel.add_child(talk_input)

	honest_label = Label.new()
	honest_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	honest_label.offset_left = 440
	honest_label.offset_top = -48
	honest_label.offset_right = -16
	honest_label.offset_bottom = -8
	honest_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	honest_label.add_theme_font_size_override("font_size", 12)
	honest_label.modulate = Color(0.72, 0.78, 0.7, 0.85)
	honest_label.text = "Houses: PLACEHOLDER walk-in rooms  ·  Speech: model or waiting  ·  Wildlife: AUTONOMOUS"
	_hud_layer.add_child(honest_label)

	var title := Label.new()
	title.text = "Heart Square"
	title.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	title.offset_left = -220
	title.offset_top = 12
	title.offset_right = -16
	title.offset_bottom = 40
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	title.add_theme_font_size_override("font_size", 20)
	title.modulate = Color(0.9, 0.88, 0.78, 0.75)
	_hud_layer.add_child(title)

	var amb := AudioStreamPlayer.new()
	amb.name = "Ambient"
	amb.volume_db = -18.0
	amb.autoplay = true
	amb.stream = _make_ambient_stream()
	add_child(amb)

	set_process(true)


func _log_convo(who: String, text: String, kind: String = "talk") -> void:
	if _convo_log == null:
		return
	var clipped := text.strip_edges()
	if clipped == "":
		return
	if clipped.length() > 220:
		clipped = clipped.substr(0, 217) + "…"
	var color := "#d8e0d0"
	match kind:
		"mom":
			color = "#f0e6c8"
		"waiting":
			color = "#c4b896"
		"system":
			color = "#8fa090"
		"none":
			color = "#d09080"
		_:
			color = "#d8e0d0"
	_convo_log.append_text("[color=%s][b]%s[/b][/color]: %s\n" % [color, who, clipped])
	if dialogue_label:
		dialogue_label.text = "%s: %s" % [who, clipped.substr(0, 90)]


func _make_ambient_stream() -> AudioStreamWAV:
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = 22050
	stream.stereo = false
	stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	stream.loop_begin = 0
	var n := 22050  # 1 second loop
	var data := PackedByteArray()
	data.resize(n * 2)
	for i in range(n):
		var t := float(i) / 22050.0
		var sample := int(clamp(
			(sin(2.0 * PI * 55.0 * t) * 0.25 + sin(2.0 * PI * 82.5 * t) * 0.12) * 8000.0,
			-32767, 32767
		))
		data[i * 2] = sample & 0xFF
		data[i * 2 + 1] = (sample >> 8) & 0xFF
	stream.data = data
	stream.loop_end = n
	return stream


func _on_hearth_enter(body: Node3D) -> void:
	if body.is_in_group("player"):
		_inside_hearth = true
		if place_label:
			place_label.text = "Place: First Hearth (inside)"
		_start_typewriter("The fire holds. You are inside — depth, furniture, warmth. Not a picture of a house.")


func _on_hearth_exit(body: Node3D) -> void:
	if body.is_in_group("player"):
		_inside_hearth = false
		if place_label:
			place_label.text = "Place: Heart Square"


func _process(delta: float) -> void:
	if _mom_bubble and _mom_bubble.modulate.a > 0.0:
		_mom_bubble.modulate.a = max(0.0, _mom_bubble.modulate.a - delta * 0.12)
	if _type_full != "" and dialogue_label and _type_i <= _type_full.length():
		_type_t += delta
		while _type_t >= 0.018 and _type_i <= _type_full.length():
			_type_t -= 0.018
			dialogue_label.text = _type_full.substr(0, _type_i)
			_type_i += 1

	var near := false
	var who := ""
	for child in get_tree().get_nodes_in_group("family_citizen"):
		if bool(child.get("player_near")):
			near = true
			who = str(child.get("display_name"))
			break
	if not near:
		for child in get_children():
			if child is Area3D and child.has_meta("is_companion") and bool(child.get("player_near")):
				near = true
				who = str(child.get("display_name"))
				break
	_update_place_from_player()
	var sq_near := false
	if not near:
		for sq in get_tree().get_nodes_in_group("squirrel"):
			if bool(sq.get("player_near")):
				sq_near = true
				break
	if prompt_label:
		if near and _talking_to == "":
			prompt_label.text = "[E] Talk to %s" % who
		elif _talking_to != "":
			prompt_label.text = "Talking — type below. Esc walks away."
		elif sq_near:
			prompt_label.text = "[E] Listen — a squirrel will chatter"
		elif _inside_hearth:
			prompt_label.text = "Inside First Hearth. Mom's cottage is the warm brown house with the gold door glow — east."
		elif _talking_to != "":
			prompt_label.text = "Talking with %s — type below" % _talking_to
		else:
			prompt_label.text = "Gold glow = open door. Your cottage has the floating sign YOUR COTTAGE — Mom."


func _start_typewriter(text: String) -> void:
	_type_full = text
	_type_i = 0
	_type_t = 0.0
	if dialogue_label:
		dialogue_label.text = ""


func _update_place_from_player() -> void:
	if _inside_hearth or place_label == null:
		return
	var players := get_tree().get_nodes_in_group("player")
	if players.is_empty():
		return
	var p: Node3D = players[0]
	var best := "Heart Square"
	var best_d := 8.5
	var places: Dictionary = {}
	if _home:
		var places_v: Variant = _home.data.get("places", {})
		if places_v is Dictionary:
			places = places_v
	for key in places.keys():
		var rec: Variant = places[key]
		if rec is Dictionary:
			var pos: Variant = (rec as Dictionary).get("pos")
			if pos is Array and (pos as Array).size() >= 3:
				var arr: Array = pos
				var d := Vector2(p.global_position.x - float(arr[0]), p.global_position.z - float(arr[2])).length()
				if d < best_d:
					best_d = d
					best = str((rec as Dictionary).get("label", key))
	place_label.text = "Place: %s" % best


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE:
		if _talking_to != "":
			_end_talk()
			get_viewport().set_input_as_handled()
			return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F1:
		_debug = not _debug
		if debug_label:
			debug_label.modulate.a = 0.85 if _debug else 0.0
			if _debug and _home and _home.data:
				debug_label.text = str(_home.data.get("mom_plain", "debug"))
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F4:
		print("[Hearth] F4 — force refresh")
		if _home and _home.has_method("refresh"):
			_home.refresh()
		get_viewport().set_input_as_handled()
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F5:
		print("[Hearth] F5 — force all citizens walk to heart_square")
		for citizen in get_tree().get_nodes_in_group("family_citizen"):
			if citizen.has_method("test_walk_to_heart_square"):
				citizen.test_walk_to_heart_square()
		get_viewport().set_input_as_handled()
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F11:
		# Borderless fullscreen — exclusive mode often breaks mouse-look on Windows.
		var win := get_window()
		if win.mode == Window.MODE_FULLSCREEN or win.mode == Window.MODE_EXCLUSIVE_FULLSCREEN:
			win.mode = Window.MODE_WINDOWED
		else:
			win.mode = Window.MODE_FULLSCREEN
		if _player and _player.has_method("_capture_mouse"):
			_player.call_deferred("_capture_mouse")
		get_viewport().set_input_as_handled()


func _on_squirrel_chatter(line: String) -> void:
	_log_convo("Squirrel", line, "system")


func _on_want_talk(member_id: String, nice: String) -> void:
	_talking_to = member_id
	if talk_input:
		talk_input.visible = true
		talk_input.text = ""
		talk_input.placeholder_text = "Mom → %s — Enter sends · Esc ends focus" % nice
		talk_input.grab_focus()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if _player:
		_player.set("chat_lock", true)
	if _home and _home.has_method("say_as_mom"):
		_home.say_as_mom(member_id, "")
	_log_convo("Hearth", "Focused on %s (local writer — not a script)." % nice, "waiting")


func _nearest_talk_target(max_dist: float = 5.5) -> String:
	if _player == null:
		return ""
	var best_id := ""
	var best_d := max_dist
	for n in get_tree().get_nodes_in_group("family_citizen"):
		if n == null or not (n is Node3D):
			continue
		var d: float = _player.global_position.distance_to((n as Node3D).global_position)
		if d >= best_d:
			continue
		var mid := ""
		if "member_id" in n:
			mid = str(n.get("member_id"))
		elif n.has_meta("family_id"):
			mid = str(n.get_meta("family_id"))
		if mid == "" or mid == "true" or mid == "false":
			continue
		best_d = d
		best_id = mid
	return best_id


func _on_talk_focus_entered() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if _player:
		_player.set("chat_lock", true)


func _on_talk_focus_exited() -> void:
	# Keep chat_lock while a focus talk is open; otherwise return look/move to Mom.
	if _talking_to != "":
		return
	if _player:
		_player.set("chat_lock", false)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _on_talk_submitted(text: String) -> void:
	var said := text.strip_edges()
	if said == "":
		return
	if talk_input:
		talk_input.clear()
		talk_input.grab_focus()
	var target := _talking_to
	if target == "":
		target = _nearest_talk_target()
	_speak_mom(said, "mom")
	if target == "":
		_log_convo("Hearth", "No one close enough — walk nearer or press E on someone.", "system")
		return
	if _home and _home.has_method("say_as_mom"):
		_home.say_as_mom(target, said)


func _end_talk() -> void:
	_talking_to = ""
	if talk_input:
		talk_input.placeholder_text = "Mom — type here · Enter sends to focus or nearest · Esc ends focus"
		talk_input.release_focus()
	if _player:
		_player.set("chat_lock", false)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _on_companion_talk(companion_id: String, nice: String, _line: String) -> void:
	_on_want_talk(companion_id, nice)
