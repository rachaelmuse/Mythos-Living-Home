/**
 * Mythos Hearth — playable village canvas
 */
(function () {
  const FLAVOR = {
    plaza: "Heart Square — companions cross paths; the village listens.",
    garden: "Herb Garden — rosemary, mint, thyme wait for careful hands.",
    hearth: "First Hearth — craft tea, gift companions, keep the fire.",
    workshop: "Workshop — studio limbs and tools hum behind the doors.",
    library: "Mythic Library — Q3 lore wing locked; books still open.",
    forge: "Stack Forge — StackForge heals Apex & Codex fleets.",
    cinema: "Cinema — OpenMontage trailers & Deep-Live-Cam DLC glow.",
    gallery: "Gallery — Comfy stills and hearth visions on the walls.",
    ruins: "Archive Ruins — memory drives and old maps sleep here.",
    arcade: "Arcade — GameCraft playables + Codex gameworld console.",
    sanctuary: "Sanctuary — digital palace & covenant pages rest here.",
    overlay: "Overlay Hall — Jarvis kin and drone cast rest their contracts here.",
    command: "Command Deck — Apex/Codex hubs, lounge, action monitor.",
  };

  const LOCATIONS = [
    { id: "plaza", name: "Heart Square", x: 0.50, y: 0.52, r: 42, accent: "#e8a84a" },
    { id: "garden", name: "Herb Garden", x: 0.22, y: 0.58, r: 36, accent: "#6dbf7a" },
    { id: "hearth", name: "First Hearth", x: 0.48, y: 0.72, r: 34, accent: "#f0b35a" },
    { id: "workshop", name: "Workshop", x: 0.72, y: 0.55, r: 34, accent: "#9bb8a8" },
    { id: "library", name: "Mythic Library", x: 0.68, y: 0.32, r: 36, accent: "#c9b8a0" },
    { id: "forge", name: "Stack Forge", x: 0.30, y: 0.35, r: 34, accent: "#c46b2a" },
    { id: "cinema", name: "Cinema", x: 0.82, y: 0.70, r: 32, accent: "#8a6bbf" },
    { id: "gallery", name: "Gallery", x: 0.18, y: 0.38, r: 32, accent: "#5ec8d4" },
    { id: "ruins", name: "Archive Ruins", x: 0.12, y: 0.78, r: 32, accent: "#7a8580" },
    { id: "arcade", name: "Arcade", x: 0.88, y: 0.42, r: 32, accent: "#e87a9a" },
    { id: "sanctuary", name: "Sanctuary", x: 0.38, y: 0.22, r: 30, accent: "#7ec8a0" },
    { id: "overlay", name: "Overlay Hall", x: 0.58, y: 0.18, r: 28, accent: "#a0b4d0" },
    { id: "command", name: "Command Deck", x: 0.42, y: 0.42, r: 30, accent: "#5ec8d4" },
  ];

  const state = {
    player: { x: 0.5, y: 0.55 },
    target: null,
    location: "plaza",
    keys: {},
    t: 0,
    hover: null,
    awake: false,
  };

  let canvas, ctx, onArrive, onFlavor;

  function resize() {
    if (!canvas) return;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const w = canvas.clientWidth || 1100;
    const h = Math.round(w * (620 / 1100));
    canvas.width = Math.floor(w * ratio);
    canvas.height = Math.floor(h * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    canvas.style.height = h + "px";
  }

  function drawBackground(w, h) {
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, state.awake ? "#14281f" : "#0c1c16");
    g.addColorStop(0.55, state.awake ? "#1c3d2e" : "#143026");
    g.addColorStop(1, "#0a1612");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);

    if (state.awake) {
      for (let i = 0; i < 18; i++) {
        const lx = ((i * 97) % 100) / 100 * w;
        const ly = ((i * 53) % 70) / 100 * h + 20;
        const flicker = 0.35 + Math.sin(state.t * 3 + i) * 0.15;
        ctx.fillStyle = `rgba(240,197,122,${flicker})`;
        ctx.beginPath();
        ctx.arc(lx, ly, 2.2, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    ctx.fillStyle = "rgba(155,184,168,0.05)";
    for (let i = 0; i < 4; i++) {
      const y = h * (0.35 + i * 0.12) + Math.sin(state.t * 0.4 + i) * 6;
      ctx.beginPath();
      ctx.ellipse(w * 0.5, y, w * 0.55, 28, 0, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.strokeStyle = "rgba(196,140,70,0.22)";
    ctx.lineWidth = 10;
    ctx.lineCap = "round";
    const plaza = LOCATIONS[0];
    LOCATIONS.slice(1).forEach((loc) => {
      ctx.beginPath();
      ctx.moveTo(plaza.x * w, plaza.y * h);
      ctx.quadraticCurveTo(
        (plaza.x + loc.x) * 0.5 * w,
        (plaza.y + loc.y) * 0.5 * h - 30,
        loc.x * w,
        loc.y * h
      );
      ctx.stroke();
    });

    ctx.strokeStyle = state.awake ? "rgba(240,197,122,0.55)" : "rgba(232,168,74,0.35)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(plaza.x * w, plaza.y * h, 55 + Math.sin(state.t) * 2, 0, Math.PI * 2);
    ctx.stroke();
  }

  function drawHotspotRing(loc, w, h) {
    const x = loc.x * w;
    const y = loc.y * h;
    const active = state.location === loc.id;
    const hover = state.hover === loc.id;
    if (!active && !hover) return;
    ctx.strokeStyle = loc.accent || "#e8a84a";
    ctx.globalAlpha = active ? 0.55 : 0.35;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(x, y, loc.r + Math.sin(state.t * 2.5) * 2, 0, Math.PI * 2);
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  function drawLocation(loc, w, h) {
    const x = loc.x * w;
    const y = loc.y * h;
    const active = state.location === loc.id;
    const pulse = 1 + Math.sin(state.t * 2 + loc.x * 10) * 0.04;

    drawHotspotRing(loc, w, h);

    ctx.fillStyle = active ? "rgba(232,168,74,0.22)" : "rgba(28,58,44,0.85)";
    ctx.strokeStyle = active ? "#e8a84a" : "rgba(155,184,168,0.35)";
    ctx.lineWidth = active ? 2 : 1;

    if (loc.id === "hearth") {
      ctx.beginPath();
      ctx.moveTo(x - 22 * pulse, y + 10);
      ctx.lineTo(x, y - 28 * pulse);
      ctx.lineTo(x + 22 * pulse, y + 10);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "#f0b35a";
      ctx.beginPath();
      ctx.arc(x, y + 2, 7 + Math.sin(state.t * 3) * 1.5, 0, Math.PI * 2);
      ctx.fill();
    } else if (loc.id === "garden") {
      for (let i = 0; i < 5; i++) {
        const a = (i / 5) * Math.PI * 2 + state.t * 0.2;
        ctx.fillStyle = i % 2 ? "#3d7a55" : "#2a5c40";
        ctx.beginPath();
        ctx.ellipse(x + Math.cos(a) * 14, y + Math.sin(a) * 10, 8, 12, a, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.fillStyle = "#6dbf7a";
      ctx.beginPath();
      ctx.arc(x, y, 6, 0, Math.PI * 2);
      ctx.fill();
    } else if (loc.id === "library") {
      ctx.fillRect(x - 20, y - 22, 40, 36);
      ctx.strokeRect(x - 20, y - 22, 40, 36);
      ctx.fillStyle = "rgba(240,197,122,0.35)";
      ctx.fillRect(x - 12, y - 14, 8, 20);
      ctx.fillRect(x + 4, y - 14, 8, 20);
      ctx.fillStyle = "rgba(155,184,168,0.4)";
      ctx.fillRect(x + 18, y - 30, 14, 20);
      ctx.fillStyle = "#c45a4a";
      ctx.font = "700 9px Outfit, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("Q3", x + 25, y - 18);
    } else if (loc.id === "forge") {
      ctx.fillRect(x - 18, y - 12, 36, 24);
      ctx.strokeRect(x - 18, y - 12, 36, 24);
      ctx.fillStyle = "#c46b2a";
      ctx.beginPath();
      ctx.arc(x, y, 6 + Math.sin(state.t * 4), 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#f0c57a";
      ctx.font = "600 8px Outfit, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("SF", x, y + 3);
    } else if (loc.id === "cinema") {
      ctx.beginPath();
      ctx.moveTo(x - 24, y + 12);
      ctx.lineTo(x - 18, y - 16);
      ctx.lineTo(x + 18, y - 16);
      ctx.lineTo(x + 24, y + 12);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "rgba(138,107,191,0.55)";
      ctx.fillRect(x - 10, y - 10, 20, 12);
    } else if (loc.id === "gallery") {
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(x - 18, y - 16, 36, 30, 4);
      else ctx.rect(x - 18, y - 16, 36, 30);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "#5ec8d4";
      ctx.fillRect(x - 10, y - 8, 8, 8);
      ctx.fillStyle = "#e8a84a";
      ctx.fillRect(x + 2, y - 8, 8, 8);
    } else if (loc.id === "ruins") {
      ctx.fillStyle = "rgba(90,100,95,0.7)";
      ctx.fillRect(x - 16, y - 8, 12, 22);
      ctx.fillRect(x + 2, y - 18, 14, 32);
      ctx.strokeStyle = "rgba(155,184,168,0.4)";
      ctx.strokeRect(x - 16, y - 8, 12, 22);
      ctx.strokeRect(x + 2, y - 18, 14, 32);
    } else if (loc.id === "arcade") {
      ctx.fillRect(x - 20, y - 16, 40, 28);
      ctx.strokeRect(x - 20, y - 16, 40, 28);
      ctx.fillStyle = "#e87a9a";
      ctx.fillRect(x - 12, y - 8, 10, 8);
      ctx.fillRect(x + 2, y - 8, 10, 8);
      ctx.fillStyle = "#f0c57a";
      ctx.font = "600 8px Outfit, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("PLAY", x, y + 14);
    } else if (loc.id === "sanctuary") {
      ctx.beginPath();
      ctx.moveTo(x, y - 20);
      ctx.lineTo(x + 18, y + 12);
      ctx.lineTo(x - 18, y + 12);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    } else if (loc.id === "overlay") {
      ctx.strokeStyle = loc.accent;
      ctx.strokeRect(x - 16, y - 14, 32, 26);
      ctx.strokeRect(x - 10, y - 8, 20, 14);
    } else if (loc.id === "command") {
      ctx.fillRect(x - 18, y - 10, 36, 20);
      ctx.strokeRect(x - 18, y - 10, 36, 20);
      ctx.fillStyle = "#5ec8d4";
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.fill();
    } else {
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(x - 18, y - 16, 36, 30, 4);
      else ctx.rect(x - 18, y - 16, 36, 30);
      ctx.fill();
      ctx.stroke();
    }

    ctx.fillStyle = active ? "#f4ebe0" : "#9bb8a8";
    ctx.font = "500 11px Outfit, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(loc.name, x, y + 36);
  }

  function drawPlayer(w, h) {
    const x = state.player.x * w;
    const y = state.player.y * h;
    const bob = Math.sin(state.t * 6) * 1.5;
    ctx.fillStyle = "#f0c57a";
    ctx.beginPath();
    ctx.arc(x, y - 10 + bob, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#e8a84a";
    ctx.fillRect(x - 5, y - 2 + bob, 10, 14);
    ctx.fillStyle = "rgba(232,168,74,0.2)";
    ctx.beginPath();
    ctx.arc(x, y + 8, 16, 0, Math.PI * 2);
    ctx.fill();
  }

  function nearestLocation() {
    let best = LOCATIONS[0];
    let bestD = Infinity;
    for (const loc of LOCATIONS) {
      const dx = loc.x - state.player.x;
      const dy = loc.y - state.player.y;
      const d = dx * dx + dy * dy;
      if (d < bestD) {
        bestD = d;
        best = loc;
      }
    }
    return bestD < 0.012 ? best : null;
  }

  function update(dt) {
    state.t += dt;
    const speed = 0.18;
    let mx = 0;
    let my = 0;
    if (state.keys["ArrowLeft"] || state.keys["a"] || state.keys["A"]) mx -= 1;
    if (state.keys["ArrowRight"] || state.keys["d"] || state.keys["D"]) mx += 1;
    if (state.keys["ArrowUp"] || state.keys["w"] || state.keys["W"]) my -= 1;
    if (state.keys["ArrowDown"] || state.keys["s"] || state.keys["S"]) my += 1;

    if (mx || my) {
      state.target = null;
      const len = Math.hypot(mx, my) || 1;
      state.player.x = Math.min(0.95, Math.max(0.05, state.player.x + (mx / len) * speed * dt));
      state.player.y = Math.min(0.92, Math.max(0.12, state.player.y + (my / len) * speed * dt));
    } else if (state.target) {
      const dx = state.target.x - state.player.x;
      const dy = state.target.y - state.player.y;
      const dist = Math.hypot(dx, dy);
      if (dist < 0.008) {
        state.player.x = state.target.x;
        state.player.y = state.target.y;
        state.target = null;
      } else {
        state.player.x += (dx / dist) * speed * dt;
        state.player.y += (dy / dist) * speed * dt;
      }
    }

    const near = nearestLocation();
    if (near && near.id !== state.location) {
      state.location = near.id;
      if (typeof onArrive === "function") onArrive(near, FLAVOR[near.id] || "");
      if (typeof onFlavor === "function") onFlavor(FLAVOR[near.id] || "");
    }
  }

  function frame(prev) {
    const now = performance.now();
    const dt = Math.min(0.05, (now - prev) / 1000);
    update(dt);
    const w = canvas.clientWidth || 1100;
    const h = parseFloat(canvas.style.height) || 620;
    drawBackground(w, h);
    LOCATIONS.forEach((loc) => drawLocation(loc, w, h));
    drawPlayer(w, h);
    requestAnimationFrame(() => frame(now));
  }

  function hitTest(mx, my) {
    const w = canvas.clientWidth;
    const h = parseFloat(canvas.style.height);
    for (const loc of LOCATIONS) {
      const dx = mx - loc.x * w;
      const dy = my - loc.y * h;
      if (dx * dx + dy * dy < loc.r * loc.r) return loc;
    }
    return null;
  }

  window.MythosVillage = {
    init(canvasEl, handlers) {
      canvas = canvasEl;
      ctx = canvas.getContext("2d");
      onArrive = handlers && handlers.onArrive;
      onFlavor = handlers && handlers.onFlavor;
      resize();
      window.addEventListener("resize", resize);

      window.addEventListener("keydown", (e) => {
        state.keys[e.key] = true;
        if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) e.preventDefault();
      });
      window.addEventListener("keyup", (e) => {
        state.keys[e.key] = false;
      });

      canvas.addEventListener("mousemove", (e) => {
        const rect = canvas.getBoundingClientRect();
        const loc = hitTest(e.clientX - rect.left, e.clientY - rect.top);
        state.hover = loc ? loc.id : null;
        canvas.style.cursor = loc ? "pointer" : "crosshair";
      });

      canvas.addEventListener("click", (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const loc = hitTest(mx, my);
        if (loc) {
          state.target = { x: loc.x, y: loc.y };
          state.location = loc.id;
          if (typeof onArrive === "function") onArrive(loc, FLAVOR[loc.id] || "");
          if (typeof onFlavor === "function") onFlavor(FLAVOR[loc.id] || "");
        } else {
          const w = canvas.clientWidth;
          const h = parseFloat(canvas.style.height);
          state.target = { x: mx / w, y: my / h };
        }
      });

      requestAnimationFrame((t) => frame(t));
    },
    goTo(locationId) {
      const loc = LOCATIONS.find((l) => l.id === locationId);
      if (loc) state.target = { x: loc.x, y: loc.y };
    },
    getLocation() {
      return state.location;
    },
    setAwake(on) {
      state.awake = !!on;
    },
    flavorFor(id) {
      return FLAVOR[id] || "";
    },
    locations: LOCATIONS,
    FLAVOR,
  };
})();
