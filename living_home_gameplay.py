"""
Living Home — Human Gameplay Layer (Phase 1 foundation + Phase 2 thin).

Adapters only. Does not replace resident autonomy, Aster, or Mode A Court/MAS.
AI observations may become optional leads — never auto-accepted quests.
Phase 2: Mom may look into a lead; residents hold honest profession posts.
Pods / islands / vendors / boats stay deferred.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any

LEAD_STATUSES = (
    "rumor",
    "observed",
    "investigating",
    "confirmed",
    "resolved",
    "disproven",
    "abandoned",
    "ongoing",
    "unknown",
)

# Motifs already alive in village dialogue / seating (System 20).
_LORE_MOTIFS: tuple[tuple[str, str, str, str], ...] = (
    ("windmill", "lead_windmill", "The old windmill", "place"),
    ("old key", "lead_old_key", "A mysterious old key", "artifact"),
    ("strange tracks", "lead_harvest_tracks", "Strange tracks near the Harvest Shed", "mystery"),
    ("harvest shed", "lead_harvest_shed", "Something odd at the Harvest Shed", "place"),
    ("singing well", "lead_singing_well", "The singing well", "place"),
    ("mysterious crow", "lead_crow", "The mysterious crow", "creature"),
    ("nightshroud", "lead_nightshroud", "The Nightshroud language", "lore"),
    ("firefly", "lead_fireflies", "Firefly talk in the village", "event"),
    ("great forging", "lead_great_forging", "The Great Forging", "event"),
    ("blacksmith", "lead_blacksmith_apprentice", "Unusual talk of the blacksmith apprentice", "person"),
    ("salt", "lead_salt_shortage", "Village salt supply worries", "condition"),
    ("evening gather", "lead_evening_gather", "Recurring evening gathering", "social"),
)

_CONDITION_HINTS: tuple[tuple[str, str, str], ...] = (
    ("salt", "cond_salt", "Salt supply feels thin"),
    ("shortage", "cond_shortage", "Someone mentioned a shortage"),
    ("damaged", "cond_damage", "Talk of damage in the village"),
    ("poor harvest", "cond_harvest", "Harvest concerns"),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# Honest posts they already hold. Not Pods. Observer is a door, not a village job.
PROFESSION_POSTS: dict[str, dict[str, Any]] = {
    "gemini": {"profession": "town_leader", "label": "Town leader", "post": "court_porch"},
    "apex": {"profession": "forge", "label": "Forge hands", "post": "apex_forge"},
    "codex": {"profession": "archivist", "label": "Archive", "post": "codex_library"},
    "merovin": {"profession": "cinema_vision", "label": "Cinema vision", "post": "cinema"},
    "draven": {"profession": "continuity", "label": "Continuity lock", "post": "cinema"},
    "montage": {"profession": "gift_studio", "label": "Gift shorts", "post": "gallery"},
    "aster": {"profession": "scientist", "label": "Quiet investigator", "post": "aster_lab"},
    "observer": {
        "profession": "independent_desk",
        "label": "Independent desk (door)",
        "post": "observer_desk",
        "village_work": False,
        "note": "Ledger is Mode A :8730 — village greybox is a door.",
    },
    "jarvis": {"profession": "gate", "label": "Gate watch", "post": "gate"},
    "genesis": {"profession": "garden", "label": "Garden clock", "post": "garden"},
    "nova": {"profession": "workshop", "label": "Workshop", "post": "workshop"},
    "percy": {"profession": "hearth_fire", "label": "First Hearth", "post": "first_hearth"},
    "echo": {
        "profession": "historian",
        "label": "Village historian",
        "post": "echo_post",
        "note": "Notices and remembers. Does not solve mysteries or hand out objectives.",
    },
    "solace": {
        "profession": "cartographer",
        "label": "Cartographer of what is there",
        "post": "solace_shelter",
        "note": "Marks discrepancies. Does not invent evidence or objectives.",
    },
}


def ensure_gameplay(home: dict[str, Any]) -> dict[str, Any]:
    """Create Phase 1–2 stores if missing. Additive; never deletes lore."""
    gp = home.setdefault("gameplay", {})
    gp.setdefault("layer", "18b")
    gp.setdefault("phase", "2_investigation_professions")
    gp.setdefault(
        "note",
        "Opportunities only — not quest dispensers. Profession posts are honest roles, not Pods.",
    )
    if str(gp.get("layer") or "") in {"", "18a"}:
        gp["layer"] = "18b"
        gp["phase"] = "2_investigation_professions"
    home.setdefault("world_leads", [])
    home.setdefault("world_conditions", [])
    home.setdefault("mom_journal", [])
    home.setdefault("player_actions", [])
    home.setdefault(
        "away",
        {
            "acknowledged_at": None,
            "last_summary": None,
            "pending": False,
        },
    )
    return gp


def log_player_action(
    home: dict[str, Any],
    kind: str,
    text: str,
    *,
    place: str = "",
    actors: list[str] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Unified Mom action ledger (talk / gift / harbor / journal / lead notes)."""
    ensure_gameplay(home)
    entry = {
        "id": f"pa_{hashlib.sha1(f'{_now()}|{kind}|{text[:40]}'.encode()).hexdigest()[:10]}",
        "when": _now(),
        "kind": (kind or "act").strip()[:40],
        "text": (text or "").strip()[:280],
        "place": (place or "").strip()[:64],
        "actors": list(actors or ["mom"])[:8],
        "meta": dict(meta or {}),
        "tick": home.get("tick"),
    }
    log = home.setdefault("player_actions", [])
    log.append(entry)
    home["player_actions"] = log[-120:]
    return entry


