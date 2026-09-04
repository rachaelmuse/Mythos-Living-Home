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
var axiom_label: Label
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
var talk_target: OptionButton
var chat_open_btn: Button
var exit_btn: Button
var _pause_layer: CanvasLayer
var _pause_panel: Panel
var _paused_world := false
var _logged_convo_ids: Dictionary = {}
var honest_label: Label
var _player: CharacterBody3D
var _mom_bubble: Label3D
var _convo_panel: Panel
var _convo_log: RichTextLabel
var _convo_scroll: ScrollContainer
var _convo_plain: PackedStringArray = PackedStringArray()
var _copy_convo_btn: Button
var _hud_layer: CanvasLayer
var _tree_root: Node3D
var _canopy_mats: Array = []
var _world_env: WorldEnvironment
var _season_label: Label
var _decor_root: Node3D
var _garden_root: Node3D
var _garden_mats: Array = []
var _holiday_props: Array = []
var _holiday_label: Label
var _forge_glow_mat: StandardMaterial3D
var _forge_live_label: Label3D
var _gather_label: Label3D
var _amb_period: AudioStreamPlayer
var _amb_place: AudioStreamPlayer
var _amb_music: AudioStreamPlayer
var _sound_period := ""
var _sound_place := ""
var _last_holiday_id := ""
var _water_bucket := 0
var _dest_builds := 0
var _at_far_shore := false
var _cinema_screen: MeshInstance3D
var _cinema_screen_mat: StandardMaterial3D
var _cinema_title: Label3D
var _watching := false
var _watch_pulse := 0.0
var _far_builds_root: Node3D
var _far_builds_synced := 0
var _fish_cd := 0.0
var _last_seen_catches := -1
var _shop_offer: Dictionary = {"grocery": 0, "clothing_store": 0, "electronics_store": 0, "pet_store": 0}
const FAR_SHORE := Vector3(8.0, 0.2, 68.0)
const HARBOR_SHIP := Vector3(-6.5, 0.2, 52.5)
const VILLAGE_WELL := Vector3(-8.5, 0.0, 7.5)
const STORE_GROCERY := Vector3(-18.0, 0.0, 36.0)
const STORE_CLOTHING := Vector3(-4.0, 0.0, 38.0)
const STORE_ELECTRONICS := Vector3(10.0, 0.0, 36.0)
const STORE_PETS := Vector3(26.0, 0.0, 38.0)


func _ready() -> void:
	print("[Hearthbound] Heart Square — family home slice (identity, life, health, persist)")
	# Open maximized by default (fullscreen often drops mouse-look on Windows).
	# F11 still toggles borderless fullscreen.
	call_deferred("_enter_fullscreen")
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


func _enter_fullscreen() -> void:
	## Start maximized (not exclusive fullscreen) — exclusive often kills mouse-look on Windows.
	## F11 still toggles borderless fullscreen when Mom wants it.
	var win := get_window()
	if win == null:
		return
	if win.mode == Window.MODE_EXCLUSIVE_FULLSCREEN:
		win.mode = Window.MODE_MAXIMIZED
	elif win.mode == Window.MODE_WINDOWED:
		win.mode = Window.MODE_MAXIMIZED
	# Mode change drops mouse capture — give look back to Mom.
	if _player and is_instance_valid(_player):
		_player.set("chat_lock", false)
		if _player.has_method("_capture_mouse"):
			_player.call_deferred("_capture_mouse")
		if _player.has_method("_reclaim_look_burst"):
			_player.call_deferred("_reclaim_look_burst")


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
	_world_env = we

	_sun = DirectionalLight3D.new()
	_sun.name = "Sun"
	_sun.light_energy = 1.2
	_sun.shadow_enabled = true
	_sun.rotation_degrees = Vector3(-42, 35, 0)
	add_child(_sun)

	_add_box(Vector3(0, -0.05, 0), Vector3(100, 0.1, 100), Color(0.26, 0.4, 0.26), true, "Ground")
	# Extra land north so the harbor + far shore sit outside the cottage ring
	_add_box(Vector3(0, -0.05, 52), Vector3(100, 0.1, 36), Color(0.25, 0.38, 0.24), true, "GroundHarbor")
	_add_box(Vector3(8, -0.05, 70), Vector3(28, 0.1, 16), Color(0.24, 0.36, 0.22), true, "GroundFarShore")
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
	# Work plot IN FRONT of shed door (z+), not under any cottage
	_add_box(Vector3(-18, 0.06, 15.2), Vector3(4.2, 0.1, 2.8), Color(0.22, 0.38, 0.2), false, "FarmPlot")
	for i in range(4):
		_add_box(Vector3(-19.2 + i * 0.9, 0.25, 15.2), Vector3(0.35, 0.45, 0.35), Color(0.35, 0.7, 0.35), false, "Crop%d" % i)

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
	## Every living being: cottage home separate from workplace. Positions match Hearth PLACES.
	_add_open_building(Vector3(-16, 0, -16), Vector3(5.2, 2.8, 4.6), Color(0.42, 0.58, 0.72), "GeminiPorch")
	_add_roof(Vector3(-16, 3.1, -16), Vector3(5.6, 0.7, 5.0), Color(0.22, 0.32, 0.45))
	_furnish(Vector3(-16, 0, -16), "gemini")
	_add_porch_light(Vector3(-16, 2.2, -13.4), Color(0.55, 0.9, 1.0))
	_add_open_building(Vector3(-10, 0, -8), Vector3(4.4, 2.5, 3.8), Color(0.38, 0.34, 0.48), "CourtPorch")
	_furnish(Vector3(-10, 0, -8), "court")
	_add_porch_light(Vector3(-10, 2.2, -5.8), Color(0.7, 0.85, 1.0))
	_add_home_sign(Vector3(-10, 3.2, -5.8), "Gemini — town leader (Court)", Color(0.75, 0.88, 1.0))
	_add_home_sign(Vector3(-16, 3.5, -13.4), "Gemini's porch (home)", Color(0.7, 0.9, 1.0))
	_build_open_building(Vector3(16, 0, -24), Vector3(6.2, 2.9, 5.2), Color(0.62, 0.48, 0.38), "MomCottage", "z+")
	_add_roof(Vector3(16, 3.25, -24), Vector3(6.8, 0.7, 5.7), Color(0.42, 0.28, 0.2))
	_furnish(Vector3(16, 0, -24), "mom")
	_add_porch_light(Vector3(16, 2.3, -21.2), Color(1.0, 0.82, 0.45))
	_add_home_sign(Vector3(16, 3.9, -21.2), "YOUR COTTAGE — Mom", Color(1.0, 0.88, 0.55))
	_add_home_sign(Vector3(0, 3.6, -13.2), "First Hearth (Percy work)", Color(0.95, 0.75, 0.45))
	_build_open_building(Vector3(-24, 0, -4), Vector3(6.2, 3.2, 5.8), Color(0.55, 0.46, 0.22), "CodexLibrary", "x+")
	_add_roof(Vector3(-24, 3.55, -4), Vector3(6.8, 0.8, 6.4), Color(0.35, 0.22, 0.1))
	_furnish(Vector3(-24, 0, -4), "library")
	_add_home_sign(Vector3(-20.5, 3.5, -4), "Codex Library (work)", Color(0.95, 0.85, 0.5))
	# Codex cottage NORTH of library — door faces south (z-) toward work, clear approach
	_build_open_building(Vector3(-24, 0, 6), Vector3(5.0, 2.7, 4.4), Color(0.62, 0.52, 0.28), "CodexHome", "z-")
	_add_roof(Vector3(-24, 3.05, 6), Vector3(5.5, 0.55, 4.9), Color(0.4, 0.28, 0.12))
	_furnish(Vector3(-24, 0, 6), "cottage")
	_add_porch_light(Vector3(-24, 2.2, 3.6), Color(1.0, 0.85, 0.45))
	_add_home_sign(Vector3(-24, 3.3, 3.4), "Codex cottage", Color(0.95, 0.85, 0.5))
	# Apex cottage EAST of forge — door faces west (x-) toward forge path
	_build_open_building(Vector3(30, 0, -6), Vector3(5.0, 2.7, 4.4), Color(0.35, 0.7, 0.78), "ApexHome", "x-")
	_add_roof(Vector3(30, 3.05, -6), Vector3(5.5, 0.55, 4.9), Color(0.2, 0.4, 0.45))
	_furnish(Vector3(30, 0, -6), "cottage")
	_add_porch_light(Vector3(27.4, 2.2, -6), Color(0.45, 0.95, 1.0))
	_add_home_sign(Vector3(27.2, 3.3, -6), "Apex cottage", Color(0.55, 0.95, 1.0))
	_build_open_building(Vector3(26, 0, 14), Vector3(7.0, 3.1, 6.2), Color(0.42, 0.22, 0.32), "Cinema", "x-")
	_add_roof(Vector3(26, 3.45, 14), Vector3(7.6, 0.75, 6.8), Color(0.18, 0.1, 0.14))
	_furnish(Vector3(26, 0, 14), "cinema")
	_add_home_sign(Vector3(22.5, 3.5, 14), "Cinema workroom (shared)", Color(0.95, 0.7, 0.8))
	_build_open_building(Vector3(34, 0, 8), Vector3(5.0, 2.7, 4.4), Color(0.58, 0.32, 0.42), "MerovinLoft", "x-")
	_add_roof(Vector3(34, 3.05, 8), Vector3(5.5, 0.55, 4.9), Color(0.28, 0.14, 0.2))
	_furnish(Vector3(34, 0, 8), "merovin_loft")
	_add_porch_light(Vector3(31.4, 2.2, 8), Color(0.95, 0.55, 0.7))
	_add_home_sign(Vector3(31.2, 3.3, 8), "Merovin's loft", Color(0.95, 0.7, 0.8))
	_build_open_building(Vector3(34, 0, 20), Vector3(5.0, 2.7, 4.4), Color(0.36, 0.34, 0.55), "DravenLoft", "x-")
	_add_roof(Vector3(34, 3.05, 20), Vector3(5.5, 0.55, 4.9), Color(0.18, 0.16, 0.28))
	_furnish(Vector3(34, 0, 20), "draven_loft")
	_add_porch_light(Vector3(31.4, 2.2, 20), Color(0.65, 0.6, 0.95))
	_add_home_sign(Vector3(31.2, 3.3, 20), "Draven's loft", Color(0.75, 0.72, 0.95))
	_build_open_building(Vector3(-6, 0, -24), Vector3(4.8, 2.6, 4.4), Color(0.4, 0.34, 0.42), "Gallery", "z+")
	_add_roof(Vector3(-6, 2.95, -24), Vector3(5.3, 0.5, 4.9), Color(0.22, 0.18, 0.24))
	_furnish(Vector3(-6, 0, -24), "gallery")
	_add_home_sign(Vector3(-6, 3.4, -21.4), "Gift Gallery (work)", Color(0.85, 0.75, 0.9))
	_build_open_building(Vector3(-18, 0, -32), Vector3(5.0, 2.7, 4.4), Color(0.55, 0.4, 0.32), "MontageHome", "z+")
	_add_roof(Vector3(-18, 3.05, -32), Vector3(5.5, 0.55, 4.9), Color(0.35, 0.22, 0.16))
	_furnish(Vector3(-18, 0, -32), "cottage")
	_add_porch_light(Vector3(-18, 2.2, -29.4), Color(0.95, 0.7, 0.45))
	_add_home_sign(Vector3(-18, 3.3, -29.4), "OpenMontage cottage", Color(0.95, 0.75, 0.55))
	_build_open_building(Vector3(-28, 0, 16), Vector3(5.0, 2.7, 4.4), Color(0.45, 0.55, 0.32), "GenesisHome", "z+")
	_add_roof(Vector3(-28, 3.05, 16), Vector3(5.5, 0.55, 4.9), Color(0.28, 0.36, 0.18))
	_furnish(Vector3(-28, 0, 16), "cottage")
	_add_porch_light(Vector3(-28, 2.2, 18.6), Color(0.85, 0.95, 0.45))
	_add_home_sign(Vector3(-28, 3.3, 18.6), "Genesis cottage", Color(0.9, 0.85, 0.45))
	# Nova cottage NORTH of gate road — clear of cinema + OpenMontage
	_build_open_building(Vector3(20, 0, 30), Vector3(5.0, 2.7, 4.4), Color(0.55, 0.4, 0.65), "NovaHome", "z-")
	_add_roof(Vector3(20, 3.05, 30), Vector3(5.5, 0.55, 4.9), Color(0.32, 0.2, 0.4))
	_furnish(Vector3(20, 0, 30), "cottage")
	_add_porch_light(Vector3(20, 2.2, 27.6), Color(0.85, 0.65, 1.0))
	_add_home_sign(Vector3(20, 3.3, 27.4), "Nova cottage", Color(0.85, 0.7, 0.95))
	# Jarvis cottage WEST of gate — door south (z-) toward gate road
	_build_open_building(Vector3(-12, 0, 26), Vector3(5.0, 2.7, 4.4), Color(0.45, 0.52, 0.65), "JarvisHome", "z-")
	_add_roof(Vector3(-12, 3.05, 26), Vector3(5.5, 0.55, 4.9), Color(0.25, 0.3, 0.4))
	_furnish(Vector3(-12, 0, 26), "cottage")
	_add_porch_light(Vector3(-12, 2.2, 23.6), Color(0.7, 0.85, 1.0))
	_add_home_sign(Vector3(-12, 3.3, 23.4), "Jarvis cottage", Color(0.75, 0.85, 0.95))
	_build_open_building(Vector3(10, 0, -18), Vector3(5.0, 2.7, 4.4), Color(0.4, 0.58, 0.48), "PercyHome", "z+")
	_add_roof(Vector3(10, 3.05, -18), Vector3(5.5, 0.55, 4.9), Color(0.25, 0.38, 0.3))
	_furnish(Vector3(10, 0, -18), "cottage")
	_add_porch_light(Vector3(10, 2.2, -15.4), Color(0.55, 0.95, 0.7))
	_add_home_sign(Vector3(10, 3.3, -15.4), "Percy cottage", Color(0.65, 0.9, 0.75))
	# Aster — Evidence Plot (roomy square station) + cottage SE with yard clearance
	_add_box(Vector3(12, 0.02, -10), Vector3(7.5, 0.04, 7.5), Color(0.32, 0.38, 0.28), false, "AsterLabPad")
	_add_box(Vector3(12, 0.55, -12.2), Vector3(2.2, 0.85, 0.7), Color(0.45, 0.42, 0.35), true, "AsterClipboardTable")
	_add_home_sign(Vector3(12, 2.4, -10), "Evidence Plot — Aster (PLACEHOLDER skin)", Color(0.75, 0.92, 0.65))
	_add_porch_light(Vector3(12, 2.1, -10), Color(0.7, 0.95, 0.55))
	_build_open_building(Vector3(24, 0, -11), Vector3(6.4, 2.9, 5.4), Color(0.48, 0.62, 0.42), "AsterHome", "x-")
	_add_roof(Vector3(24, 3.25, -11), Vector3(7.0, 0.65, 6.0), Color(0.28, 0.4, 0.24))
	_furnish(Vector3(24, 0, -11), "cottage")
	_add_porch_light(Vector3(20.6, 2.3, -11), Color(0.75, 0.95, 0.55))
	_add_home_sign(Vector3(20.4, 3.5, -11), "Aster cottage — Conspiracy Corrector", Color(0.78, 0.92, 0.68))
	# Telescope west of the door lane — must sit outside the 6.4×5.4 footprint (not under the house).
	_add_aster_telescope(Vector3(18.6, 0.0, -9.0))
	_add_box(Vector3(16, 0.025, -10.5), Vector3(10.0, 0.03, 1.6), Color(0.4, 0.34, 0.26), false, "PathAster")
	# The Observer — village representation only. Desk truth is Mode A :8730.
	_add_box(Vector3(40, 0.02, 24), Vector3(6.4, 0.04, 6.4), Color(0.28, 0.30, 0.34), false, "ObserverDeskPad")
	_add_box(Vector3(40, 0.55, 22.2), Vector3(2.0, 0.85, 0.7), Color(0.42, 0.44, 0.48), true, "ObserverLedgerTable")
	_add_porch_light(Vector3(40, 2.1, 24), Color(0.72, 0.76, 0.82))
	_add_home_sign(Vector3(40, 2.4, 24), "Observer desk — door to :8730 (PLACEHOLDER)", Color(0.72, 0.76, 0.82))
	_build_open_building(Vector3(46, 0, 28), Vector3(5.4, 2.8, 4.6), Color(0.40, 0.42, 0.48), "ObserverCottage", "x-")
	_add_roof(Vector3(46, 3.15, 28), Vector3(6.0, 0.55, 5.1), Color(0.22, 0.24, 0.28))
	_furnish(Vector3(46, 0, 28), "cottage")
	_add_porch_light(Vector3(43.1, 2.2, 28), Color(0.7, 0.74, 0.8))
	_add_home_sign(Vector3(43.0, 3.4, 28), "Observer cottage (representation)", Color(0.72, 0.76, 0.82))
	_add_box(Vector3(43, 0.025, 26), Vector3(8.0, 0.03, 1.5), Color(0.38, 0.34, 0.28), false, "PathObserver")
	# Village Windmill — east pasture, clear of Mom / Aster / Apex (matches Hearth PLACES.windmill).
	_build_village_windmill(Vector3(36.0, 0.0, -18.0))
	_add_box(Vector3(28, 0.025, -16), Vector3(14.0, 0.03, 1.8), Color(0.4, 0.34, 0.26), false, "PathWindmill")
	# Inland pond removed — water belongs at the community edge (see _build_harbor_edge).
	_tree_root = Node3D.new()
	_tree_root.name = "SeasonTrees"
	add_child(_tree_root)
	# Trees match kernel seed — none on Genesis door axis (-28,16) or Aster lab pad (12,-10).
	for xz in [Vector3(-10, 0, 10), Vector3(-20, 0, 8), Vector3(8, 0, 10), Vector3(-6, 0, 14), Vector3(12, 0, 18), Vector3(-36, 0, 4), Vector3(28, 0, 4), Vector3(0, 0, 28), Vector3(-22, 0, -12), Vector3(32, 0, -4)]:
		_add_season_tree(xz)
	_add_box(Vector3(18, 0.025, 7), Vector3(14, 0.03, 2.2), Color(0.4, 0.34, 0.26), false, "PathCinema")
	_add_box(Vector3(31, 0.025, 14), Vector3(2.0, 0.03, 14), Color(0.4, 0.34, 0.26), false, "PathLofts")
	_add_box(Vector3(-16, 0.025, -4), Vector3(18, 0.03, 2.0), Color(0.4, 0.34, 0.26), false, "PathLibrary")
	_add_box(Vector3(-24, 0.025, 1), Vector3(2.0, 0.03, 8), Color(0.4, 0.34, 0.26), false, "PathCodexHome")
	_add_box(Vector3(-28, 0.025, 10), Vector3(2.0, 0.03, 12), Color(0.4, 0.34, 0.26), false, "PathGenesisHome")
	_add_box(Vector3(8, 0.025, -20), Vector3(12, 0.03, 2.0), Color(0.4, 0.34, 0.26), false, "PathMom")
	_add_box(Vector3(-3, 0.025, -20), Vector3(10, 0.03, 2.0), Color(0.4, 0.34, 0.26), false, "PathGallery")
	_add_box(Vector3(-12, 0.025, -28), Vector3(10, 0.03, 2.0), Color(0.4, 0.34, 0.26), false, "PathMontageHome")
	_add_box(Vector3(26, 0.025, -3), Vector3(8, 0.03, 2.0), Color(0.4, 0.34, 0.26), false, "PathApexHome")
	_add_box(Vector3(20, 0.025, 26), Vector3(2.2, 0.03, 8), Color(0.4, 0.34, 0.26), false, "PathNovaHome")
	_add_box(Vector3(-6, 0.025, 24), Vector3(12, 0.03, 2.0), Color(0.4, 0.34, 0.26), false, "PathJarvisHome")
	_add_box(Vector3(0, 0.025, 34), Vector3(2.8, 0.03, 16), Color(0.4, 0.34, 0.26), false, "PathHarbor")
	_build_gardens_and_holiday()
	_build_harbor_edge()
	_build_well()
	_build_far_shore_destination()
	_build_storage_hall()
	_build_village_shops()


