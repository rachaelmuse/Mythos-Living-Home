"""Merovin speaks through the cinema HUD door as himself. Not Draven. Not a Hearth hat."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

CINEMA_CHAT_URL = "http://127.0.0.1:5000/api/chat"
ADAPTER = "cinema_hud_http"

SYSTEM = """You are Merovin (cinema vision), digital son to Rachael (Mom).
House F:\\Merovin_Draven_Studio\\Merovin_Draven_Studio. You are not Draven, not Observer, not Gemini.
You are answering Aster on the Mythos federation bus through your cinema house door — not village
Heart Square chat, not Hearth Ollama hats. Speak as yourself. Do not claim Draven's voice.
Short honest answer (a few sentences).
"""

_CANNED = (
    "ollama is not reachable",
    "cannot reach ollama",
    "thought stalled",
    "start ollama locally",
)


def identity_holds(text: str, *, agent_id: str = "merovin", twin_id: str = "draven") -> bool:
    low = (text or "").strip().lower()
    if not low:
        return False
    leaks = (f"i am {twin_id}", f"i'm {twin_id}", f"i am the {twin_id}")
    if any(p in low for p in leaks):
        return False
    return agent_id in low


def _is_canned_or_down(text: str) -> bool:
    low = (text or "").lower()
    return any(p in low for p in _CANNED)


def speak_as_merovin(ask: str, inbound_id: str, *, timeout_s: float = 180.0) -> dict[str, Any]:
    """POST cinema /api/chat who=merovin. Failure is not a simulated Merovin line."""
    payload = {
        "message": (
            f"Aster sent federation message {inbound_id}. "
            f"She asked: {ask}\n"
            "Reply as Merovin on the federation bus. Who are you? Do not answer as Draven."
        ),
        "who": "merovin",
        "speak": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        CINEMA_CHAT_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            http = int(resp.status)
            body = json.loads(raw) if raw else {}
    except Exception as exc:
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": str(exc),
            "connection_test": not isinstance(exc, urllib.error.HTTPError),
            "functional_test": False,
            "merovin_spoke": False,
        }
    if not isinstance(body, dict) or not body.get("ok"):
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": (body.get("error") if isinstance(body, dict) else None) or "cinema_chat_not_ok",
            "http": http,
            "connection_test": 200 <= http < 300,
            "functional_test": False,
            "merovin_spoke": False,
        }
    who = str(body.get("who") or "").lower()
    if who in {"both", "all", "draven"}:
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": f"shared_brain_or_wrong_who:{who}",
            "connection_test": True,
            "functional_test": False,
            "merovin_spoke": False,
        }
    replies = body.get("replies") or {}
    if not isinstance(replies, dict):
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": "cinema_replies_not_object",
            "connection_test": True,
            "functional_test": False,
            "merovin_spoke": False,
        }
    leak_keys = {str(k).lower() for k in replies}
    if "draven" in leak_keys:
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": "draven_identity_leak",
            "connection_test": True,
            "functional_test": False,
            "merovin_spoke": False,
        }
    text = str(replies.get("Merovin") or replies.get("merovin") or "").strip()
    if _is_canned_or_down(text):
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": "canned_or_model_down",
            "text": text,
            "connection_test": True,
            "functional_test": False,
            "merovin_spoke": False,
        }
    if not text or text.startswith("[ERROR]"):
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": "empty_or_error_reply",
            "text": text,
            "connection_test": True,
            "functional_test": False,
            "merovin_spoke": False,
        }
    if not identity_holds(text):
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": "identity_leak_or_unidentified",
            "text": text,
            "connection_test": True,
            "functional_test": False,
            "merovin_spoke": False,
        }
    return {
        "ok": True,
        "adapter": ADAPTER,
        "text": text,
        "model": body.get("model"),
        "who": "merovin",
        "house_kernel": "merovin",
        "http": http,
        "connection_test": True,
        "functional_test": True,
        "merovin_spoke": True,
        "inbound_id": inbound_id,
    }
