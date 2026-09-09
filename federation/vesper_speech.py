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
_META_HEADER_RE = re.compile(
    r"(?im)^\s*(from (?:my |the )?memories?|per the memories|recalled memories|"
    r"instructions?:|constraints?:|requirements?:|response format:|reply format:)"
)
_SELF_DIRECTIVE_RE = re.compile(
    r"(?im)^\s*(?:we|i)\s+(?:must|need to|should|have to|will|'ll)\s+"
    r"(?:respond|reply|answer|craft|write|make|avoid|keep|ensure|produce|deliver)\b"
)


def _structural_scratchpad(text: str) -> bool:
    """Structure beats phrasing: planning dumps share a shape, not exact words."""
    t = text or ""
    if not t:
        return False
    bullets = len(re.findall(r"(?m)^\s*[-*•]\s+\S", t))
    numbered = len(re.findall(r"(?m)^\s*\d+[\).]\s+\S", t))
    if bullets >= 2 or numbered >= 2:
        return True
    if _SELF_DIRECTIVE_RE.search(t) and (_META_HEADER_RE.search(t) or bullets >= 1 or numbered >= 1):
        return True
    if _META_HEADER_RE.search(t) and len(re.findall(r'"[^"]{12,500}"', t)) >= 1:
        return True
    if re.search(r"(?i)(per the memories|from (?:my |the )?memories|recalled memories)", t) and len(
        re.findall(r'"[^"]{12,500}"', t)
    ) >= 1:
        return True
    if t.count("\n") >= 3 and len(t) > 240:
        return True
    return False


def _is_scratchpad(text: str) -> bool:
    t = text or ""
    if any(m in t for m in _SCRATCHPAD_MARKERS):
        return True
    if _structural_scratchpad(t):
        return True
    return False


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
    # Unquoted fallback: a bare line that opens as Vesper's house voice.
    for raw_line in (text or "").splitlines():
        line = raw_line.strip().strip('"').strip()
        low = line.lower()
        if len(line) < 12:
            continue
        if not (low.startswith("i am vesper") or low.startswith("i'm vesper")):
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
