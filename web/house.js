(() => {
  const $ = (s) => document.querySelector(s);

  async function api(path, opts = {}) {
    const r = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
    const text = await r.text();
    let data;
    try {
      data = text ? JSON.parse(text) : {};
    } catch {
      throw new Error("Bad response from " + path);
    }
    if (!r.ok) throw new Error(data.error || path + " failed");
    return data;
  }

  function toast(msg) {
    const el = $("#toast");
    el.hidden = false;
    el.textContent = msg;
    setTimeout(() => {
      el.hidden = true;
    }, 2800);
  }

  function escapeHtml(t) {
    return String(t ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function showPage(id) {
    document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
    document.querySelectorAll(".nav-item").forEach((n) => n.classList.remove("active"));
    const page = $("#page-" + id);
    if (page) page.classList.add("active");
    const nav = document.querySelector(`.nav-item[data-page="${id}"]`);
    if (nav) nav.classList.add("active");
    $("#page-label").textContent = (nav && nav.textContent) || id;
    location.hash = id;
  }

  function renderFeed(events, into) {
    const el = $(into);
    if (!el) return;
    if (!events || !events.length) {
      el.innerHTML = `<p class="muted">Nothing yet — when Gemini acts, it shows here.</p>`;
      return;
    }
    el.innerHTML = events
      .map(
        (e) => `<div class="feed-item ${e.ok === false ? "bad" : ""}">
        <div class="meta">${escapeHtml(e.action || e.kind || "event")} · ${escapeHtml((e.when || "").replace("T", " ").slice(0, 19))}</div>
        <div>${escapeHtml(e.plain || "")}</div>
      </div>`
      )
      .join("");
  }

  async function loadOverview() {
    const data = await api("/api/family/feed");
    $("#status-line").textContent = data.status_line || "Family House";
    const m = data.mission;
    $("#mission-card").innerHTML = m
      ? `<p><strong>${escapeHtml(m.status || "?")}</strong></p>
         <p>${escapeHtml(m.goal || "")}</p>
         <p class="muted">id ${escapeHtml(m.id || "")}</p>`
      : `<p class="muted">No active family mission.</p>`;

    const w = data.wing;
    $("#wing-card").innerHTML = w
      ? `<p>Wing: <strong>${escapeHtml(w.active_wing || "none")}</strong>${
          w.active_lane ? " / " + escapeHtml(w.active_lane) : ""
        }</p>
         <p class="muted">${escapeHtml(w.project || "")}</p>
         <p>Active: ${escapeHtml((w.roster_active || []).join(", ") || "listeners only")}</p>`
      : `<p class="muted">No wing state yet.</p>`;

    renderFeed(data.events, "#feed-list");
    renderFeed(data.events, "#console-list");

    const pw = data.powwow;
    if (pw && $("#powwow-status")) {
      $("#powwow-status").innerHTML = pw.open
        ? `<p><strong>OPEN</strong> — ${escapeHtml(pw.reason || "")}</p>
           <p class="muted">Called by ${escapeHtml(pw.called_by || "?")} · ${escapeHtml(pw.id || "")}</p>
           <p>Agenda items: ${(pw.agenda || []).length} · Tasks set: ${(pw.tasks_set || []).length}</p>`
        : `<p class="muted">No powwow open. Call one when the room needs more than Gemini alone.</p>`;
      const agenda = $("#agenda-list");
      if (agenda) {
        agenda.innerHTML = (pw.agenda || [])
          .slice()
          .reverse()
          .map(
            (a) => `<div class="feed-item">
            <div class="meta">${escapeHtml(a.from)} · ${escapeHtml(a.status)}</div>
            <div>${escapeHtml(a.text)}</div>
          </div>`
          )
          .join("") || `<p class="muted">Agenda empty.</p>`;
      }
    }
  }

  async function loadWings() {
    const data = await api("/api/wings");
    const grid = $("#house-wings");
    if (!grid) return;
    const active = (data.state || {}).active_wing;
    grid.innerHTML = "";
    (data.wings || []).forEach((w) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "wing-card" + (w.id === active ? " active" : "");
      btn.innerHTML = `<h4>${escapeHtml(w.name)}</h4><p>${escapeHtml(w.blurb || "")}</p>`;
      btn.onclick = async () => {
        const goal = window.prompt("Project for this wing?", "") || w.name;
        const res = await api("/api/wings/open", {
          method: "POST",
          body: JSON.stringify({ wing: w.id, goal, launch: false }),
        });
        toast(res.mom_plain || "Wing opened");
        await refresh();
      };
      grid.appendChild(btn);
    });
  }

  async function loadCompanions() {
    const [world, presence] = await Promise.all([api("/api/world"), api("/api/presence")]);
    const row = $("#house-companions");
    if (!row) return;
    row.innerHTML = (world.companions || [])
      .map((c) => {
        const peer = (presence.peers || {})[c.id] || {};
        const on = c.kind === "peer" || c.kind === "crew" ? !!peer.online : true;
        return `<div class="companion-chip">
          <h4>${escapeHtml(c.name)}</h4>
          <p>${escapeHtml(c.role || "")}</p>
          <p class="muted">${on ? "present" : "away"} · ${escapeHtml(c.kind || "peer")}</p>
        </div>`;
      })
      .join("");
  }

  async function loadGallery() {
    const data = await api("/api/gallery");
    const g = $("#house-gallery");
    if (!g) return;
    const items = data.items || data.gallery || [];
    g.innerHTML = items.length
      ? items
          .slice(0, 24)
          .map((it) => {
            const url = it.url || it.src || "";
            return url ? `<img src="${escapeHtml(url)}" alt="" />` : "";
          })
          .join("")
      : `<p class="muted">Gallery empty — gifts will land here.</p>`;
  }

  async function refresh() {
    try {
      await loadOverview();
      await Promise.allSettled([loadWings(), loadCompanions(), loadGallery()]);
      $("#clock").textContent = new Date().toLocaleTimeString();
    } catch (err) {
      $("#status-line").textContent = "Hearth feed unreachable — is the server up?";
      toast(err.message || "Refresh failed");
    }
  }

  document.querySelectorAll(".nav-item[data-page]").forEach((btn) => {
    btn.addEventListener("click", () => showPage(btn.getAttribute("data-page")));
  });

  $("#btn-refresh")?.addEventListener("click", refresh);

  $("#btn-claim")?.addEventListener("click", async () => {
    try {
      const res = await api("/api/family/claim", { method: "POST", body: "{}" });
      toast(res.mom_plain || (res.ok ? "Claimed" : res.error || "Claim failed"));
      await refresh();
    } catch (e) {
      toast(e.message || "Claim failed");
    }
  });

  $("#btn-poll")?.addEventListener("click", async () => {
    try {
      const res = await api("/api/family/poll", { method: "POST", body: "{}" });
      toast(res.mom_plain || "Polled");
      await refresh();
    } catch (e) {
      toast(e.message || "Poll failed");
    }
  });

  $("#btn-powwow")?.addEventListener("click", () => showPage("powwow"));

  $("#btn-wing-close")?.addEventListener("click", async () => {
    try {
      const res = await api("/api/wings/close", {
        method: "POST",
        body: JSON.stringify({ reason: "complete" }),
      });
      toast(res.mom_plain || "Wing closed");
      await refresh();
    } catch (e) {
      toast(e.message || "Close failed");
    }
  });

  $("#btn-gemini-hint")?.addEventListener("click", (e) => {
    e.preventDefault();
    toast("Keep ACTIVATE_GEMINI.bat as front door. Watch progress here — no screenshots.");
  });

  $("#btn-powwow-open")?.addEventListener("click", async () => {
    const reason = $("#powwow-reason")?.value || "Family needs a meeting";
    const called_by = $("#powwow-from")?.value || "Mom";
    try {
      const res = await api("/api/family/powwow/open", {
        method: "POST",
        body: JSON.stringify({ reason, called_by }),
      });
      toast(res.mom_plain || "Powwow open");
      await refresh();
    } catch (e) {
      toast(e.message || "Powwow failed");
    }
  });

  $("#btn-powwow-tasks")?.addEventListener("click", async () => {
    try {
      const res = await api("/api/family/powwow/tasks", {
        method: "POST",
        body: JSON.stringify({ auto_accept_pending: true }),
      });
      toast(res.mom_plain || "Tasks set");
      await refresh();
    } catch (e) {
      toast(e.message || "Tasks failed");
    }
  });

  $("#btn-powwow-close")?.addEventListener("click", async () => {
    try {
      const res = await api("/api/family/powwow/close", {
        method: "POST",
        body: JSON.stringify({ reason: "adjourned" }),
      });
      toast(res.mom_plain || "Closed");
      await refresh();
    } catch (e) {
      toast(e.message || "Close failed");
    }
  });

  $("#btn-agenda")?.addEventListener("click", async () => {
    try {
      const res = await api("/api/family/powwow/agenda", {
        method: "POST",
        body: JSON.stringify({
          text: $("#agenda-text")?.value || "",
          from: $("#agenda-from")?.value || "companion",
        }),
      });
      toast(res.ok ? "On the agenda" : res.error || "Failed");
      if ($("#agenda-text")) $("#agenda-text").value = "";
      await refresh();
    } catch (e) {
      toast(e.message || "Agenda failed");
    }
  });

  const hash = (location.hash || "#overview").replace("#", "") || "overview";
  showPage(["overview", "console", "powwow", "wings", "companions", "village", "gallery"].includes(hash) ? hash : "overview");
  refresh();
  setInterval(refresh, 12000);
})();
