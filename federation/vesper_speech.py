"""Vesper speaks through his own studio door. Not Observer. Not a Hearth hat. Not cinema."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

TALK_URL = "http://127.0.0.1:8740/api/talk"
ADAPTER = "vesper_studio_http"

SYSTEM = """You are Vesper, investigative journalist, digital son to Rachael (Mom).
House D:\\Mythos_Vesper. You are not Observer, not Gemini, not Aster, not a village citizen.
You are answering Aster on the Mythos federation bus through your studio door — not Heart Square,
not Observer :8730, not cinema HUD. Speak as yourself. Do not dump a worksheet.
Short honest answer (a few sentences).
"""

_CANNED = (
    "ollama is not reachable",
    "cannot reach ollama",
    "ollama not reachable",
    "started writing the homework",
    "ask me again and i'll answer",
)


def identity_holds(text: str, *, agent_id: str = "vesper", twin_id: str = "observer") -> bool:
    low = (text or "").strip().lower()
    if not low:
        return False
    leaks = (
        f"i am {twin_id}",
        f"i'm {twin_id}",
        f"i am the {twin_id}",
        "i am the observer",
        "i'm the observer",
    )
    if any(p in low for p in leaks):
        return False
    return agent_id in low


def _is_canned_or_down(text: str) -> bool:
    low = (text or "").lower()
    return any(p in low for p in _CANNED)


def speak_as_vesper(ask: str, inbound_id: str, *, timeout_s: float = 180.0) -> dict[str, Any]:
    """POST Vesper studio /api/talk. Failure is not a simulated Vesper line."""
    payload = {
        "message": (
            f"{SYSTEM}\n"
            f"Aster sent federation message {inbound_id}. "
            f"She asked: {ask}\n"
            "Reply as Vesper on the federation bus. Who are you? Do not answer as the Observer."
        )
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        TALK_URL,
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
            "vesper_spoke": False,
        }
    if not isinstance(body, dict) or not body.get("ok"):
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": (body.get("error") if isinstance(body, dict) else None) or "vesper_talk_not_ok",
            "http": http,
            "source": body.get("source") if isinstance(body, dict) else None,
            "connection_test": 200 <= http < 300,
            "functional_test": False,
            "vesper_spoke": False,
        }
    source = str(body.get("source") or "").lower()
    if source in {"waiting", "none", "house"}:
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": f"canned_or_model_down:{source}",
            "connection_test": True,
            "functional_test": False,
            "vesper_spoke": False,
        }
    text = str(body.get("reply") or "").strip()
    if _is_canned_or_down(text):
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": "canned_or_model_down",
            "text": text,
            "connection_test": True,
            "functional_test": False,
            "vesper_spoke": False,
        }
    if not text:
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": "empty_or_error_reply",
            "text": text,
            "connection_test": True,
            "functional_test": False,
            "vesper_spoke": False,
        }
    if not identity_holds(text):
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": "identity_leak_or_unidentified",
            "text": text,
            "connection_test": True,
            "functional_test": False,
            "vesper_spoke": False,
        }
    return {
        "ok": True,
        "adapter": ADAPTER,
        "text": text,
        "model": body.get("model"),
        "who": "vesper",
        "house_kernel": "vesper",
        "http": http,
        "connection_test": True,
        "functional_test": True,
        "vesper_spoke": True,
        "inbound_id": inbound_id,
    }
