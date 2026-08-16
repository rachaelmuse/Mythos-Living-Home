extends Node
## Talks to Hearth living home (:8790) — one source of truth.
## If Hearth is down, the village still idles locally (no fake tool seating).

signal home_updated(data: Dictionary)

var data: Dictionary = {}
var last_ok := false
var _get: HTTPRequest
var _post: HTTPRequest
var _tick_ago := 0.0
var _poll_ago := 0.0
var _busy_post := false
var _busy_get := false
var hearth_url := "http://127.0.0.1:8790"


func _ready() -> void:
	_get = HTTPRequest.new()
	_get.timeout = 15.0
	add_child(_get)
	_get.request_completed.connect(_on_get)
	_post = HTTPRequest.new()
	_post.timeout = 15.0
	add_child(_post)
	_post.request_completed.connect(_on_post)
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
	if _busy_post:
		return
	_busy_post = true
	var body := JSON.stringify({"who": "mom", "with": with_id, "line": line})
	var headers := PackedStringArray(["Content-Type: application/json"])
	_post.request(hearth_url + "/api/home/talk", headers, HTTPClient.METHOD_POST, body)


func _process(delta: float) -> void:
	_poll_ago += delta
	if _poll_ago >= 2.2:
		_poll_ago = 0.0
		refresh()
	_tick_ago += delta
	if _tick_ago >= 6.5:
		_tick_ago = 0.0
		if last_ok:
			tick_world()


func _on_get(_result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	_busy_get = false
	_ingest(code, body)


func _on_post(_result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	_busy_post = false
	_ingest(code, body)


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
	home_updated.emit(data)


func period() -> String:
	var c = data.get("clock", {})
	return str(c.get("period", "morning"))
