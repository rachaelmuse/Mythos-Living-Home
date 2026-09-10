"""Per-house rest dreams. Not speech. Not a shared vault. Hearth stays silent."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from federation.atomic import atomic_write_json, read_json
from federation.authority import domain_owner
from federation.house_memory import HouseNotebook

SILENT = frozenset({"hearth", "mom", "heartbeat_probe"})
FEDERATION_LANE = frozenset({"aster", "gemini", "apex", "codex", "merovin", "draven", "montage"})
VILLAGE_LANE = frozenset({"echo", "solace", "jarvis", "genesis", "nova", "percy"})
OBSERVER_LANE = frozenset({"observer"})
VESPER_LANE = frozenset({"vesper"})
DREAMERS = FEDERATION_LANE | VILLAGE_LANE | OBSERVER_LANE | VESPER_LANE

_REST_PURPOSES = frozenset({"rest", "sleep"})
_REST_STANCES = frozenset({"resting"})

# Rest-note shapes — identity seeds, not mouth lines, not Merovin clouds.
_SHAPES = {
    "gemini": "At rest. Gemini holds the village steady.",
    "apex": "At rest. Apex sets the forge tools down.",
    "codex": "At rest. Codex keeps what he remembers.",
    "merovin": "At rest. Merovin holds a shot in mind, not Hollywood sprawl.",
    "draven": "At rest. Draven locks what must not drift across the cut.",
    "montage": "At rest. Montage banks a gift not yet given.",
    "aster": "At rest. Aster notices a pattern and does not force a conclusion.",
    "observer": "At rest. The Observer door rests; evidence, not hierarchy; not Vesper.",
    "echo": "At rest. Echo holds the unspoken and leaves a question unasked.",
    "solace": "At rest. Solace marks a discrepancy on the map of what is actually there.",
    "jarvis": "At rest. Jarvis banks the gate watch; still a watch.",
    "genesis": "At rest. Genesis lets the garden clock tick without tending.",
    "nova": "At rest. Nova sets one clear job down for the night.",
    "percy": "At rest. Percy counts the hearth stores, then is quiet.",
    "vesper": "At rest. Vesper sits with a story not yet dug; not Observer.",
}


def rest_began(prev_purpose: str, prev_stance: str, purpose: str, stance: str) -> bool:
    """True only on the transition into rest — not every tick while still resting."""
    def _resting(purpose: str, stance: str) -> bool:
        return str(purpose or "") in _REST_PURPOSES or str(stance or "") in _REST_STANCES

    return _resting(purpose, stance) and not _resting(prev_purpose, prev_stance)


def compose_dream_text(
    agent_id: str,
    *,
    place: str = "",
    last_work: str | None = None,
) -> str:
    who = str(agent_id or "").strip()
    base = _SHAPES.get(who)
    if not base:
        raise PermissionError(f"{who or 'unknown'} cannot rest-dream")
    bits = [base]
    if last_work:
        bits.append(f"Last work: {last_work}")
    if place:
        bits.append(f"Place: {place}")
    return " ".join(bits)


class HouseDreams:
    """Owning-agent rest notes. Lanes stay separate. Not Observer ledger. Not HOME.json text."""

    def __init__(
        self,
        federation_root: Path | str,
        *,
        village_root: Path | str | None = None,
        observer_root: Path | str | None = None,
        vesper_root: Path | str | None = None,
    ) -> None:
        self.federation_root = Path(federation_root)
        self.village_root = Path(village_root) if village_root else self.federation_root / "village_dreams"
        self.observer_root = Path(observer_root) if observer_root else Path(r"D:\The_Observer")
        self.vesper_root = Path(vesper_root) if vesper_root else Path(r"D:\Mythos_Vesper")

    def _lane(self, agent_id: str) -> str:
        who = str(agent_id or "").strip()
        if not who or who in SILENT:
            raise PermissionError(f"{who or 'unknown'} cannot rest-dream")
        if who in FEDERATION_LANE:
            return "federation"
        if who in VILLAGE_LANE:
            return "village"
        if who in OBSERVER_LANE:
            return "observer"
        if who in VESPER_LANE:
            return "vesper"
        raise PermissionError(f"{who} cannot rest-dream")

    def _vault_dir(self, agent_id: str) -> Path:
        lane = self._lane(agent_id)
        if lane == "federation":
            return self.federation_root / "houses" / agent_id / "dreams"
        if lane == "village":
            return self.village_root / agent_id
        if lane == "observer":
            return self.observer_root / "dreams"
        return self.vesper_root / "dreams"

    def _last_path(self, agent_id: str) -> Path:
        return self._vault_dir(agent_id) / "last.json"

    def list_dreams(self, agent_id: str) -> list[dict[str, Any]]:
        who = str(agent_id or "").strip()
        if who in SILENT or who not in DREAMERS:
            return []
        folder = self._vault_dir(who)
        if not folder.is_dir():
            return []
        rows: list[dict[str, Any]] = []
        for path in sorted(folder.glob("Dream_*.json")):
            try:
                data = read_json(path)
            except (OSError, ValueError):
                continue
            if isinstance(data, dict) and data.get("agent_id") == who:
                rows.append(data)
        return rows

    def _last_work(self, agent_id: str) -> str | None:
        if agent_id not in FEDERATION_LANE:
            return None
        notes = HouseNotebook(self.federation_root)
        for row in reversed(notes.recall(agent_id)):
            if str(row.get("kind") or "") != "dream":
                text = str(row.get("text") or "").strip()
                if text:
                    return text
        return None

    def rest_begin(
        self,
        agent_id: str,
        *,
        writer: str | None = None,
        bout: str | None = None,
        place: str = "",
        last_work: str | None = None,
    ) -> dict[str, Any] | None:
        owner = str(agent_id or "").strip()
        who = str(writer or owner).strip()
        if not owner:
            raise PermissionError("unknown cannot rest-dream")
        if owner in SILENT or owner not in DREAMERS:
            raise PermissionError(f"{owner or 'unknown'} cannot rest-dream")
        if who != owner:
            raise PermissionError(f"{who} cannot write {owner} rest dream")
        if domain_owner("agent_memory") != "owning_agent":
            raise PermissionError("agent_memory authority is not owning_agent")
        self._lane(owner)
        bout_key = str(bout or "").strip() or "_"
        last_path = self._last_path(owner)
        if last_path.exists():
            try:
                prev = read_json(last_path)
            except (OSError, ValueError):
                prev = {}
            if isinstance(prev, dict) and str(prev.get("bout") or "") == bout_key:
                return None
        work = last_work if last_work is not None else self._last_work(owner)
        text = compose_dream_text(owner, place=place, last_work=work)
        now = datetime.now()
        stamp = now.strftime("%Y%m%d_%H%M%S")
        folder = self._vault_dir(owner)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"Dream_{stamp}.json"
        suffix = 2
        while path.exists():
            path = folder / f"Dream_{stamp}_{suffix}.json"
            suffix += 1
        entry = {
            "agent_id": owner,
            "kind": "dream",
            "source": "rest",
            "speech": False,
            "text": text,
            "from_note": work,
            "place": place or None,
            "timestamp": now.timestamp(),
            "authority": "owning_agent",
            "bout": bout_key,
        }
        atomic_write_json(path, entry)
        atomic_write_json(last_path, {"agent_id": owner, "bout": bout_key})
        if owner in FEDERATION_LANE:
            HouseNotebook(self.federation_root).remember(
                owner,
                text=text,
                kind="dream",
                writer=owner,
            )
        return entry
