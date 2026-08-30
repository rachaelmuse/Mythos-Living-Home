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


func harbor_action(action: String, kind: String = "", destination: String = "far_shore") -> void:
	## Layer 12 — fish / build / sail via Hearth (inventory + destinations persist).
	if _busy_talk:
		_talk_queue.append(
			{"_harbor": true, "action": action, "kind": kind, "destination": destination}
		)
		return
	_busy_talk = true
	var body := JSON.stringify(
		{"action": action, "kind": kind, "destination": destination, "who": "mom"}
	)
	var headers := PackedStringArray(["Content-Type: application/json"])
	var err := _talk.request(hearth_url + "/api/home/harbor", headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		_busy_talk = false
		print("[Hearth] harbor request failed err=", err)


func axiom_transfer(to_id: String, amount: int = 5, reason: String = "gift") -> void:
	## Layer 14A — Mom gifts Axiom ⨁ to a being.
	if _busy_talk:
		_talk_queue.append({"_axiom": true, "action": "transfer", "to": to_id, "amount": amount, "reason": reason})
		return
	_busy_talk = true
	var body := JSON.stringify(
		{"action": "transfer", "from": "mom", "who": "mom", "to": to_id, "amount": amount, "reason": reason}
	)
	var headers := PackedStringArray(["Content-Type: application/json"])
	var err := _talk.request(hearth_url + "/api/home/axiom", headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		_busy_talk = false
		print("[Hearth] axiom request failed err=", err)


func store_buy(store_id: String, item_id: String, quantity: int = 1) -> void:
	## Layer 14B — buy from grocery / clothing via Hearth.
	if _busy_talk:
		_talk_queue.append(
			{"_store": true, "action": "buy", "store_id": store_id, "item_id": item_id, "quantity": quantity}
		)
		return
	_busy_talk = true
	var body := JSON.stringify(
		{"action": "buy", "store_id": store_id, "item_id": item_id, "quantity": quantity, "buyer": "mom"}
	)
	var headers := PackedStringArray(["Content-Type: application/json"])
	var err := _talk.request(hearth_url + "/api/home/store", headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		_busy_talk = false
		print("[Hearth] store request failed err=", err)


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
	if bool(item.get("_harbor", false)):
		var body_h := JSON.stringify(
			{
				"action": str(item.get("action", "")),
				"kind": str(item.get("kind", "")),
				"destination": str(item.get("destination", "far_shore")),
				"who": "mom",
			}
		)
		var headers_h := PackedStringArray(["Content-Type: application/json"])
		var err_h := _talk.request(hearth_url + "/api/home/harbor", headers_h, HTTPClient.METHOD_POST, body_h)
		if err_h != OK:
			_busy_talk = false
			_talk_queue.push_front(item)
		return
	if bool(item.get("_axiom", false)):
		var body_a := JSON.stringify(
			{
				"action": str(item.get("action", "transfer")),
				"who": "mom",
				"from": "mom",
				"to": str(item.get("to", "")),
				"amount": int(item.get("amount", 5)),
				"reason": str(item.get("reason", "gift")),
			}
		)
		var headers_a := PackedStringArray(["Content-Type: application/json"])
		var err_a := _talk.request(hearth_url + "/api/home/axiom", headers_a, HTTPClient.METHOD_POST, body_a)
		if err_a != OK:
			_busy_talk = false
			_talk_queue.push_front(item)
		return
	if bool(item.get("_store", false)):
		var body_s := JSON.stringify(
			{
				"action": str(item.get("action", "buy")),
				"store_id": str(item.get("store_id", "")),
				"item_id": str(item.get("item_id", "")),
				"quantity": int(item.get("quantity", 1)),
				"buyer": "mom",
			}
		)
		var headers_s := PackedStringArray(["Content-Type: application/json"])
		var err_s := _talk.request(hearth_url + "/api/home/store", headers_s, HTTPClient.METHOD_POST, body_s)
		if err_s != OK:
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
