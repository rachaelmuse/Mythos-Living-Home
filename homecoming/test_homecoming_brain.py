"""Homecoming / Covert must ride the live Ollama brain, not force an 8B swap on a full 4060."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "homecoming_sentinel",
    str(Path(__file__).resolve().parent / "HOMECOMING_SENTINEL.py"),
)
hc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hc)


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


def _tags(*names):
    return _Resp({"models": [{"name": n} for n in names]})


def _ps(*rows):
    return _Resp({"models": list(rows)})


def _get(url, **_kwargs):
    if url.endswith("/api/tags"):
        return _get.tags
    if url.endswith("/api/ps"):
        return _get.ps
    raise AssertionError(url)


def test_prefers_warm_llama_over_unloaded_preferred_8b():
    _get.tags = _tags("llama3.1:8b", "llama3.2:3b")
    _get.ps = _ps({"name": "llama3.2:3b", "context_length": 1536})
    with patch.object(hc.requests, "get", side_effect=_get):
        assert hc.resolve_ollama_model() == "llama3.2:3b"


def test_prefers_warm_preferred_8b_when_already_loaded():
    _get.tags = _tags("llama3.1:8b", "llama3.2:3b")
    _get.ps = _ps({"name": "llama3.1:8b", "context_length": 1536})
    with patch.object(hc.requests, "get", side_effect=_get):
        assert hc.resolve_ollama_model() == "llama3.1:8b"


def test_empty_gpu_uses_preferred_if_installed():
    _get.tags = _tags("llama3.1:8b", "llama3.2:3b")
    _get.ps = _ps()
    with patch.object(hc.requests, "get", side_effect=_get):
        assert hc.resolve_ollama_model() == "llama3.1:8b"


def test_num_ctx_reuses_warm_slot():
    _get.tags = _tags("llama3.2:3b")
    _get.ps = _ps({"name": "llama3.2:3b", "context_length": 1536})
    with patch.object(hc.requests, "get", side_effect=_get):
        assert hc.resolve_num_ctx("llama3.2:3b") == 1536


def test_probe_brain_reports_down_when_tags_fail():
    with patch.object(hc.requests, "get", side_effect=hc.requests.exceptions.ConnectionError("down")):
        probe = hc.probe_brain()
    assert probe["ok"] is False
    assert "11434" in probe["error"]
