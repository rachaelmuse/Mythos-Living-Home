"""Thin Court adapter: federation notices live beside Court, never in MAS inbox.

Does not add Aster or Observer to Court AGENTS.
Does not call family_court.post_packet.
Does not speak as Gemini.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from federation.atomic import atomic_write_json

INBOX_BOX = "inbox"
FEDERATION_BOX = "federation"

DEFAULT_COURT_ROOTS = (
    Path(r"G:\The-Axiom-Codex\SUPERPOWER_VAULT\FAMILY_COURT"),
    Path(r"D:\Court\mailbox\family"),
)


class CourtFederationAdapter:
    def __init__(self, roots: list[Path] | None = None) -> None:
        self.roots = [Path(r) for r in (roots or list(DEFAULT_COURT_ROOTS))]

    def drop_notice(
        self,
        *,
        message_id: str,
        sender: str,
        recipient: str,
        payload: dict[str, Any],
    ) -> list[str]:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
        fname = f"{stamp}_{message_id[:8]}.json"
        body = {
            "id": message_id,
            "from": sender,
            "to": recipient,
            "kind": "federation_notice",
            "goal": "federation delivery copy — not a Court MAS claim",
            "status": "delivered",
            "simulated": False,
            "gemini_spoke": False,
            "payload": payload,
            "bus": "local_federation",
            "note": "Not a Court worker task. Identities are not merged. Delivery copy only.",
            "created": datetime.now(timezone.utc).isoformat(),
        }
        written: list[str] = []
        for root in self.roots:
            dest = root / recipient / FEDERATION_BOX / fname
            dest.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_json(dest, body)
            written.append(str(dest))
        return written

    def drop_spoken_reply(
        self,
        *,
        message_id: str,
        sender: str,
        recipient: str,
        payload: dict[str, Any],
    ) -> list[str]:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
        fname = f"{stamp}_{message_id[:8]}_reply.json"
        body = {
            "id": message_id,
            "from": sender,
            "to": recipient,
            "kind": "federation_reply",
            "goal": "Gemini spoken reply on federation bus — not MAS, not village hat",
            "status": "delivered",
            "simulated": False,
            "gemini_spoke": True,
            "payload": payload,
            "bus": "local_federation",
            "created": datetime.now(timezone.utc).isoformat(),
        }
        written: list[str] = []
        for root in self.roots:
            dest = root / recipient / FEDERATION_BOX / fname
            dest.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_json(dest, body)
            written.append(str(dest))
        return written
