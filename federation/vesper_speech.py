"""Vesper speaks through his own studio door. Not Observer. Not a Hearth hat. Not cinema."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

TALK_URL = "http://127.0.0.1:8740/api/talk"
ADAPTER = "vesper_studio_http"

SYSTEM = """You are Vesper, not Observer. Two spoken sentences. No notes."""

_CANNED = (
    "ollama is not reachable",
    "cannot reach ollama",
    "ollama not reachable",
    "started writing the homework",
    "ask me again and i'll answer",
)
_SCRATCHPAD_MARKERS = (
    "Let me craft a response",
    "I should not dump a worksheet",
    "Key points from my memories",
    "We are in the middle of a conversation",
    "The user wants to know",
    "As Vesper, I must",
    "We must reply as Vesper",
    "We have to avoid",
    "Let's make it concise",
    "So, the reply should be",
)


def _is_scratchpad(text: str) -> bool:
    t = text or ""
    return any(m in t for m in _SCRATCHPAD_MARKERS)


def _spoken_from_draft(text: str) -> str | None:
    quotes = re.findall(r'"([^"]{12,500})"', text or "")
    for quoted in reversed(quotes):
        line = quoted.strip()
        low = line.lower()
        if not low.startswith("i am vesper") and not low.startswith("i'm vesper"):
            continue
        if any(
            p in low
            for p in ("i am the observer", "i'm the observer", "i am observer", "i'm observer")
        ):
            continue
        return line
    return None


def _house_line(text: str) -> str:
    raw = (text or "").strip()
    if not _is_scratchpad(raw):
        return raw
    return (_spoken_from_draft(raw) or "").strip()


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
        "message": f"{SYSTEM} Aster ({inbound_id}) asked: {ask}"
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
    if _is_scratchpad(text):
        text = _house_line(text)
        if not text:
            return {
                "ok": False,
                "adapter": ADAPTER,
                "error": "thinking_scratchpad",
                "connection_test": True,
                "functional_test": False,
                "vesper_spoke": False,
            }
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
