"""Phase B Aster refresh: live lab pulse + snapshot provenance. No new agents. No Gemini speech."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.health import AgentHealth
from federation.heartbeat import HeartbeatLog
from federation.law import CapabilityState, HonestStatus
from federation.manifests import AgentManifest, CapabilityManifest
from federation.prove import refresh_aster
from federation.registry import FederationRegistry


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


def test_refresh_aster_rejects_non_aster_lab(tmp_path: Path):
    root = tmp_path / "fed"
    registry = FederationRegistry(root)
    registry.register(_aster())
    with pytest.raises(PermissionError):
        refresh_aster(root, get_lab_status=lambda: {"ok": True, "id": "gemini"})
    assert HeartbeatLog(root).presence("aster").value == "UNKNOWN"


def test_refresh_aster_pulses_and_verifies_snapshot_without_adding_agents(
    tmp_path: Path,
):
    root = tmp_path / "fed"
    registry = FederationRegistry(root)
    registry.register(_aster())
    registry.register(_hearth())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.hearth_snapshot",
            agent_id="aster",
            name="Hearth snapshot read",
        )
    )

    def lab() -> dict:
        return {"ok": True, "id": "aster", "name": "Aster", "world": {"hearth": "REACHABLE"}}

    def snap() -> dict:
        return {
            "ok": True,
            "hearth": "REACHABLE",
            "adapter": "aster_hearth_bridge",
            "connection_test": True,
            "functional_test": True,
        }

    report = refresh_aster(root, get_lab_status=lab, snapshot_fn=snap)
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert ids == {"aster", "hearth"}
    assert report["new_agents"] == []
    assert report["gemini_spoke"] is False
    assert report["full_aster_acceptance"] is False
    rec = FederationRegistry(root).get_capability("aster.hearth_snapshot")
    assert rec.state == CapabilityState.VERIFIED
    assert rec.honest_status == HonestStatus.VERIFIED
    assert rec.provenance.get("adapter") == "aster_hearth_bridge"
    assert rec.provenance.get("verified_at")
    assert rec.provenance.get("declared_by") == "aster"
    assert FederationRegistry(root).agent_health("aster") == AgentHealth.ACTIVE
    beat = HeartbeatLog(root)
    assert beat.presence("aster").value == "READY"
    pulse = __import__("json").loads(
        (root / "heartbeats" / "aster.json").read_text(encoding="utf-8")
    )
    assert pulse["source"] == "aster_lab_http"
