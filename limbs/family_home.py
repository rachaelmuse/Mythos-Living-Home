#!/usr/bin/env python3
"""Family living home — Gemini limb over the Hearth kernel (D:\\Mythos_Hearth\\living_home.py).

Does not merge identities. Does not auto-start houses. Evidence only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HEARTH = Path(r"D:\Mythos_Hearth")
if str(HEARTH) not in sys.path:
    sys.path.insert(0, str(HEARTH))


def _kernel():
    import living_home  # type: ignore

    return living_home


def snapshot(_: dict | None = None) -> dict[str, Any]:
    k = _kernel()
    snap = k.snapshot()
    snap["mom_plain"] = snap.get("mom_plain") or "Home kernel answered."
    snap["disclosure"] = (
        f"save={snap.get('save_path')} capabilities={snap.get('capability_count')} "
        f"clock={snap.get('clock')}"
    )
    return snap


def health(_: dict | None = None) -> dict[str, Any]:
    return _kernel().health_scan()


def tick(args: dict | None = None) -> dict[str, Any]:
    n = int((args or {}).get("n") or 1)
    return _kernel().tick(n)


def repair(args: dict | None = None) -> dict[str, Any]:
    args = args or {}
    fid = str(args.get("id") or args.get("failure_id") or "")
    if not fid:
        return {"ok": False, "error": "need failure id (from home health)"}
    return _kernel().try_repair(fid, authorized=bool(args.get("authorized", True)))


def phases(_: dict | None = None) -> dict[str, Any]:
    return _kernel().status_phases()


def run_job(goal: str | None = None) -> dict[str, Any]:
    g = (goal or "status").strip().lower()
    if g in {"health", "scan", "home health"}:
        return health()
    if g in {"tick", "life"}:
        return tick({"n": 1})
    if g in {"phases", "phase"}:
        return phases()
    if g.startswith("repair "):
        return repair({"id": g.split(" ", 1)[1].strip()})
    return snapshot()
