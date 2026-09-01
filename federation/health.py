"""Agent health. One failure does not take down the federation."""

from __future__ import annotations

from enum import Enum


class AgentHealth(str, Enum):
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    QUARANTINED = "QUARANTINED"