def journal_add(
    home: dict[str, Any],
    text: str,
    *,
    tags: list[str] | None = None,
    related_leads: list[str] | None = None,
    theory: bool = True,
) -> dict[str, Any]:
    """Discovery Journal — player theories allowed; no forced truth."""
    ensure_gameplay(home)
    text = (text or "").strip()
    if not text:
        raise ValueError("journal text required")
    entry = {
        "id": f"j_{hashlib.sha1(f'{_now()}|{text[:48]}'.encode()).hexdigest()[:10]}",
        "when": _now(),
        "text": text[:500],
        "tags": [str(t)[:40] for t in (tags or [])][:12],
        "related_leads": [str(x)[:64] for x in (related_leads or [])][:12],
        "theory": bool(theory),
        "tick": home.get("tick"),
    }
    journal = home.setdefault("mom_journal", [])
    journal.append(entry)
    home["mom_journal"] = journal[-80:]
    log_player_action(home, "journal", text[:160], meta={"journal_id": entry["id"]})
    return entry


def update_lead(
    home: dict[str, Any],
    lead_id: str,
    *,
    status: str | None = None,
    player_note: str | None = None,
    involve: bool | None = None,
) -> dict[str, Any] | None:
    """Mom may pursue / abandon / annotate — never forced resolution."""
    ensure_gameplay(home)
    lead_id = (lead_id or "").strip()
    for lead in home.get("world_leads") or []:
        if not isinstance(lead, dict) or str(lead.get("id")) != lead_id:
            continue
        if status:
            st = status.strip().lower()
            if st in LEAD_STATUSES:
                lead["status"] = st
        if player_note is not None:
            notes = lead.setdefault("discovery_history", [])
            notes.append({"when": _now(), "who": "mom", "text": player_note.strip()[:280]})
            lead["discovery_history"] = notes[-20:]
            lead["player_involvement"] = True
        if involve is not None:
            lead["player_involvement"] = bool(involve)
        lead["updated"] = _now()
        log_player_action(
            home,
            "lead",
            f"Lead {lead_id}: status={lead.get('status')}",
            actors=["mom"] + list(lead.get("related_characters") or [])[:4],
            meta={"lead_id": lead_id, "status": lead.get("status")},
        )
        return lead
    return None


