"""Durable local federation bus. Extends the Court *idea*; does not replace Court mailboxes."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from federation.atomic import atomic_write_json, read_json


class DuplicateMessage(ValueError):
    pass


@dataclass
class FederationMessage:
    message_id: str
    sender: str
    recipient: str
    timestamp: float
    message_type: str
    payload: dict[str, Any]
    correlation_id: str
    status: str
    attempts: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FederationMessage:
        return cls(
            message_id=data["message_id"],
            sender=data["sender"],
            recipient=data["recipient"],
            timestamp=float(data["timestamp"]),
            message_type=data["message_type"],
            payload=dict(data.get("payload") or {}),
            correlation_id=data.get("correlation_id") or data["message_id"],
            status=data["status"],
            attempts=int(data.get("attempts") or 0),
            extra=dict(data.get("extra") or {}),
        )


class LocalFederationBus:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.pending = self.root / "bus" / "pending"
        self.inbox_root = self.root / "bus" / "inbox"
        self.acks = self.root / "bus" / "acks"
        self.archive = self.root / "bus" / "archive"
        for d in (self.pending, self.inbox_root, self.acks, self.archive):
            d.mkdir(parents=True, exist_ok=True)

    def _pending_path(self, message_id: str) -> Path:
        return self.pending / f"{message_id}.json"

    def _archive_path(self, message_id: str) -> Path:
        return self.archive / f"{message_id}.json"

    def _inbox_path(self, recipient: str, message_id: str) -> Path:
        return self.inbox_root / recipient / f"{message_id}.json"

    def _exists_anywhere(self, message_id: str) -> bool:
        return (
            self._pending_path(message_id).exists()
            or self._archive_path(message_id).exists()
        )

    def send(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        payload: dict[str, Any],
        *,
        message_id: str | None = None,
        correlation_id: str | None = None,
    ) -> FederationMessage:
        mid = message_id or uuid.uuid4().hex
        if self._exists_anywhere(mid):
            raise DuplicateMessage(mid)
        msg = FederationMessage(
            message_id=mid,
            sender=sender,
            recipient=recipient,
            timestamp=time.time(),
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id or mid,
            status="pending",
            attempts=0,
        )
        atomic_write_json(self._pending_path(mid), msg.to_dict())
        atomic_write_json(self._archive_path(mid), msg.to_dict())
        return msg

    def get(self, message_id: str) -> FederationMessage:
        for path in (self._pending_path(message_id), self._archive_path(message_id)):
            if path.exists():
                return FederationMessage.from_dict(read_json(path))
        raise KeyError(message_id)

    def deliver(self, message_id: str) -> FederationMessage:
        msg = self.get(message_id)
        msg.attempts += 1
        msg.status = "delivered"
        dest = self._inbox_path(msg.recipient, message_id)
        atomic_write_json(dest, msg.to_dict())
        atomic_write_json(self._pending_path(message_id), msg.to_dict())
        atomic_write_json(self._archive_path(message_id), msg.to_dict())
        return msg

    def inbox(self, recipient: str) -> list[FederationMessage]:
        folder = self.inbox_root / recipient
        if not folder.exists():
            return []
        rows = []
        for path in sorted(folder.glob("*.json")):
            rows.append(FederationMessage.from_dict(read_json(path)))
        return rows

    def acknowledge(self, message_id: str, recipient: str) -> FederationMessage:
        msg = self.get(message_id)
        if msg.recipient != recipient:
            raise PermissionError(f"{recipient} is not the recipient of {message_id}")
        msg.status = "acknowledged"
        atomic_write_json(self.acks / f"{message_id}.json", msg.to_dict())
        atomic_write_json(self._archive_path(message_id), msg.to_dict())
        atomic_write_json(self._pending_path(message_id), msg.to_dict())
        inbox_copy = self._inbox_path(recipient, message_id)
        if inbox_copy.exists():
            atomic_write_json(inbox_copy, msg.to_dict())
        return msg

    def history(self, message_id: str) -> Path | None:
        path = self._archive_path(message_id)
        return path if path.exists() else None
