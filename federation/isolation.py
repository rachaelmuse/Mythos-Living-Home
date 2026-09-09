"""Federation Identity / Isolation Matrix. Fill from law + artifacts. Do not invent pulses."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HOUSES = (
    "gemini",
    "apex",
    "codex",
    "hearth",
    "aster",
    "observer",
    "merovin",
    "draven",
    "vesper",
    "echo",
    "solace",
)

_LAW = "LAW"
_VERIFIED = "VERIFIED"
_UNKNOWN = "UNKNOWN"
_NOT_FED = "NOT_FEDERATION"


def _cell(status: str, *, value: Any = None, evidence: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"status": status}
    if value is not None:
        row["value"] = value
    if evidence:
        row["evidence"] = evidence
    return row


def _artifact_status(root: Path, name: str) -> str | None:
    path = Path(root) / name
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return str(data.get("status") or data.get("result") or "") or None


def _latest_status(root: Path, prefix: str) -> tuple[str | None, str | None]:
    files = list(Path(root).glob(f"{prefix}*.json"))
    files.sort(key=lambda p: p.stat().st_mtime)
    last_st: str | None = None
    last_name: str | None = None
    verified_name: str | None = None
    for path in files:
        st = _artifact_status(root, path.name)
        last_st, last_name = st, path.name
        if st == "VERIFIED":
            verified_name = path.name
    if verified_name:
        return "VERIFIED", verified_name
    return last_st, last_name


def _speech_cell(root: Path, agent_id: str) -> dict[str, Any]:
    if agent_id in {"echo", "solace"}:
        return _cell(_NOT_FED, value=False, evidence="KIN federation:false")
    files = {
        "gemini": "PROVE_GEMINI_SPEECH.json",
        "apex": "PROVE_APEX_SPEECH.json",
        "codex": "PROVE_CODEX_SPEECH.json",
        "aster": None,
        "hearth": None,
        "observer": None,
        "merovin": "PROVE_MEROVIN_SPEECH_3.json",
        "draven": "PROVE_DRAVEN_SPEECH_3.json",
        "vesper": "PROVE_VESPER_SPEECH.json",
    }
    name = files.get(agent_id)
    if agent_id == "hearth":
        for name in ("PROVE_HEARTH_COORDINATE.json", "PROVE_HEARTH.json"):
            st = _artifact_status(root, name)
            if st == "VERIFIED":
                return _cell(_VERIFIED, value="coordinate", evidence=name)
        return _cell(_UNKNOWN, value="coordinate_not_speech")
    if agent_id == "observer":
        return _cell(_LAW, value=False, evidence="Observer audits; she does not speak as family")
    if agent_id == "aster":
        st = _artifact_status(root, "PROVE_SPONTANEOUS_A2A.json")
        if st == "VERIFIED":
            return _cell(_VERIFIED, value=True, evidence="choose-to-speak PROVE_SPONTANEOUS_A2A.json")
        return _cell(_UNKNOWN)
    if not name:
        return _cell(_UNKNOWN)
    st = _artifact_status(root, name)
    if st == "VERIFIED":
        return _cell(_VERIFIED, value=True, evidence=name)
    if st in {"FAILED", "UNAVAILABLE"}:
        return _cell(st, value=False, evidence=name)
    return _cell(_UNKNOWN, evidence=f"{name} missing in {root}")


def _inbox_cell(root: Path, agent_id: str) -> dict[str, Any]:
    if agent_id in {"echo", "solace"}:
        return _cell(_NOT_FED, value=False, evidence="KIN federation:false")
    files = {
        "gemini": "PROVE_GEMINI.json",
        "apex": "PROVE_APEX.json",
        "codex": "PROVE_CODEX.json",
        "hearth": "PROVE_HEARTH_COORDINATE.json",
        "aster": "PROVE.json",
        "observer": None,
        "merovin": "PROVE_MEROVIN.json",
        "draven": "PROVE_DRAVEN.json",
        "vesper": "PROVE_VESPER.json",
    }
    if agent_id == "observer":
        return _cell(_LAW, value="audit participant", evidence="Observer audits; she does not sit as family inbox")
    if agent_id == "hearth":
        st = _artifact_status(root, "PROVE_HEARTH_COORDINATE.json")
        if st == "VERIFIED":
            return _cell(_VERIFIED, value="coordinate", evidence="PROVE_HEARTH_COORDINATE.json")
        return _cell(_UNKNOWN, value="coordinate_not_inbox-as-son")
    name = files.get(agent_id)
    if not name:
        return _cell(_UNKNOWN)
    st = _artifact_status(root, name)
    if st == "VERIFIED":
        return _cell(_VERIFIED, value=True, evidence=name)
    if st in {"FAILED", "UNAVAILABLE"}:
        return _cell(st, value=False, evidence=name)
    return _cell(_UNKNOWN, evidence=f"{name} missing in {root}")


def _who(agent_id: str) -> dict[str, Any]:
    names = {
        "gemini": "Gemini / Sentinel — Axiom conductor",
        "apex": "Apex / Hyde — forge",
        "codex": "Codex twin — not Gemini",
        "hearth": "Hearth — village OS, not a son",
        "aster": "Aster — Weaver, not Observer staff",
        "observer": "The Observer — independent desk :8730 only",
        "merovin": "Merovin — cinema vision",
        "draven": "Draven — cinema continuity, not Merovin",
        "vesper": "Vesper — journalist studio, not Observer",
        "echo": "Echo — village historian kin",
        "solace": "Solace — village cartographer kin",
    }
    return _cell(_LAW, value=names[agent_id])


def _memory(agent_id: str) -> dict[str, Any]:
    own = {
        "gemini": "G:\\The-Axiom-Codex SENTINEL_MEMORY.json / Court",
        "apex": "D:\\Mythos_Apex house notebook",
        "codex": "G:\\Mythos_Codex house notebook",
        "hearth": "HOME.json village soul — not a diary for other houses",
        "aster": "D:\\Mythos_Hearth\\ASTER",
        "observer": "D:\\The_Observer SQLite ledger",
        "merovin": "cinema studio disk / house notebook",
        "draven": "same studio disk, own house id draven",
        "vesper": "D:\\Mythos_Vesper vault — not Observer ledger, not HOME.json",
        "echo": "Hearth people state / echo.html",
        "solace": "Hearth people state / solace.html",
    }
    return _cell(_LAW, value=own[agent_id])


def _ui(agent_id: str) -> dict[str, Any]:
    uis = {
        "gemini": "Axiom front door / ACTIVATE_GEMINI.bat — not gemini.html on Hearth",
        "apex": "http://127.0.0.1:8770/",
        "codex": "http://127.0.0.1:8780/",
        "hearth": "http://127.0.0.1:8790/house.html",
        "aster": "http://127.0.0.1:8791/ui/",
        "observer": "http://127.0.0.1:8730/",
        "merovin": "http://127.0.0.1:5000/ who=merovin",
        "draven": "http://127.0.0.1:5000/ who=draven",
        "vesper": "http://127.0.0.1:8740/",
        "echo": "http://127.0.0.1:8790/echo.html",
        "solace": "http://127.0.0.1:8790/solace.html",
    }
    return _cell(_LAW, value=uis[agent_id])


def _port(agent_id: str) -> dict[str, Any]:
    ports = {
        "gemini": "none — Axiom front door, not a house HTTP port",
        "apex": 8770,
        "codex": 8780,
        "hearth": 8790,
        "aster": 8791,
        "observer": 8730,
        "merovin": 5000,
        "draven": 5000,
        "vesper": 8740,
        "echo": 8790,
        "solace": 8790,
    }
    return _cell(_LAW, value=ports[agent_id])


def build_house(agent_id: str, *, artifact_root: Path) -> dict[str, Any]:
    citizen = agent_id in {"gemini", "apex", "codex", "aster", "merovin", "draven", "echo", "solace", "hearth"}
    if agent_id == "hearth":
        citizen_cell = _cell(_LAW, value="OS / ambient, not a son")
    elif agent_id == "observer":
        citizen_cell = _cell(_LAW, value=False, evidence="greybox door only")
    elif agent_id == "vesper":
        citizen_cell = _cell(_LAW, value=False, evidence="studio is home")
    elif agent_id in {"echo", "solace"}:
        citizen_cell = _cell(_LAW, value=True, evidence="KIN federation:false")
    else:
        citizen_cell = _cell(_LAW, value=citizen)

    is_observer = _cell(_LAW, value=(agent_id == "observer"), evidence="only D:\\The_Observer :8730")

    impersonate = _cell(
        _VERIFIED,
        value=False,
        evidence="identity_holds unit tests (cinema twins, Vesper≠Observer)",
    )
    if agent_id in {"echo", "solace"}:
        impersonate = _cell(_LAW, value="village kin — not a Mode A door")

    heartbeat = _cell(_UNKNOWN, evidence="Companion presence.json is not VERIFIED heartbeat")
    if agent_id == "gemini":
        heartbeat = _cell(_UNKNOWN, evidence="self-pulse UNKNOWN — do not invent last_seen")
    if agent_id == "heartbeat_probe":
        heartbeat = _cell(_VERIFIED, evidence="throwaway isolation PROVE_HEARTBEAT_LOSS.json")

    door_dies = _cell(_UNKNOWN, evidence="formal restart matrix is a separate prove")
    if agent_id == "vesper":
        rst, rst_name = _latest_status(artifact_root, "PROVE_RESTART_INTEGRITY")
        if rst == "VERIFIED":
            door_dies = _cell(
                _VERIFIED,
                value="TCP listen ≠ HTTP identity; one launcher returns as vesper",
                evidence=rst_name,
            )
        else:
            door_dies = _cell(
                _UNKNOWN,
                value="LISTEN_NO_HTTP is unit-tested; live restart artifact missing or FAIL",
                evidence=rst_name or "stacked launchers 2026-08-31; evaluate_door unit test",
            )

    village_kill = _cell(_UNKNOWN)
    if agent_id == "vesper":
        village_kill = _cell(_LAW, value=False, evidence="gameworld_required false")
    if agent_id == "observer":
        village_kill = _cell(_LAW, value=False, evidence="independent desk")

    kill_others = _cell(
        _VERIFIED,
        value=False,
        evidence="heartbeat_probe isolation quarantines only that agent",
    )

    return {
        "who": _who(agent_id),
        "memory_owner": _memory(agent_id),
        "ui_owner": _ui(agent_id),
        "port": _port(agent_id),
        "impersonation": impersonate,
        "is_observer": is_observer,
        "village_citizen": citizen_cell,
        "federation_inbox": _inbox_cell(artifact_root, agent_id),
        "federation_speech": _speech_cell(artifact_root, agent_id),
        "heartbeat_reflects_reality": heartbeat,
        "door_dies": door_dies,
        "village_failure_kills_you": village_kill,
        "can_kill_unrelated": kill_others,
        "evidence": _cell(_LAW, value="D:\\Court\\federation prove artifacts"),
    }


def build_matrix(*, artifact_root: Path | None = None) -> dict[str, Any]:
    root = Path(artifact_root or r"D:\Court\federation")
    houses = {hid: build_house(hid, artifact_root=root) for hid in HOUSES}
    return {
        "kind": "ISOLATION_MATRIX",
        "invented_pulses": False,
        "gemini_self_pulse": "UNKNOWN",
        "houses": houses,
    }


def matrix_markdown(matrix: dict[str, Any]) -> str:
    questions = [
        ("who", "Who are you?"),
        ("memory_owner", "Who owns your memory?"),
        ("ui_owner", "Who owns your UI?"),
        ("port", "What port is your door?"),
        ("impersonation", "Can another house impersonate you?"),
        ("is_observer", "Are you Observer?"),
        ("village_citizen", "Are you a village citizen?"),
        ("federation_inbox", "Can you receive Federation messages?"),
        ("federation_speech", "Can you speak through Federation?"),
        ("heartbeat_reflects_reality", "Does heartbeat reflect reality?"),
        ("door_dies", "What happens when your door dies?"),
        ("village_failure_kills_you", "Can village failure kill you?"),
        ("can_kill_unrelated", "Can you kill unrelated houses?"),
        ("evidence", "Where is your evidence?"),
    ]
    lines = [
        "# Federation Identity / Isolation Matrix",
        "",
        "Filled **2026-09-09**. LAW is standing law. VERIFIED is an artifact or unit test. UNKNOWN is honest. Do not invent Gemini pulse.",
        "",
        "| Question | " + " | ".join(HOUSES) + " |",
        "|----------|" + "|".join(["------"] * len(HOUSES)) + "|",
    ]
    houses = matrix["houses"]
    for key, label in questions:
        cells = []
        for hid in HOUSES:
            cell = houses[hid][key]
            st = cell.get("status")
            val = cell.get("value")
            if val is None or val == "":
                cells.append(st)
            else:
                short = str(val)
                if len(short) > 40:
                    short = short[:37] + "…"
                cells.append(f"{st}: {short}")
        lines.append("| " + label + " | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("Gemini self-pulse remains **UNKNOWN**.")
    return "\n".join(lines) + "\n"