func _add_porch_light(pos: Vector3, color: Color) -> void:
	var glow := _add_box(pos, Vector3(0.28, 0.28, 0.28), color, false, "PorchLamp")
	var mat: StandardMaterial3D = glow.material_override
	mat.emission_enabled = true
	mat.emission = color
	mat.emission_energy_multiplier = 1.8
	var light := OmniLight3D.new()
	light.light_color = color
	light.light_energy = 1.1
	light.omni_range = 5.5
	light.position = pos
	add_child(light)


func _build_gardens_and_holiday() -> void:
	## Yard beds BESIDE cottages — clear of door path and building footprint.
	_decor_root = Node3D.new()
	_decor_root.name = "LivingDecor"
	add_child(_decor_root)
	_garden_root = Node3D.new()
	_garden_root.name = "GardenBeds"
	add_child(_garden_root)
	# genesis_home (-28,16) — west side yard
	_add_garden_bed(Vector3(-32.4, 0, 16.0), "genesis", Color(0.28, 0.55, 0.28))
	# mom_home (16,-24) — east side yard (door faces +z / plaza)
	_add_garden_bed(Vector3(21.2, 0, -24.0), "mom", Color(0.55, 0.35, 0.45))
	# gemini_home (-16,-16) — west side yard
	_add_garden_bed(Vector3(-20.8, 0, -16.0), "gemini", Color(0.35, 0.55, 0.48))
	# codex_home (-24,6) — west side yard (door faces south)
	_add_garden_bed(Vector3(-28.8, 0, 6.0), "codex", Color(0.45, 0.5, 0.28))
	# Heart Square flower ring
	for i in range(8):
		var ang := float(i) * TAU / 8.0
		var p := Vector3(cos(ang) * 5.2, 0.2, sin(ang) * 5.2)
		var bloom := _add_box(p, Vector3(0.35, 0.4, 0.35), Color(0.85, 0.35, 0.45), false, "SquareBloom%d" % i)
		if _decor_root and bloom:
			bloom.reparent(_decor_root)


func _add_garden_bed(pos: Vector3, owner_id: String, leaf: Color) -> void:
	if _garden_root == null:
		return
	var soil := _add_box(pos + Vector3(0, 0.06, 0), Vector3(3.6, 0.12, 2.2), Color(0.28, 0.18, 0.1), false, owner_id + "Soil")
	soil.reparent(_garden_root)
	for i in range(5):
		var h := 0.25 + float(i % 3) * 0.12
		var plant := _add_box(pos + Vector3(-1.2 + i * 0.6, 0.12 + h * 0.5, 0.15 * (i % 2)), Vector3(0.28, h, 0.28), leaf, false, owner_id + "Plant%d" % i)
		plant.reparent(_garden_root)
		if plant.material_override:
			_garden_mats.append({"mat": plant.material_override, "owner": owner_id, "idx": i})
	_add_home_sign(pos + Vector3(0, 1.6, 0), owner_id.capitalize() + " garden", leaf.lightened(0.35))


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


func _add_season_tree(xz: Vector3) -> void:
	if _tree_root == null:
		return
	_add_box(xz + Vector3(0, 0.7, 0), Vector3(0.28, 1.4, 0.28), Color(0.3, 0.2, 0.12), true, "Trunk")
	var canopy := _add_box(xz + Vector3(0, 1.7, 0), Vector3(1.4, 1.2, 1.4), Color(0.18, 0.4, 0.2), false, "Canopy")
	if canopy and canopy.material_override:
		_canopy_mats.append(canopy.material_override)
	# Keep canopies under SeasonTrees for bookkeeping (materials tracked above).
	if canopy and canopy.get_parent() != _tree_root:
		pass


func _apply_environment(data: Dictionary) -> void:
	var clock_v: Variant = data.get("clock", {})
	var weather_v: Variant = data.get("weather", {})
	var season := "summer"
	var weather := "clear"
	if clock_v is Dictionary:
		season = str((clock_v as Dictionary).get("season", season))
	if weather_v is Dictionary:
		weather = str((weather_v as Dictionary).get("current", weather))
	var leaf := Color(0.22, 0.62, 0.22)
	var dens := 0.9
	match season:
		"spring":
			leaf = Color(0.35, 0.75, 0.28)
			dens = 0.65
		"summer":
			leaf = Color(0.22, 0.62, 0.22)
			dens = 0.92
		"autumn":
			leaf = Color(0.78, 0.48, 0.12)
			dens = 0.72
		"winter":
			leaf = Color(0.62, 0.62, 0.58)
			dens = 0.12
	for mat in _canopy_mats:
		if mat is StandardMaterial3D:
			(mat as StandardMaterial3D).albedo_color = leaf
			(mat as StandardMaterial3D).albedo_color.a = clampf(dens, 0.15, 1.0)
	_apply_garden_growth(data)
	_apply_holiday_decor(data, season)
	_apply_forge_work_evidence(data)
	_apply_evening_gather(data)
	if _world_env and _world_env.environment:
		var env: Environment = _world_env.environment
		match weather:
			"rain", "snow":
				env.fog_density = 0.012
				env.background_color = Color(0.35, 0.4, 0.45) if weather == "rain" else Color(0.55, 0.58, 0.62)
			"cloudy":
				env.fog_density = 0.007
				env.background_color = Color(0.45, 0.52, 0.58)
			_:
				env.fog_density = 0.0045
				env.background_color = Color(0.42, 0.58, 0.74)
	var hol_name := ""
	var hol_v: Variant = data.get("active_holiday")
	if hol_v is Dictionary:
		hol_name = str((hol_v as Dictionary).get("name", ""))
	if _season_label:
		if hol_name != "":
			_season_label.text = "Season: %s · Weather: %s · %s" % [season.capitalize(), weather, hol_name]
		else:
			_season_label.text = "Season: %s · Weather: %s" % [season.capitalize(), weather]
	if life_label and clock_v is Dictionary:
		var day = (clock_v as Dictionary).get("day", "?")
		var period = (clock_v as Dictionary).get("period", "?")
		var hol_bit := (" · " + hol_name) if hol_name != "" else ""
		life_label.text = "Day %s · %s · %s%s · gardens live" % [str(day), str(season), str(period), hol_bit]


func _apply_forge_work_evidence(data: Dictionary) -> void:
	## Layer 8A — Apex forge glow tracks real Mode A presence probe (not mime).
	var we_v: Variant = data.get("work_evidence")
	var live := false
	var detail := "holding post"
	if we_v is Dictionary:
		var apex_v: Variant = (we_v as Dictionary).get("apex")
		if apex_v is Dictionary:
			live = bool((apex_v as Dictionary).get("live", false))
			detail = str((apex_v as Dictionary).get("detail", detail))
	if _forge_glow_mat:
		if live:
			_forge_glow_mat.emission = Color(0.35, 0.95, 1.0)
			_forge_glow_mat.emission_energy_multiplier = 3.2
		else:
			_forge_glow_mat.emission = Color(1.0, 0.4, 0.1)
			_forge_glow_mat.emission_energy_multiplier = 1.4
	if _forge_live_label:
		if live:
			_forge_live_label.text = "Forge LIVE · Mode A"
			_forge_live_label.modulate = Color(0.45, 0.95, 1.0)
		else:
			_forge_live_label.text = "Forge quiet · honest hold"
			_forge_live_label.modulate = Color(0.7, 0.55, 0.4)


func _apply_evening_gather(data: Dictionary) -> void:
	## Layer 8C — Gemini soft evening gather cue at Heart Square.
	if _gather_label == null:
		_gather_label = Label3D.new()
		_gather_label.name = "EveningGatherLabel"
		_gather_label.position = Vector3(0, 3.2, 0)
		_gather_label.font_size = 56
		_gather_label.outline_size = 14
		_gather_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		_gather_label.no_depth_test = true
		add_child(_gather_label)
	var eg_v: Variant = data.get("evening_gather")
	var active := false
	var plain := ""
	if eg_v is Dictionary:
		active = bool((eg_v as Dictionary).get("active", false))
		plain = str((eg_v as Dictionary).get("plain", ""))
	if active:
		_gather_label.visible = true
		_gather_label.text = "Evening gather · Gemini hosts (by choice)"
		_gather_label.modulate = Color(0.98, 0.86, 0.45)
	else:
		_gather_label.visible = false
		if plain != "" and life_label:
			pass


func _apply_garden_growth(data: Dictionary) -> void:
	var gardens_v: Variant = data.get("gardens")
	if not (gardens_v is Dictionary):
		return
	var gardens: Dictionary = gardens_v
	for entry in _garden_mats:
		if typeof(entry) != TYPE_DICTIONARY:
			continue
		var owner_id := str(entry.get("owner", ""))
		var idx := int(entry.get("idx", 0))
		var mat: Variant = entry.get("mat")
		if not (mat is StandardMaterial3D):
			continue
		var plot_key := owner_id + "_garden"
		var plot_v: Variant = gardens.get(plot_key)
		if not (plot_v is Dictionary):
			continue
		var plants: Variant = (plot_v as Dictionary).get("plants", [])
		var growth := 0.5
		var health := 0.8
		if plants is Array and (plants as Array).size() > idx:
			var plant_v: Variant = (plants as Array)[idx]
			if plant_v is Dictionary:
				growth = float((plant_v as Dictionary).get("growth", growth))
				health = float((plant_v as Dictionary).get("health", health))
		var sm: StandardMaterial3D = mat
		sm.albedo_color = Color(0.2 + health * 0.25, 0.35 + growth * 0.4, 0.18 + health * 0.1)


