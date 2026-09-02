"""Read-only Mom federation check. No new agents. No bus send. No Gemini speech."""
from __future__ import annotations

import json
from pathlib import Path

from federation.heartbeat import HeartbeatLog
from federation.manifests import AgentManifest, CapabilityManifest
from federation.prove import status_check
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


def _aster() -> AgentManifest:
    return AgentManifest(
        agent_id="aster",
        name="Aster",
        version="1.0",
        role="weaver",
        house="hearth_lab",
        capabilities=[],
        tools=[],
        runtime={"endpoint": "http://127.0.0.1:8791", "protocol": "http"},
        protocol_version="1",
        requested_permissions=["read_hearth_snapshot"],
        declared_status="DECLARED",
        identity_root=r"D:\Mythos_Hearth\ASTER",
    )


def _observer() -> AgentManifest:
    return AgentManifest(
        agent_id="observer",
        name="The Observer",
        version="0.1.0",
        role="independent_auditor",
        house="the_observer",
        capabilities=[],
        tools=[],
        runtime={"endpoint": "http://127.0.0.1:8730", "protocol": "http"},
        protocol_version="1",
        requested_permissions=[],
        declared_status="DECLARED",
        identity_root=r"D:\The_Observer",
    )


def _hearth() -> AgentManifest:
    return AgentManifest(
        agent_id="hearth",
        name="Hearth",
        version="1",
        role="village_os",
        house="hearth",
        capabilities=[],
        tools=[],
        runtime={"endpoint": "http://127.0.0.1:8790", "protocol": "http"},
        protocol_version="1",
        requested_permissions=[],
        declared_status="DECLARED",
        identity_root=r"D:\Mythos_Hearth",
    )


def _seed(root: Path) -> LocalFederationBus:
    registry = FederationRegistry(root)
    registry.register(_aster())
    registry.register(_observer())
    registry.register(_hearth())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.hearth_snapshot",
            agent_id="aster",
            name="Hearth snapshot read",
        )
    )
    bus = LocalFederationBus(root)
    msg = bus.send(
        sender="aster",
        recipient="hearth",
        message_type="capability_query",
        payload={"ask": "snapshot"},
    )
    bus.deliver(msg.message_id)
    bus.acknowledge(msg.message_id, recipient="hearth")
    HeartbeatLog(root).pulse("aster", source="aster_lab_http")
    (root / "ASTER_ACCEPTANCE.json").write_text(
        json.dumps(
            {
                "overall": "FAIL",
                "full_aster_acceptance": False,
                "gemini_spoke": False,
            }
        ),
        encoding="utf-8",
    )
    return bus


def _bus_names(root: Path) -> set[str]:
    bus = root / "bus"
    if not bus.exists():
        return set()
    return {p.name for p in bus.rglob("*.json")}


def test_status_check_is_read_only(tmp_path: Path):
    root = tmp_path / "fed"
    _seed(root)
    before_ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    before_bus = _bus_names(root)
    before_pulse = json.loads(
        (root / "heartbeats" / "aster.json").read_text(encoding="utf-8")
    )

    report = status_check(
        root,
        ping_fn=lambda: {
            "observer": {"ok": True, "http": 200, "id": None},
            "hearth": {"ok": True, "http": 200, "id": None},
            "aster_lab": {"ok": True, "http": 200, "id": "aster"},
        },
    )

    after_ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert after_ids == before_ids == {"aster", "hearth", "observer"}
    assert _bus_names(root) == before_bus
    after_pulse = json.loads(
        (root / "heartbeats" / "aster.json").read_text(encoding="utf-8")
    )
    assert after_pulse["ts"] == before_pulse["ts"]
    assert report["kind"] == "MOM_FEDERATION_STATUS"
    assert report["wrote_bus"] is False
    assert report["gemini_spoke"] is False
    assert report["full_aster_acceptance"] is False
    assert report["observer_owns_aster"] is False
    assert report["participants"] == ["aster", "hearth", "observer"]
    assert report["aster_lab"]["id"] == "aster"
    assert report["overall"] == "FAIL"
    saved = json.loads((root / "MOM_STATUS.json").read_text(encoding="utf-8"))
    assert saved["kind"] == "MOM_FEDERATION_STATUS"
