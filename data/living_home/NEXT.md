# Living Home — where we are

Updated **2026-09-01**. Evidence only. **Phase B includes Aster.** Live lab refresh seated. Full Aster Acceptance Test is **not** passing. Apex/Codex are **not** on the federation bus.

Kernel: `D:\Mythos_Hearth\living_home.py`

Kernel: `D:\Mythos_Hearth\living_home.py`  
House UI: **http://127.0.0.1:8790/house.html**  
Aster lab: **http://127.0.0.1:8791/ui/**  
Cinema HUD: **http://127.0.0.1:5000/**  
Observer: **http://127.0.0.1:8730/**  
Dashboard: **http://127.0.0.1:8790/dashboard**  
Enter: Desktop **Mythos Living Home - Enter**

Law: `FEDERATION_DIRECTIVE.md` · Map: `FEDERATION_RECONCILIATION.md` · Wiring: `FEDERATION_WIRING.md` · Tracker: `FAMILY_PHASES.md`

## CURRENT PHASE

**Village:** **18B LIVE**. **16E** still needs you in Heart Square.  
**Federation:** Gemini speech **LIVE**. **The Axiom Codex** accepted a federation notice **LIVE** (`aster.gameworld_notice` VERIFIED, HOME.json updated; CLI `prove consume` is the action, not the world’s name). Full Aster test **FAIL** (live negatives still open). Apex/Codex **not** on the bus.

## Next task

1. **The Axiom Codex notice LIVE.** World name is The Axiom Codex, not “consume.” Evidence: `D:\Court\federation\PROVE_GAMEWORLD_CONSUME.json`. Hearth authorized; Aster performed; `HOME.json` `federation.last_consumed` written. Full Aster test still **FAIL** (live negatives). Do not add Apex/Codex on the bus until their doors are up (Apex `:8770` down this audit).  
2. **Aster lab** was hanging, not dead: Hearth `:8790` was down and `/api/status` blocked on Ollama tags + Hearth. Door hardened; Hearth restarted; lab `:8791` **200** `id=aster` ~0.7s.  
3. **Agent readiness:** `D:\Court\federation\AGENT_READINESS.json`. Mom check: `python -m federation.prove status`. Village: Heart Square 16E when you want it.

Baseline tag `living-home-baseline-001` — do not rewrite.