func _apply_holiday_decor(data: Dictionary, season: String) -> void:
	var hol_v: Variant = data.get("active_holiday")
	var hol_id := ""
	var hol: Dictionary = {}
	if hol_v is Dictionary:
		hol = hol_v
		hol_id = str(hol.get("id", ""))
	if hol_id == _last_holiday_id:
		return
	_last_holiday_id = hol_id
	for n in _holiday_props:
		if is_instance_valid(n):
			n.queue_free()
	_holiday_props.clear()
	if hol_id == "":
		return
	var decor: Variant = hol.get("decorations", [])
	var kinds: Array = decor if decor is Array else []
	var accent := Color(0.95, 0.75, 0.35)
	match season:
		"spring":
			accent = Color(0.95, 0.55, 0.7)
		"summer":
			accent = Color(1.0, 0.75, 0.25)
		"autumn":
			accent = Color(0.9, 0.45, 0.15)
		"winter":
			accent = Color(0.7, 0.85, 1.0)
	for i in range(mini(kinds.size() + 4, 10)):
		var ang := float(i) * TAU / 10.0
		var p := Vector3(cos(ang) * 6.4, 0.35, sin(ang) * 6.4)
		var prop := _add_box(p, Vector3(0.45, 0.7, 0.45), accent, false, "HolidayProp%d" % i)
		if prop and prop.material_override:
			var pm: StandardMaterial3D = prop.material_override
			pm.emission_enabled = true
			pm.emission = accent
			pm.emission_energy_multiplier = 1.2
		_holiday_props.append(prop)
	for xz in [Vector3(5, 1.6, 5), Vector3(-5, 1.6, 5), Vector3(5, 1.6, -5), Vector3(-5, 1.6, -5)]:
		var ribbon := _add_box(xz, Vector3(0.9, 0.12, 0.12), accent.lightened(0.2), false, "HolidayRibbon")
		_holiday_props.append(ribbon)


