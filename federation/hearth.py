"""Hearth coordinates on the federation bus as village OS. Not Aster snapshot. Not a son."""
from __future__ import annotations

import json
import urllib.request
from typing import Any

HEARTH_PORT = 8790
HEARTH_HOME_URL = "http://127.0.0.1:8790/api/home"
ADAPTER = "hearth_home_http"


def _family_ids(body: dict[str, Any]) -> list[str]:
    raw = body.get("family") or body.get("core_ids") or []
    ids: list[str] = []
    if isinstance(raw, list):
        for row in raw:
            if isinstance(row, dict) and row.get("id"):
                ids.append(str(row["id"]))
            elif isinstance(row, str) and row.strip():
                ids.append(row.strip())
    extra = body.get("core_ids")
    if isinstance(extra, list):
        for item in extra:
            s = str(item)
            if s and s not in ids:
                ids.append(s)
    return ids


def probe_hearth_door(timeout_s: float = 8.0) -> dict[str, Any]:
    """Live GET /api/home. Snapshot-read is Aster's cap; this is Hearth's own door."""
    try:
        with urllib.request.urlopen(HEARTH_HOME_URL, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            http = int(resp.status)
            body = json.loads(raw) if raw else {}
            if not isinstance(body, dict):
                body = {}
            ids = _family_ids(body)
            clock = body.get("clock") if isinstance(body.get("clock"), dict) else None
            ok = 200 <= http < 300 and bool(ids)
            return {
                "ok": ok,
                "http": http,
                "id": "hearth" if ok else None,
                "url": HEARTH_HOME_URL,
                "family_ids": ids,
                "clock": clock,
                "town_leader": body.get("town_leader"),
            }
    except Exception as exc:
        return {
            "ok": False,
            "http": None,
            "id": None,
            "url": HEARTH_HOME_URL,
            "error": str(exc),
        }


def coordinate_as_hearth(ask: str, inbound_id: str, *, timeout_s: float = 8.0) -> dict[str, Any]:
    """Hearth answers with live kernel facts. Failure is not a fake village."""
    door = probe_hearth_door(timeout_s=timeout_s)
    if not door.get("ok"):
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": door.get("error") or "hearth_home_unreachable_or_empty",
            "door": door,
            "connection_test": bool(door.get("http")),
            "functional_test": False,
            "hearth_coordinated": False,
        }
    return {
        "ok": True,
        "adapter": ADAPTER,
        "family_ids": door.get("family_ids") or [],
        "clock": door.get("clock"),
        "town_leader": door.get("town_leader"),
        "ask": ask,
        "inbound_id": inbound_id,
        "connection_test": True,
        "functional_test": True,
        "hearth_coordinated": True,
    }
