/**
 * Mythos Hearth — UI controller
 */
(function () {
  const $ = (sel) => document.querySelector(sel);

  const CHECKLIST = [
    { id: "herb", label: "Pick an herb", match: (s) => ["herb_picked", "tea_crafted", "gifted", "complete"].includes(s) },
    { id: "tea", label: "Craft tea at the hearth", match: (s) => ["tea_crafted", "gifted", "complete"].includes(s) },
    { id: "gift", label: "Gift to Gemini, Apex, or Codex", match: (s) => ["gifted", "complete"].includes(s) || s === "complete" },
  ];

  const STEP_LABELS = {
    idle: "1 · Pick an herb",
    herb_picked: "2 · Craft tea at the hearth",
    tea_crafted: "3 · Gift to Apex or Codex",
    gifted: "4 · Story beat",
    complete: "✓ Village awake",
  };

  let celebrationShown = false;

  async function api(path, opts = {}) {
    const ctrl = new AbortController();
    const ms = opts.timeoutMs || 45000;
    const t = setTimeout(() => ctrl.abort(), ms);
    try {
      const res = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...opts,
        signal: ctrl.signal,
      });
      const text = await res.text();
      let data;
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        throw new Error(`Bad JSON from ${path} (${res.status})`);
      }
      if (!res.ok) {
        throw new Error(data.error || `${path} failed (${res.status})`);
      }
      return data;
    } finally {
      clearTimeout(t);
    }
  }

  function renderChecklist(step) {
    const el = $("#quest-checklist");
    if (!el) return;
    const doneGift = step === "complete" || step === "gifted";
    el.innerHTML = CHECKLIST.map((c) => {
      let done = c.match(step);
      if (c.id === "gift" && doneGift) done = true;
      return `<li class="check ${done ? "done" : ""}"><span class="mark">${done ? "✓" : "○"}</span>${c.label}</li>`;
    }).join("");
  }

  function setCelebration(on, quest) {
    const body = document.body;
    const banner = $("#village-awake");
    if (on) {
      body.classList.add("village-awake");
      if (window.MythosVillage) window.MythosVillage.setAwake(true);
      if (banner) banner.hidden = false;
      if (!celebrationShown && quest && quest.unlock) {
        celebrationShown = true;
        try {
          if (!sessionStorage.getItem("hearth_story_opened")) {
            sessionStorage.setItem("hearth_story_opened", "1");
            openUnlockedStory(quest);
          }
        } catch {
          openUnlockedStory(quest);
        }
      }
    } else {
      body.classList.remove("village-awake");
      if (window.MythosVillage) window.MythosVillage.setAwake(false);
      if (banner) banner.hidden = true;
    }
  }

  function openUnlockedStory(quest) {
    const reader = $("#book-reader");
    const unlock = quest.unlock || {};
    reader.innerHTML = `<h3>${unlock.title || "Care Beat"}</h3><div>${escapeHtml(
      (unlock.text || "") + "\n\n" + (quest.markdown || "").slice(0, 1200)
    )}</div>`;
    document.getElementById("companions")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderQuest(q) {
    $("#quest-hint").textContent = q.hint || "";
    renderChecklist(q.step);

    const stepsEl = $("#quest-steps");
    const order = ["idle", "herb_picked", "tea_crafted", "complete"];
    const idx = order.indexOf(q.step === "gifted" ? "complete" : q.step);
    stepsEl.innerHTML = order
      .map((s, i) => {
        let cls = "step";
        if (i < idx || q.step === "complete") cls += " done";
        if (s === q.step || (q.step === "gifted" && s === "complete") || (q.step === "complete" && s === "complete"))
          cls += " current";
        return `<div class="${cls}">${STEP_LABELS[s] || s}</div>`;
      })
      .join("");

    const actions = $("#quest-actions");
    actions.innerHTML = "";

    const add = (label, action, extra = {}) => {
      const b = document.createElement("button");
      b.className = "btn tiny primary";
      b.textContent = label;
      b.onclick = () => doQuest(action, extra);
      actions.appendChild(b);
    };

    if (q.step === "idle" || q.step === "herb_picked") {
      ["rosemary", "mint", "thyme"].forEach((h) => {
        const b = document.createElement("button");
        b.className = "btn tiny ghost";
        b.textContent = `Pick ${h}`;
        b.onclick = () => {
          window.MythosVillage.goTo("garden");
          doQuest("pick_herb", { herb: h });
        };
        actions.appendChild(b);
      });
    }
    if (q.step === "herb_picked") {
      add("Craft tea", "craft_tea");
      window.MythosVillage.goTo("hearth");
    }
    if (q.step === "tea_crafted") {
      add("Gift to Gemini", "gift_gemini");
      add("Gift to Apex", "gift_apex");
      add("Gift to Codex", "gift_codex");
    }
    const reset = document.createElement("button");
    reset.className = "btn tiny ghost";
    reset.textContent = "Reset quest";
    reset.onclick = () => {
      celebrationShown = false;
      try {
        sessionStorage.removeItem("hearth_story_opened");
      } catch {}
      doQuest("reset");
    };
    actions.appendChild(reset);

    const unlock = $("#quest-unlock");
    if (q.unlock) {
      unlock.hidden = false;
      unlock.innerHTML = `<strong>${q.unlock.title}</strong><br/>${q.unlock.text}`;
    } else {
      unlock.hidden = true;
      unlock.innerHTML = "";
    }

    const sideEl = $("#arcade-side-quest");
    if (sideEl && q.side_quests && q.side_quests.arcade_cozy) {
      const sq = q.side_quests.arcade_cozy;
      sideEl.hidden = false;
      sideEl.classList.toggle("done", !!sq.done);
      sideEl.textContent = sq.done
        ? "✓ Side quest complete — Visit Arcade · Cozy Valley played."
        : "Side quest: Visit Arcade — play Cozy Valley once.";
    }

    renderVillageLife(q);

    setCelebration(q.step === "complete" || q.story_unlocked, q);
  }

  function renderVillageLife(q) {
    const lifeSq = $("#life-side-quests");
    const actions = $("#life-actions");
    const inv = $("#inv-grid");
    const plotEl = $("#plot-status");
    const statusEl = $("#life-status");
    const aiNeed = $("#ai-need");
    if (!actions || !inv) return;

    if (!q.career_chosen) {
      showCareerModal(q);
    } else {
      hideCareerModal();
    }

    if (statusEl) {
      const c = q.career;
      const house = q.housing_state || "none";
      statusEl.textContent = q.career_chosen && c
        ? `${q.player_name} · ${c.name} · ${c.seat} · ${q.money} coin · rent due ${q.rent_due} · ${house}`
        : "Choose a career to seat your digital life.";
    }

    if (lifeSq && q.side_quests) {
      const bits = [];
      ["first_seed", "meet_jarvis", "arcade_cozy", "ai_favor"].forEach((id) => {
        const sq = q.side_quests[id];
        if (!sq) return;
        bits.push(`${sq.done ? "✓" : "○"} ${sq.title}`);
      });
      lifeSq.textContent = bits.join("  ·  ");
    }

    if (aiNeed) {
      const aq = q.ai_quest;
      if (aq && !aq.done) {
        aiNeed.hidden = false;
        aiNeed.textContent = `${(aq.from || "AI").toString()} needs you: ${aq.brief} (${aq.item} ×${aq.qty || 1}) · reward ${aq.reward} coin`;
      } else if (aq && aq.done) {
        aiNeed.hidden = false;
        aiNeed.textContent = "Last AI need complete — ask again when a resident needs hands.";
      } else {
        aiNeed.hidden = true;
      }
    }

    actions.innerHTML = "";
    const mk = (label, action, extra = {}) => {
      const b = document.createElement("button");
      b.className = "btn tiny ghost";
      b.textContent = label;
      b.onclick = () => {
        if (extra.location) window.MythosVillage?.goTo?.(extra.location);
        doQuest(action, extra);
      };
      actions.appendChild(b);
    };
    if (q.career_chosen) {
      mk("Work shift", "work_shift", {});
      mk("Pay bills", "pay_rent", {});
      mk("Ask AI for work", "ai_need", {});
      mk("Turn in AI need", "turn_in_ai", {});
      if (q.housing_state === "warning") mk("…risk eviction", "evict_tick", {});
      mk("Change career…", "show_career_ui", {});
    }
    mk("Gather emberpetal", "gather", { item: "emberpetal", location: "garden" });
    mk("Catch lantern moth", "gather", { item: "lantern_moth", location: "garden" });
    mk("Collect softstone", "gather", { item: "softstone", location: "garden" });
    mk("Find garden seed", "gather", { item: "garden_seed", location: "garden" });
    mk("Plant seed (90s)", "plant_seed", { plot_id: "plot_a", location: "garden" });
    mk("Harvest plot", "harvest", { plot_id: "plot_a", location: "garden" });
    mk("Fish brook", "fish", { location: "garden" });
    mk("Meet Jarvis", "meet_jarvis", { location: "plaza" });

    inv.innerHTML = "";
    const bag = q.inventory || {};
    Object.keys(bag).forEach((k) => {
      const n = bag[k] || 0;
      if (!n && k !== "garden_seed") return;
      const el = document.createElement("div");
      el.className = "inv-chip";
      el.textContent = `${k.replace(/_/g, " ")} · ${n}`;
      inv.appendChild(el);
    });

    const plot = (q.plots || [])[0];
    if (plotEl && plot) {
      if (plot.state === "growing") {
        const left = Math.max(0, Math.ceil((plot.ready_at || 0) - Date.now() / 1000));
        plotEl.textContent = `Plot A: growing hearth herbs — ~${left}s left.`;
      } else if (plot.state === "ready") {
        plotEl.textContent = "Plot A: READY — harvest your herbs.";
      } else {
        plotEl.textContent = "Plot A: empty — plant a garden seed.";
      }
    }
  }

  function showCareerModal(q) {
    const modal = $("#career-modal");
    const grid = $("#career-grid");
    if (!modal || !grid) return;
    modal.hidden = false;
    const nameInput = $("#career-player-name");
    if (nameInput && !nameInput.value) nameInput.value = q.player_name || "Keeper";
    grid.innerHTML = "";
    (q.careers || []).forEach((c) => {
      const el = document.createElement("button");
      el.type = "button";
      el.className = "career-card";
      el.innerHTML = `<strong>${c.name}</strong><span>${c.seat}</span><p>${c.blurb}</p>`;
      el.onclick = () => {
        doQuest("choose_career", {
          career: c.id,
          player_name: ($("#career-player-name")?.value || "Keeper").trim(),
        });
      };
      grid.appendChild(el);
    });
  }

  function hideCareerModal() {
    const modal = $("#career-modal");
    if (modal) modal.hidden = true;
  }

  async function doQuest(action, extra = {}) {
    if (action === "show_career_ui") {
      try {
        const q = await api("/api/quest");
        q.career_chosen = false; // force picker UI only
        showCareerModal(q);
      } catch (err) {
        toast(err.message || "Could not load careers");
      }
      return;
    }
    try {
      const data = await api("/api/quest/action", {
        method: "POST",
        body: JSON.stringify({ action, ...extra }),
      });
      if (data.quest) renderQuest(data.quest);
      if (data.quest && data.quest.location) {
        const loc = window.MythosVillage.locations.find((l) => l.id === data.quest.location);
        if (loc) $("#loc-name").textContent = loc.name;
      }
      if (!data.ok && data.error) {
        $("#quest-hint").textContent = data.error + " — " + (data.quest?.hint || "");
      }
    } catch (err) {
      toast(err.message || "Quest action failed");
    }
  }

  function statusClass(s) {
    return "status " + (s || "missing");
  }

  function statusLabel(s) {
    const map = {
      live: "live",
      ready: "ready — Launch starts it",
      offline: "offline",
      missing: "missing path",
      lore: "lore",
      link: "link",
    };
    return map[s] || s || "unknown";
  }

  let cachedTools = [];
  let districtFilter = null;

  function renderToolsGrid(tools) {
    const grid = $("#tools-grid");
    if (!grid) return;
    grid.innerHTML = "";
    if (districtFilter) {
      const bar = document.createElement("div");
      bar.className = "district-filter-bar";
      bar.innerHTML = `<span>Showing <strong>${districtFilter}</strong> district</span>`;
      const clear = document.createElement("button");
      clear.type = "button";
      clear.className = "btn tiny ghost";
      clear.textContent = "Show all";
      clear.onclick = () => {
        districtFilter = null;
        renderToolsGrid(cachedTools);
      };
      bar.appendChild(clear);
      grid.appendChild(bar);
    }
    const list = districtFilter
      ? tools.filter((t) => t.district === districtFilter)
      : tools;
    if (!list.length) {
      const empty = document.createElement("p");
      empty.className = "muted";
      empty.textContent = districtFilter
        ? `No tools tagged for ${districtFilter} yet — show all.`
        : "No tools loaded.";
      grid.appendChild(empty);
      return;
    }
    list.forEach((t) => {
      const el = document.createElement("div");
      el.className = "tool";
      el.dataset.district = t.district || "";
      el.innerHTML = `
        <div class="tool-top">
          <span class="tool-name">${t.name}</span>
          <span class="${statusClass(t.status)}">${statusLabel(t.status)}</span>
        </div>
        <p class="tool-desc">${t.desc || ""}</p>
        <div class="cta-row"></div>
      `;
      const row = el.querySelector(".cta-row");
      if (t.lore_only) {
        const launch = document.createElement("button");
        launch.className = "btn tiny primary";
        launch.type = "button";
        launch.textContent = "Lore only";
        launch.disabled = true;
        row.appendChild(launch);
      } else if (t.url) {
        // Real <a> under the click — Chrome/Edge block window.open after await
        // (Cursor test window often allows it; your normal browser does not).
        const launch = document.createElement("a");
        launch.className = "btn tiny primary";
        launch.href = t.url;
        launch.target = "_blank";
        launch.rel = "noopener";
        launch.textContent = "Launch";
        launch.onclick = () => {
          // Fire-and-forget: start bat if offline; tab already opens via href
          kickLaunch(t.id, t.name, { expectUrl: true });
        };
        row.appendChild(launch);
      } else {
        const launch = document.createElement("button");
        launch.className = "btn tiny primary";
        launch.type = "button";
        launch.textContent = "Launch";
        launch.onclick = () => launchTool(t.id, { label: t.name });
        row.appendChild(launch);
      }
      if (t.url && !t.lore_only) {
        const a = document.createElement("a");
        a.className = "btn tiny ghost";
        a.href = t.url;
        a.target = "_blank";
        a.rel = "noopener";
        a.textContent = "Open";
        row.appendChild(a);
      }
      grid.appendChild(el);
    });
  }

  async function loadTools() {
    const grid = $("#tools-grid");
    if (grid && !grid.children.length) {
      grid.innerHTML = `<p class="muted">Probing districts…</p>`;
    }
    const data = await api("/api/tools", { timeoutMs: 60000 });
    cachedTools = data.tools || [];
    renderToolsGrid(cachedTools);
  }

  function assignPopup(popup, url) {
    if (!popup || popup.closed) {
      if (url) window.open(url, "_blank", "noopener");
      return;
    }
    try {
      popup.location.href = url;
    } catch {
      try {
        popup.close();
      } catch {}
      window.open(url, "_blank", "noopener");
    }
  }

  function closePopup(popup) {
    if (!popup || popup.closed) return;
    try {
      popup.close();
    } catch {}
  }

  function kickLaunch(toolId, label, opts = {}) {
    toast(opts.expectUrl ? `Starting ${label}… reload the tab if it says refused` : `Launching ${label}…`);
    api("/api/launch", {
      method: "POST",
      body: JSON.stringify({ tool_id: toolId }),
      timeoutMs: 30000,
    })
      .then((data) => {
        if (data.lore) {
          toast(data.message || "Lore wing — not runnable on this hardware.");
          return;
        }
        if (data.action === "started_bat" || data.action === "started_exe") {
          toast(`Started ${label} — give it a few seconds, then refresh the tab`);
        } else if (data.action === "opened_folder" || data.action === "opened_file") {
          toast(`Opened ${data.path || label} on this PC`);
        } else if (data.ok && !opts.expectUrl) {
          toast(`Launched ${label}`);
        }
        setTimeout(() => loadTools().catch(() => {}), 2000);
      })
      .catch((err) => toast(err.message || "Launch failed — is Hearth running?"));
  }

  async function launchTool(toolId, opts = {}) {
    const popup = opts.popup || null;
    const label = opts.label || toolId;
    toast(`Launching ${label}…`);
    try {
      const data = await api("/api/launch", {
        method: "POST",
        body: JSON.stringify({ tool_id: toolId }),
        timeoutMs: 30000,
      });
      if (data.lore) {
        closePopup(popup);
        toast(data.message || "Lore wing — not runnable on this hardware.");
        return;
      }
      // Prefer in-Hearth hubs (Living Game) — same tab
      if (toolId === "living_game" || (data.url && String(data.url).includes("8790/living"))) {
        closePopup(popup);
        window.location.href = data.url || "/living.html";
        return;
      }
      if (data.url && (data.action === "open_url" || data.ok)) {
        if (String(data.url).includes("/play/")) {
          closePopup(popup);
          openPlayModal(data.url, label);
        } else {
          assignPopup(popup, data.url);
          toast(`Opened ${label}`);
        }
        return;
      }
      if (data.action === "opened_folder" || data.action === "opened_file") {
        closePopup(popup);
        toast(`Opened ${data.path || label} on this PC`);
        return;
      }
      if (data.action === "started_bat" || data.action === "started_exe") {
        if (data.url) {
          assignPopup(popup, data.url);
          toast(`Started ${label} — refresh the tab in a few seconds`);
        } else {
          closePopup(popup);
          toast(`Started ${label} on this PC`);
        }
        return;
      }
      closePopup(popup);
      if (!data.ok) {
        toast(data.error || "Launch failed");
      } else if (opts.fallbackUrl) {
        assignPopup(null, opts.fallbackUrl);
        toast(`Opened ${label}`);
      } else {
        toast(`Launch returned no action for ${label}`);
      }
      setTimeout(() => loadTools().catch(() => {}), 1500);
    } catch (err) {
      closePopup(popup);
      toast(err.message || "Launch failed — is Hearth running?");
    }
  }

  function toast(msg) {
    let el = document.getElementById("hearth-toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "hearth-toast";
      el.className = "hearth-toast";
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.hidden = false;
    clearTimeout(toast._t);
    toast._t = setTimeout(() => {
      el.hidden = true;
    }, 2800);
  }

  function openPlayModal(url, title) {
    const modal = $("#play-modal");
    const frame = $("#play-frame");
    const titleEl = $("#play-modal-title");
    const tab = $("#play-modal-tab");
    if (!modal || !frame) {
      window.open(url, "_blank", "noopener");
      return;
    }
    titleEl.textContent = title || "Arcade";
    frame.src = url;
    tab.href = url;
    modal.hidden = false;
    const playId = (url.match(/\/play\/([^/]+)/) || [])[1];
    if (playId) {
      api("/api/quest/action", {
        method: "POST",
        body: JSON.stringify({ action: "arcade_play", play_id: playId }),
      }).then((data) => {
        if (data.quest) renderQuest(data.quest);
      }).catch(() => {});
    }
  }

  function closePlayModal() {
    const modal = $("#play-modal");
    const frame = $("#play-frame");
    if (frame) frame.src = "about:blank";
    if (modal) modal.hidden = true;
  }

  async function loadArcade() {
    const data = await api("/api/playables");
    const grid = $("#arcade-grid");
    if (!grid) return;
    grid.innerHTML = "";
    (data.playables || []).forEach((p) => {
      const el = document.createElement("div");
      el.className = "arcade-card";
      el.innerHTML = `
        <h3>${p.name}</h3>
        <p>${p.desc || ""}</p>
        <div class="cta-row"></div>
      `;
      const row = el.querySelector(".cta-row");
      const play = document.createElement("button");
      play.className = "btn tiny primary";
      play.textContent = p.ready ? "Play" : "Missing";
      play.disabled = !p.ready;
      if (p.id === "gameworld") {
        play.textContent = "Open tab";
        play.onclick = () => window.open(p.url, "_blank", "noopener");
      } else {
        play.onclick = () => openPlayModal(p.url, p.name);
      }
      row.appendChild(play);
      const tab = document.createElement("a");
      tab.className = "btn tiny ghost";
      tab.href = p.url;
      tab.target = "_blank";
      tab.rel = "noopener";
      tab.textContent = "New tab";
      tab.onclick = () => {
        api("/api/quest/action", {
          method: "POST",
          body: JSON.stringify({ action: "arcade_play", play_id: p.id }),
        }).then((d) => {
          if (d.quest) renderQuest(d.quest);
        }).catch(() => {});
      };
      row.appendChild(tab);
      grid.appendChild(el);
    });
  }

  function avatarCandidates(c) {
    const id = c.id;
    const list = [c.avatar];
    if (id === "codex") {
      list.push(
        "/assets/codex_reference.png",
        "/assets/codex_male.png",
        "/assets/codex.png",
        "/assets/renders/codex_reference.png"
      );
    }
    if (id === "apex") {
      list.push("/assets/apex_reference.png", "/assets/apex.png");
    }
    if (id === "gemini") {
      list.push("/assets/gemini_reference.png", "/assets/codex_alt.png", "/assets/codex_reference.png");
    }
    if (id === "merovin") {
      list.push("/assets/merovin_reference.png");
    }
    if (id === "draven") {
      list.push("/assets/draven_reference.png");
    }
    return [...new Set(list.filter(Boolean))];
  }

  function wireAvatar(img, candidates) {
    let i = 0;
    img.src = candidates[0];
    img.onerror = () => {
      i += 1;
      if (i < candidates.length) img.src = candidates[i];
      else img.style.display = "none";
    };
  }

  async function loadPresence() {
    const [world, presence] = await Promise.all([api("/api/world"), api("/api/presence")]);
    const row = $("#companions-row");
    row.innerHTML = "";
    (world.companions || []).forEach((c) => {
      const kind = c.kind || "peer";
      const peer = (presence.peers || {})[c.id] || {};
      const online =
        kind === "peer" || kind === "crew"
          ? !!peer.online
          : kind === "conductor"
            ? peer.online !== false
            : true;
      const el = document.createElement("div");
      el.className = `companion ${c.id} ${kind}`;
      let status;
      if (kind === "drone") {
        status = c.line || "Drone on plaza duty";
      } else if (kind === "conductor") {
        status = online ? "At the fire · front door (Sentinel)" : "Home missing — check Axiom path";
      } else if (kind === "crew") {
        status = online ? "Cinema crew live · :" + (c.port || 5000) : "Cinema quiet — launch studio";
      } else {
        status = online ? "Present at :" + c.port : "Away — launch from Districts";
      }
      const kindTag =
        kind === "drone"
          ? ' <span class="drone-tag">drone</span>'
          : kind === "conductor"
            ? ' <span class="drone-tag">conductor</span>'
            : kind === "crew"
              ? ' <span class="drone-tag">crew</span>'
              : "";
      el.innerHTML = `
        <img alt="${c.name}" />
        <div>
          <h4>${c.name}${kindTag}</h4>
          <p>${c.role}</p>
          <p>${status}</p>
        </div>
        <span class="presence-dot ${online ? "on" : ""}" title="${online ? "online" : "offline"}"></span>
      `;
      wireAvatar(el.querySelector("img"), avatarCandidates(c));
      el.addEventListener("click", () => {
        if (kind === "drone") {
          kickLaunch("drone_cast", c.name);
          toast(`${c.name}: ${c.line || c.role}`);
          return;
        }
        if (kind === "conductor" || c.id === "gemini") {
          kickLaunch(c.tool_id || "gemini", c.name);
          toast(`${c.name}: ${c.line || "Family conductor — talk via Sentinel."}`);
          return;
        }
        if (kind === "crew" || c.id === "merovin" || c.id === "draven") {
          if (c.url) window.open(c.url, "_blank", "noopener");
          kickLaunch(c.tool_id || "merovin_draven", c.name, { expectUrl: true });
          toast(`${c.name}: ${c.line || c.role}`);
          return;
        }
        if (c.url) {
          // Open under the click gesture, then wake the peer if needed
          window.open(c.url, "_blank", "noopener");
          const toolId = c.id === "codex" ? "codex" : c.id === "apex" ? "apex" : null;
          if (toolId && !online) kickLaunch(toolId, c.name, { expectUrl: true });
        }
      });
      row.appendChild(el);
    });
  }

  async function loadStories() {
    const data = await api("/api/stories");
    const books = $("#books");
    books.innerHTML = "";
    (data.stories || []).forEach((s) => {
      const b = document.createElement("button");
      b.className = "btn tiny ghost";
      b.textContent = s.title;
      b.onclick = () => openStory(s.id);
      books.appendChild(b);
    });
    const qb = document.createElement("button");
    qb.className = "btn tiny ghost";
    qb.textContent = "First Hearth Gift";
    qb.onclick = async () => {
      const q = await api("/api/quest");
      const reader = $("#book-reader");
      reader.innerHTML = `<h3>First Hearth Gift</h3><div>${escapeHtml(q.markdown || "")}</div>`;
    };
    books.appendChild(qb);

    // Sprint DEMO as book if synced
    const demo = document.createElement("button");
    demo.className = "btn tiny ghost";
    demo.textContent = "Sprint 0001 Demo";
    demo.onclick = () => openStory("sprint_0001_demo");
    books.appendChild(demo);
  }

  async function openStory(id) {
    const s = await api("/api/story/" + encodeURIComponent(id));
    const reader = $("#book-reader");
    if (!s.markdown) {
      // try data/sprint path via special ids
      if (id === "sprint_0001_demo") {
        reader.innerHTML = `<p class="muted">Demo note lives in data/sprint — open living_game or see gallery prompts.</p>`;
        return;
      }
      reader.innerHTML = `<p class="muted">Could not load story.</p>`;
      return;
    }
    reader.innerHTML = `<h3>${s.id.replace(/_/g, " ")}</h3><div>${escapeHtml(s.markdown)}</div>`;
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function svgVillageArt(title, accent, motif) {
    const mid = motif || "hearth";
    let decor = "";
    if (mid === "garden") {
      decor = `<ellipse cx="100" cy="120" rx="18" ry="28" fill="#3d7a55"/><ellipse cx="140" cy="115" rx="16" ry="26" fill="#2a5c40"/><ellipse cx="180" cy="122" rx="18" ry="28" fill="#3d7a55"/>`;
    } else if (mid === "forge") {
      decor = `<rect x="120" y="90" width="80" height="40" fill="#2a1a10"/><circle cx="160" cy="110" r="14" fill="${accent}"/>`;
    } else if (mid === "cinema") {
      decor = `<polygon points="110,130 120,80 200,80 210,130" fill="#1a1428"/><rect x="135" y="95" width="50" height="28" fill="${accent}" opacity="0.7"/>`;
    } else if (mid === "gallery") {
      decor = `<rect x="90" y="85" width="50" height="40" fill="#5ec8d4" opacity="0.5"/><rect x="160" y="85" width="50" height="40" fill="${accent}" opacity="0.55"/>`;
    } else {
      decor = `<circle cx="160" cy="100" r="18" fill="${accent}" opacity="0.85"/><circle cx="160" cy="100" r="7" fill="#fff3d0"/>`;
    }
    const gid = "g" + accent.replace("#", "") + mid;
    return `<svg viewBox="0 0 320 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <defs>
        <linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#0c1c16"/>
          <stop offset="100%" stop-color="#1a3428"/>
        </linearGradient>
      </defs>
      <rect width="320" height="180" fill="url(#${gid})"/>
      <ellipse cx="160" cy="140" rx="120" ry="40" fill="${accent}" opacity="0.25"/>
      <path d="M0,110 C80,90 120,130 180,100 C240,70 280,110 320,95 L320,180 L0,180 Z" fill="#132820"/>
      ${decor}
      <text x="16" y="28" fill="#f0c57a" font-family="Fraunces,serif" font-size="14">${title}</text>
    </svg>`;
  }

  async function loadGallery() {
    const data = await api("/api/gallery");
    const grid = $("#gallery-grid");
    grid.innerHTML = "";

    (data.renders || []).forEach((r) => {
      const el = document.createElement("div");
      el.className = "gal-item";
      el.innerHTML = `<img src="${r.url}" alt="${r.name}"/><h4>${r.name}</h4><p>${r.source || "Render"}</p>`;
      grid.appendChild(el);
    });

    const visions = [
      { title: "Dawn of the Hearth Square", accent: "#e8a84a", motif: "hearth" },
      { title: "Herb Garden Mist", accent: "#6dbf7a", motif: "garden" },
      { title: "Stack Forge Fire", accent: "#c46b2a", motif: "forge" },
      { title: "Cinema Lanterns", accent: "#8a6bbf", motif: "cinema" },
      { title: "Comfy Gallery Wall", accent: "#5ec8d4", motif: "gallery" },
      { title: "Companion Meeting", accent: "#5ec8d4", motif: "hearth" },
    ];
    visions.forEach((v) => {
      const el = document.createElement("div");
      el.className = "gal-item";
      el.innerHTML = `${svgVillageArt(v.title, v.accent, v.motif)}<h4>${v.title}</h4><p>Village vision · SVG hearth art</p>`;
      grid.appendChild(el);
    });

    if (data.prompts) {
      const el = document.createElement("div");
      el.className = "gal-item";
      el.innerHTML = `<h4>Concept prompts</h4><pre>${escapeHtml(data.prompts)}</pre>`;
      grid.appendChild(el);
    }
  }

  async function health() {
    try {
      const h = await api("/api/health");
      $("#health-pill").textContent = h.ok ? `Hearth :${h.port} · alive` : "Hearth down";
    } catch {
      $("#health-pill").textContent = "Hearth unreachable";
    }
  }

  function setupKeysOverlay() {
    const overlay = $("#keys-overlay");
    const dismiss = $("#keys-dismiss");
    if (!overlay) return;
    try {
      if (sessionStorage.getItem("hearth_keys_seen")) {
        overlay.hidden = true;
        return;
      }
    } catch {}
    overlay.hidden = false;
    const hide = () => {
      overlay.hidden = true;
      try {
        sessionStorage.setItem("hearth_keys_seen", "1");
      } catch {}
    };
    dismiss?.addEventListener("click", hide);
    setTimeout(hide, 9000);
    window.addEventListener(
      "keydown",
      (e) => {
        if (["w", "a", "s", "d", "W", "A", "S", "D", "ArrowUp"].includes(e.key)) hide();
      },
      { once: true }
    );
  }

  async function init() {
    const canvas = $("#village-canvas");
    window.MythosVillage.init(canvas, {
      onArrive(loc, flavor) {
        $("#loc-name").textContent = loc.name;
        const flavorEl = $("#loc-flavor");
        if (flavorEl) flavorEl.textContent = flavor || window.MythosVillage.flavorFor(loc.id);
        api("/api/quest/action", {
          method: "POST",
          body: JSON.stringify({ action: "set_location", location: loc.id }),
        }).catch(() => {});
        if (loc.id === "arcade") {
          document.getElementById("arcade")?.scrollIntoView({ behavior: "smooth", block: "start" });
        } else if (loc.id !== "plaza") {
          districtFilter = loc.id;
          if (cachedTools.length) renderToolsGrid(cachedTools);
          document.getElementById("districts")?.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      },
      onFlavor(text) {
        const flavorEl = $("#loc-flavor");
        if (flavorEl) flavorEl.textContent = text;
      },
    });

    setupKeysOverlay();

    $("#btn-quest-jump").onclick = () => {
      document.getElementById("village").scrollIntoView({ behavior: "smooth" });
      window.MythosVillage.goTo("garden");
    };

    $("#btn-enter-3d")?.addEventListener("click", () => {
      launchTool("godot_play", { label: "Enter immersive 3D" });
    });

    $("#play-modal-close")?.addEventListener("click", closePlayModal);
    $("#play-modal-backdrop")?.addEventListener("click", closePlayModal);
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closePlayModal();
    });

    $("#btn-build-game")?.addEventListener("click", async () => {
      const log = $("#prod-log");
      log.hidden = false;
      log.textContent = "Starting Hearthbound Game Builder (no Apex/Codex)…";
      try {
        const data = await api("/api/game_builder", {
          method: "POST",
          body: JSON.stringify({ goal: "sprint_0002 Stage 1→2 vertical slice" }),
          timeoutMs: 15000,
        });
        log.textContent = JSON.stringify(data, null, 2);
        if (data.ok) toast("Game Builder started — watch the console window");
        else toast(data.error || "Builder failed to start");
      } catch (err) {
        log.textContent = err.message || "Game Builder request failed";
        toast(err.message || "Game Builder failed");
      }
    });

    $("#btn-builder-status")?.addEventListener("click", async () => {
      const log = $("#prod-log");
      log.hidden = false;
      try {
        const data = await api("/api/game_builder");
        log.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        log.textContent = err.message || "Status failed";
      }
    });

    $("#btn-open-lg").onclick = async () => {
      try {
        const data = await api("/api/open_living_game", { method: "POST", body: "{}" });
        toast(data.ok ? "Opened Court living_game folder" : (data.error || "Folder missing"));
      } catch (err) {
        toast(err.message || "Could not open folder");
      }
    };

    async function loadWings() {
      const data = await api("/api/wings");
      const status = $("#wing-status");
      const grid = $("#wings-grid");
      const rosterEl = $("#wing-roster");
      const sugEl = $("#wing-suggestions");
      if (!grid) return;

      const st = data.state || {};
      const active = st.active_wing;
      if (status) {
        status.innerHTML = active
          ? `<strong>Active wing:</strong> ${(data.wings || []).find((w) => w.id === active)?.name || active}` +
            (st.active_lane ? ` · lane <em>${st.active_lane}</em>` : "") +
            (st.project ? ` · project “${escapeHtml(st.project)}”` : "") +
            (st.sandbox_path ? `<br/><span class="muted">Sandbox: ${escapeHtml(st.sandbox_path)}</span>` : "") +
            ` <button type="button" class="btn tiny ghost" id="btn-wing-close">Close wing (listening again)</button>`
          : `<strong>All listening.</strong> ${escapeHtml(data.law || "Pick a wing for the project — others stay aware.")}`;
      }

      grid.innerHTML = "";
      (data.wings || []).forEach((w) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "wing-card" + (w.id === active ? " active" : "");
        const laneHint =
          w.lanes && typeof w.lanes === "object" && !Array.isArray(w.lanes)
            ? Object.keys(w.lanes).join(" · ")
            : Array.isArray(w.lanes)
              ? w.lanes.join(" · ")
              : "";
        btn.innerHTML = `
          <h3>${escapeHtml(w.name)}</h3>
          <p>${escapeHtml(w.blurb || "")}</p>
          <div class="wing-meta">${w.sandbox ? "Sandbox copy first · " : ""}${escapeHtml(laneHint)}</div>
        `;
        btn.addEventListener("click", async () => {
          const goal = window.prompt("Project / goal for this wing (optional):", st.project || "") || "";
          try {
            const res = await api("/api/wings/open", {
              method: "POST",
              body: JSON.stringify({ wing: w.id, goal, launch: false }),
            });
            toast(res.mom_plain || (res.ok ? "Wing opened" : res.error || "Failed"));
            await loadWings();
            await loadPresence();
          } catch (err) {
            toast(err.message || "Could not open wing");
          }
        });
        grid.appendChild(btn);
      });

      $("#btn-wing-close")?.addEventListener("click", async () => {
        try {
          const res = await api("/api/wings/close", {
            method: "POST",
            body: JSON.stringify({ reason: "complete" }),
          });
          toast(res.mom_plain || "Wing closed");
          await loadWings();
        } catch (err) {
          toast(err.message || "Close failed");
        }
      });

      if (rosterEl) {
        const roster = st.roster || {};
        const ids = Object.keys(roster);
        if (!ids.length || !active) {
          rosterEl.hidden = true;
          rosterEl.innerHTML = "";
        } else {
          rosterEl.hidden = false;
          rosterEl.innerHTML = ids
            .map((id) => {
              const m = roster[id] || {};
              const mode = m.mode || "listening";
              return `<span class="wing-chip ${mode}" title="${escapeHtml(m.note || "")}">${escapeHtml(id)} · ${mode}</span>`;
            })
            .join("");
        }
      }

      if (sugEl) {
        const list = data.suggestions_pending || [];
        const all = await api("/api/wings/suggestions").catch(() => ({ suggestions: list }));
        const rows = (all.suggestions || list).slice(0, 12);
        sugEl.innerHTML = rows.length
          ? rows
              .map((s) => {
                const pending = s.status === "pending";
                return `<div class="wing-sug ${escapeHtml(s.status || "")}">
                  <strong>${escapeHtml(s.from || "?")}</strong>
                  ${s.wing ? ` · ${escapeHtml(s.wing)}` : ""}
                  <span class="muted"> · ${escapeHtml(s.status || "")}</span>
                  <div>${escapeHtml(s.text || "")}</div>
                  ${
                    pending
                      ? `<div class="wing-sug-actions">
                          <button type="button" class="btn tiny ghost" data-sug="${escapeHtml(s.id)}" data-dec="accept">Accept</button>
                          <button type="button" class="btn tiny ghost" data-sug="${escapeHtml(s.id)}" data-dec="decline">Decline</button>
                          <button type="button" class="btn tiny ghost" data-sug="${escapeHtml(s.id)}" data-dec="defer">Defer</button>
                        </div>`
                      : s.review_note
                        ? `<div class="muted">${escapeHtml(s.review_note)}</div>`
                        : ""
                  }
                </div>`;
              })
              .join("")
          : `<p class="muted">No suggestions yet — listeners may pipe up anytime.</p>`;

        sugEl.querySelectorAll("[data-sug]").forEach((el) => {
          el.addEventListener("click", async () => {
            const id = el.getAttribute("data-sug");
            const decision = el.getAttribute("data-dec");
            try {
              const res = await api("/api/wings/suggest/review", {
                method: "POST",
                body: JSON.stringify({ id, decision }),
              });
              toast(res.ok ? `Suggestion ${decision}ed` : res.error || "Review failed");
              await loadWings();
            } catch (err) {
              toast(err.message || "Review failed");
            }
          });
        });
      }
    }

    $("#btn-wing-suggest")?.addEventListener("click", async () => {
      const from = ($("#wing-suggest-from")?.value || "companion").trim();
      const text = ($("#wing-suggest-text")?.value || "").trim();
      if (!text) {
        toast("Write a suggestion first");
        return;
      }
      try {
        const res = await api("/api/wings/suggest", {
          method: "POST",
          body: JSON.stringify({ from, text }),
        });
        toast(res.ok ? "Queued for review" : res.error || "Failed");
        if ($("#wing-suggest-text")) $("#wing-suggest-text").value = "";
        await loadWings();
      } catch (err) {
        toast(err.message || "Suggest failed");
      }
    });

    try {
      const quest = await api("/api/quest");
      renderQuest(quest);
      const flavorEl = $("#loc-flavor");
      if (flavorEl) flavorEl.textContent = window.MythosVillage.flavorFor(quest.location || "plaza");
    } catch (err) {
      $("#quest-hint").textContent = "Hearth unreachable — run START_HEARTH.bat (:8790).";
      toast(err.message || "Could not load quest");
    }

    const settled = await Promise.allSettled([
      loadTools(),
      loadArcade(),
      loadPresence(),
      loadStories(),
      loadGallery(),
      loadWings(),
      health(),
    ]);
    settled.forEach((r, i) => {
      if (r.status === "rejected") {
        console.warn("Hearth panel failed", i, r.reason);
      }
    });

    setInterval(() => {
      loadTools().catch(() => {});
      loadPresence().catch(() => {});
      loadWings().catch(() => {});
      health().catch(() => {});
    }, 20000);
  }

  document.addEventListener("DOMContentLoaded", init);
})();
