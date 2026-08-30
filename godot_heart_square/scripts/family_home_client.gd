extends Node
## Talks to Hearth living home (:8790) — one source of truth.
## If Hearth is down, the village still idles locally (no fake tool seating).
## Mom talk uses its own HTTP channel so ticks never drop her words.

signal home_updated(data: Dictionary)

var data: Dictionary = {}
var last_ok := false
var _get: HTTPRequest
var _post: HTTPRequest
var _talk: HTTPRequest
var _tick_ago := 0.0
var _poll_ago := 0.0
var _busy_post := false
var _busy_get := false
var _busy_talk := false
var _talk_queue: Array = []
var hearth_url := "http://127.0.0.1:8790"
var mom_place := "heart_square"


func _ready() -> void:
	print("[Hearth] family_home_client ready, polling ", hearth_url)
	_get = HTTPRequest.new()
	_get.timeout = 25.0
	add_child(_get)
	_get.request_completed.connect(_on_get)
	_post = HTTPRequest.new()
	_post.timeout = 25.0
	add_child(_post)
	_post.request_completed.connect(_on_post)
	_talk = HTTPRequest.new()
	_talk.timeout = 60.0
	add_child(_talk)
	_talk.request_completed.connect(_on_talk)
	refresh()
	set_process(true)


func refresh() -> void:
	if _busy_get:
		return
	_busy_get = true
	_get.request(hearth_url + "/api/home")


func tick_world() -> void:
	if _busy_post:
		return
	_busy_post = true
	var body := JSON.stringify({"n": 1})
	var headers := PackedStringArray(["Content-Type: application/json"])
	_post.request(hearth_url + "/api/home/tick", headers, HTTPClient.METHOD_POST, body)


func record_talk(who: String, line: String) -> void:
	say_as_mom(who, line)


func say_as_mom(with_id: String, line: String) -> void:
	## Never drop Mom's voice — queue behind in-flight talk requests.
	_talk_queue.append({"with": with_id, "line": line, "place": mom_place})
	_drain_talk_queue()


func set_mom_place(place_id: String) -> void:
	if place_id != "":
		mom_place = place_id


func set_media_watch(watching: bool, place: String = "cinema", title: String = "", source: String = "none") -> void:
	## Layer 11 — tell Hearth a village watch started/stopped (evidence, not Mode A launch).
	if _busy_talk:
		_talk_queue.append(
			{
				"_media": true,
				"watching": watching,
				"place": place,
				"title": title,
				"source": source,
			}
		)
		return
	_busy_talk = true
	var body := JSON.stringify(
		{"watching": watching, "place": place, "title": title, "source": source, "who": "mom"}
	)
	var headers := PackedStringArray(["Content-Type: application/json"])
	var err := _talk.request(hearth_url + "/api/home/media", headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		_busy_talk = false
		print("[Hearth] media request failed err=", err)


func _drain_talk_queue() -> void:
	if _busy_talk or _talk_queue.is_empty():
		return
	_busy_talk = true
	var item: Dictionary = _talk_queue.pop_front()
	if bool(item.get("_media", false)):
		var body_m := JSON.stringify(
			{
				"watching": bool(item.get("watching", false)),
				"place": str(item.get("place", "cinema")),
				"title": str(item.get("title", "")),
				"source": str(item.get("source", "none")),
				"who": "mom",
			}
		)
		var headers_m := PackedStringArray(["Content-Type: application/json"])
		var err_m := _talk.request(hearth_url + "/api/home/media", headers_m, HTTPClient.METHOD_POST, body_m)
		if err_m != OK:
			_busy_talk = false
			_talk_queue.push_front(item)
		return
	var body := JSON.stringify(
		{
			"who": "mom",
			"with": str(item.get("with", "gemini")),
			"line": str(item.get("line", "")),
			"place": str(item.get("place", mom_place)),
		}
	)
	var headers := PackedStringArray(["Content-Type: application/json"])
	var err := _talk.request(hearth_url + "/api/home/talk", headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		_busy_talk = false
		_talk_queue.push_front(item)
		print("[Hearth] talk request failed to start err=", err)


func _process(delta: float) -> void:
	_poll_ago += delta
	if _poll_ago >= 2.2:
		_poll_ago = 0.0
		refresh()
	_tick_ago += delta
	# Only tick the village clock when Hearth is linked — offline idle must not pretend to choose.
	if last_ok and _tick_ago >= 6.5:
		_tick_ago = 0.0
		tick_world()
	elif not last_ok and _tick_ago >= 6.5:
		_tick_ago = 0.0


func _on_get(_result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	_busy_get = false
	_ingest(code, body)


func _on_post(_result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	_busy_post = false
	_ingest(code, body)


func _on_talk(_result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	_busy_talk = false
	_ingest(code, body)
	_drain_talk_queue()


func _ingest(code: int, body: PackedByteArray) -> void:
	if code != 200:
		last_ok = false
		return
	var parsed = JSON.parse_string(body.get_string_from_utf8())
	if typeof(parsed) != TYPE_DICTIONARY:
		last_ok = false
		return
	if not parsed.has("family") and not parsed.has("home"):
		refresh()
		return
	data = parsed
	last_ok = true
	var fam_v: Variant = data.get("family", [])
	var fam_n := (fam_v as Array).size() if fam_v is Array else 0
	print("[Hearth] data received. family_count=", fam_n, " last_ok=", last_ok, " utterances=", (data.get("utterances") as Array).size() if data.get("utterances") is Array else 0)
	home_updated.emit(data)


func period() -> String:
	var c = data.get("clock", {})
	return str(c.get("period", "morning"))
