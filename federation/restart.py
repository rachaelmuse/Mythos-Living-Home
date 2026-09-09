"""Shutdown / restart integrity. TCP listen is not HTTP identity."""
from __future__ import annotations

import json
import socket
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any

VESPER_PORT = 8740
VESPER_IDENTITY = "http://127.0.0.1:8740/api/identity"
VESPER_LAUNCHER = Path(r"D:\Mythos_Vesper\LAUNCH_VESPER.py")
VESPER_ROOT = Path(r"D:\Mythos_Vesper")


def evaluate_door(probe: dict[str, Any]) -> dict[str, Any]:
    tcp = bool(probe.get("tcp"))
    http_ok = bool(probe.get("http_ok") or probe.get("ok"))
    ident = probe.get("identity") or probe.get("id")
    expected = probe.get("expected_id")
    identity_ok = bool(http_ok and ident and (expected is None or ident == expected))
    if tcp and not http_ok:
        status = "LISTEN_NO_HTTP"
    elif identity_ok:
        status = "HTTP_IDENTITY"
    elif not tcp and not http_ok:
        status = "CLOSED"
    else:
        status = "WRONG_IDENTITY"
    return {
        "id": probe.get("id") or expected,
        "tcp": tcp,
        "http_ok": http_ok,
        "identity": ident,
        "expected_id": expected,
        "identity_ok": identity_ok,
        "status": status,
        "phantom_online": bool(probe.get("claimed_online") and not identity_ok),
    }


def tcp_listening(port: int, host: str = "127.0.0.1", timeout: float = 0.4) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        return sock.connect_ex((host, int(port))) == 0
    finally:
        sock.close()


def listeners_on_port(port: int) -> list[int]:
    """Windows netstat PIDs in LISTENING on this port. Duplicate PIDs mean stacked launchers."""
    try:
        out = subprocess.check_output(
            ["netstat", "-ano", "-p", "tcp"],
            text=True,
            errors="replace",
            timeout=8,
        )
    except Exception:
        return []
    pids: set[int] = set()
    needle = f":{int(port)}"
    for line in out.splitlines():
        if "LISTENING" not in line.upper() and "LISTEN" not in line.upper():
            continue
        if needle not in line:
            continue
        parts = line.split()
        if not parts:
            continue
        try:
            pids.add(int(parts[-1]))
        except ValueError:
            continue
    return sorted(pids)


def probe_vesper_live(timeout_s: float = 6.0) -> dict[str, Any]:
    tcp = tcp_listening(VESPER_PORT)
    pids = listeners_on_port(VESPER_PORT)
    url = VESPER_IDENTITY
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            http = int(resp.status)
            body = json.loads(raw) if raw else {}
            ident = str(body.get("id") or "") if isinstance(body, dict) else ""
            ok = 200 <= http < 300 and ident == "vesper"
            return {
                "ok": ok,
                "http": http,
                "id": ident or None,
                "identity": ident or None,
                "tcp": tcp,
                "url": url,
                "pids": pids,
                "duplicate_launchers": len(pids) > 1,
            }
    except Exception as exc:
        return {
            "ok": False,
            "http": None,
            "id": None,
            "identity": None,
            "tcp": tcp,
            "url": url,
            "error": str(exc),
            "pids": pids,
            "duplicate_launchers": len(pids) > 1,
        }


def stop_vesper_live() -> dict[str, Any]:
    """Kill the single :8740 listener only. Refuse stacked launchers — do not pick a random PID."""
    pids = listeners_on_port(VESPER_PORT)
    if len(pids) > 1:
        return {"ok": False, "error": "stacked_launchers", "pids": pids}
    if not pids:
        return {"ok": True, "pids": [], "note": "already_closed"}
    pid = pids[0]
    try:
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/F"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc), "pids": pids}
    deadline = time.time() + 20
    while time.time() < deadline:
        if not tcp_listening(VESPER_PORT) and not listeners_on_port(VESPER_PORT):
            return {"ok": True, "killed": pid}
        time.sleep(0.4)
    return {"ok": False, "error": "stale_port_owner", "killed": pid, "pids": listeners_on_port(VESPER_PORT)}


def start_vesper_live(*, wait_s: float = 25.0) -> dict[str, Any]:
    existing = listeners_on_port(VESPER_PORT)
    if len(existing) > 1:
        return {"ok": False, "error": "stacked_launchers", "pids": existing}
    if existing:
        return {"ok": False, "error": "already_listening", "pids": existing}
    if not VESPER_LAUNCHER.is_file():
        return {"ok": False, "error": f"missing_launcher:{VESPER_LAUNCHER}"}
    proc = subprocess.Popen(
        ["python", str(VESPER_LAUNCHER)],
        cwd=str(VESPER_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + wait_s
    last: dict[str, Any] = {}
    while time.time() < deadline:
        last = probe_vesper_live()
        if last.get("ok") and last.get("id") == "vesper":
            return {"ok": True, "pid": proc.pid, "door": last}
        time.sleep(0.5)
    return {"ok": bool(last.get("ok")), "pid": proc.pid, "door": last, "error": last.get("error") or "no_http_identity"}
