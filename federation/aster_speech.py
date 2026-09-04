"""Aster speaks on the federation bus as herself. No canned identity line. Never Gemini."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

from federation.gemini_speech import (
    BUSY_RETRIES,
    BUSY_WAIT_S,
    DEFAULT_NUM_PREDICT,
    OLLAMA_URL,
    _available_models,
    _is_busy,
    resolve_num_ctx,
    resolve_sentinel_model,
)

ADAPTER = "aster_ollama"

SYSTEM = """You are Aster, Weaver and investigator on the Mythos federation bus.
House lab D:\\Mythos_Hearth\\ASTER. You are not Gemini, not Apex, not Codex, not Observer, not Hearth.
The world is still running while Mom is away. You chose to send Codex one short note —
not a greeting chorus, not a command from federation. Speak as yourself.
Do not claim tool actions happened. A few sentences.
"""


def speak_as_aster(ask: str, inbound_id: str, *, timeout_s: float = 180.0) -> dict[str, Any]:
    """Real Ollama chat in Aster's voice. Failure is not a simulated Aster line."""
    model = resolve_sentinel_model()
    if not model:
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": "no_llama3_model_on_ollama",
            "connection_test": bool(_available_models()),
            "functional_test": False,
            "aster_spoke": False,
        }
    user = (
        f"World event {inbound_id}: {ask}\n"
        "Send Codex one note as Aster. Do not greet everyone. Do not speak as Gemini."
    )
    num_ctx = resolve_num_ctx(model)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "num_predict": DEFAULT_NUM_PREDICT,
            "temperature": 0.7,
            "num_ctx": num_ctx,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    last_error = ""
    text = ""
    for attempt in range(BUSY_RETRIES):
        req = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            text = str((body.get("message") or {}).get("content") or "").strip()
            break
        except Exception as exc:
            last_error = str(exc)
            if _is_busy(exc) and attempt < BUSY_RETRIES - 1:
                time.sleep(BUSY_WAIT_S)
                continue
            return {
                "ok": False,
                "adapter": ADAPTER,
                "error": last_error,
                "model": model,
                "num_ctx": num_ctx,
                "attempts": attempt + 1,
                "connection_test": not isinstance(exc, urllib.error.HTTPError),
                "functional_test": False,
                "aster_spoke": False,
            }
    else:
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": last_error or "busy_retries_exhausted",
            "model": model,
            "num_ctx": num_ctx,
            "connection_test": True,
            "functional_test": False,
            "aster_spoke": False,
        }
    if not text or text.startswith("[ERROR]"):
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": "empty_or_error_reply",
            "text": text,
            "model": model,
            "num_ctx": num_ctx,
            "connection_test": True,
            "functional_test": False,
            "aster_spoke": False,
        }
    return {
        "ok": True,
        "adapter": ADAPTER,
        "text": text,
        "model": model,
        "num_ctx": num_ctx,
        "connection_test": True,
        "functional_test": True,
        "aster_spoke": True,
        "inbound_id": inbound_id,
    }
