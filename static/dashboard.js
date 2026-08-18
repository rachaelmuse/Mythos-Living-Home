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
    connStatus: document.getElementById("connStatus"),
    lastUpdate: document.getElementById("lastUpdate"),
    filterPerson: document.getElementById("filterPerson"),
    filterPlace: document.getElementById("filterPlace"),
    filterCapStatus: document.getElementById("filterCapStatus"),
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
        <span class="name">${escapeHtml(person.name || id)}</span>
        <span class="meta">${escapeHtml(stance)}</span>
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

  function relRowsFor(id) {
    const rels = state.relationships || {};
    const out = [];
    for (const [key, rec] of Object.entries(rels)) {
      if (!key.includes(id)) continue;
      const parts = key.split("|");
      const other = parts.find((x) => x !== id) || key;
      const otherName = (state.family.find((f) => f.id === other) || {}).name || other;
      out.push({
        other,
        otherName,
        trust: rec.trust ?? rec.familiarity ?? 0,
        text: (rec.shared_experiences || []).slice(-1)[0],
      });
    }
    out.sort((a, b) => Number(b.trust) - Number(a.trust));
    return out.slice(0, 8);
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

  function renderBeingDetail(person) {
    if (!person || person.error) {
      el.beingDetail.innerHTML = `<p class="empty">${escapeHtml(person?.error || "Being not found")}</p>`;
      return;
    }
    const stance = stanceClass(person.stance);
    const caps = capabilityChips(person);
    const rels = relRowsFor(person.id);
    const recent = recentForBeing(person.id);
    const initial = String(person.name || "?").slice(0, 1).toUpperCase();

    el.beingDetail.innerHTML = `
      <div class="being-hero">
        <div class="avatar" aria-hidden="true">${escapeHtml(initial)}</div>
        <div>
          <h3>${escapeHtml(person.name || person.id)}</h3>
          <p class="role">${escapeHtml(person.role || person.personality || "family")}</p>
          <span class="dot ${stance}"></span>
          <strong style="margin-left:0.35rem;text-transform:capitalize">${escapeHtml(stance)}</strong>
        </div>
      </div>
      <div class="stats">
        <div class="stat"><label>Location</label><span>${escapeHtml(placeLabel(person.place))}</span></div>
        <div class="stat"><label>Activity</label><span>${escapeHtml(person.activity || "—")}</span></div>
        <div class="stat"><label>Stance</label><span>${escapeHtml(person.stance || "—")}</span></div>
        <div class="stat"><label>Talking to</label><span>${escapeHtml(person.talking_to || "—")}</span></div>
      </div>
      <div class="stat"><label>Purpose</label><span>${escapeHtml(person.purpose_plain || person.purpose || "—")}</span></div>

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
        <h4>Relationships</h4>
        <div class="chip-row">
          ${
            rels.length
              ? rels
                  .map(
                    (r) =>
                      `<span class="chip">${escapeHtml(r.otherName)} · trust ${Number(r.trust).toFixed(2)}</span>`
                  )
                  .join("")
              : `<span class="muted">No relationship rows yet.</span>`
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
        <button type="button" class="btn ghost" id="btnTools">View tools</button>
      </div>
      <p class="hint" style="margin-top:0.7rem">Writes go through Hearth APIs only. Godot is presentation; identities never merge.</p>
    `;

    document.getElementById("btnSend")?.addEventListener("click", () => openTalk(person));
    document.getElementById("btnStance")?.addEventListener("click", () => openStance(person));
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

  async function selectBeing(id) {
    state.selectedId = id;
    renderFamily(state.family);
    try {
      const data = await getJson(`/api/dashboard/being/${encodeURIComponent(id)}`);
      renderBeingDetail(data);
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
      const day = state.clock.day ?? "—";
      const period = state.clock.period ?? "—";
      el.clockBadge.textContent = `Day ${day} · ${String(period).replace(/^\w/, (c) => c.toUpperCase())}`;
      fillPlaceFilter();
      renderFamily(home.family || []);
      renderConversations();
      renderCapabilities(state.capabilities);
      if (state.selectedId) {
        const person = (home.family || []).find((f) => f.id === state.selectedId);
        if (person) renderBeingDetail(person);
      }
      el.connStatus.textContent = "Connected to Hearth · window only · identities unmerged";
      el.lastUpdate.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
    } catch (err) {
      el.connStatus.textContent = `Hearth unreachable — ${err.message}`;
    }
  }

  document.getElementById("btnRefresh")?.addEventListener("click", refreshAll);
  el.filterPerson.addEventListener("change", renderConversations);
  el.filterPlace.addEventListener("change", renderConversations);
  el.filterCapStatus.addEventListener("change", () => renderCapabilities(state.capabilities));
  document.getElementById("talkCancel")?.addEventListener("click", () => el.talkDialog.close());
  document.getElementById("stanceCancel")?.addEventListener("click", () => el.stanceDialog.close());

  refreshAll();
  setInterval(refreshAll, 5000);
})();