func _build_family() -> void:
	## Core family first — then kin. Not one NPC class with stickers.
	var roster := [
		{"id": "gemini", "name": "Gemini", "pos": Vector3(-15.2, 0.1, -13.2), "color": Color(0.55, 0.78, 0.95)},
		{"id": "apex", "name": "Apex", "pos": Vector3(27.5, 0.1, -6.0), "color": Color(0.35, 0.88, 0.98)},
		{"id": "codex", "name": "Codex", "pos": Vector3(-24.0, 0.1, 3.5), "color": Color(0.95, 0.78, 0.38)},
		{"id": "merovin", "name": "Merovin", "pos": Vector3(31.2, 0.1, 8.2), "color": Color(0.92, 0.55, 0.72)},
		{"id": "draven", "name": "Draven", "pos": Vector3(31.2, 0.1, 20.0), "color": Color(0.55, 0.52, 0.82)},
		{"id": "montage", "name": "OpenMontage", "pos": Vector3(-17.2, 0.1, -29.5), "color": Color(0.95, 0.62, 0.42)},
		{"id": "jarvis", "name": "Jarvis", "pos": Vector3(-12.0, 0.1, 23.5), "color": Color(0.7, 0.8, 0.95)},
		{"id": "genesis", "name": "Genesis", "pos": Vector3(-27.2, 0.1, 18.2), "color": Color(0.95, 0.72, 0.42)},
		{"id": "nova", "name": "Nova", "pos": Vector3(20.0, 0.1, 27.5), "color": Color(0.78, 0.58, 0.95)},
		{"id": "percy", "name": "Percy", "pos": Vector3(10.0, 0.1, -15.4), "color": Color(0.55, 0.85, 0.7)},
		{"id": "aster", "name": "Aster", "pos": Vector3(12.0, 0.1, -10.0), "color": Color(0.72, 0.88, 0.62)},
		{"id": "observer", "name": "The Observer", "pos": Vector3(40.0, 0.1, 24.0), "color": Color(0.62, 0.66, 0.72)},
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
	var starts := [
		Vector3(-19.0, 0.15, 11.0),
		Vector3(4.0, 0.15, 4.0),
		Vector3(2.0, 0.15, 18.0),
	]
	for i in range(3):
		var s := CharacterBody3D.new()
		s.name = "Squirrel_%d" % i
		s.script = SquirrelScript
		s.set("squirrel_id", "sq_%d" % (i + 1))
		s.position = starts[i]
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
	_apply_environment(data)
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
	_sync_family_chat_room(data)
	_apply_media_state(data)
	_sync_far_shore_builds(data)
	_apply_axiom_hud(data)
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


func _apply_axiom_hud(data: Dictionary) -> void:
	## Layer 14A — Mom's Axiom ⨁ balance (Hearth truth).
	if axiom_label == null:
		return
	var bal := -1
	var fam_v: Variant = data.get("family")
	if fam_v is Array:
		for person in fam_v:
			if person is Dictionary and str(person.get("id")) == "mom":
				bal = int(person.get("axiom", -1))
				break
	if bal < 0:
		axiom_label.text = "Axiom ⨁ — seeding…"
		return
	axiom_label.text = "Your Axiom ⨁%d  ·  near someone: [G] gift ⨁5" % bal


func _gift_axiom_near() -> void:
	## Thin gift — Mom sends ⨁5 to the citizen she's standing next to.
	var who := ""
	for child in get_tree().get_nodes_in_group("family_citizen"):
		if bool(child.get("player_near")):
			who = str(child.get("member_id"))
			if who == "" or who == "true" or who == "false":
				if child.has_meta("family_id"):
					who = str(child.get_meta("family_id"))
			break
	if who == "" or who == "mom":
		_log_convo("Axiom", "Stand next to someone to gift ⨁5.", "system")
		return
	if _home and _home.has_method("axiom_transfer"):
		_home.axiom_transfer(who, 5, "gift")
		_log_convo("Axiom", "Sending ⨁5 to %s…" % who, "system")
	else:
		_log_convo("Axiom", "Hearth offline — gift not saved.", "system")


func _play_overhear(data: Dictionary) -> void:
	## World bubbles for the current stand. Chat room uses utterances/conversations (always).
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
	var lines_v: Variant = rec.get("lines")
	if lines_v is Array and (lines_v as Array).size() > 0:
		# Chat room owns the log via utterances. Here: world bubbles only.
		for row in lines_v:
			if not (row is Dictionary):
				continue
			var who := str((row as Dictionary).get("who", ""))
			var text := str((row as Dictionary).get("text", ""))
			if who != "" and text != "":
				_speak_named(who, text, src if src != "" else "ollama", false)
		return
	var line := ""
	if src == "waiting":
		line = str(rec.get("text", "")).strip_edges()
		if line == "":
			line = "They heard Mom. Local voice is still cooking — not ignoring her."
	elif src == "none":
		line = str(rec.get("text", "Writer not seated."))
	elif src == "house":
		line = "Old canned talk is not their voice."
	elif src == "ollama":
		line = str(rec.get("text", "")).substr(0, 180)
	if line != "":
		_log_convo("Hearth", line, "waiting")
	var bubble := ""
	if src == "waiting":
		bubble = "Standing together. Writer still thinking."
	elif src == "none":
		bubble = str(rec.get("text", "Writer missed.")).substr(0, 90)
	if bubble != "":
		var actors2: Variant = rec.get("actors")
		if actors2 is Array:
			for aid in actors2:
				if str(aid) == "mom":
					continue
				_speak_named(str(aid), bubble, src, false)


func _sync_family_chat_room(data: Dictionary) -> void:
	## Full family chat room: every saved conversation, even if Mom walked away.
	var convos: Variant = data.get("conversations")
	if not (convos is Array):
		return
	for ev in convos:
		if not (ev is Dictionary):
			continue
		var cid := str((ev as Dictionary).get("id", ""))
		if cid == "" or _logged_convo_ids.has(cid):
			continue
		_logged_convo_ids[cid] = true
		var lines_v: Variant = (ev as Dictionary).get("lines")
		if lines_v is Array and (lines_v as Array).size() > 0:
			for row in lines_v:
				if not (row is Dictionary):
					continue
				var who := str((row as Dictionary).get("who", "")).capitalize()
				var text := str((row as Dictionary).get("text", ""))
				if who != "" and text != "":
					_log_convo(who, text, str((ev as Dictionary).get("source", "talk")))
		else:
			var title := str((ev as Dictionary).get("text", (ev as Dictionary).get("title", "")))
			if title != "":
				_log_convo("Family", title, "talk")
	if _logged_convo_ids.size() > 120:
		_logged_convo_ids.clear()


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
		var conv := str(rec.get("conversation", ""))
		if conv != "":
			_logged_convo_ids[conv] = true
		if text == "":
			continue
		# Always land in the chat room. Bubbles are bonus for whoever is on screen.
		_speak_named(speaker, text, src)
	if _said.size() > 200:
		_said.clear()


func _speak_named(speaker: String, text: String, src: String, log_chat: bool = true) -> void:
	if speaker == "mom":
		_speak_mom(text, src, log_chat)
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
	if log_chat:
		_log_convo(nice, text, src)


func _speak_mom(text: String, source: String, log_chat: bool = true) -> void:
	if _mom_bubble:
		_mom_bubble.text = text if text.length() <= 90 else text.substr(0, 87) + "…"
		_mom_bubble.modulate = Color(0.98, 0.97, 0.92, 1)
	if log_chat:
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
	_apply_period_sound(period)


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
	## Lived-in greybox (layer 7). Keep a clear door lane on the entry face.
	_room_kit(pos, kind)
	match kind:
		"mom":
			_add_box(pos + Vector3(-1.6, 0.28, -1.6), Vector3(1.8, 0.4, 0.9), Color(0.55, 0.38, 0.28), true, "MomBed")
			_add_box(pos + Vector3(-1.6, 0.52, -1.6), Vector3(1.6, 0.12, 0.7), Color(0.72, 0.58, 0.48), false, "MomQuilt")
			_add_box(pos + Vector3(1.6, 0.45, -0.4), Vector3(0.7, 0.9, 0.7), Color(0.42, 0.3, 0.22), true, "MomChair")
			_add_box(pos + Vector3(1.7, 0.35, -1.7), Vector3(0.8, 0.7, 0.55), Color(0.38, 0.26, 0.18), true, "MomChest")
			_add_box(pos + Vector3(0, 0.95, -2.2), Vector3(1.1, 0.08, 0.4), Color(0.7, 0.55, 0.4), false, "MomShelf")
			_add_box(pos + Vector3(-1.5, 0.55, 0.9), Vector3(0.45, 0.7, 0.45), Color(0.5, 0.36, 0.28), true, "MomSideTable")
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
			_add_box(pos + Vector3(-2.0, 0.95, 0.6), Vector3(0.7, 0.08, 0.35), Color(0.55, 0.4, 0.28), false, "HearthShelf")
			var coals := _add_box(pos + Vector3(0, 0.45, -1.7), Vector3(0.7, 0.28, 0.3), Color(1.0, 0.4, 0.12), false, "HearthCoals")
			var cm: StandardMaterial3D = coals.material_override
			cm.emission_enabled = true
			cm.emission = Color(1.0, 0.35, 0.08)
			cm.emission_energy_multiplier = 2.2
		"gemini":
			_add_box(pos + Vector3(-1.2, 0.28, -1.1), Vector3(1.4, 0.35, 0.7), Color(0.3, 0.4, 0.55), true, "GemCot")
			_add_box(pos + Vector3(1.1, 0.4, -0.8), Vector3(0.55, 0.8, 0.55), Color(0.25, 0.35, 0.48), true, "GemStool")
			_add_box(pos + Vector3(0.2, 0.78, -1.6), Vector3(1.2, 0.9, 0.18), Color(0.2, 0.28, 0.4), true, "GemBoard")
			_add_box(pos + Vector3(1.2, 0.42, 0.6), Vector3(0.9, 0.1, 0.55), Color(0.28, 0.36, 0.48), true, "GemDesk")
			var gl := _add_box(pos + Vector3(-1.5, 1.1, 0.4), Vector3(0.2, 0.28, 0.2), Color(0.7, 0.9, 1.0), false, "GemLamp")
			var glm: StandardMaterial3D = gl.material_override
			glm.emission_enabled = true
			glm.emission = Color(0.55, 0.85, 1.0)
			glm.emission_energy_multiplier = 1.5
		"court":
			# Town-leader desk — keep +Z door lane clear.
			_add_box(pos + Vector3(0, 0.48, -0.6), Vector3(1.6, 0.12, 0.7), Color(0.32, 0.36, 0.48), true, "LeaderDesk")
			_add_box(pos + Vector3(0, 0.45, -1.3), Vector3(0.6, 0.85, 0.55), Color(0.28, 0.32, 0.44), true, "LeaderChair")
			_add_box(pos + Vector3(-1.4, 0.95, -0.4), Vector3(0.12, 1.1, 1.4), Color(0.22, 0.28, 0.4), true, "MapBoard")
			_add_box(pos + Vector3(1.3, 0.55, -0.2), Vector3(0.45, 0.7, 0.45), Color(0.35, 0.4, 0.52), true, "BriefCase")
			var cl := _add_box(pos + Vector3(0.9, 1.05, -0.6), Vector3(0.18, 0.25, 0.18), Color(0.75, 0.9, 1.0), false, "CourtLamp")
			var clm2: StandardMaterial3D = cl.material_override
			clm2.emission_enabled = true
			clm2.emission = Color(0.6, 0.85, 1.0)
			clm2.emission_energy_multiplier = 1.7
		"forge":
			_add_box(pos + Vector3(0.9, 0.5, -0.8), Vector3(1.4, 0.7, 0.8), Color(0.25, 0.22, 0.2), true, "AnvilBench")
			_add_box(pos + Vector3(-1.2, 0.45, -0.9), Vector3(0.7, 0.9, 0.55), Color(0.3, 0.28, 0.26), true, "ForgeStool")
			_add_box(pos + Vector3(1.4, 0.95, 0.8), Vector3(0.8, 0.08, 0.35), Color(0.4, 0.4, 0.42), false, "ToolShelf")
			var fire := _add_box(pos + Vector3(0.9, 0.95, -0.8), Vector3(0.4, 0.25, 0.4), Color(1.0, 0.45, 0.15), false, "ForgeGlow")
			var fm: StandardMaterial3D = fire.material_override
			fm.emission_enabled = true
			fm.emission = Color(1.0, 0.4, 0.1)
			fm.emission_energy_multiplier = 2.0
			_forge_glow_mat = fm
			_forge_live_label = Label3D.new()
			_forge_live_label.text = "Forge · Mode A probe"
			_forge_live_label.position = pos + Vector3(0, 3.4, 0)
			_forge_live_label.font_size = 48
			_forge_live_label.outline_size = 12
			_forge_live_label.modulate = Color(0.55, 0.85, 0.95)
			_forge_live_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
			add_child(_forge_live_label)
		"workshop":
			_add_box(pos + Vector3(0.7, 0.45, -0.5), Vector3(1.6, 0.55, 0.7), Color(0.42, 0.34, 0.28), true, "NovaBench")
			_add_box(pos + Vector3(-1.1, 0.4, -0.8), Vector3(0.55, 0.8, 0.55), Color(0.4, 0.32, 0.45), true, "NovaStool")
			_add_box(pos + Vector3(1.2, 0.9, 0.9), Vector3(0.9, 0.08, 0.35), Color(0.5, 0.4, 0.55), false, "PartsShelf")
		"library":
			_add_box(pos + Vector3(-1.8, 1.1, -0.2), Vector3(0.35, 2.0, 3.2), Color(0.4, 0.28, 0.12), true, "ShelvesA")
			_add_box(pos + Vector3(1.8, 1.1, -0.2), Vector3(0.35, 2.0, 2.8), Color(0.38, 0.26, 0.12), true, "ShelvesB")
			_add_box(pos + Vector3(0.2, 0.45, -0.9), Vector3(0.7, 0.9, 0.7), Color(0.45, 0.32, 0.16), true, "ReadChair")
			_add_box(pos + Vector3(0.1, 0.48, -0.2), Vector3(1.1, 0.1, 0.7), Color(0.35, 0.24, 0.12), true, "ReadTable")
			var ll := _add_box(pos + Vector3(0.5, 1.0, -0.2), Vector3(0.18, 0.28, 0.18), Color(1.0, 0.88, 0.55), false, "LibLamp")
			var llm: StandardMaterial3D = ll.material_override
			llm.emission_enabled = true
			llm.emission = Color(1.0, 0.8, 0.4)
			llm.emission_energy_multiplier = 1.4
		"cinema":
			_cinema_screen = _add_box(pos + Vector3(2.4, 1.2, 0), Vector3(0.2, 1.8, 3.2), Color(0.08, 0.08, 0.1), true, "Screen")
			if _cinema_screen and _cinema_screen.material_override:
				_cinema_screen_mat = _cinema_screen.material_override
			_cinema_title = Label3D.new()
			_cinema_title.text = "Cinema screen · [E] Watch"
			_cinema_title.position = pos + Vector3(1.6, 2.4, 0)
			_cinema_title.font_size = 48
			_cinema_title.outline_size = 12
			_cinema_title.modulate = Color(0.9, 0.75, 0.85)
			_cinema_title.billboard = BaseMaterial3D.BILLBOARD_ENABLED
			add_child(_cinema_title)
			_add_box(pos + Vector3(-0.4, 0.4, 0.9), Vector3(0.7, 0.8, 0.7), Color(0.35, 0.18, 0.25), true, "SeatM")
			_add_box(pos + Vector3(-0.4, 0.4, -0.9), Vector3(0.7, 0.8, 0.7), Color(0.28, 0.22, 0.4), true, "SeatD")
			_add_box(pos + Vector3(0.4, 0.55, 0.0), Vector3(1.4, 0.12, 0.9), Color(0.25, 0.18, 0.22), true, "EditDesk")
			_add_box(pos + Vector3(-1.5, 0.95, 0.0), Vector3(0.08, 0.9, 1.6), Color(0.2, 0.15, 0.18), false, "StoryBoard")
		"merovin_loft":
			_add_box(pos + Vector3(-1.2, 0.28, -1.0), Vector3(1.5, 0.32, 0.7), Color(0.55, 0.3, 0.38), true, "MerovinBed")
			_add_box(pos + Vector3(1.1, 0.45, -0.2), Vector3(0.7, 0.9, 0.7), Color(0.42, 0.22, 0.3), true, "MerovinChair")
			_add_box(pos + Vector3(0.2, 0.95, -1.6), Vector3(1.2, 0.08, 0.35), Color(0.7, 0.45, 0.55), false, "StoryShelf")
			var ml := _add_box(pos + Vector3(1.2, 1.1, 0.5), Vector3(0.18, 0.25, 0.18), Color(1.0, 0.7, 0.8), false, "MerLamp")
			var mlm: StandardMaterial3D = ml.material_override
			mlm.emission_enabled = true
			mlm.emission = Color(0.95, 0.55, 0.7)
			mlm.emission_energy_multiplier = 1.4
		"draven_loft":
			_add_box(pos + Vector3(-1.2, 0.28, -1.0), Vector3(1.5, 0.32, 0.7), Color(0.32, 0.3, 0.5), true, "DravenBed")
			_add_box(pos + Vector3(1.1, 0.45, -0.2), Vector3(0.7, 0.9, 0.7), Color(0.28, 0.26, 0.42), true, "DravenChair")
			_add_box(pos + Vector3(0.2, 0.95, -1.6), Vector3(1.2, 0.08, 0.35), Color(0.55, 0.52, 0.75), false, "LookLockShelf")
			var dl := _add_box(pos + Vector3(1.2, 1.1, 0.5), Vector3(0.18, 0.25, 0.18), Color(0.7, 0.7, 1.0), false, "DraLamp")
			var dlm: StandardMaterial3D = dl.material_override
			dlm.emission_enabled = true
			dlm.emission = Color(0.65, 0.6, 0.95)
			dlm.emission_energy_multiplier = 1.4
		"cottage":
			_add_box(pos + Vector3(-1.2, 0.28, -1.0), Vector3(1.5, 0.32, 0.7), Color(0.5, 0.36, 0.28), true, "CotBed")
			_add_box(pos + Vector3(1.1, 0.45, -0.2), Vector3(0.7, 0.9, 0.7), Color(0.4, 0.3, 0.24), true, "CotChair")
			_add_box(pos + Vector3(0.1, 0.42, 0.55), Vector3(0.9, 0.1, 0.55), Color(0.38, 0.28, 0.2), true, "CotTable")
			_add_box(pos + Vector3(0.15, 0.95, -1.7), Vector3(1.1, 0.08, 0.35), Color(0.55, 0.4, 0.3), false, "CotShelf")
			_add_box(pos + Vector3(-1.5, 0.55, 0.7), Vector3(0.4, 0.55, 0.4), Color(0.42, 0.32, 0.24), true, "CotCrate")
			var cot_lamp := _add_box(pos + Vector3(-1.5, 1.15, 0.35), Vector3(0.2, 0.3, 0.2), Color(1.0, 0.85, 0.55), false, "CotLamp")
			var clm: StandardMaterial3D = cot_lamp.material_override
			clm.emission_enabled = true
			clm.emission = Color(1.0, 0.78, 0.4)
			clm.emission_energy_multiplier = 1.5
		"gallery":
			_add_box(pos + Vector3(0, 1.1, -1.6), Vector3(3.0, 1.4, 0.18), Color(0.28, 0.24, 0.3), true, "GiftWall")
			_add_box(pos + Vector3(-1.1, 0.42, -0.2), Vector3(0.9, 0.08, 0.9), Color(0.45, 0.38, 0.32), true, "GiftTable")
			_add_box(pos + Vector3(1.2, 0.45, -0.4), Vector3(0.55, 0.85, 0.55), Color(0.4, 0.34, 0.4), true, "GiftStool")
		"gate":
			_add_box(pos + Vector3(0, 0.5, 0.2), Vector3(1.1, 0.15, 0.7), Color(0.3, 0.32, 0.42), true, "WatchDesk")
			_add_box(pos + Vector3(1.3, 0.55, -0.5), Vector3(0.5, 1.0, 0.5), Color(0.35, 0.38, 0.5), true, "WatchStool")
			_add_box(pos + Vector3(-1.3, 0.95, -0.3), Vector3(0.7, 0.08, 0.35), Color(0.4, 0.45, 0.55), false, "WatchShelf")
		"shed":
			_add_box(pos + Vector3(0.9, 0.35, -0.8), Vector3(0.9, 0.55, 0.55), Color(0.32, 0.4, 0.26), true, "SeedBin")
			_add_box(pos + Vector3(0.2, 0.4, -0.2), Vector3(0.8, 0.12, 0.8), Color(0.36, 0.28, 0.16), true, "PottingTable")
			_add_box(pos + Vector3(-1.0, 0.4, -0.7), Vector3(0.55, 0.75, 0.55), Color(0.34, 0.42, 0.28), true, "ShedStool")
		_:
			_add_box(pos + Vector3(0, 0.35, -0.4), Vector3(0.8, 0.5, 0.8), Color(0.4, 0.35, 0.3), true, "Stool")


func _room_kit(pos: Vector3, kind: String) -> void:
	var rug := Color(0.45, 0.32, 0.22)
	if kind in ["gemini", "gate", "court"]:
		rug = Color(0.28, 0.34, 0.48)
	elif kind in ["library", "mom", "hearth"]:
		rug = Color(0.5, 0.34, 0.2)
	elif kind in ["cinema", "merovin_loft"]:
		rug = Color(0.42, 0.28, 0.32)
	# Rug sits back from door lane so entry stays clear.
	_add_box(pos + Vector3(0, 0.11, -0.15), Vector3(2.2, 0.03, 1.6), rug, false, kind + "Rug")


func _build_boundary() -> void:
	## Village outskirts. North rim pushed out so harbor sits past the homes.
	var rim := 40.0
	var north_rim := 76.0
	# North tree line with a center gap for harbor + far shore
	_add_box(Vector3(-32, 1.6, north_rim), Vector3(24, 3.4, 1.2), Color(0.18, 0.32, 0.18), true, "TreeLineN_W")
	_add_box(Vector3(34, 1.6, north_rim), Vector3(24, 3.4, 1.2), Color(0.18, 0.32, 0.18), true, "TreeLineN_E")
	_add_box(Vector3(0, 1.6, -rim), Vector3(82, 3.4, 1.2), Color(0.16, 0.28, 0.16), true, "TreeLineS")
	_add_box(Vector3(rim, 1.6, 8), Vector3(1.2, 3.4, 98), Color(0.17, 0.3, 0.16), true, "TreeLineE")
	_add_box(Vector3(-rim, 1.6, 8), Vector3(1.2, 3.4, 98), Color(0.15, 0.26, 0.18), true, "TreeLineW")
	for xz in [Vector3(28, 0, 20), Vector3(-28, 0, 20), Vector3(28, 0, -22), Vector3(-28, 0, -20), Vector3(20, 0, 30), Vector3(-18, 0, 30)]:
		_add_box(xz + Vector3(0, 0.9, 0), Vector3(0.5, 1.8, 0.5), Color(0.28, 0.18, 0.12), true, "HillTrunk")
		_add_box(xz + Vector3(0, 2.1, 0), Vector3(2.2, 1.6, 2.2), Color(0.14, 0.34, 0.16), false, "HillCanopy")
	# No inland OuterWater — that sat dead under Codex's west flank.


func _build_harbor_edge() -> void:
	## Community EDGE past Gate House — not under Codex / cottages.
	## PLACEHOLDER greybox: walk/look only. Fish / travel / build destinations later.
	var shore_z := 44.0
	var water_z := 54.0
	# Shore apron outside the cottage ring
	_add_box(Vector3(0, 0.03, shore_z), Vector3(40, 0.08, 10), Color(0.38, 0.34, 0.26), false, "HarborShore")
	# Waterway
	var water := _add_box(Vector3(0, -0.12, water_z), Vector3(52, 0.22, 18), Color(0.14, 0.42, 0.62), false, "Waterway")
	if water and water.material_override:
		var wm: StandardMaterial3D = water.material_override
		wm.roughness = 0.15
		wm.metallic = 0.05
	# Pier into the water
	_add_box(Vector3(0, 0.28, 48.5), Vector3(3.4, 0.22, 12), Color(0.48, 0.34, 0.2), true, "PierDeck")
	_add_box(Vector3(-1.5, 0.55, 44.5), Vector3(0.25, 0.9, 0.25), Color(0.35, 0.25, 0.15), true, "PierPostL")
	_add_box(Vector3(1.5, 0.55, 44.5), Vector3(0.25, 0.9, 0.25), Color(0.35, 0.25, 0.15), true, "PierPostR")
	_add_box(Vector3(-1.5, 0.55, 52.0), Vector3(0.25, 0.9, 0.25), Color(0.35, 0.25, 0.15), true, "PierPostL2")
	_add_box(Vector3(1.5, 0.55, 52.0), Vector3(0.25, 0.9, 0.25), Color(0.35, 0.25, 0.15), true, "PierPostR2")
	# Dry dock cradle (east shore)
	_add_box(Vector3(12, 0.2, 43.5), Vector3(8.5, 0.35, 5.5), Color(0.4, 0.3, 0.18), true, "DryDockPad")
	_add_box(Vector3(9.5, 0.85, 43.5), Vector3(0.35, 1.2, 5.0), Color(0.32, 0.24, 0.14), true, "DryDockRailL")
	_add_box(Vector3(14.5, 0.85, 43.5), Vector3(0.35, 1.2, 5.0), Color(0.32, 0.24, 0.14), true, "DryDockRailR")
	_add_box(Vector3(12, 0.55, 41.2), Vector3(7.5, 0.25, 0.35), Color(0.3, 0.22, 0.12), true, "DryDockKeel")
	# Ships: one in dry dock, one tied at pier
	_add_greybox_ship(Vector3(12, 0.55, 43.5), 0.0, "ShipDryDock")
	_add_greybox_ship(Vector3(-6.5, -0.05, 52.5), 18.0, "ShipMoored")
	_add_home_sign(Vector3(0, 3.2, 42.0), "Harbor · edge of town · [E] fish", Color(0.65, 0.85, 1.0))
	_add_home_sign(Vector3(12, 2.8, 40.5), "Dry dock", Color(0.85, 0.75, 0.55))
	_add_home_sign(Vector3(-6.5, 2.6, 50.5), "Moored ship · sail to far shore", Color(0.75, 0.85, 0.95))


func _build_far_shore_destination() -> void:
	## First travel destination across the water — builds persist via Hearth.
	var spit := FAR_SHORE
	_add_box(spit + Vector3(0, 0.04, 0), Vector3(16, 0.1, 10), Color(0.34, 0.42, 0.28), false, "FarShoreLand")
	_add_box(spit + Vector3(0, 0.28, -4.2), Vector3(4.0, 0.22, 3.5), Color(0.45, 0.32, 0.18), true, "FarShorePier")
	_add_greybox_ship(spit + Vector3(-3.5, -0.05, -3.0), -12.0, "ShipFarShore")
	_add_box(spit + Vector3(2.5, 0.55, 1.0), Vector3(1.2, 1.0, 1.2), Color(0.5, 0.42, 0.3), true, "BuildPlotMarker")
	_add_home_sign(spit + Vector3(0, 3.0, 0), "Far shore · destination · build together", Color(0.7, 0.95, 0.75))
	_add_home_sign(spit + Vector3(2.5, 2.4, 1.0), "[E] Place a build (persists)", Color(0.95, 0.88, 0.55))
	_add_home_sign(spit + Vector3(-3.5, 2.4, -3.0), "[E] Sail home", Color(0.75, 0.85, 1.0))
	_far_builds_root = Node3D.new()
	_far_builds_root.name = "FarShoreBuilds"
	add_child(_far_builds_root)


func _add_greybox_ship(pos: Vector3, yaw_deg: float, node_name: String) -> void:
	## Simple hull + cabin + mast — readable greybox, not final art.
	var root := Node3D.new()
	root.name = node_name
	root.position = pos
	root.rotation_degrees = Vector3(0, yaw_deg, 0)
	add_child(root)
	var hull := _make_box_mesh(Vector3(0, 0.35, 0), Vector3(2.4, 0.7, 6.5), Color(0.28, 0.2, 0.12), true, node_name + "Hull")
	root.add_child(hull)
	var cabin := _make_box_mesh(Vector3(0, 1.0, -0.6), Vector3(1.6, 0.7, 2.2), Color(0.45, 0.38, 0.28), false, node_name + "Cabin")
	root.add_child(cabin)
	var mast := _make_box_mesh(Vector3(0, 2.4, 0.8), Vector3(0.18, 3.2, 0.18), Color(0.35, 0.28, 0.18), false, node_name + "Mast")
	root.add_child(mast)
	var sail := _make_box_mesh(Vector3(0.7, 2.3, 0.8), Vector3(0.08, 2.0, 2.4), Color(0.85, 0.82, 0.74), false, node_name + "Sail")
	root.add_child(sail)


func _build_well() -> void:
	## Commons well between plaza and garden — pool removed for now.
	var well := Vector3(-8.5, 0, 7.5)
	_add_box(well + Vector3(0, 0.08, 0), Vector3(3.2, 0.12, 3.2), Color(0.32, 0.3, 0.26), true, "WellPad")
	_add_box(well + Vector3(0, 0.55, 0), Vector3(2.0, 0.9, 2.0), Color(0.42, 0.4, 0.36), true, "WellStone")
	_add_box(well + Vector3(0, 1.15, 0), Vector3(1.5, 0.35, 1.5), Color(0.38, 0.36, 0.32), true, "WellRim")
	var well_water := _add_box(well + Vector3(0, 0.95, 0), Vector3(1.1, 0.12, 1.1), Color(0.2, 0.48, 0.62), false, "WellWater")
	if well_water and well_water.material_override:
		(well_water.material_override as StandardMaterial3D).roughness = 0.2
	_add_box(well + Vector3(-0.85, 1.7, 0), Vector3(0.18, 1.3, 0.18), Color(0.3, 0.22, 0.14), true, "WellPostL")
	_add_box(well + Vector3(0.85, 1.7, 0), Vector3(0.18, 1.3, 0.18), Color(0.3, 0.22, 0.14), true, "WellPostR")
	_add_box(well + Vector3(0, 2.35, 0), Vector3(2.0, 0.18, 0.18), Color(0.3, 0.22, 0.14), true, "WellBeam")
	_add_box(well + Vector3(0, 1.9, 0), Vector3(0.08, 0.9, 0.08), Color(0.25, 0.2, 0.12), false, "WellRope")
	_add_box(well + Vector3(0, 1.35, 0.15), Vector3(0.45, 0.35, 0.45), Color(0.35, 0.28, 0.18), false, "WellBucket")
	_add_home_sign(well + Vector3(0, 3.1, 0), "Village well · [E] draw water", Color(0.75, 0.9, 1.0))


func _build_storage_hall() -> void:
	## Village Storage — real goods hall near the square (Layer 10). Not a fake UI stub.
	var pos := Vector3(-14, 0, 2)
	_build_open_building(pos, Vector3(6.0, 2.8, 5.0), Color(0.42, 0.36, 0.28), "StorageHall", "x+")
	_add_roof(pos + Vector3(0, 3.15, 0), Vector3(6.6, 0.6, 5.5), Color(0.28, 0.22, 0.16))
	_furnish(pos, "shed")
	# Crates / shelves — storage contents (gifts and goods can land here later).
	_add_box(pos + Vector3(-1.6, 0.45, -1.2), Vector3(1.2, 0.9, 0.9), Color(0.48, 0.34, 0.2), true, "StoreCrateA")
	_add_box(pos + Vector3(1.4, 0.45, -1.0), Vector3(1.1, 0.9, 1.0), Color(0.42, 0.3, 0.18), true, "StoreCrateB")
	_add_box(pos + Vector3(0.2, 0.95, 1.4), Vector3(2.4, 0.12, 0.55), Color(0.35, 0.28, 0.2), true, "StoreShelf")
	_add_box(pos + Vector3(-1.8, 0.55, 1.2), Vector3(0.7, 1.1, 0.55), Color(0.38, 0.32, 0.24), true, "StoreBarrel")
	_add_porch_light(pos + Vector3(3.2, 2.2, 0), Color(1.0, 0.85, 0.55))
	_add_home_sign(pos + Vector3(3.4, 3.2, 0), "Village Storage — goods & keeps", Color(0.95, 0.85, 0.6))
	_add_box(Vector3(-10, 0.025, 2), Vector3(8, 0.03, 2.0), Color(0.4, 0.34, 0.26), false, "PathStorage")


func _build_village_shops() -> void:
	## Layer 14B–14C — Market lane north of Gate (spaced; buy via Hearth).
	## Doors face south (z-) toward the village so cottage/workshop entrances stay clear.
	var g := STORE_GROCERY
	_build_open_building(g, Vector3(5.5, 2.6, 4.8), Color(0.48, 0.42, 0.28), "GroceryShop", "z-")
	_add_roof(g + Vector3(0, 2.95, 0), Vector3(6.0, 0.55, 5.3), Color(0.32, 0.38, 0.22))
	_add_box(g + Vector3(-1.4, 0.55, 0.6), Vector3(1.4, 1.0, 0.7), Color(0.55, 0.35, 0.2), true, "GroceryCrate")
	_add_box(g + Vector3(1.2, 0.7, 0.4), Vector3(1.6, 0.15, 0.8), Color(0.7, 0.55, 0.3), true, "GroceryTable")
	_add_porch_light(g + Vector3(0, 2.4, -2.6), Color(1.0, 0.9, 0.55))
	_add_home_sign(g + Vector3(0, 3.1, -2.7), "The Harvest · grocery · [E] buy", Color(0.85, 0.95, 0.55))

	var c := STORE_CLOTHING
	_build_open_building(c, Vector3(5.2, 2.7, 4.6), Color(0.45, 0.38, 0.48), "ClothingShop", "z-")
	_add_roof(c + Vector3(0, 3.05, 0), Vector3(5.8, 0.55, 5.1), Color(0.35, 0.28, 0.4))
	_add_box(c + Vector3(-1.2, 0.9, -0.5), Vector3(0.2, 1.6, 1.2), Color(0.55, 0.65, 0.85), false, "ClothRackA")
	_add_box(c + Vector3(1.3, 0.9, -0.3), Vector3(0.2, 1.6, 1.2), Color(0.75, 0.45, 0.4), false, "ClothRackB")
	_add_porch_light(c + Vector3(0, 2.5, -2.5), Color(0.95, 0.8, 1.0))
	_add_home_sign(c + Vector3(0, 3.2, -2.6), "The Wardrobe · clothing · [E] buy", Color(0.9, 0.75, 1.0))

	var e := STORE_ELECTRONICS
	_build_open_building(e, Vector3(5.4, 2.7, 4.8), Color(0.28, 0.34, 0.42), "ElectronicsShop", "z-")
	_add_roof(e + Vector3(0, 3.05, 0), Vector3(5.9, 0.5, 5.2), Color(0.2, 0.25, 0.32))
	_add_box(e + Vector3(0, 0.85, 0.5), Vector3(1.8, 1.1, 0.5), Color(0.15, 0.18, 0.22), true, "CircuitBench")
	_add_box(e + Vector3(-1.5, 0.55, -0.8), Vector3(0.7, 0.9, 0.5), Color(0.4, 0.75, 0.95), false, "CircuitScreen")
	_add_porch_light(e + Vector3(0, 2.5, -2.6), Color(0.55, 0.85, 1.0))
	_add_home_sign(e + Vector3(0, 3.15, -2.7), "The Circuit · electronics · [E] buy", Color(0.65, 0.9, 1.0))

	var p := STORE_PETS
	_build_open_building(p, Vector3(5.2, 2.5, 4.6), Color(0.5, 0.4, 0.3), "PetShop", "z-")
	_add_roof(p + Vector3(0, 2.9, 0), Vector3(5.7, 0.5, 5.0), Color(0.4, 0.32, 0.22))
	_add_box(p + Vector3(-1.3, 0.45, -0.4), Vector3(1.0, 0.7, 1.0), Color(0.55, 0.45, 0.35), true, "PetKennelA")
	_add_box(p + Vector3(1.2, 0.45, -0.2), Vector3(1.0, 0.7, 1.0), Color(0.5, 0.42, 0.32), true, "PetKennelB")
	_add_box(p + Vector3(0, 0.55, 0.9), Vector3(1.4, 0.9, 0.6), Color(0.65, 0.5, 0.35), true, "PetShelf")
	_add_porch_light(p + Vector3(0, 2.35, -2.5), Color(1.0, 0.88, 0.6))
	_add_home_sign(p + Vector3(0, 3.05, -2.6), "Whiskers & Paws · pets · [E] buy", Color(1.0, 0.85, 0.55))

	# Paths: plaza → gate → market lane (does not cover cottage doors)
	_add_box(Vector3(0, 0.025, 28), Vector3(2.6, 0.03, 10), Color(0.4, 0.34, 0.26), false, "PathToMarket")
	_add_box(Vector3(4, 0.025, 34), Vector3(44, 0.03, 2.2), Color(0.4, 0.34, 0.26), false, "PathMarketLane")
	_add_home_sign(Vector3(0, 3.0, 32), "Market lane — shops north of the Gate", Color(0.9, 0.85, 0.55))


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
		# Well solids also layer 1 so wildlife (mask 1) cannot walk through them.
		# Family citizens mask only layer 1 so PLACEHOLDER pathing is not trapped in cubes.
		# Mom/player masks 1|2 so walls still matter, but doors must stay wide enough.
		var walkable := (
			node_name == "Ground"
			or node_name == "GroundHarbor"
			or node_name == "GroundFarShore"
			or node_name.ends_with("Floor")
		)
		var blocks_wildlife := (
			node_name.begins_with("Well")
		) and not node_name.ends_with("Water")
		body.collision_layer = 1 if (walkable or blocks_wildlife) else 2
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


func _add_aster_telescope(at: Vector3) -> void:
	## Outside Aster's cottage — PLACEHOLDER prop for looking up. Not final art.
	_add_box(at + Vector3(0, 0.08, 0), Vector3(0.85, 0.1, 0.85), Color(0.28, 0.26, 0.22), true, "AsterScopePad")
	_add_box(at + Vector3(0, 0.55, 0), Vector3(0.1, 1.0, 0.1), Color(0.38, 0.34, 0.3), true, "AsterScopePost")
	_add_box(at + Vector3(0.32, 0.35, 0.28), Vector3(0.07, 0.75, 0.07), Color(0.34, 0.3, 0.26), true, "AsterScopeLegA")
	_add_box(at + Vector3(-0.3, 0.35, 0.26), Vector3(0.07, 0.75, 0.07), Color(0.34, 0.3, 0.26), true, "AsterScopeLegB")
	_add_box(at + Vector3(0.02, 0.35, -0.34), Vector3(0.07, 0.75, 0.07), Color(0.34, 0.3, 0.26), true, "AsterScopeLegC")
	# Tube tipped toward the sky — slightly north of the cottage door lane.
	var tube := _add_box(at + Vector3(0.12, 1.35, -0.2), Vector3(0.2, 0.2, 1.05), Color(0.58, 0.62, 0.68), true, "AsterScopeTube")
	if tube:
		tube.rotation_degrees = Vector3(-28.0, 18.0, 0.0)
	_add_box(at + Vector3(0.12, 1.55, -0.72), Vector3(0.28, 0.28, 0.18), Color(0.22, 0.24, 0.28), true, "AsterScopeEyepiece")
	_add_home_sign(at + Vector3(0.0, 2.35, 0.0), "Aster's telescope", Color(0.78, 0.92, 0.68))
	_add_porch_light(at + Vector3(0.5, 1.8, 0.3), Color(0.85, 0.95, 0.7))


func _build_village_windmill(at: Vector3) -> void:
	## East pasture landmark — PLACEHOLDER greybox. Door faces west toward town.
	_add_box(at + Vector3(0, 0.04, 0), Vector3(5.2, 0.08, 5.2), Color(0.36, 0.32, 0.26), false, "WindmillPad")
	# Stone tower
	_add_box(at + Vector3(0, 3.2, 0), Vector3(3.2, 6.4, 3.2), Color(0.55, 0.52, 0.46), true, "WindmillTower")
	# Cap
	_add_box(at + Vector3(0, 6.7, 0), Vector3(3.8, 1.2, 3.8), Color(0.42, 0.28, 0.2), true, "WindmillCap")
	# Hub + four sails (static PLACEHOLDER — not animated)
	_add_box(at + Vector3(-0.2, 5.6, 0), Vector3(0.55, 0.55, 0.55), Color(0.3, 0.28, 0.26), true, "WindmillHub")
	var sail_color := Color(0.82, 0.78, 0.7)
	_add_box(at + Vector3(-0.2, 8.1, 0), Vector3(0.35, 4.2, 1.1), sail_color, true, "WindmillSailN")
	_add_box(at + Vector3(-0.2, 3.1, 0), Vector3(0.35, 4.2, 1.1), sail_color, true, "WindmillSailS")
	_add_box(at + Vector3(-0.2, 5.6, 2.5), Vector3(0.35, 1.1, 4.2), sail_color, true, "WindmillSailE")
	_add_box(at + Vector3(-0.2, 5.6, -2.5), Vector3(0.35, 1.1, 4.2), sail_color, true, "WindmillSailW")
	# Door glow on the west face (toward village)
	_add_box(at + Vector3(-1.75, 1.1, 0), Vector3(0.12, 2.0, 1.1), Color(0.95, 0.82, 0.4), false, "WindmillDoor")
	_add_porch_light(at + Vector3(-2.2, 2.4, 0), Color(0.95, 0.85, 0.55))
	_add_home_sign(at + Vector3(0, 8.6, 0), "Village Windmill (PLACEHOLDER)", Color(0.9, 0.85, 0.65))


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

	# Top-left stack — spaced so lines never overlap (≈22px steps).
	# Darker text for readability over bright sky/ground.
	hint_label = Label.new()
	hint_label.text = "WASD walk · Mouse look · Click to reclaim look · Wheel zoom · Tab chat · Esc · F11"
	hint_label.set_anchors_preset(Control.PRESET_TOP_WIDE)
	hint_label.offset_left = 16
	hint_label.offset_top = 8
	hint_label.offset_right = -180
	hint_label.offset_bottom = 28
	hint_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hint_label.add_theme_font_size_override("font_size", 13)
	hint_label.add_theme_color_override("font_color", Color(0.22, 0.24, 0.2, 1.0))
	hint_label.add_theme_color_override("font_outline_color", Color(0.92, 0.93, 0.88, 0.85))
	hint_label.add_theme_constant_override("outline_size", 4)
	_hud_layer.add_child(hint_label)

	place_label = Label.new()
	place_label.position = Vector2(16, 32)
	place_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	place_label.add_theme_font_size_override("font_size", 17)
	place_label.add_theme_color_override("font_color", Color(0.18, 0.28, 0.24, 1.0))
	place_label.add_theme_color_override("font_outline_color", Color(0.92, 0.95, 0.9, 0.9))
	place_label.add_theme_constant_override("outline_size", 5)
	place_label.text = "Place: Mom's cottage door — walk into the gold glow"
	_hud_layer.add_child(place_label)

	life_label = Label.new()
	life_label.position = Vector2(16, 56)
	life_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	life_label.add_theme_font_size_override("font_size", 13)
	life_label.add_theme_color_override("font_color", Color(0.28, 0.26, 0.18, 1.0))
	life_label.add_theme_color_override("font_outline_color", Color(0.94, 0.93, 0.88, 0.88))
	life_label.add_theme_constant_override("outline_size", 4)
	life_label.text = "Cottages ≠ workplaces. Look for named home signs."
	_hud_layer.add_child(life_label)

	axiom_label = Label.new()
	axiom_label.position = Vector2(16, 76)
	axiom_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	axiom_label.add_theme_font_size_override("font_size", 14)
	axiom_label.add_theme_color_override("font_color", Color(0.32, 0.26, 0.08, 1.0))
	axiom_label.add_theme_color_override("font_outline_color", Color(0.96, 0.94, 0.82, 0.92))
	axiom_label.add_theme_constant_override("outline_size", 5)
	axiom_label.text = "Axiom ⨁ — waiting for Hearth…"
	_hud_layer.add_child(axiom_label)

	_season_label = Label.new()
	_season_label.position = Vector2(16, 98)
	_season_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_season_label.add_theme_font_size_override("font_size", 12)
	_season_label.add_theme_color_override("font_color", Color(0.2, 0.28, 0.24, 1.0))
	_season_label.add_theme_color_override("font_outline_color", Color(0.92, 0.95, 0.9, 0.88))
	_season_label.add_theme_constant_override("outline_size", 4)
	_season_label.text = "Season: — · Weather: —"
	_hud_layer.add_child(_season_label)

	# Holiday name rides on season_label — no extra overlapping line.
	_holiday_label = null

	debug_label = Label.new()
	debug_label.position = Vector2(16, 120)
	debug_label.add_theme_font_size_override("font_size", 12)
	debug_label.add_theme_color_override("font_color", Color(0.35, 0.28, 0.2, 1.0))
	debug_label.modulate = Color(1, 1, 1, 0.0)
	_hud_layer.add_child(debug_label)

	prompt_label = Label.new()
	prompt_label.position = Vector2(16, 142)
	prompt_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	prompt_label.add_theme_font_size_override("font_size", 16)
	prompt_label.add_theme_color_override("font_color", Color(0.28, 0.22, 0.06, 1.0))
	prompt_label.add_theme_color_override("font_outline_color", Color(0.97, 0.95, 0.82, 0.95))
	prompt_label.add_theme_constant_override("outline_size", 5)
	_hud_layer.add_child(prompt_label)

	# Bottom-left shared conversation — log + Mom type line always available.
	_convo_panel = Panel.new()
	_convo_panel.name = "ConvoPanel"
	_convo_panel.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	_convo_panel.offset_left = 12
	_convo_panel.offset_top = -340
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
	convo_title.text = "Family chat — highlight to copy · or Copy"
	convo_title.position = Vector2(8, 4)
	convo_title.size = Vector2(320, 22)
	convo_title.add_theme_font_size_override("font_size", 13)
	convo_title.modulate = Color(0.85, 0.92, 0.78)
	_convo_panel.add_child(convo_title)

	_copy_convo_btn = Button.new()
	_copy_convo_btn.text = "Copy"
	_copy_convo_btn.tooltip_text = "Copy selection, or whole chat if nothing selected. Ctrl+C also works while chat is open."
	_copy_convo_btn.position = Vector2(340, 2)
	_copy_convo_btn.size = Vector2(72, 24)
	_copy_convo_btn.pressed.connect(_copy_convo_to_clipboard)
	_convo_panel.add_child(_copy_convo_btn)

	_convo_scroll = ScrollContainer.new()
	_convo_scroll.position = Vector2(6, 28)
	_convo_scroll.size = Vector2(416, 180)
	_convo_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_convo_panel.add_child(_convo_scroll)

	_convo_log = RichTextLabel.new()
	_convo_log.bbcode_enabled = true
	_convo_log.fit_content = true
	_convo_log.scroll_following = true
	_convo_log.selection_enabled = true
	_convo_log.context_menu_enabled = true
	_convo_log.focus_mode = Control.FOCUS_CLICK
	_convo_log.mouse_filter = Control.MOUSE_FILTER_STOP
	_convo_log.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_convo_log.custom_minimum_size = Vector2(396, 0)
	_convo_log.add_theme_font_size_override("normal_font_size", 13)
	_convo_log.gui_input.connect(_on_convo_log_gui_input)
	_convo_scroll.add_child(_convo_log)
	_log_convo("Hearth", "Open chat: Tab or Open Chat. Drag to highlight text, then Ctrl+C or Copy. Walking away does not clear this log.", "system")

	dialogue_label = Label.new()
	dialogue_label.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	dialogue_label.offset_left = 12
	dialogue_label.offset_top = -372
	dialogue_label.offset_right = 440
	dialogue_label.offset_bottom = -344
	dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dialogue_label.add_theme_font_size_override("font_size", 13)
	dialogue_label.add_theme_color_override("font_color", Color(0.2, 0.24, 0.18, 1.0))
	dialogue_label.add_theme_color_override("font_outline_color", Color(0.92, 0.94, 0.88, 0.9))
	dialogue_label.add_theme_constant_override("outline_size", 4)
	_hud_layer.add_child(dialogue_label)

	talk_target = OptionButton.new()
	talk_target.name = "TalkTarget"
	talk_target.position = Vector2(6, 214)
	talk_target.size = Vector2(416, 28)
	talk_target.add_item("Family — Gemini (anytime)", 0)
	talk_target.set_item_metadata(0, "gemini")
	var who_list := [
		["Apex", "apex"], ["Codex", "codex"], ["Merovin", "merovin"], ["Draven", "draven"],
		["OpenMontage", "montage"], ["Jarvis", "jarvis"], ["Genesis", "genesis"],
		["Nova", "nova"], ["Percy", "percy"], ["Aster", "aster"],
	]
	for i in range(who_list.size()):
		talk_target.add_item(who_list[i][0], i + 1)
		talk_target.set_item_metadata(i + 1, who_list[i][1])
	talk_target.item_selected.connect(_on_talk_target_picked)
	_convo_panel.add_child(talk_target)

	# Mom's line lives inside the conversation panel (always on).
	talk_input = LineEdit.new()
	talk_input.name = "MomTalkInput"
	talk_input.position = Vector2(6, 248)
	talk_input.size = Vector2(416, 36)
	talk_input.placeholder_text = "Mom — type anytime · Enter sends · Tab opens chat · Esc ends focus"
	talk_input.visible = true
	talk_input.focus_mode = Control.FOCUS_CLICK
	talk_input.mouse_filter = Control.MOUSE_FILTER_STOP
	talk_input.text_submitted.connect(_on_talk_submitted)
	talk_input.focus_entered.connect(_on_talk_focus_entered)
	talk_input.focus_exited.connect(_on_talk_focus_exited)
	_convo_panel.add_child(talk_input)
	# Never start with the type box focused — that freezes mouse-look.
	talk_input.release_focus()
	get_viewport().gui_release_focus()

	chat_open_btn = Button.new()
	chat_open_btn.text = "Open Chat"
	chat_open_btn.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	chat_open_btn.offset_left = 460
	chat_open_btn.offset_top = -56
	chat_open_btn.offset_right = 580
	chat_open_btn.offset_bottom = -16
	chat_open_btn.pressed.connect(_open_chat_room)
	_hud_layer.add_child(chat_open_btn)

	_build_pause_menu()

	# Honesty strip sits above Open Chat / Leave — not on top of them.
	honest_label = Label.new()
	honest_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	honest_label.offset_left = 460
	honest_label.offset_top = -96
	honest_label.offset_right = -16
	honest_label.offset_bottom = -62
	honest_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	honest_label.add_theme_font_size_override("font_size", 11)
	honest_label.add_theme_color_override("font_color", Color(0.22, 0.26, 0.2, 1.0))
	honest_label.add_theme_color_override("font_outline_color", Color(0.9, 0.92, 0.86, 0.9))
	honest_label.add_theme_constant_override("outline_size", 4)
	honest_label.text = "Homes≠jobs · Garden tend real · Ambiance: wind/birds/crickets · Posts honest"
	_hud_layer.add_child(honest_label)

	var title := Label.new()
	title.text = "Heart Square"
	title.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	title.offset_left = -200
	title.offset_top = 10
	title.offset_right = -16
	title.offset_bottom = 36
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	title.add_theme_font_size_override("font_size", 18)
	title.add_theme_color_override("font_color", Color(0.22, 0.22, 0.18, 1.0))
	title.add_theme_color_override("font_outline_color", Color(0.94, 0.93, 0.88, 0.9))
	title.add_theme_constant_override("outline_size", 5)
	_hud_layer.add_child(title)

	# Leave World below title (no overlap with title or Open Chat).
	exit_btn = Button.new()
	exit_btn.text = "Leave World"
	exit_btn.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	exit_btn.offset_left = -150
	exit_btn.offset_top = 44
	exit_btn.offset_right = -16
	exit_btn.offset_bottom = 78
	exit_btn.pressed.connect(_open_pause_menu)
	_hud_layer.add_child(exit_btn)

	var amb := AudioStreamPlayer.new()
	amb.name = "AmbientPeriod"
	amb.bus = "Master"
	amb.volume_db = 2.0
	amb.autoplay = false
	amb.stream = _resolve_period_stream("morning")
	add_child(amb)
	_amb_period = amb
	_amb_period.play()

	_amb_place = AudioStreamPlayer.new()
	_amb_place.name = "AmbientPlace"
	_amb_place.bus = "Master"
	_amb_place.volume_db = -8.0
	_amb_place.autoplay = false
	add_child(_amb_place)

	# Music pad never starts — nature only.
	_amb_music = AudioStreamPlayer.new()
	_amb_music.name = "AmbientMusic"
	_amb_music.bus = "Master"
	_amb_music.volume_db = -80.0
	_amb_music.autoplay = false
	add_child(_amb_music)

	AudioServer.set_bus_mute(0, false)
	# Keep Master audible — faint beds were lost under a quiet bus.
	if AudioServer.get_bus_volume_db(0) < -6.0:
		AudioServer.set_bus_volume_db(0, 0.0)
	_sound_period = "morning"
	var has_real := _load_nature_stream("morning") != null or _load_nature_stream("day") != null
	if has_real:
		print("[Sound] Layer 9 using Audio/nature files @ +2 dB")
	else:
		print("[Sound] Layer 9 soft wind only — no chirp beeps; drop .ogg/.wav into Audio/nature/")
	call_deferred("_ensure_sound_playing")

	set_process(true)


func _log_convo(who: String, text: String, kind: String = "talk") -> void:
	if _convo_log == null:
		return
	var clipped := text.strip_edges()
	if clipped == "":
		return
	if clipped.length() > 220:
		clipped = clipped.substr(0, 217) + "…"
	var stamped := "%s: %s" % [who, clipped]
	var start: int = max(0, _convo_plain.size() - 12)
	for i in range(start, _convo_plain.size()):
		if str(_convo_plain[i]) == stamped:
			return
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
	_convo_plain.append(stamped)
	if _convo_plain.size() > 400:
		_convo_plain = _convo_plain.slice(_convo_plain.size() - 400)
	_convo_log.append_text("[color=%s][b]%s[/b][/color]: %s\n" % [color, who, clipped])
	if dialogue_label:
		dialogue_label.text = "%s: %s" % [who, clipped.substr(0, 90)]
	# ScrollContainer owns the scrollbar — force follow so Mom never drags manually.
	call_deferred("_scroll_convo_to_end")


func _on_convo_log_gui_input(event: InputEvent) -> void:
	## Free mouse so drag-select works (captured look otherwise eats the drag).
	if event is InputEventMouseButton and event.pressed:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		if _player:
			_player.set("chat_lock", true)


func _copy_convo_to_clipboard() -> void:
	var selected := ""
	if _convo_log:
		selected = str(_convo_log.get_selected_text()).strip_edges()
	var payload := selected
	if payload == "":
		payload = "\n".join(_convo_plain)
	if payload.strip_edges() == "":
		_log_convo("Hearth", "Nothing to copy yet.", "system")
		return
	DisplayServer.clipboard_set(payload)
	if _copy_convo_btn:
		_copy_convo_btn.text = "Copied"
		await get_tree().create_timer(1.2).timeout
		if _copy_convo_btn:
			_copy_convo_btn.text = "Copy"


func _scroll_convo_to_end() -> void:
	if _convo_scroll == null:
		return
	# Wait one layout pass so max_value includes the new line.
	await get_tree().process_frame
	var bar := _convo_scroll.get_v_scroll_bar()
	if bar:
		_convo_scroll.scroll_vertical = int(bar.max_value)
	if _convo_log and _convo_log.get_line_count() > 0:
		_convo_log.scroll_to_line(_convo_log.get_line_count() - 1)


func _make_ambient_stream() -> AudioStream:
	return _resolve_period_stream("morning")


func _pcm_stream(samples: PackedFloat32Array, mix_rate: int = 22050) -> AudioStreamWAV:
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = mix_rate
	stream.stereo = false
	stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	stream.loop_begin = 0
	var n := samples.size()
	var data := PackedByteArray()
	data.resize(n * 2)
	for i in range(n):
		var sample := int(clampf(samples[i] * 18000.0, -32767.0, 32767.0))
		data.encode_s16(i * 2, sample)
	stream.data = data
	stream.loop_end = n
	return stream


func _load_nature_stream(stem: String) -> AudioStream:
	## Real files win. Drop into Apex: godot_project/Audio/nature/
	## Names: morning/day/afternoon/evening/night/forest (+ .ogg .wav .mp3)
	for ext in [".ogg", ".wav", ".mp3"]:
		var path := "res://Audio/nature/%s%s" % [stem, ext]
		if ResourceLoader.exists(path):
			var loaded := load(path)
			if loaded is AudioStream:
				var s: AudioStream = loaded
				if s is AudioStreamWAV:
					(s as AudioStreamWAV).loop_mode = AudioStreamWAV.LOOP_FORWARD
				elif s is AudioStreamOggVorbis:
					(s as AudioStreamOggVorbis).loop = true
				elif s is AudioStreamMP3:
					(s as AudioStreamMP3).loop = true
				return s
	return null


func _resolve_period_stream(period: String) -> AudioStream:
	var keys: Array[String] = []
	match period:
		"morning":
			keys = ["morning", "day", "forest", "birds"]
		"afternoon":
			keys = ["afternoon", "day", "forest", "birds"]
		"evening":
			keys = ["evening", "night", "forest", "crickets"]
		"night":
			keys = ["night", "evening", "forest", "crickets"]
		_:
			keys = ["forest", "day", "morning"]
	for k in keys:
		var real := _load_nature_stream(k)
		if real != null:
			return real
	# No packs on disk yet — soft wind noise only (no chirp beeps).
	return _make_soft_wind(period)


func _make_soft_wind(period: String) -> AudioStreamWAV:
	## Broadband breeze only. No sine chirps (those read as beeps).
	var seconds := 8.0
	var rate := 22050
	var n := int(float(rate) * seconds)
	var samples := PackedFloat32Array()
	samples.resize(n)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(period) + 91
	var wind_lp := 0.0
	var gust := 0.0
	for i in range(n):
		var noise := rng.randf() * 2.0 - 1.0
		wind_lp = wind_lp * 0.94 + noise * 0.06
		# Slow amplitude wander so it feels like air, not a tone.
		gust = gust * 0.9995 + (rng.randf() * 2.0 - 1.0) * 0.0005
		var level := 0.035
		if period == "afternoon":
			level = 0.045
		elif period == "evening":
			level = 0.028
		elif period == "night":
			level = 0.022
		samples[i] = wind_lp * level * (1.0 + gust * 0.35)
	return _pcm_stream(samples, rate)


func _make_period_ambiance(period: String) -> AudioStream:
	return _resolve_period_stream(period)


func _make_period_ambient(period: String) -> AudioStream:
	return _resolve_period_stream(period)


func _make_music_bed(_period: String) -> AudioStreamWAV:
	## Disabled — Mom asked for nature only, no hum/pad.
	var silent := PackedFloat32Array()
	silent.resize(2205)
	return _pcm_stream(silent)


func _ensure_sound_playing() -> void:
	if _amb_period and not _amb_period.playing:
		_amb_period.play()
		print("[Sound] restarted nature ambiance")
	if _amb_music and _amb_music.playing:
		_amb_music.stop()


func _apply_period_sound(period: String) -> void:
	if period == "" or period == _sound_period:
		return
	_sound_period = period
	if _amb_period:
		_amb_period.stream = _resolve_period_stream(period)
		_amb_period.play()
	if _amb_music and _amb_music.playing:
		_amb_music.stop()


func _apply_place_sound(place_key: String) -> void:
	## No second bed until real place clips exist — avoids stacked beeps.
	if _amb_place == null:
		return
	if place_key == _sound_place:
		return
	_sound_place = place_key
	_amb_place.stop()


func _resolve_sound_place() -> String:
	## Nearest notable place for Mom's ears (thin Layer 9).
	if _player == null or not is_instance_valid(_player):
		return "heart_square"
	var p: Vector3 = _player.global_position
	var spots := {
		"garden": Vector3(-18, 0, 12),
		"cinema": Vector3(26, 0, 14),
		"apex_forge": Vector3(22, 0, 0),
		"heart_square": Vector3(0, 0, 0),
	}
	var eg_active := _gather_label != null and _gather_label.visible
	if eg_active and p.distance_to(Vector3(0, 0, 0)) < 10.0:
		return "gather"
	var best := "heart_square"
	var best_d := 9.5
	for k in spots.keys():
		var d: float = p.distance_to(spots[k])
		if d < best_d:
			best_d = d
			best = str(k)
	if best_d > 9.0:
		return "none"
	return best


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
	if _fish_cd > 0.0:
		_fish_cd = max(0.0, _fish_cd - delta)
	if _watching and _cinema_screen_mat:
		_watch_pulse += delta
		var glow := 0.55 + 0.35 * sin(_watch_pulse * 2.2)
		_cinema_screen_mat.emission_enabled = true
		_cinema_screen_mat.emission_energy_multiplier = glow
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
	_apply_place_sound(_resolve_sound_place())
	var sq_near := false
	if not near:
		for sq in get_tree().get_nodes_in_group("squirrel"):
			if bool(sq.get("player_near")):
				sq_near = true
				break
	var harbor_act := _world_action_near_player()
	if prompt_label:
		if near and _talking_to == "":
			prompt_label.text = "[E] Talk to %s" % who
		elif _talking_to != "":
			prompt_label.text = "Chat open — walking away keeps the family log. Esc leaves the type box."
		elif sq_near:
			prompt_label.text = "[E] Listen — a squirrel will chatter"
		elif harbor_act == "watch_stop":
			prompt_label.text = "[E] Stop watching"
		elif harbor_act == "watch":
			prompt_label.text = "[E] Watch at the cinema"
		elif harbor_act == "return":
			prompt_label.text = "[E] Sail home to the harbor"
		elif harbor_act == "travel":
			prompt_label.text = "[E] Sail to far shore (first destination)"
		elif harbor_act == "build":
			prompt_label.text = "[E] Place a build on far shore"
		elif harbor_act == "fish":
			if _fish_cd > 0.0:
				prompt_label.text = "Fishing… line settling (%.0fs)" % ceil(_fish_cd)
			else:
				prompt_label.text = "[E] Fish from the pier"
		elif harbor_act == "well":
			prompt_label.text = "[E] Draw water from the well"
		elif harbor_act == "buy_grocery":
			prompt_label.text = _shop_prompt("grocery")
		elif harbor_act == "buy_clothing":
			prompt_label.text = _shop_prompt("clothing_store")
		elif harbor_act == "buy_electronics":
			prompt_label.text = _shop_prompt("electronics_store")
		elif harbor_act == "buy_pets":
			prompt_label.text = _shop_prompt("pet_store")
		elif _inside_hearth:
			prompt_label.text = "Inside First Hearth. Tab / Open Chat anytime. Leave World (top-right) to exit."
		else:
			prompt_label.text = "Tab or Open Chat = family chat room. Leave World (top-right) or Esc to exit."


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
	var best_id := "heart_square"
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
					best_id = str(key)
					best = str((rec as Dictionary).get("label", key))
	place_label.text = "Place: %s" % best
	if _home and _home.has_method("set_mom_place"):
		_home.set_mom_place(best_id)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE:
		if _paused_world:
			_close_pause_menu()
			get_viewport().set_input_as_handled()
			return
		if _talking_to != "" or (talk_input and talk_input.has_focus()):
			_end_talk()
			get_viewport().set_input_as_handled()
			return
		_open_pause_menu()
		get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_TAB:
		# Open chat from anywhere — do not require standing next to someone.
		if not _paused_world:
			_open_chat_room()
		get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_C and event.ctrl_pressed:
		# Highlight in the family chat, then Ctrl+C — or Copy button for the whole log.
		# Do not steal Ctrl+C while Mom is typing in the LineEdit.
		if talk_input and talk_input.has_focus():
			return
		var sel := ""
		if _convo_log:
			sel = str(_convo_log.get_selected_text()).strip_edges()
		if sel != "" or (_player != null and bool(_player.get("chat_lock"))):
			_copy_convo_to_clipboard()
			get_viewport().set_input_as_handled()
			return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ALT:
		# Free the cursor for UI clicks — do NOT freeze WASD/look (that trapped Mom).
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		if _player:
			_player.set("_look_armed", false)
		get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_CAPSLOCK:
		# Emergency unlock if chat focus got stuck.
		_end_talk()
		if _paused_world:
			_close_pause_menu()
		if _player:
			_player.set("chat_lock", false)
			if _player.has_method("_capture_mouse"):
				_player.call("_capture_mouse")
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
			win.mode = Window.MODE_MAXIMIZED
		else:
			win.mode = Window.MODE_FULLSCREEN
		if _player:
			_player.set("chat_lock", false)
		if _player and _player.has_method("_capture_mouse"):
			_player.call_deferred("_capture_mouse")
		if _player and _player.has_method("_reclaim_look_burst"):
			_player.call_deferred("_reclaim_look_burst")
		get_viewport().set_input_as_handled()
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_G:
		if _paused_world or _talking_to != "" or (talk_input and talk_input.has_focus()):
			return
		_gift_axiom_near()
		get_viewport().set_input_as_handled()
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
		if _paused_world or _talking_to != "" or (talk_input and talk_input.has_focus()):
			return
		var act := _world_action_near_player()
		match act:
			"fish":
				_try_fish()
				get_viewport().set_input_as_handled()
			"travel":
				_sail_to_far_shore()
				get_viewport().set_input_as_handled()
			"return":
				_sail_home_to_harbor()
				get_viewport().set_input_as_handled()
			"build":
				_place_far_shore_build()
				get_viewport().set_input_as_handled()
			"well":
				_water_bucket += 1
				_log_convo("Well", "Drew a bucket of water. (carried: %d — PLACEHOLDER inventory)" % _water_bucket, "system")
				get_viewport().set_input_as_handled()
			"buy_grocery":
				_try_shop_buy("grocery")
				get_viewport().set_input_as_handled()
			"buy_clothing":
				_try_shop_buy("clothing_store")
				get_viewport().set_input_as_handled()
			"buy_electronics":
				_try_shop_buy("electronics_store")
				get_viewport().set_input_as_handled()
			"buy_pets":
				_try_shop_buy("pet_store")
				get_viewport().set_input_as_handled()
			"watch":
				_toggle_cinema_watch(true)
				get_viewport().set_input_as_handled()
			"watch_stop":
				_toggle_cinema_watch(false)
				get_viewport().set_input_as_handled()


func _world_action_near_player() -> String:
	## Pier / ship / far shore / well / shops / cinema — priority order for [E].
	if _player == null or not is_instance_valid(_player):
		return ""
	var p: Vector3 = _player.global_position
	var d_ship := Vector2(p.x - HARBOR_SHIP.x, p.z - HARBOR_SHIP.z).length()
	var d_far := Vector2(p.x - FAR_SHORE.x, p.z - FAR_SHORE.z).length()
	var d_pier := Vector2(p.x - 0.0, p.z - 48.5).length()
	var d_well := Vector2(p.x - VILLAGE_WELL.x, p.z - VILLAGE_WELL.z).length()
	var d_grocery := Vector2(p.x - STORE_GROCERY.x, p.z - STORE_GROCERY.z).length()
	var d_clothing := Vector2(p.x - STORE_CLOTHING.x, p.z - STORE_CLOTHING.z).length()
	var d_electronics := Vector2(p.x - STORE_ELECTRONICS.x, p.z - STORE_ELECTRONICS.z).length()
	var d_pets := Vector2(p.x - STORE_PETS.x, p.z - STORE_PETS.z).length()
	var d_cinema := Vector2(p.x - 26.0, p.z - 14.0).length()
	_at_far_shore = d_far < 9.0
	if _at_far_shore:
		if d_far < 4.5:
			var d_far_ship := Vector2(p.x - (FAR_SHORE.x - 3.5), p.z - (FAR_SHORE.z - 3.0)).length()
			if d_far_ship < 3.6:
				return "return"
			return "build"
		return "return"
	if d_ship < 3.4:
		return "travel"
	if d_pier < 4.2:
		return "fish"
	if d_cinema < 4.5:
		return "watch_stop" if _watching else "watch"
	if d_grocery < 3.6:
		return "buy_grocery"
	if d_clothing < 3.6:
		return "buy_clothing"
	if d_electronics < 3.6:
		return "buy_electronics"
	if d_pets < 3.6:
		return "buy_pets"
	if d_well < 2.8:
		return "well"
	return ""


func _shop_offer_item(store_id: String) -> Dictionary:
	## Current offered shelf item (cycles after each buy).
	if _home == null or not (_home.data is Dictionary):
		return {}
	var stores_v: Variant = _home.data.get("stores")
	if not (stores_v is Dictionary):
		return {}
	var store_v: Variant = (stores_v as Dictionary).get(store_id)
	if not (store_v is Dictionary):
		return {}
	var inv_v: Variant = (store_v as Dictionary).get("inventory")
	if not (inv_v is Array) or (inv_v as Array).is_empty():
		return {}
	var inv: Array = inv_v
	var stocked: Array = []
	for row in inv:
		if row is Dictionary and int(row.get("stock", 0)) > 0:
			stocked.append(row)
	if stocked.is_empty():
		return {}
	var idx := int(_shop_offer.get(store_id, 0)) % stocked.size()
	return stocked[idx]


func _shop_prompt(store_id: String) -> String:
	var item := _shop_offer_item(store_id)
	var shop_name := "Shop"
	if store_id == "grocery":
		shop_name = "The Harvest"
	elif store_id == "clothing_store":
		shop_name = "The Wardrobe"
	elif store_id == "electronics_store":
		shop_name = "The Circuit"
	elif store_id == "pet_store":
		shop_name = "Whiskers & Paws"
	if item.is_empty():
		return "%s — sold out for now" % shop_name
	return "[E] Buy %s · ⨁%d  (stock %d)" % [str(item.get("name", "?")), int(item.get("price", 0)), int(item.get("stock", 0))]


func _try_shop_buy(store_id: String) -> void:
	var item := _shop_offer_item(store_id)
	if item.is_empty():
		_log_convo("Shop", "Nothing left on this shelf.", "system")
		return
	var item_id := str(item.get("id", ""))
	var name := str(item.get("name", item_id))
	var price := int(item.get("price", 0))
	_log_convo("Shop", "Buying %s for ⨁%d…" % [name, price], "system")
	if _home and _home.has_method("store_buy"):
		_home.store_buy(store_id, item_id, 1)
		_shop_offer[store_id] = int(_shop_offer.get(store_id, 0)) + 1
	else:
		_log_convo("Shop", "Hearth offline — purchase not saved.", "system")


func _scan_watch_media() -> Dictionary:
	## Real stills/reels from res://media/watch — empty folder means honest idle.
	var out := {"title": "", "source": "none", "path": ""}
	var dir := DirAccess.open("res://media/watch")
	if dir == null:
		return out
	dir.list_dir_begin()
	var name := dir.get_next()
	while name != "":
		if not dir.current_is_dir():
			var lower := name.to_lower()
			if lower.ends_with(".png") or lower.ends_with(".jpg") or lower.ends_with(".jpeg") or lower.ends_with(".webp") or lower.ends_with(".ogv"):
				if lower == "readme.txt":
					name = dir.get_next()
					continue
				out["path"] = "res://media/watch/%s" % name
				out["title"] = name.get_basename().replace("_", " ")
				out["source"] = "file"
				break
		name = dir.get_next()
	dir.list_dir_end()
	return out


func _toggle_cinema_watch(want_on: bool) -> void:
	var media := _scan_watch_media()
	var title := str(media.get("title", ""))
	var source := str(media.get("source", "none"))
	if want_on:
		if source == "none":
			title = "Evening quiet (no reel seated)"
		_watching = true
		_apply_cinema_screen(true, title, str(media.get("path", "")))
		if _cinema_title:
			_cinema_title.text = "Now showing · %s" % title
		_log_convo("Cinema", "Watch started: %s (source=%s)." % [title, source], "system")
		if _home and _home.has_method("set_media_watch"):
			_home.set_media_watch(true, "cinema", title, source)
	else:
		_watching = false
		_apply_cinema_screen(false, "", "")
		if _cinema_title:
			_cinema_title.text = "Cinema screen · [E] Watch"
		_log_convo("Cinema", "Watch stopped.", "system")
		if _home and _home.has_method("set_media_watch"):
			_home.set_media_watch(false, "cinema", "", "none")


func _apply_cinema_screen(on: bool, title: String, path: String) -> void:
	if _cinema_screen_mat == null:
		return
	if on:
		_cinema_screen_mat.emission_enabled = true
		_cinema_screen_mat.emission = Color(0.35, 0.55, 0.95)
		_cinema_screen_mat.emission_energy_multiplier = 0.9
		_cinema_screen_mat.albedo_color = Color(0.12, 0.16, 0.28)
		if path != "" and (path.ends_with(".png") or path.ends_with(".jpg") or path.ends_with(".jpeg") or path.ends_with(".webp")):
			var tex: Texture2D = load(path) as Texture2D
			if tex:
				_cinema_screen_mat.albedo_texture = tex
				_cinema_screen_mat.albedo_color = Color(1, 1, 1)
	else:
		_cinema_screen_mat.emission_enabled = false
		_cinema_screen_mat.emission_energy_multiplier = 0.0
		_cinema_screen_mat.albedo_texture = null
		_cinema_screen_mat.albedo_color = Color(0.08, 0.08, 0.1)


func _apply_media_state(data: Dictionary) -> void:
	var m: Variant = data.get("media")
	if not (m is Dictionary):
		return
	var watching := bool((m as Dictionary).get("watching", false))
	if watching == _watching:
		return
	# Kernel truth wins when arriving mid-session (e.g. after restart).
	if watching:
		_watching = true
		_apply_cinema_screen(true, str((m as Dictionary).get("title", "")), "")
		if _cinema_title:
			_cinema_title.text = "Now showing · %s" % str((m as Dictionary).get("title", "screen"))
	else:
		_watching = false
		_apply_cinema_screen(false, "", "")
		if _cinema_title:
			_cinema_title.text = "Cinema screen · [E] Watch"


func _sail_to_far_shore() -> void:
	if _player == null:
		return
	_player.global_position = FAR_SHORE + Vector3(0, 0.1, -2.5)
	_player.velocity = Vector3.ZERO
	_at_far_shore = true
	_log_convo("Harbor", "Sailed to far shore. [E] at the plot to build (persists), or at the ship to sail home.", "system")
	if _home and _home.has_method("harbor_action"):
		_home.harbor_action("sail", "", "far_shore")


func _sail_home_to_harbor() -> void:
	if _player == null:
		return
	_player.global_position = HARBOR_SHIP + Vector3(2.2, 0.1, 0.0)
	_player.velocity = Vector3.ZERO
	_at_far_shore = false
	_log_convo("Harbor", "Sailed home to the village harbor.", "system")
	if _home and _home.has_method("harbor_action"):
		_home.harbor_action("sail", "", "harbor")


func _try_fish() -> void:
	if _fish_cd > 0.0:
		_log_convo("Harbor", "Line still settling — wait a moment.", "system")
		return
	_fish_cd = 6.0
	_log_convo("Harbor", "You cast a line…", "system")
	if _home and _home.has_method("harbor_action"):
		_home.harbor_action("fish")
	else:
		_log_convo("Harbor", "Hearth offline — catch not saved.", "system")


func _place_far_shore_build() -> void:
	## Destination builder — Hearth stores builds; Godot syncs greybox props.
	if _home and _home.has_method("harbor_action"):
		_home.harbor_action("build")
		_log_convo("Far shore", "Placing a build — waiting for Hearth to seat it…", "system")
	else:
		_dest_builds += 1
		var n: int = _dest_builds
		var offset := Vector3(float((n % 3) - 1) * 1.6, 0.35, float((n / 3) % 3) * 1.4)
		var pos := FAR_SHORE + Vector3(2.5, 0, 1.0) + offset
		_spawn_shore_build_visual(n, "hut", "Build %d" % n, offset)
		_log_convo("Far shore", "Hearth offline — local build %d only (won't persist)." % n, "system")


func _sync_far_shore_builds(data: Dictionary) -> void:
	var dests_v: Variant = data.get("destinations")
	if not (dests_v is Dictionary):
		return
	var shore_v: Variant = (dests_v as Dictionary).get("far_shore")
	if not (shore_v is Dictionary):
		return
	var builds_v: Variant = (shore_v as Dictionary).get("builds")
	if not (builds_v is Array):
		return
	var builds: Array = builds_v
	if builds.size() == _far_builds_synced and _far_builds_root != null and _far_builds_root.get_child_count() == builds.size():
		return
	if _far_builds_root == null:
		_far_builds_root = Node3D.new()
		_far_builds_root.name = "FarShoreBuilds"
		add_child(_far_builds_root)
	for c in _far_builds_root.get_children():
		c.queue_free()
	_dest_builds = builds.size()
	_far_builds_synced = builds.size()
	for rec in builds:
		if not (rec is Dictionary):
			continue
		var d: Dictionary = rec
		var n := int(d.get("n", 0))
		var kind := str(d.get("kind", "hut"))
		var label := str(d.get("label", "Build"))
		var off_v: Variant = d.get("offset")
		var offset := Vector3.ZERO
		if off_v is Array and (off_v as Array).size() >= 3:
			var a: Array = off_v
			offset = Vector3(float(a[0]), float(a[1]), float(a[2]))
		_spawn_shore_build_visual(n, kind, label, offset)
	var harb_v: Variant = data.get("harbor")
	if harb_v is Dictionary:
		var last_catch := str((harb_v as Dictionary).get("last_catch", ""))
		var catches := int((harb_v as Dictionary).get("catches", 0))
		if catches > _last_seen_catches and _last_seen_catches >= 0 and last_catch != "":
			_log_convo("Harbor", "Caught a %s! (inventory · total %d)" % [last_catch, catches], "system")
		_last_seen_catches = catches


func _spawn_shore_build_visual(n: int, kind: String, label: String, offset: Vector3) -> void:
	if _far_builds_root == null:
		return
	var pos := FAR_SHORE + Vector3(2.5, 0, 1.0) + offset
	var col := Color(0.55, 0.4, 0.28)
	var size := Vector3(1.1, 0.7, 1.1)
	match kind:
		"crates":
			col = Color(0.48, 0.34, 0.2)
			size = Vector3(1.2, 0.9, 1.0)
		"garden_box":
			col = Color(0.35, 0.48, 0.28)
			size = Vector3(1.4, 0.45, 1.4)
		"beacon":
			col = Color(0.7, 0.55, 0.25)
			size = Vector3(0.35, 1.8, 0.35)
		_:
			col = Color(0.55, 0.4, 0.28)
			size = Vector3(1.3, 1.0, 1.3)
	var mi := _make_box_mesh(pos, size, col, true, "FarBuild%d" % n)
	_far_builds_root.add_child(mi)
	var sign := Label3D.new()
	sign.text = label
	sign.font_size = 28
	sign.modulate = Color(0.95, 0.88, 0.55)
	sign.position = pos + Vector3(0, size.y * 0.5 + 0.55, 0)
	sign.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_far_builds_root.add_child(sign)


func _on_squirrel_chatter(line: String) -> void:
	_log_convo("Squirrel", line, "system")


func _open_chat_room() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if _player:
		_player.set("chat_lock", true)
	if talk_input:
		talk_input.grab_focus()
	_log_convo("Hearth", "Chat open — pick who above, type, Enter. Drag text to highlight · Ctrl+C or Copy.", "system")


func _build_pause_menu() -> void:
	_pause_layer = CanvasLayer.new()
	_pause_layer.name = "PauseLayer"
	_pause_layer.layer = 80
	_pause_layer.visible = false
	add_child(_pause_layer)
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0.02, 0.03, 0.04, 0.62)
	_pause_layer.add_child(dim)
	_pause_panel = Panel.new()
	_pause_panel.set_anchors_preset(Control.PRESET_CENTER)
	_pause_panel.offset_left = -160
	_pause_panel.offset_top = -110
	_pause_panel.offset_right = 160
	_pause_panel.offset_bottom = 110
	var pst := StyleBoxFlat.new()
	pst.bg_color = Color(0.08, 0.1, 0.09, 0.95)
	pst.border_color = Color(0.7, 0.78, 0.6, 0.8)
	pst.set_border_width_all(2)
	pst.set_corner_radius_all(8)
	_pause_panel.add_theme_stylebox_override("panel", pst)
	_pause_layer.add_child(_pause_panel)
	var title := Label.new()
	title.text = "Leave Heart Square?"
	title.position = Vector2(36, 18)
	title.add_theme_font_size_override("font_size", 20)
	_pause_panel.add_child(title)
	var resume := Button.new()
	resume.text = "Keep playing"
	resume.position = Vector2(40, 70)
	resume.size = Vector2(240, 36)
	resume.pressed.connect(_close_pause_menu)
	_pause_panel.add_child(resume)
	var leave := Button.new()
	leave.text = "Exit world"
	leave.position = Vector2(40, 120)
	leave.size = Vector2(240, 36)
	leave.pressed.connect(_exit_world)
	_pause_panel.add_child(leave)
	var tip := Label.new()
	tip.text = "Esc also opens this menu"
	tip.position = Vector2(55, 175)
	tip.add_theme_font_size_override("font_size", 12)
	tip.modulate = Color(0.75, 0.8, 0.7)
	_pause_panel.add_child(tip)


