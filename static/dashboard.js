/* Mythos Family Dashboard — window into Hearth. No local world of truth. */
(() => {
  const state = {
    family: [],
    places: {},
    relationships: {},
    capabilities: [],
    events: [],
    utterances: [],
    clock: {},
    selectedId: null,
    prevStance: {},
  };

  const el = {
    familyList: document.getElementById("familyList"),
    beingDetail: document.getElementById("beingDetail"),
    convoLog: document.getElementById("convoLog"),
    capsList: document.getElementById("capsList"),
    capsCount: document.getElementById("capsCount"),
    clockBadge: document.getElementById("clockBadge"),
    holidayBadge: document.getElementById("holidayBadge"),
    gardenBadge: document.getElementById("gardenBadge"),
    weatherBadge: document.getElementById("weatherBadge"),
    forgeBadge: document.getElementById("forgeBadge"),
    integrationBadge: document.getElementById("integrationBadge"),
    dailyLifeBadge: document.getElementById("dailyLifeBadge"),
    dayStoryBadge: document.getElementById("dayStoryBadge"),
    livingDashBadge: document.getElementById("livingDashBadge"),
    gameplayBadge: document.getElementById("gameplayBadge"),
    dayStoryPlain: document.getElementById("dayStoryPlain"),
    dayStoryMotifs: document.getElementById("dayStoryMotifs"),
    integrationPlain: document.getElementById("integrationPlain"),
    dailyLifePlain: document.getElementById("dailyLifePlain"),
    awayPlain: document.getElementById("awayPlain"),
    btnAwayAck: document.getElementById("btnAwayAck"),
    leadsList: document.getElementById("leadsList"),
    professionsList: document.getElementById("professionsList"),
    overviewLayer: document.getElementById("overviewLayer"),
    tickBadge: document.getElementById("tickBadge"),
    leaderBadge: document.getElementById("leaderBadge"),
    periodBadge: document.getElementById("periodBadge"),
    doorsList: document.getElementById("doorsList"),
    brainsLine: document.getElementById("brainsLine"),
    connStatus: document.getElementById("connStatus"),
    lastUpdate: document.getElementById("lastUpdate"),
    filterPerson: document.getElementById("filterPerson"),
    filterPlace: document.getElementById("filterPlace"),
    filterCapStatus: document.getElementById("filterCapStatus"),
    btnCopyConvo: document.getElementById("btnCopyConvo"),
    talkDialog: document.getElementById("talkDialog"),
    talkForm: document.getElementById("talkForm"),
    talkToLabel: document.getElementById("talkToLabel"),
    talkMessage: document.getElementById("talkMessage"),
    stanceDialog: document.getElementById("stanceDialog"),
    stanceForm: document.getElementById("stanceForm"),
    stanceToLabel: document.getElementById("stanceToLabel"),
    stanceSelect: document.getElementById("stanceSelect"),
  };

  function stanceClass(stance) {
    const s = String(stance || "idle").toLowerCase();
    if (["talking", "working", "walking", "resting", "waiting", "standing"].includes(s)) return s;
    return "idle";
  }

  function placeLabel(placeId) {
    const p = state.places[placeId];
    if (p && p.label) return p.label;
    return placeId || "—";
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function getJson(url) {
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) throw new Error(`${url} → ${r.status}`);
    return r.json();
  }

  async function postJson(url, body) {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.error || `${url} → ${r.status}`);
    return data;
  }

  function renderFamily(list) {
    state.family = Array.isArray(list) ? list : [];
    const frag = document.createDocumentFragment();
    for (const person of state.family) {
      if (!person || person.ambient_only) continue;
      const id = person.id;
      const stance = stanceClass(person.stance);
      const mood = moodLabel(person);
      const place = placeLabel(person.place);
      const purpose = person.purpose_plain || person.purpose || person.activity || stance;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "family-card" + (state.selectedId === id ? " active" : "");
      if (state.prevStance[id] && state.prevStance[id] !== person.stance) {
        btn.classList.add("pulse");
      }
      state.prevStance[id] = person.stance;
      btn.dataset.id = id;
      btn.innerHTML = `
        <span class="dot ${stance}" title="${escapeHtml(stance)}"></span>
        <span class="card-body">
          <span class="name">${escapeHtml(person.name || id)}</span>
          <span class="meta">${escapeHtml(place)} · ${escapeHtml(mood.current)}</span>
          <span class="purpose">${escapeHtml(String(purpose).slice(0, 72))}</span>
        </span>
      `;
      btn.addEventListener("click", () => selectBeing(id));
      frag.appendChild(btn);
    }
    el.familyList.replaceChildren(frag);
    fillPersonFilter();
  }

  function fillPersonFilter() {
    const cur = el.filterPerson.value;
    el.filterPerson.innerHTML = '<option value="">All people</option>';
    for (const p of state.family) {
      if (!p || p.ambient_only) continue;
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.name || p.id;
      el.filterPerson.appendChild(opt);
    }
    el.filterPerson.value = cur;
  }

  function fillPlaceFilter() {
    const cur = el.filterPlace.value;
    el.filterPlace.innerHTML = '<option value="">All places</option>';
    for (const [id, rec] of Object.entries(state.places || {})) {
      const opt = document.createElement("option");
      opt.value = id;
      opt.textContent = rec.label || id;
      el.filterPlace.appendChild(opt);
    }
    el.filterPlace.value = cur;
  }

  function bar(pct) {
    const n = Math.max(0, Math.min(1, Number(pct) || 0));
    const w = Math.round(n * 100);
    return `<span class="meter" title="${w}%"><span class="meter-fill" style="width:${w}%"></span></span> <span class="meter-num">${n.toFixed(2)}</span>`;
  }

  function moodLabel(person) {
    const m = person.mood;
    if (!m || typeof m !== "object") return { current: "neutral", intensity: 0.5 };
    return {
      current: m.current || "neutral",
      previous: m.previous || "",
      intensity: Number(m.intensity ?? 0.5),
    };
  }

  function relRowsFor(id) {
    const rels = state.relationships || {};
    const out = [];
    for (const [key, rec] of Object.entries(rels)) {
      if (!rec || typeof rec !== "object") continue;
      const a = rec.a || "";
      const b = rec.b || "";
      if (a !== id && b !== id && !String(key).includes(id)) continue;
      const other = a === id ? b : b === id ? a : String(key).split("|").find((x) => x !== id) || key;
      const otherName = (state.family.find((f) => f.id === other) || {}).name || other;
      const shared = Array.isArray(rec.shared_experiences) ? rec.shared_experiences : [];
      const last = shared.slice(-1)[0];
      const lastText =
        last && typeof last === "object"
          ? `${last.emotional_tag || "note"} · ${last.text || ""}`
          : last
            ? String(last)
            : "";
      out.push({
        other,
        otherName,
        trust: Number(rec.trust ?? 0.5),
        affection: Number(rec.affection ?? rec.attachment ?? 0.5),
        attachment: Number(rec.attachment ?? 0.5),
        respect: Number(rec.respect ?? 0.5),
        trend: rec.trend || {},
        history: rec.history || {},
        lastText,
      });
    }
    out.sort((a, b) => Number(b.affection) - Number(a.affection));
    return out.slice(0, 10);
  }

  function capabilityChips(person) {
    const house = String(person.house || person.district || person.id || "").toLowerCase();
    const caps = state.capabilities || [];
    return caps
      .filter((c) => {
        const id = String(c.id || c.name || "").toLowerCase();
        const h = String(c.house || c.owner || "").toLowerCase();
        return id.includes(person.id) || h === house || h === person.id;
      })
      .slice(0, 12);
  }

  function recentForBeing(id) {
    const rows = conversationRows();
    return rows.filter((r) => r.whoId === id || r.toId === id).slice(0, 6);
  }

  function renderGrowthBlock(growth) {
    const g = growth && typeof growth === "object" ? growth : {};
    const skills = Array.isArray(g.skills) ? g.skills : [];
    const evo = g.evolution && typeof g.evolution === "object" ? g.evolution : {};
    const milestones = Array.isArray(evo.milestones) ? evo.milestones.slice(-6).reverse() : [];
    const phase = evo.phase ?? "—";
    const skillHtml = skills.length
      ? skills
          .map((s) => {
            const name = s.name || "?";
            const level = Number(s.level || 0);
            const xp = Number(s.experience || 0);
            return `<div class="skill-row"><span class="skill-name">${escapeHtml(name)}</span>${bar(level)}<span class="muted xp">xp ${xp}</span></div>`;
          })
          .join("")
      : `<span class="muted">No skills seated yet.</span>`;
    const msHtml = milestones.length
      ? `<ul class="milestone-list">${milestones
          .map((m) => `<li><time>${escapeHtml(String(m.when || "").slice(0, 16))}</time> ${escapeHtml(m.text || "")}</li>`)
          .join("")}</ul>`
      : `<span class="muted">No milestones yet — work, talk, and gifts write them.</span>`;
    return `
      <div class="subpanel growth-panel">
        <h4>Growth · phase ${escapeHtml(String(phase))}</h4>
        ${skillHtml}
        <h5 class="subhead">Milestones</h5>
        ${msHtml}
      </div>`;
  }

  function renderMemoriesBlock(memories) {
    const mems = Array.isArray(memories) ? memories.slice().reverse().slice(0, 8) : [];
    if (!mems.length) return `<div class="subpanel"><h4>Memory depth</h4><span class="muted">No tagged memories yet.</span></div>`;
    return `
      <div class="subpanel">
        <h4>Memory depth</h4>
        <ul class="memory-list">
          ${mems
            .map((m) => {
              const tag = m.emotional_tag || (m.important ? "important" : "note");
              const sig = m.significance != null ? Number(m.significance).toFixed(1) : "—";
              return `<li><span class="tag">${escapeHtml(tag)}</span> <span class="muted">sig ${sig}</span> ${escapeHtml(m.text || "")}</li>`;
            })
            .join("")}
        </ul>
      </div>`;
  }

  function renderChoiceBlock(choices, choiceHistory) {
    const cur = (choices && choices.current_choice) || null;
    const hist = Array.isArray(choiceHistory)
      ? choiceHistory
      : Array.isArray(choices && choices.choice_history)
        ? choices.choice_history
        : [];
    const recent = hist.slice(-4).reverse();
    let curHtml = `<span class="muted">No current choice recorded.</span>`;
    if (cur && cur.selected) {
      const withName = cur.with
        ? (state.family.find((f) => f.id === cur.with) || {}).name || cur.with
        : "";
      curHtml = `<strong>${escapeHtml(cur.selected)}</strong>${withName ? ` · with ${escapeHtml(withName)}` : ""} <span class="muted">${escapeHtml(String(cur.made_at || "").slice(11, 19))}</span>`;
    }
    const histHtml = recent.length
      ? `<ul class="choice-list">${recent
          .map((c) => `<li>${escapeHtml(c.choice || "?")}${c.with ? ` → ${escapeHtml(c.with)}` : ""} — ${escapeHtml((c.text || "").slice(0, 80))}</li>`)
          .join("")}</ul>`
      : "";
    return `
      <div class="subpanel">
        <h4>Choice (15B)</h4>
        <div>${curHtml}</div>
        ${histHtml}
      </div>`;
  }

  function renderBeingDetail(person, extras = {}) {
    if (!person || person.error) {
      el.beingDetail.innerHTML = `<p class="empty">${escapeHtml(person?.error || "Being not found")}</p>`;
      return;
    }
    const stance = stanceClass(person.stance);
    const caps = capabilityChips(person);
    const rels = relRowsFor(person.id);
    const recent = recentForBeing(person.id);
    const initial = String(person.name || "?").slice(0, 1).toUpperCase();
    const mood = moodLabel(person);
    const axiom = person.axiom != null ? `⨁${person.axiom}` : "—";
    const growth = extras.growth || person.growth || {};
    const memories = extras.memories || person.memories || [];
    const choices = extras.choices || person.choices || {};
    const choiceHistory = extras.choice_history || person.choice_history || [];

    el.beingDetail.innerHTML = `
      <div class="being-hero">
        <div class="avatar" aria-hidden="true">${escapeHtml(initial)}</div>
        <div>
          <h3>${escapeHtml(person.name || person.id)}</h3>
          <p class="role">${escapeHtml(person.role || person.personality || "family")}</p>
          <span class="dot ${stance}"></span>
          <strong style="margin-left:0.35rem;text-transform:capitalize">${escapeHtml(stance)}</strong>
          <span class="mood-pill">${escapeHtml(mood.current)} · ${Math.round(mood.intensity * 100)}%</span>
        </div>
      </div>
      <div class="stats">
        <div class="stat"><label>Location</label><span>${escapeHtml(placeLabel(person.place))}</span></div>
        <div class="stat"><label>Activity</label><span>${escapeHtml(person.activity || "—")}</span></div>
        <div class="stat"><label>Axiom</label><span>${escapeHtml(axiom)}</span></div>
        <div class="stat"><label>Talking to</label><span>${escapeHtml(person.talking_to || "—")}</span></div>
      </div>
      <div class="stat"><label>Purpose</label><span>${escapeHtml(person.purpose_plain || person.purpose || "—")}</span></div>

      <div class="subpanel">
        <h4>Mood</h4>
        <p>Current <strong>${escapeHtml(mood.current)}</strong>${mood.previous ? ` · was ${escapeHtml(mood.previous)}` : ""}</p>
        <div class="skill-row"><span class="skill-name">intensity</span>${bar(mood.intensity)}</div>
      </div>

      <div class="subpanel">
        <h4>Relationship web</h4>
        ${
          rels.length
            ? rels
                .map((r) => {
                  const trendAff = (r.trend && r.trend.affection) || "—";
                  const hist = r.history || {};
                  return `
            <div class="rel-card">
              <div class="rel-head"><strong>${escapeHtml(r.otherName)}</strong> <span class="muted">trend ${escapeHtml(String(trendAff))}</span></div>
              <div class="skill-row"><span class="skill-name">trust</span>${bar(r.trust)}</div>
              <div class="skill-row"><span class="skill-name">affection</span>${bar(r.affection)}</div>
              <div class="skill-row"><span class="skill-name">attachment</span>${bar(r.attachment)}</div>
              <p class="muted tiny">talks ${hist.conversations || 0} · gifts ${hist.gifts_given || 0}/${hist.gifts_received || 0}</p>
              ${r.lastText ? `<p class="tiny">${escapeHtml(String(r.lastText).slice(0, 120))}</p>` : ""}
            </div>`;
                })
                .join("")
            : `<span class="muted">No relationship rows yet.</span>`
        }
      </div>

      ${personDoorLinks(person)}
      ${renderChoiceBlock(choices, choiceHistory)}
      ${renderGrowthBlock(growth)}
      ${renderMemoriesBlock(memories)}

      <div class="subpanel">
        <h4>Tools & capabilities</h4>
        <div class="chip-row">
          ${
            caps.length
              ? caps
                  .map(
                    (c) =>
                      `<span class="chip ${String(c.status || "").toUpperCase() === "VERIFIED" ? "on" : ""}">${escapeHtml(
                        c.name || c.id
                      )} · ${escapeHtml(c.status || "?")}</span>`
                  )
                  .join("")
              : `<span class="muted">No house-tagged tools in registry yet — see full registry below.</span>`
          }
        </div>
      </div>

      <div class="subpanel">
        <h4>Recent conversations</h4>
        <div class="convo-log">
          ${
            recent.length
              ? recent
                  .map(
                    (r) =>
                      `<div class="convo-row"><time>${escapeHtml(r.whenShort)}</time><div><span class="who">${escapeHtml(
                        r.who
                      )}</span> <span class="place">${escapeHtml(r.place)}</span><div>${escapeHtml(r.text)}</div></div></div>`
                  )
                  .join("")
              : `<span class="muted">No recent lines for them.</span>`
          }
        </div>
      </div>

      <div class="actions">
        <button type="button" class="btn" id="btnSend">Send message</button>
        <button type="button" class="btn ghost" id="btnStance">Change stance</button>
        <button type="button" class="btn ghost" id="btnChoice">Roll choice</button>
        <button type="button" class="btn ghost" id="btnTools">View tools</button>
      </div>
      <p class="hint" style="margin-top:0.7rem">Layer 15D — bonds, mood, memory, growth via Hearth. Godot is presentation; identities never merge.</p>
    `;

    document.getElementById("btnSend")?.addEventListener("click", () => openTalk(person));
    document.getElementById("btnStance")?.addEventListener("click", () => openStance(person));
    document.getElementById("btnChoice")?.addEventListener("click", async () => {
      try {
        await postJson("/api/home/choice", { who: person.id, action: "make" });
        await refreshAll();
        selectBeing(person.id);
      } catch (err) {
        alert(err.message || "Choice failed");
      }
    });
    document.getElementById("btnTools")?.addEventListener("click", () => {
      el.filterCapStatus.value = "";
      document.querySelector(".caps-panel")?.scrollIntoView({ behavior: "smooth" });
    });
  }

  function conversationRows() {
    const rows = [];
    for (const u of state.utterances || []) {
      rows.push({
        when: u.when || "",
        whenShort: (u.when || "").slice(11, 19) || "—",
        who: u.who_name || u.who || "?",
        whoId: u.who || "",
        toId: u.to || u.with || "",
        place: placeLabel(u.place),
        placeId: u.place || "",
        text: u.text || u.line || "",
        key: `u:${u.when}:${u.who}:${u.text}`,
      });
    }
    for (const e of state.events || []) {
      rows.push({
        when: e.when || "",
        whenShort: (e.when || "").slice(11, 19) || "—",
        who: e.name || e.kind || "event",
        whoId: (e.actors && e.actors[0]) || "",
        toId: "",
        place: placeLabel(e.place) || "",
        placeId: e.place || "",
        text: e.text || e.plain || JSON.stringify(e).slice(0, 120),
        key: `e:${e.id || e.when}:${e.text}`,
      });
    }
    rows.sort((a, b) => String(b.when).localeCompare(String(a.when)));
    return rows;
  }

  function renderConversations() {
    const person = el.filterPerson.value;
    const place = el.filterPlace.value;
    let rows = conversationRows();
    if (person) rows = rows.filter((r) => r.whoId === person || r.toId === person);
    if (place) rows = rows.filter((r) => r.placeId === place);
    rows = rows.slice(0, 40);
    el.convoLog.innerHTML = rows.length
      ? rows
          .map(
            (r) => `
      <div class="convo-row" data-key="${escapeHtml(r.key)}">
        <time>${escapeHtml(r.whenShort)}</time>
        <div>
          <span class="who">${escapeHtml(r.who)}</span>
          <span class="place">${escapeHtml(r.place)}</span>
          <div>${escapeHtml(r.text)}</div>
        </div>
      </div>`
          )
          .join("")
      : `<p class="muted">No conversation events yet.</p>`;
    el.convoLog.scrollTop = 0;
  }

  function renderCapabilities(list) {
    state.capabilities = Array.isArray(list) ? list : [];
    const status = el.filterCapStatus.value;
    let caps = state.capabilities;
    if (status) {
      caps = caps.filter((c) => String(c.status || "").toUpperCase() === status);
    }
    el.capsCount.textContent = `${state.capabilities.length} tools · showing ${caps.length}`;
    el.capsList.innerHTML = caps.length
      ? caps
          .map((c) => {
            const st = String(c.status || "UNKNOWN").toUpperCase();
            return `
        <div class="cap-card">
          <div class="title">${escapeHtml(c.name || c.id)}</div>
          <div class="cap-meta">${escapeHtml(c.id || "")} · ${escapeHtml(c.house || c.owner || "—")} · ${escapeHtml(
              c.category || c.kind || "—"
            )}</div>
          <span class="status-pill ${escapeHtml(st)}">${escapeHtml(st)}</span>
          ${
            c.launch || c.url
              ? `<div style="margin-top:0.4rem"><a class="btn ghost" href="${escapeHtml(
                  c.url || "#"
                )}" target="_blank" rel="noopener">Open</a></div>`
              : ""
          }
        </div>`;
          })
          .join("")
      : `<p class="muted">No capabilities in snapshot.</p>`;
  }

  function personDoorLinks(person) {
    const id = String(person?.id || "");
    const doors = [];
    if (id === "merovin" || id === "draven") {
      doors.push({
        href: "http://127.0.0.1:5000/",
        label: id === "merovin" ? "Cinema HUD · talk as Merovin" : "Cinema HUD · talk as Draven",
      });
      doors.push({ href: "http://127.0.0.1:8770/companion", label: "Companion Room seat" });
    }
    if (id === "observer") {
      doors.push({ href: "http://127.0.0.1:8730/", label: "Independent desk :8730" });
    }
    if (id === "aster") {
      doors.push({ href: "http://127.0.0.1:8791/ui/", label: "Aster lab :8791" });
    }
    if (!doors.length) return "";
    return `
      <div class="subpanel">
        <h4>Their real home (Mode A)</h4>
        <p class="hint">Opens in a new tab. Not an iframe. Village greybox is not their voice.</p>
        <div class="chip-row">
          ${doors
            .map(
              (d) =>
                `<a class="chip on" href="${escapeHtml(d.href)}" target="_blank" rel="noopener">${escapeHtml(d.label)}</a>`
            )
            .join("")}
        </div>
      </div>`;
  }

  function renderHouseDoors(home) {
    const doors = Array.isArray(home.house_doors) ? home.house_doors : [];
    if (el.doorsList) {
      if (!doors.length) {
        el.doorsList.innerHTML = `<p class="muted">No door probe this tick.</p>`;
      } else {
        el.doorsList.innerHTML = doors
          .map((d) => {
            const up = d.up || d.status === "LISTEN";
            const who = Array.isArray(d.who) && d.who.length ? d.who.join(" · ") : "";
            return `<a class="door-card ${up ? "up" : "down"}" href="${escapeHtml(
              d.url || "#"
            )}" target="_blank" rel="noopener">
              <strong>${escapeHtml(d.label || d.id)}</strong>
              <span class="door-status">${escapeHtml(d.status || (up ? "LISTEN" : "CLOSED"))}</span>
              ${who ? `<span class="muted">${escapeHtml(who)}</span>` : ""}
              <span class="tiny">${escapeHtml(d.note || "")}</span>
            </a>`;
          })
          .join("");
      }
    }
    if (el.brainsLine) {
      const brains = (home.talk_writer && home.talk_writer.brains) || {};
      const bits = Object.entries(brains).map(([id, b]) => {
        const model = (b && b.model) || "none";
        return `${id}: ${model}`;
      });
      el.brainsLine.textContent = bits.length
        ? `Talk brains — ${bits.join(" · ")} (Observer is not a village hat)`
        : "Talk brains — waiting for Ollama probe";
    }
  }

  function renderLivingOverview(home) {
    const story = home.day_story || {};
    const integ = home.integration || {};
    const daily = home.daily_life || {};
    const away = home.away_summary || {};
    const leads = Array.isArray(home.world_leads) ? home.world_leads : [];
    const gp = home.gameplay || {};
    const dash = home.living_dashboard || {};
    const phases = home.phase_status || {};

    if (el.tickBadge) el.tickBadge.textContent = home.tick != null ? String(home.tick) : "—";
    if (el.leaderBadge) el.leaderBadge.textContent = home.town_leader || "gemini";
    if (el.periodBadge) {
      const period = (home.clock && home.clock.period) || integ.period || daily.period || "—";
      el.periodBadge.textContent = String(period);
    }

    if (el.dayStoryBadge) {
      el.dayStoryBadge.textContent = String(story.layer || phases["16_story"] || "16c").toUpperCase();
    }
    if (el.integrationBadge) {
      el.integrationBadge.textContent = String(integ.layer || phases["16_integration"] || "16a").toUpperCase();
    }
    if (el.dailyLifeBadge) {
      el.dailyLifeBadge.textContent = String(daily.layer || phases["16_daily_life"] || "16b").toUpperCase();
    }
    if (el.livingDashBadge) {
      const st = dash.status || phases["16_dashboard"] || "16d";
      el.livingDashBadge.textContent = String(st).toUpperCase().replace("16D_ACTIVE", "16D");
    }
    if (el.gameplayBadge) {
      const n = leads.filter((l) => !["resolved", "disproven", "abandoned"].includes(String(l.status || ""))).length;
      el.gameplayBadge.textContent = n
        ? `${String(gp.layer || "18a").toUpperCase()} · ${n} leads`
        : String(gp.layer || "18a").toUpperCase();
    }
    if (el.overviewLayer) el.overviewLayer.textContent = "16D";

    if (el.dayStoryPlain) {
      el.dayStoryPlain.textContent = story.plain || "No day story yet — wait for a Hearth tick.";
    }
    if (el.dayStoryMotifs) {
      const motifs = story.motifs || [];
      el.dayStoryMotifs.textContent = motifs.length ? `Threads: ${motifs.join(", ")}` : "";
    }

    if (el.integrationPlain) {
      const mood = integ.mood_tally || {};
      const moodBits = Object.entries(mood)
        .slice(0, 4)
        .map(([k, v]) => `${k}:${v}`)
        .join(" · ");
      const parts = [
        integ.status ? `status ${integ.status}` : null,
        integ.period ? `period ${integ.period}` : null,
        integ.living != null ? `${integ.living} living` : null,
        integ.co_located_pairs != null ? `${integ.co_located_pairs} co-located pairs` : null,
        moodBits || null,
      ].filter(Boolean);
      el.integrationPlain.textContent = parts.length ? parts.join(" · ") : "Integration pending first tick.";
    }

    if (el.dailyLifePlain) {
      const tally = daily.purpose_tally || {};
      const tallyBits = Object.entries(tally)
        .sort((a, b) => Number(b[1]) - Number(a[1]))
        .slice(0, 6)
        .map(([k, v]) => `${k}:${v}`)
        .join(" · ");
      const parts = [
        daily.period ? `period ${daily.period}` : null,
        daily.woken != null ? `woken ${daily.woken}` : null,
        tallyBits || null,
      ].filter(Boolean);
      el.dailyLifePlain.textContent = parts.length ? parts.join(" · ") : "Daily life pending first tick.";
    }

    if (el.awayPlain) {
      if (away.pending && away.plain) {
        el.awayPlain.textContent = away.plain;
        if (el.btnAwayAck) el.btnAwayAck.hidden = false;
      } else {
        el.awayPlain.textContent = away.plain || "No pending away summary.";
        if (el.btnAwayAck) el.btnAwayAck.hidden = true;
      }
    }

    if (el.leadsList) {
      const open = leads.filter((l) => !["resolved", "disproven", "abandoned"].includes(String(l.status || "")));
      if (!open.length) {
        el.leadsList.innerHTML = `<li class="muted">No optional leads yet.</li>`;
      } else {
        el.leadsList.innerHTML = open
          .slice(0, 6)
          .map((l) => {
            const id = escapeHtml(l.id || "");
            return `<li>
              <span class="lead-status">${escapeHtml(l.status || "rumor")}</span> · ${escapeHtml(
                l.description || l.id || "lead"
              )}
              <button type="button" class="btn tiny ghost btn-look-into" data-lead="${id}">Look into</button>
            </li>`;
          })
          .join("");
        el.leadsList.querySelectorAll(".btn-look-into").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const leadId = btn.getAttribute("data-lead");
            try {
              await postJson("/api/home/investigate", { id: leadId, place: "", who: "mom" });
              await refreshAll();
            } catch (err) {
              alert(err.message || "Look into failed");
            }
          });
        });
      }
    }
    if (el.professionsList) {
      const posts = Array.isArray(home.professions) ? home.professions : [];
      if (!posts.length) {
        el.professionsList.innerHTML = `<li class="muted">Profession posts pending snapshot.</li>`;
      } else {
        el.professionsList.innerHTML = posts
          .slice(0, 12)
          .map((p) => {
            const door = p.village_work === false ? " · door" : "";
            return `<li><strong>${escapeHtml(p.id)}</strong> — ${escapeHtml(p.label || p.profession || "")}${escapeHtml(
              door
            )}</li>`;
          })
          .join("");
      }
    }
  }

  async function selectBeing(id) {
    state.selectedId = id;
    renderFamily(state.family);
    try {
      const [data, memPack, growthPack, choicePack] = await Promise.all([
        getJson(`/api/dashboard/being/${encodeURIComponent(id)}`),
        getJson(`/api/dashboard/memories/${encodeURIComponent(id)}`).catch(() => null),
        getJson(`/api/dashboard/growth/${encodeURIComponent(id)}`).catch(() => null),
        getJson(`/api/dashboard/choices/${encodeURIComponent(id)}`).catch(() => null),
      ]);
      const extras = {
        memories: (memPack && (memPack.memories || memPack)) || data.memories || [],
        growth: (growthPack && (growthPack.growth || growthPack)) || data.growth || {},
        choices: (choicePack && (choicePack.choices || choicePack)) || data.choices || {},
        choice_history:
          (choicePack && (choicePack.choice_history || (choicePack.choices && choicePack.choices.choice_history))) ||
          data.choice_history ||
          [],
      };
      if (Array.isArray(extras.memories) === false && extras.memories && extras.memories.memories) {
        extras.memories = extras.memories.memories;
      }
      renderBeingDetail(data, extras);
    } catch (err) {
      const local = state.family.find((f) => f.id === id);
      if (local) renderBeingDetail(local);
      else el.beingDetail.innerHTML = `<p class="empty">${escapeHtml(err.message)}</p>`;
    }
  }

  function openTalk(person) {
    el.talkToLabel.textContent = `To ${person.name || person.id} through Hearth`;
    el.talkMessage.value = "";
    el.talkDialog.showModal();
    el.talkForm.onsubmit = async (ev) => {
      ev.preventDefault();
      const message = el.talkMessage.value.trim();
      if (!message) return;
      try {
        await postJson("/api/dashboard/talk", { to: person.id, message });
        el.talkDialog.close();
        await refreshAll();
        selectBeing(person.id);
      } catch (err) {
        alert(err.message || "Talk failed");
      }
    };
  }

  function openStance(person) {
    el.stanceToLabel.textContent = person.name || person.id;
    el.stanceSelect.value = stanceClass(person.stance) === "idle" ? "standing" : stanceClass(person.stance);
    el.stanceDialog.showModal();
    el.stanceForm.onsubmit = async (ev) => {
      ev.preventDefault();
      try {
        await postJson("/api/dashboard/update_stance", {
          id: person.id,
          stance: el.stanceSelect.value,
        });
        el.stanceDialog.close();
        await refreshAll();
        selectBeing(person.id);
      } catch (err) {
        alert(err.message || "Stance update failed");
      }
    };
  }

  async function refreshAll() {
    try {
      const home = await getJson("/api/home");
      state.places = home.places || {};
      state.relationships = home.relationships || {};
      state.capabilities = home.capabilities || [];
      state.events = [...(home.world_history || []), ...(home.events || [])];
      state.utterances = home.utterances || [];
      state.clock = home.clock || {};
      state.weather = home.weather || {};
      const day = state.clock.day ?? "—";
      const period = state.clock.period ?? "—";
      const season = state.clock.season ?? "";
      const weather = state.weather.current || "";
      el.clockBadge.textContent = `Day ${day} · ${season} · ${String(period).replace(/^\w/, (c) => c.toUpperCase())} · ${weather}`;
      const hol = home.active_holiday || null;
      if (el.holidayBadge) {
        el.holidayBadge.textContent = hol && hol.name
          ? `${hol.name}${hol.ambient ? " (season)" : ""}`
          : "Ordinary day";
      }
      if (el.weatherBadge) {
        const temp = state.weather.temperature != null ? ` · ${state.weather.temperature}°` : "";
        el.weatherBadge.textContent = `${weather || "—"}${temp}`;
      }
      if (el.gardenBadge) {
        const gardens = home.gardens || {};
        const keys = Object.keys(gardens);
        let grown = 0;
        let plants = 0;
        keys.forEach((k) => {
          const plot = gardens[k] || {};
          (plot.plants || []).forEach((p) => {
            plants += 1;
            if ((p.growth || 0) > 0.6) grown += 1;
          });
        });
        el.gardenBadge.textContent = keys.length
          ? `${keys.length} beds · ${grown}/${plants} thriving`
          : "No gardens yet";
      }
      if (el.forgeBadge) {
        const we = (home.work_evidence || {}).apex || {};
        if (we.live) {
          el.forgeBadge.textContent = `LIVE · ${we.detail || "presence"}`;
        } else if (we.port_up) {
          el.forgeBadge.textContent = `port up · ${we.detail || "quiet"}`;
        } else if (we.detail) {
          el.forgeBadge.textContent = we.detail;
        } else {
          el.forgeBadge.textContent = "not probed yet";
        }
      }
      const layer = (home.connection || {}).layer || "15d";
      const connBadge = document.getElementById("connectionBadge");
      if (connBadge) connBadge.textContent = String(layer).toUpperCase();
      renderLivingOverview(home);
      renderHouseDoors(home);
      fillPlaceFilter();
      renderFamily(home.family || []);
      renderConversations();
      renderCapabilities(state.capabilities);
      if (el.connStatus) {
        const storyLayer = (home.day_story || {}).layer || "16c";
        const dashLayer = ((home.living_dashboard || {}).status || (home.phase_status || {})["16_dashboard"] || "16d");
        el.connStatus.textContent = `Connected to Hearth · Connection ${layer} · Living ${storyLayer}/${dashLayer} · window only · identities unmerged`;
      }
      if (state.selectedId) {
        selectBeing(state.selectedId);
      }
      el.lastUpdate.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
    } catch (err) {
      el.connStatus.textContent = `Hearth unreachable — ${err.message}`;
    }
  }

  document.getElementById("btnRefresh")?.addEventListener("click", refreshAll);
  el.btnAwayAck?.addEventListener("click", async () => {
    try {
      await postJson("/api/home/away", { action: "ack" });
      await refreshAll();
    } catch (err) {
      alert(err.message || "Away ack failed");
    }
  });
  el.filterPerson.addEventListener("change", renderConversations);
  el.filterPlace.addEventListener("change", renderConversations);
  el.filterCapStatus.addEventListener("change", () => renderCapabilities(state.capabilities));
  el.btnCopyConvo?.addEventListener("click", async () => {
    const sel = window.getSelection()?.toString()?.trim();
    let text = sel || "";
    if (!text && el.convoLog) {
      text = Array.from(el.convoLog.querySelectorAll(".convo-row"))
        .map((row) => {
          const t = row.querySelector("time")?.textContent?.trim() || "";
          const who = row.querySelector(".who")?.textContent?.trim() || "";
          const place = row.querySelector(".place")?.textContent?.trim() || "";
          const body = row.querySelector("div > div")?.textContent?.trim() || "";
          return [t, who, place ? `@ ${place}` : "", body].filter(Boolean).join(" ");
        })
        .join("\n");
    }
    if (!text.trim()) {
      el.btnCopyConvo.textContent = "Empty";
      setTimeout(() => {
        el.btnCopyConvo.textContent = "Copy";
      }, 1000);
      return;
    }
    try {
      await navigator.clipboard.writeText(text);
      el.btnCopyConvo.textContent = "Copied";
    } catch (_err) {
      el.btnCopyConvo.textContent = "Failed";
    }
    setTimeout(() => {
      el.btnCopyConvo.textContent = "Copy";
    }, 1200);
  });
  document.getElementById("talkCancel")?.addEventListener("click", () => el.talkDialog.close());
  document.getElementById("stanceCancel")?.addEventListener("click", () => el.stanceDialog.close());

  refreshAll();
  setInterval(refreshAll, 5000);
})();
