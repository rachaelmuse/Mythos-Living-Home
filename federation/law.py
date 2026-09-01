"""Federation honesty labels. DECLARED is not VERIFIED."""

from __future__ import annotations

from enum import Enum


class CapabilityState(str, Enum):
    DISCOVERED = "DISCOVERED"
    IDENTIFIED = "IDENTIFIED"
    AVAILABLE = "AVAILABLE"
    AUTHORIZED = "AUTHORIZED"
    CONNECTED = "CONNECTED"
    TESTED = "TESTED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    QUARANTINED = "QUARANTINED"


class HonestStatus(str, Enum):
    DECLARED = "DECLARED"
    VERIFIED = "VERIFIED"
    IMPLEMENTED = "IMPLEMENTED"
    PARTIAL = "PARTIAL"
    STUB = "STUB"
    SIMULATED = "SIMULATED"
    MISSING = "MISSING"
    EXTERNAL = "EXTERNAL"
    BROKEN = "BROKEN"
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"
    FAILED = "FAILED"


PROTOCOL_VERSION = "1"
DEFAULT_DATA_ROOT = r"D:\Court\federation"