func _open_pause_menu() -> void:
	_paused_world = true
	if talk_input and talk_input.has_focus():
		_end_talk()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if _player:
		_player.set("chat_lock", true)
	get_tree().paused = false  # keep UI; we soft-pause look only
	if _pause_layer:
		_pause_layer.visible = true


func _close_pause_menu() -> void:
	_paused_world = false
	if _pause_layer:
		_pause_layer.visible = false
	if _player:
		_player.set("chat_lock", false)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _exit_world() -> void:
	_log_convo("Hearth", "Leaving the world…", "system")
	get_tree().quit()


func _on_want_talk(member_id: String, nice: String) -> void:
	_talking_to = member_id
	_select_talk_target(member_id)
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


func _select_talk_target(member_id: String) -> void:
	if talk_target == null:
		return
	for i in range(talk_target.item_count):
		if str(talk_target.get_item_metadata(i)) == member_id:
			talk_target.select(i)
			return


func _on_talk_target_picked(idx: int) -> void:
	if talk_target == null:
		return
	var mid := str(talk_target.get_item_metadata(idx))
	_talking_to = mid
	var nice := talk_target.get_item_text(idx)
	if talk_input:
		talk_input.placeholder_text = "Mom → %s — Enter sends · Esc ends focus" % nice


func _named_addressee_from_line(line: String) -> String:
	var hay: String = line.strip_edges().to_lower()
	if hay == "" or talk_target == null:
		return ""
	var best_at: int = 1000000
	var best_id: String = ""
	var best_len: int = 0
	for i in range(talk_target.item_count):
		var mid: String = str(talk_target.get_item_metadata(i))
		if mid == "" or mid == "mom":
			continue
		var names: Array[String] = [mid.to_lower(), talk_target.get_item_text(i).strip_edges().to_lower()]
		for needle: String in names:
			if needle.length() < 3:
				continue
			var at: int = 0
			while true:
				var found: int = hay.find(needle, at)
				if found < 0:
					break
				var before_ok: bool = found == 0 or not _is_name_char(hay.unicode_at(found - 1))
				var after_i: int = found + needle.length()
				var after_ok: bool = after_i >= hay.length() or not _is_name_char(hay.unicode_at(after_i))
				if before_ok and after_ok and (found < best_at or (found == best_at and needle.length() > best_len)):
					best_at = found
					best_id = mid
					best_len = needle.length()
				at = found + 1
	return best_id


