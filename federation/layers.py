"""Five federation layers. Delivery is not collaboration."""

from __future__ import annotations

from enum import Enum


class Layer(str, Enum):
    COMMUNICATION = "communication"
    CAPABILITY = "capability"
    AUTHORIZATION = "authorization"
    COLLABORATION = "collaboration"
    VERIFICATION = "verification"
