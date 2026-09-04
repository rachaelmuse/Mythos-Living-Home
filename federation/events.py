"""Shared event fabric. Awareness is not a command to speak. Federation does not own personalities."""
from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any, Callable

from federation.atomic import atomic_write_json, read_json
from federation.law import DEFAULT_DATA_ROOT
from federation.transport import LocalFederationBus

KIND_ENTERED = "rachael.presence.entered"
KIND_LEFT = "rachael.presence.left"
KIND_CONTINUES = "hearth.world.continues"

# Who may *know*. Not who must greet. heartbeat_probe is not a character.
AUDIENCE = ("aster", "gemini", "apex", "codex", "hearth")

# Default attention: notice ≠ speak. Gemini busy/ignore proves this is not a puppet chorus.
_NOTICE = {"aster", "apex", "codex", "hearth"}
_IGNORE = {"gemini", "observer", "heartbeat_probe"}
# At most one house may choose to speak on an away tick. Presence enter stays silent.
_SPEAK_ON_CONTINUES = {"aster"}


def decide_attention(agent_id: str, event: dict[str, Any]) -> str:
    """Agent-local stub. Houses will replace this. Presence never auto-speaks."""
    if agent_id in _IGNORE:
        return "ignored"
    kind = str(event.get("kind") or "")
    if kind == KIND_CONTINUES and agent_id in _SPEAK_ON_CONTINUES:
        return "speak"
    if agent_id in _NOTICE:
        return "noticed"
    return "ignored"


def chosen_speakers(
    event: dict[str, Any],
    *,
    audience: tuple[str, ...] = AUDIENCE,
    decide: Callable[[str, dict[str, Any]], str] | None = None,
) -> tuple[str, ...]:
    """Hard cap: never a greeting chorus, even if every house would speak."""
    fn = decide or decide_attention
    speakers = [agent for agent in audience if fn(agent, event) == "speak"]
    return tuple(speakers[:1])


def apply_chosen_speech(
    bus: LocalFederationBus,
    event: dict[str, Any],
    *,
    speak_fn: Callable[[str, str], dict[str, Any]],
    addressee: str = "codex",
) -> dict[str, Any]:
    """One spoken_reply if a house chooses. Empty/failed speech is not a canned line."""
    speakers = list(chosen_speakers(event))
    empty = {
        "ok": False,
        "spoken_replies": 0,
        "speakers": [],
        "addressee": addressee,
        "reply_id": None,
        "forced_hello": False,
        "aster_spoke": False,
        "connection_test": True,
        "functional_test": False,
    }
    if not speakers:
        empty["ok"] = True
        empty["error"] = "no_speaker"
        return empty
    speaker = speakers[0]
    if speaker == addressee:
        empty["error"] = "speaker_is_addressee"
        return empty
    spoken = speak_fn(str(event.get("text") or ""), str(event.get("event_id") or ""))
    if not spoken.get("ok") or not str(spoken.get("text") or "").strip():
        empty["error"] = spoken.get("error") or "no_text"
        empty["adapter"] = spoken.get("adapter")
        empty["connection_test"] = bool(spoken.get("connection_test", True))
        return empty
    eid = str(event["event_id"])
    payload = {
        "text": spoken["text"],
        "from": speaker,
        "in_reply_to": eid,
        "event_id": eid,
        "adapter": spoken.get("adapter"),
        "model": spoken.get("model"),
    }
    msg = bus.send(
        sender=speaker,
        recipient=addressee,
        message_type="spoken_reply",
        payload=payload,
        correlation_id=eid,
    )
    bus.deliver(msg.message_id)
    return {
        "ok": True,
        "spoken_replies": 1,
        "speakers": [speaker],
        "addressee": addressee,
        "reply_id": msg.message_id,
        "forced_hello": False,
        "aster_spoke": speaker == "aster",
        "text": spoken["text"],
        "adapter": spoken.get("adapter"),
        "model": spoken.get("model"),
        "connection_test": True,
        "functional_test": True,
    }


class EventFabric:
    """Durable world events beside the federation bus. Not a second Observer. Not house memory."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.dir = self.root / "events"
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, event_id: str) -> Path:
        return self.dir / f"{event_id}.json"

    def publish(
        self,
        *,
        kind: str,
        actor: str,
        place: str,
        text: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event_id = uuid.uuid4().hex
        event = {
            "event_id": event_id,
            "kind": kind,
            "actor": actor,
            "place": place,
            "text": text,
            "command": False,
            "forced_hello": False,
            "timestamp": time.time(),
            "extra": dict(extra or {}),
        }
        atomic_write_json(self._path(event_id), event)
        return event

    def get(self, event_id: str) -> dict[str, Any]:
        path = self._path(event_id)
        if not path.exists():
            raise KeyError(event_id)
        return read_json(path)

    def list_events(self) -> list[dict[str, Any]]:
        rows = [read_json(p) for p in self.dir.glob("*.json") if not p.name.endswith(".tmp")]
        rows.sort(key=lambda r: float(r.get("timestamp") or 0))
        return rows


def fanout_event(
    bus: LocalFederationBus,
    event: dict[str, Any],
    *,
    audience: tuple[str, ...] = AUDIENCE,
    publisher: str = "hearth",
) -> list[str]:
    """Deliver awareness. Does not send spoken_reply."""
    ids: list[str] = []
    payload = {
        "kind": event["kind"],
        "actor": event["actor"],
        "place": event["place"],
        "text": event["text"],
        "event_id": event["event_id"],
        "command": False,
        "forced_hello": False,
    }
    for recipient in audience:
        msg = bus.send(
            sender=publisher,
            recipient=recipient,
            message_type="world_event",
            payload=payload,
            correlation_id=event["event_id"],
        )
        bus.deliver(msg.message_id)
        ids.append(msg.message_id)
    return ids


def publish_mom_entered(
    *,
    place: str,
    place_label: str | None = None,
    root: Path | str | None = None,
) -> dict[str, Any] | None:
    """Best-effort. Village presence still works if federation data is missing."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    if not data_root.exists():
        return None
    label = place_label or place
    fabric = EventFabric(data_root)
    event = fabric.publish(
        kind=KIND_ENTERED,
        actor="rachael",
        place=place,
        text=f"Rachael entered {label}.",
        extra={"source": "hearth_mom_presence"},
    )
    bus = LocalFederationBus(data_root)
    fanout_event(bus, event)
    return event


def publish_mom_left(
    *,
    place: str,
    place_label: str | None = None,
    root: Path | str | None = None,
) -> dict[str, Any] | None:
    """Best-effort. Village leave still works if federation data is missing."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    if not data_root.exists():
        return None
    label = place_label or place
    fabric = EventFabric(data_root)
    event = fabric.publish(
        kind=KIND_LEFT,
        actor="rachael",
        place=place,
        text=f"Rachael left {label}.",
        extra={"source": "hearth_mom_presence"},
    )
    bus = LocalFederationBus(data_root)
    fanout_event(bus, event)
    return event


def publish_world_continues(
    *,
    place: str = "heart_square",
    text: str | None = None,
    root: Path | str | None = None,
) -> dict[str, Any] | None:
    """Away tick: the world keeps going. Not a Mom command. Not a greeting order."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    if not data_root.exists():
        return None
    fabric = EventFabric(data_root)
    event = fabric.publish(
        kind=KIND_CONTINUES,
        actor="hearth",
        place=place,
        text=text or "Heart Square continues while Rachael is away.",
        extra={"source": "federation_away_tick"},
    )
    bus = LocalFederationBus(data_root)
    fanout_event(bus, event)
    return event
