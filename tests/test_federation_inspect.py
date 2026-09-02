"""Read-only federation inspect. Observer may query; she must not create the store."""
from __future__ import annotations

import json
from pathlib import Path

from federation.audit import inspect
from federation.heartbeat import HeartbeatLog
from federation.law import CapabilityState, HonestStatus
from federation.manifests import AgentManifest, CapabilityManifest
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
        requested_permissions=[],
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


def test_inspect_missing_store_does_not_create_it(tmp_path: Path):
    root = tmp_path / "no_such_federation"
    report = inspect(root)
    assert report["ok"] is False
    assert report["owned_by"] is None
    assert report["observer_owns_aster"] is False
    assert not root.exists()


def test_inspect_reports_who_verified_and_communications(tmp_path: Path):
    root = tmp_path / "fed"
    registry = FederationRegistry(root)
    registry.register(_aster())
    registry.register(_observer())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.hearth_snapshot",
            agent_id="aster",
            name="Hearth snapshot read",
        )
    )
    registry.test_capability(
        "aster.hearth_snapshot",
        lambda: {
            "ok": True,
            "adapter": "aster_hearth_bridge",
            "connection_test": True,
            "functional_test": True,
        },
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

    report = inspect(root)
    assert report["ok"] is True
    assert report["owned_by"] is None
    assert report["observer_is_supervisor"] is False
    assert report["observer_owns_aster"] is False
    ids = {a["agent_id"] for a in report["agents"]}
    assert ids == {"aster", "observer"}
    assert all(a["owner"] is None for a in report["agents"])
    verified = [c for c in report["capabilities"] if c["verified"]]
    assert verified[0]["capability_id"] == "aster.hearth_snapshot"
    assert verified[0]["provenance"]["adapter"] == "aster_hearth_bridge"
    comm = report["communications"]
    assert any(m["message_id"] == msg.message_id and m["status"] == "acknowledged" for m in comm)
    assert report["gemini_spoke"] is False
