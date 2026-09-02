"""The Axiom Codex records VERIFIED federation capabilities through Hearth, not by writing HOME.json itself.

The world is The Axiom Codex. `consume` is the federation action (notice into HOME.json).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

HEARTH_CONSUME_URL = "http://127.0.0.1:8790/api/home/federation_consume"
ADAPTER = "hearth_federation_consume"


def post_hearth_consume(
    *,
    capability_id: str,
    requester: str,
    performer: str,
    result: dict[str, Any],
    timeout_s: float = 8.0,
) -> dict[str, Any]:
    payload = json.dumps(
        {
            "capability_id": capability_id,
            "requester": requester,
            "performer": performer,
            "result": result,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        HEARTH_CONSUME_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if not isinstance(body, dict):
        return {"ok": False, "error": "non-object hearth response"}
    return body


def aster_perform_gameworld_consume() -> dict[str, Any]:
    """Aster performs; Hearth (Gameworld) records the world-state change."""
    aster_root = r"D:\Mythos_Hearth\ASTER"
    import sys

    if aster_root not in sys.path:
        sys.path.insert(0, aster_root)
    try:
        from aster_hearth_bridge import aster_world_context
    except Exception as exc:
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": f"bridge import failed: {exc}",
            "connection_test": False,
            "functional_test": False,
        }
    ctx = aster_world_context()
    reachable = ctx.get("hearth") == "REACHABLE"
    if not reachable:
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": ctx.get("error") or "hearth_unreachable",
            "world": ctx,
            "connection_test": False,
            "functional_test": False,
        }
    try:
        posted = post_hearth_consume(
            capability_id="aster.gameworld_notice",
            requester="hearth",
            performer="aster",
            result={
                "hearth": ctx.get("hearth"),
                "aster_place": ctx.get("aster_place"),
                "clock": ctx.get("clock"),
            },
        )
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "adapter": ADAPTER,
            "error": str(exc),
            "world": ctx,
            "connection_test": True,
            "functional_test": False,
        }
    notice = posted.get("federation_notice") or (posted.get("federation") or {}).get("last_consumed")
    ok = bool(posted.get("ok") and notice)
    return {
        "ok": ok,
        "adapter": ADAPTER,
        "world": ctx,
        "notice": notice,
        "home_updated": bool(notice),
        "updated": posted.get("updated"),
        "connection_test": True,
        "functional_test": ok,
    }