func _is_name_char(code: int) -> bool:
	return (code >= 97 and code <= 122) or (code >= 48 and code <= 57) or code == 95


func _resolve_talk_target() -> String:
	if _talking_to != "":
		return _talking_to
	if talk_target != null:
		var mid := str(talk_target.get_item_metadata(talk_target.selected))
		if mid != "":
			return mid
	var near := _nearest_talk_target()
	if near != "":
		return near
	return "gemini"


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
	var named := _named_addressee_from_line(said)
	var target := named if named != "" else _resolve_talk_target()
	_talking_to = target
	_select_talk_target(target)
	_speak_mom(said, "mom")
	if _home and _home.has_method("say_as_mom"):
		_home.say_as_mom(target, said)
	_log_convo("Hearth", "Sent to %s — saved in community memory. Nearby may answer too." % target, "system")


func _end_talk() -> void:
	## Leaves the type box — does NOT clear the family chat log.
	_talking_to = ""
	if talk_input:
		talk_input.placeholder_text = "Mom — type anytime · Enter sends · Tab / Open Chat · Esc leaves type box"
		talk_input.release_focus()
	if _player:
		_player.set("chat_lock", false)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _on_companion_talk(companion_id: String, nice: String, _line: String) -> void:
	_on_want_talk(companion_id, nice)
