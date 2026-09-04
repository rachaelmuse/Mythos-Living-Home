"""Echo/Solace cottages stay off other homes. Trees line the village outside."""
from __future__ import annotations

from math import hypot

from living_home import PLACES, _clear_trees_from_doors, _seed_trees, _tree_in_keepout

KIN_SITES = ("echo_home", "echo_post", "solace_home", "solace_shelter")
SKIP_DIST = {"far_shore"}


def _xz(pid: str) -> tuple[float, float]:
    pos = PLACES[pid]["pos"]
    return float(pos[0]), float(pos[2])


def _dist(a: str, b: str) -> float:
    ax, az = _xz(a)
    bx, bz = _xz(b)
    return hypot(ax - bx, az - bz)


def test_echo_solace_sit_on_village_edge_not_on_other_homes():
    for kid in KIN_SITES:
        x, z = _xz(kid)
        assert abs(x) >= 24 or abs(z) >= 24, f"{kid} still in town center {(x, z)}"
        for oid in PLACES:
            if oid in KIN_SITES or oid in SKIP_DIST:
                continue
            d = _dist(kid, oid)
            assert d >= 10.0, f"{kid} overlaps {oid} at {d:.1f}m"


def test_echo_and_solace_homes_are_apart():
    assert _dist("echo_home", "solace_home") >= 12.0
    assert _dist("echo_home", "echo_post") >= 6.0
    assert _dist("solace_home", "solace_shelter") >= 6.0


def test_seed_trees_line_the_village_outside():
    trees = _seed_trees()
    assert len(trees) >= 8
    for tree in trees:
        pos = tree["pos"]
        x, z = float(pos[0]), float(pos[2])
        assert not _tree_in_keepout(x, z), tree
        on_edge = abs(x) >= 36.0 or z <= -36.0 or z >= 64.0
        assert on_edge, f"tree {tree.get('id')} still in town {(x, z)}"


def test_interior_saved_trees_move_to_the_edge():
    home = {
        "trees": [
            {
                "id": "tree_1",
                "species": "oak",
                "pos": [8.0, 0.0, 10.0],
                "growth_stage": 0.5,
                "health": 0.8,
            }
        ]
    }
    _clear_trees_from_doors(home)
    x, z = float(home["trees"][0]["pos"][0]), float(home["trees"][0]["pos"][2])
    assert abs(x) >= 36.0 or z <= -36.0 or z >= 64.0
    assert not _tree_in_keepout(x, z)