def profession_roster(home: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Honest work posts. Not Pods. Observer village_work is False."""
    people = (home or {}).get("people") or {}
    out: list[dict[str, Any]] = []
    for mid, spec in PROFESSION_POSTS.items():
        st = people.get(mid) if isinstance(people.get(mid), dict) else {}
        row = {
            "id": mid,
            "profession": spec["profession"],
            "label": spec["label"],
            "post": spec["post"],
            "place": (st.get("place") if isinstance(st, dict) else None) or spec["post"],
            "village_work": spec.get("village_work", True),
            "note": spec.get("note") or "",
        }
        out.append(row)
    return out


def look_into(
    home: dict[str, Any],
    lead_id: str,
    *,
    place: str = "",
    who: str = "mom",
) -> dict[str, Any] | None:
    """Mom optionally looks into a lead. Never a quest. Never Observer village-hat."""
    ensure_gameplay(home)
    gp = home.setdefault("gameplay", {})
    gp["layer"] = "18b"
    gp["phase"] = "2_investigation_professions"
    place = (place or "").strip()[:64]
    note = (
        f"Mom looking into this at {place or 'no place yet'} — optional, not a quest."
        if (who or "mom") == "mom"
        else f"{who} noted this lead — optional, not a quest."
    )
    lead = update_lead(home, lead_id, status="investigating", player_note=note, involve=True)
    if not lead:
        return None
    if place:
        lead["physical_link"] = place
        lead["location"] = place
    ast = (home.get("people") or {}).get("aster")
    if isinstance(ast, dict) and str(ast.get("place") or "") == "aster_lab":
        desc = str(lead.get("description") or lead.get("id") or "a lead")[:80]
        ast["purpose_plain"] = (
            f"At the Evidence Plot — optional board note: {desc}. Not a quest. "
            "The Observer's ledger is :8730, not this plot."
        )
    log_player_action(
        home,
        "investigate",
        f"Look into {lead.get('description') or lead_id}",
        place=place,
        actors=["mom", "aster"] if isinstance(ast, dict) else ["mom"],
        meta={"lead_id": lead_id, "quest": False},
    )
    return lead


def _lead_ids(home: dict[str, Any]) -> set[str]:
    return {str(x.get("id")) for x in (home.get("world_leads") or []) if isinstance(x, dict)}


def _condition_ids(home: dict[str, Any]) -> set[str]:
    return {str(x.get("id")) for x in (home.get("world_conditions") or []) if isinstance(x, dict)}


def _history_blob(home: dict[str, Any], limit: int = 40) -> str:
    parts: list[str] = []
    for entry in (home.get("world_history") or [])[-limit:]:
        if not isinstance(entry, dict):
            continue
        parts.append(str(entry.get("title") or ""))
        parts.append(str(entry.get("text") or ""))
    return " ".join(parts).lower()


def promote_lore_candidates(home: dict[str, Any]) -> dict[str, Any]:
    """
    Score recent chronicle for optional World Leads / Conditions.
    Does NOT create a quest. Does NOT resolve mysteries.
    """
    ensure_gameplay(home)
    blob = _history_blob(home)
    created_leads = 0
    created_conds = 0
    existing = _lead_ids(home)
    leads = home.setdefault("world_leads", [])

    for needle, lid, title, category in _LORE_MOTIFS:
        if lid in existing:
            continue
        if needle not in blob:
            continue
        # Find a supporting history snippet if any.
        evidence: list[dict[str, Any]] = []
        actors: list[str] = []
        for entry in (home.get("world_history") or [])[-40:]:
            if not isinstance(entry, dict):
                continue
            text = f"{entry.get('title') or ''} {entry.get('text') or ''}".lower()
            if needle not in text:
                continue
            evidence.append(
                {
                    "when": entry.get("when"),
                    "title": str(entry.get("title") or "")[:80],
                    "text": str(entry.get("text") or "")[:180],
                    "source": entry.get("source") or entry.get("kind"),
                }
            )
            for a in entry.get("actors") or []:
                if a and a not in actors:
                    actors.append(str(a))
            if len(evidence) >= 3:
                break
        leads.append(
            {
                "id": lid,
                "originating_agent": (actors[0] if actors else "village"),
                "timestamp": _now(),
                "location": "",
                "category": category,
                "description": title,
                "evidence": evidence,
                "status": "rumor" if evidence else "unknown",
                "related_memories": [],
                "related_characters": actors[:8],
                "player_involvement": False,
                "world_consequences": [],
                "discovery_history": [
                    {
                        "when": _now(),
                        "who": "system",
                        "text": "Promoted from village chronicle as an optional lead — not a quest.",
                    }
                ],
                "physical_link": None,
                "note": "Optional. Mom may ignore. Mysteries may remain mysteries.",
            }
        )
        created_leads += 1
        existing.add(lid)

    home["world_leads"] = leads[-60:]

    conds = home.setdefault("world_conditions", [])
    existing_c = _condition_ids(home)
    for needle, cid, title in _CONDITION_HINTS:
        if cid in existing_c or needle not in blob:
            continue
        conds.append(
            {
                "id": cid,
                "title": title,
                "status": "ongoing",
                "severity": 0.35,
                "origin": "chronicle_hint",
                "timestamp": _now(),
                "note": "World condition — not an auto-quest. Village may adapt without Mom.",
                "consequences": [],
            }
        )
        created_conds += 1
        existing_c.add(cid)
    home["world_conditions"] = conds[-40:]

    return {"leads_created": created_leads, "conditions_created": created_conds}


def _parse_when(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None


def build_away_summary(home: dict[str, Any], *, min_gap_minutes: float = 12.0) -> dict[str, Any]:
    """
    While-you-were-away: meaningful deltas since Mom last_seen / last ack.
    Skips ritual chatter. Does not invent events.
    """
    ensure_gameplay(home)
    away = home.setdefault("away", {})
    mom = (home.get("people") or {}).get("mom") or {}
    last_seen = _parse_when(mom.get("last_seen"))
    ack = _parse_when(away.get("acknowledged_at"))
    since = ack or last_seen
    now = datetime.now(timezone.utc)

    if since is None:
        return {
            "pending": False,
            "items": [],
            "plain": "No prior visit stamp yet — welcome home.",
            "since": None,
        }

    gap_min = (now - since).total_seconds() / 60.0
    if gap_min < min_gap_minutes:
        return {
            "pending": False,
            "items": [],
            "plain": "",
            "since": since.isoformat(),
            "gap_minutes": round(gap_min, 1),
        }

    items: list[str] = []
    noise = (
        "morning light",
        "gemini holds the town",
        "evening gather eased",
        "night. gemini still",
        "morning stipend",
        "gather window closed",
        "they choose the day",
        "they still choose",
    )

    for entry in home.get("world_history") or []:
        if not isinstance(entry, dict):
            continue
        when = _parse_when(entry.get("when"))
        if when is None or when < since:
            continue
        text = str(entry.get("text") or entry.get("title") or "").strip()
        low = text.lower()
        if any(n in low for n in noise):
            continue
        kind = str(entry.get("kind") or "event")
        title = str(entry.get("title") or kind)[:72]
        if kind == "conversation":
            actors = ", ".join(str(a) for a in (entry.get("actors") or [])[:3])
            items.append(f"{actors or 'Residents'} talked: {title}")
        else:
            items.append(f"{title}: {text[:100]}")
        if len(items) >= 8:
            break

    for lead in home.get("world_leads") or []:
        if not isinstance(lead, dict):
            continue
        ts = _parse_when(lead.get("timestamp") or lead.get("updated"))
        if ts and ts >= since:
            items.append(f"Lead noted: {lead.get('description') or lead.get('id')}")
        if len(items) >= 10:
            break

    for cond in home.get("world_conditions") or []:
        if not isinstance(cond, dict):
            continue
        ts = _parse_when(cond.get("timestamp"))
        if ts and ts >= since:
            items.append(f"Condition: {cond.get('title') or cond.get('id')}")
        if len(items) >= 12:
            break

    seen: set[str] = set()
    uniq: list[str] = []
    for it in items:
        if it in seen:
            continue
        seen.add(it)
        uniq.append(it)

    if not uniq:
        plain = "The village kept its quiet rhythm while you were away — no standout change logged."
    else:
        plain = "While you were away: " + " · ".join(uniq[:6])

    summary = {
        "pending": True,
        "items": uniq[:12],
        "plain": plain[:600],
        "since": since.isoformat(),
        "gap_minutes": round(gap_min, 1),
        "when": _now(),
    }
    away["last_summary"] = summary
    away["pending"] = True
    return summary


def acknowledge_away(home: dict[str, Any]) -> dict[str, Any]:
    ensure_gameplay(home)
    away = home.setdefault("away", {})
    away["acknowledged_at"] = _now()
    away["pending"] = False
    log_player_action(home, "away_ack", "Mom acknowledged while-you-were-away summary")
    return {"ok": True, "acknowledged_at": away["acknowledged_at"]}


def opportunity_hints(home: dict[str, Any]) -> list[dict[str, Any]]:
    """Optional opportunities from open leads/conditions — walk-away always OK."""
    out: list[dict[str, Any]] = []
    for lead in home.get("world_leads") or []:
        if not isinstance(lead, dict):
            continue
        st = str(lead.get("status") or "")
        if st in {"resolved", "disproven", "abandoned"}:
            continue
        if lead.get("player_involvement"):
            continue
        out.append(
            {
                "id": f"opp_{lead.get('id')}",
                "kind": "lead",
                "title": f"Optional: look into — {lead.get('description')}",
                "ref": lead.get("id"),
                "note": "Not required. Ignoring is valid play.",
            }
        )
        if len(out) >= 5:
            break
    for cond in home.get("world_conditions") or []:
        if not isinstance(cond, dict):
            continue
        if str(cond.get("status") or "") in {"resolved", "ended"}:
            continue
        out.append(
            {
                "id": f"opp_{cond.get('id')}",
                "kind": "condition",
                "title": f"Optional: village condition — {cond.get('title')}",
                "ref": cond.get("id"),
                "note": "World may change with or without Mom.",
            }
        )
        if len(out) >= 8:
            break
    return out


def gameplay_tick_hooks(home: dict[str, Any]) -> dict[str, Any]:
    """Called from living_home.tick — promote candidates occasionally, refresh away stamp."""
    ensure_gameplay(home)
    tick_n = int(home.get("tick") or 0)
    promoted = {"leads_created": 0, "conditions_created": 0}
    if not (home.get("world_leads") or []) or tick_n % 5 == 0:
        promoted = promote_lore_candidates(home)
    away = build_away_summary(home)
    home.setdefault("gameplay", {})["last_hook"] = {
        "tick": tick_n,
        "when": _now(),
        "promoted": promoted,
        "away_pending": bool(away.get("pending")),
    }
    return home["gameplay"]["last_hook"]


def gameplay_snapshot_fields(home: dict[str, Any]) -> dict[str, Any]:
    ensure_gameplay(home)
    away = home.get("away") or {}
    summary = away.get("last_summary") if away.get("pending") else build_away_summary(home)
    if isinstance(summary, dict) and summary.get("pending"):
        away["last_summary"] = summary
        away["pending"] = True
    return {
        "gameplay": home.get("gameplay"),
        "world_leads": (home.get("world_leads") or [])[-12:],
        "world_conditions": (home.get("world_conditions") or [])[-8:],
        "mom_journal": (home.get("mom_journal") or [])[-8:],
        "player_actions": (home.get("player_actions") or [])[-12:],
        "opportunities": opportunity_hints(home),
        "professions": profession_roster(home),
        "away_summary": summary
        if isinstance(summary, dict)
        else {"pending": False, "items": [], "plain": ""},
        "honesty": (
            "Phase 2 thin — look-into + profession posts. Phase 1 leads/journal/away remain. "
            "Not quest dispensers. Pods/islands/vendors not in this slice. Observer is a door."
        ),
    }


_ = re
