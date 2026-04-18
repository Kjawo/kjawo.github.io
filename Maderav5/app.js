/* Madera 2026 — główna logika
   Zadanie: vanilla JS, offline-first, szybkie renderowanie kart dni,
   localStorage dla notatek i tweaks. Zero frameworków, zero zależności.
*/

(function () {
  const T = window.TRIP;

  // ---------- STATE ----------
  const LS = {
    get: (k, def) => { try { const v = localStorage.getItem(k); return v === null ? def : JSON.parse(v); } catch { return def; } },
    set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} }
  };

  const state = {
    activeDay: LS.get("mad2026.activeDay", 1),
    plan: LS.get("mad2026.plan", {}),          // per day: "A"|"B"|"C"
    variant: LS.get("mad2026.variant", "rec"), // rec | relax | iconic
    density: LS.get("mad2026.density", "comfort"),
    notes: LS.get("mad2026.notes", {})
  };

  function save() {
    LS.set("mad2026.activeDay", state.activeDay);
    LS.set("mad2026.plan", state.plan);
    LS.set("mad2026.variant", state.variant);
    LS.set("mad2026.density", state.density);
    LS.set("mad2026.notes", state.notes);
  }

  // ---------- HELPERS ----------
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const el = (tag, attrs = {}, children = []) => {
    const n = document.createElement(tag);
    for (const k in attrs) {
      if (k === "class") n.className = attrs[k];
      else if (k === "html") n.innerHTML = attrs[k];
      else if (k.startsWith("on")) n.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
      else if (attrs[k] !== undefined && attrs[k] !== null) n.setAttribute(k, attrs[k]);
    }
    for (const c of [].concat(children)) {
      if (c == null) continue;
      n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    }
    return n;
  };
  const statusBadge = (s) => {
    const def = T.statuses[s] || T.statuses.check;
    return el("span", { class: `status-badge status-${def.color}` }, [
      el("span", { class: "dot" }), def.label
    ]);
  };
  const fmtDate = (iso) => {
    const d = new Date(iso + "T12:00:00");
    const dd = String(d.getDate()).padStart(2, "0");
    const mm = String(d.getMonth() + 1).padStart(2, "0");
    return `${dd}.${mm}`;
  };

  function getTodayDayN() {
    const todayIso = new Date().toISOString().slice(0, 10);
    const d = T.days.find(x => x.date === todayIso);
    return d ? d.n : null;
  }

  // Determine current day to show based on variant overrides
  function dayFor(n) {
    let d = T.days.find(x => x.n === n);
    if (!d) return null;
    if (state.variant === "relax") {
      // wersja relaks: D2 tylko viewpointy Areeiro, D3 krótki PR8 — forsuj plan C domyślnie
      // To jest informacyjna podpowiedź, nie nadpisujemy obiektu
    }
    return d;
  }

  // ---------- RENDER: HEADER ----------
  function renderHeader() {
    const today = getTodayDayN();
    const progress = today ? today : state.activeDay;
    const pct = Math.min(100, Math.max(0, ((progress - 0.5) / 8) * 100));

    $("#trip-title").textContent = T.meta.title;
    $("#trip-sub").textContent = T.meta.subtitle;
    $("#trip-dates").textContent = T.meta.dateRange;
    $("#trip-base").textContent = "BAZA: " + T.meta.base;

    $("#arr-flight").textContent = T.meta.arrivalFlight.code;
    $("#arr-route").textContent = T.meta.arrivalFlight.route;
    $("#dep-flight").textContent = T.meta.departureFlight.code;
    $("#dep-route").textContent = T.meta.departureFlight.route;

    $("#progress-fill").style.width = pct + "%";
    $("#progress-label").textContent = today ? `DZIEŃ ${today}/8 — TRWA` : `DZIEŃ ${state.activeDay}/8 — PODGLĄD`;

    // ticks
    const ticks = $("#progress-ticks");
    ticks.innerHTML = "";
    for (let i = 0; i < 8; i++) ticks.appendChild(el("div", { class: "progress-tick" }));
  }

  // ---------- RENDER: TIMELINE ----------
  function renderTimeline() {
    const tl = $("#timeline");
    tl.innerHTML = "";
    const todayN = getTodayDayN();

    T.days.forEach(d => {
      const cls = ["tl-day"];
      if (d.n === state.activeDay) cls.push("active");
      if (d.n === todayN) cls.push("today");

      const card = el("button", { class: cls.join(" "), "data-day": d.n, onclick: () => selectDay(d.n) }, [
        el("div", { class: "dn" }, `D${String(d.n).padStart(2, "0")} · ${fmtDate(d.date).toUpperCase()} · ${d.weekday.slice(0,3).toUpperCase()}`),
        el("div", { class: "region" }, d.region),
        el("div", { class: "title" }, d.title),
        el("div", { class: "meta" }, [
          el("span", { class: "module-badge m-" + d.priority }, d.module)
        ])
      ]);
      tl.appendChild(card);
    });
  }

  function selectDay(n) {
    state.activeDay = n;
    save();
    renderTimeline();
    renderDayCard();
    // Scroll active timeline card into view horizontally
    const card = $(`#timeline [data-day="${n}"]`);
    if (card) card.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
  }

  // ---------- RENDER: SUN WIDGET ----------
  function renderSun(d) {
    const [rise, set] = T.sun[d.date] || ["—", "—"];
    const now = new Date();
    const mkTarget = (hhmm) => {
      const [h, m] = hhmm.split(":").map(Number);
      const t = new Date(d.date + "T" + hhmm + ":00+01:00"); // WEST = UTC+1
      return t;
    };
    const fmtCD = (tgt) => {
      const diff = tgt - now;
      if (isNaN(diff)) return "";
      const abs = Math.abs(diff);
      const h = Math.floor(abs / 3.6e6);
      const m = Math.floor((abs % 3.6e6) / 60000);
      const sign = diff < 0 ? "— " : "za ";
      return sign + (h > 0 ? `${h}h ${m}m` : `${m}m`);
    };
    const sr = mkTarget(rise);
    const ss = mkTarget(set);

    return el("div", { class: "sun-widget" }, [
      el("div", { class: "sun-cell" }, [
        el("span", { class: "k" }, "↑ SUNRISE"),
        el("span", { class: "v" }, rise),
        el("span", { class: "cd" }, fmtCD(sr))
      ]),
      el("div", { class: "sun-cell" }, [
        el("span", { class: "k" }, "↓ SUNSET"),
        el("span", { class: "v" }, set),
        el("span", { class: "cd" }, fmtCD(ss))
      ]),
      el("div", { class: "sun-cell" }, [
        el("span", { class: "k" }, "⌖ OKNO ŚWIATŁA"),
        el("span", { class: "v", style: "font-size: 11px; line-height: 1.3;" }, d.lightWindow || "—")
      ])
    ]);
  }

  // ---------- RENDER: DAY CARD ----------
  function renderDayCard() {
    const d = dayFor(state.activeDay);
    if (!d) return;
    const host = $("#day-card");
    host.innerHTML = "";

    const planKey = state.plan[d.n] || "A";
    const plan = d.plans[planKey];

    // HEAD
    const head = el("div", { class: "dc-head" }, [
      el("div", { class: "dc-head-top" }, [
        el("div", {}, [
          el("div", { class: "label", style: "margin-bottom:8px;" },
            `DZIEŃ ${String(d.n).padStart(2, "0")} / 08 · ${fmtDate(d.date)}.2026 · ${d.weekday.toUpperCase()}`),
          el("h2", { class: "dc-title" }, d.title),
          el("div", { class: "tick", style: "margin-top:6px;" }, d.region + " · " + d.module)
        ]),
        el("div", { class: "col", style: "align-items:flex-end;gap:6px;" }, [
          statusBadge(plan.status || "check"),
          el("span", { class: "module-badge m-" + d.priority }, d.module)
        ])
      ]),
      renderSun(d),
      el("div", { class: "dc-stats" }, [
        stat("START", d.startTime),
        stat("CZAS", d.duration),
        stat("AUTO", d.drive),
        stat("MARSZ", d.walk),
        stat("WYSIŁEK", d.effort.toUpperCase())
      ])
    ]);
    host.appendChild(head);

    // PLAN SWITCHER
    const switcher = el("div", { class: "plan-switch" }, Object.keys(d.plans).map(k => {
      const p = d.plans[k];
      const btn = el("button", {
        class: k === planKey ? "active" : "",
        onclick: () => { state.plan[d.n] = k; save(); renderDayCard(); }
      }, [
        el("span", { class: "plan-letter" }, "PLAN " + k),
        el("span", {}, p.label.toUpperCase())
      ]);
      return btn;
    }));
    host.appendChild(switcher);

    // NARRATIVE
    const narrative = el("div", { class: "plan-narrative" }, [
      el("div", { class: "plan-meta" }, [
        el("span", { class: "plan-badge" }, plan.badge || "PLAN " + planKey),
        statusBadge(plan.status || "check"),
        el("span", { class: "tick" }, "WYSIŁEK · " + (plan.effort || d.effort).toUpperCase()),
        plan.cost ? el("span", { class: "tick" }, "KOSZT · " + plan.cost) : null
      ]),
      el("div", { class: "plan-text" }, [
        el("p", { html: "<strong style='font-family:var(--ff-serif);font-size:19px;'>Cel.</strong> " + d.goal }),
        el("p", {}, plan.narrative),
        el("p", { style: "color:var(--fg-3);font-size:14px;font-style:italic;" }, "Dlaczego ten układ ma sens: " + d.reasoning)
      ])
    ]);
    host.appendChild(narrative);

    // GEAR WARNING
    if (d.gearWarning) {
      const gwBtn = el("button", { class: "gw-head", "aria-expanded": "false", onclick: (e) => {
        const b = e.currentTarget;
        b.setAttribute("aria-expanded", b.getAttribute("aria-expanded") === "true" ? "false" : "true");
      }}, [
        el("div", { class: "gw-icon" }, [el("span", {}, "!")]),
        el("span", { class: "gw-label" }, "OSTRZEŻENIE SPRZĘTOWE"),
        el("span", { class: "gw-chev" }, "▾")
      ]);
      const gw = el("div", { class: "gear-warning" }, [
        gwBtn,
        el("div", { class: "gw-body" }, d.gearWarning)
      ]);
      host.appendChild(gw);
    }

    // SEQUENCE
    host.appendChild(el("div", { class: "dc-section", style: "border-right:none;border-bottom:1px solid var(--border);" }, [
      el("h4", {}, "KOLEJNOŚĆ"),
      el("div", { style: "font-family:var(--ff-mono);font-size:13px;line-height:1.55;color:var(--fg);" }, d.sequence)
    ]));

    // SECTIONS GRID
    const sections = el("div", { class: "dc-sections" });

    sections.appendChild(sectionList("✓ BEST BET", d.bestBet));
    sections.appendChild(sectionList("✕ SKIP IF TIRED", d.skipIfTired));
    sections.appendChild(sectionList("△ RYZYKA", d.risks));
    sections.appendChild(sectionList("◉ REZERWUJ", d.reserve));
    sections.appendChild(sectionList("? SPRAWDŹ WIECZOREM", d.verify));

    // SPOTS with nav
    const spotsSection = el("div", { class: "dc-section" }, [
      el("h4", {}, "▲ PUNKTY + NAWIGACJA"),
      el("div", {}, d.spots.map(s => {
        const q = encodeURIComponent(s.name + ", Madeira, Portugal");
        return el("div", { class: "spot-row" }, [
          el("div", {}, [
            el("div", { class: "name" }, s.name),
            el("div", { class: "sub" }, [
              (T.statuses[s.status] || T.statuses.check).short,
              s.cost ? " · " + s.cost : "",
              s.note ? " · " + s.note : "",
              s.parking ? " · " + s.parking : ""
            ].join(""))
          ]),
          el("a", { class: "nav-btn", href: `https://www.google.com/maps/search/?api=1&query=${q}`, target: "_blank", rel: "noopener" },
            "◈ NAWIGUJ")
        ]);
      }))
    ]);
    sections.appendChild(spotsSection);

    // VERDICT
    sections.appendChild(el("div", { class: "dc-section" }, [
      el("h4", {}, "✦ WERDYKT"),
      el("div", { style: "font-family:var(--ff-serif);font-size:18px;line-height:1.35;color:var(--fg);" }, d.verdict),
      el("div", { style: "margin-top:10px;font-family:var(--ff-mono);font-size:11px;color:var(--fg-3);" },
        "LUNCH: " + T.lunchRule.window + " — potem Funchal lub baza.")
    ]));

    host.appendChild(sections);

    // NOTES
    const notes = state.notes[d.n] || "";
    const ta = el("textarea", {
      placeholder: "Notatki (zapisują się automatycznie w przeglądarce)…",
      oninput: (e) => { state.notes[d.n] = e.target.value; save(); }
    });
    ta.value = notes;
    host.appendChild(el("div", { class: "notes-area" }, [
      el("label", {}, `NOTATKI · DZIEŃ ${d.n}`),
      ta
    ]));
  }

  function stat(k, v) {
    return el("div", { class: "dc-stat" }, [
      el("span", { class: "k" }, k),
      el("span", { class: "v" }, v || "—")
    ]);
  }
  function sectionList(title, items) {
    return el("div", { class: "dc-section" }, [
      el("h4", {}, title),
      el("ul", {}, (items || []).map(i => el("li", {}, i)))
    ]);
  }

  // ---------- SHEETS ----------
  const sheets = {
    open(id) {
      $("#sheet-backdrop").classList.add("open");
      const s = document.getElementById(id);
      if (s) s.classList.add("open");
      document.body.style.overflow = "hidden";
    },
    close() {
      $("#sheet-backdrop").classList.remove("open");
      $$(".sheet").forEach(s => s.classList.remove("open"));
      document.body.style.overflow = "";
    }
  };
  window.__sheets = sheets;

  function renderSheets() {
    // Evening ritual
    $("#sheet-evening-body").innerHTML = "";
    const list = el("div", { class: "col", style: "gap:0;" });
    T.eveningRitual.forEach((r, i) => {
      const row = el("label", {
        style: "display:flex;gap:12px;padding:14px;border-bottom:1px solid var(--border);cursor:pointer;align-items:flex-start;"
      }, [
        el("input", { type: "checkbox", style: "margin-top:4px;width:18px;height:18px;accent-color:var(--amber);" }),
        el("div", {}, [
          el("div", { style: "font-family:var(--ff-mono);font-size:11px;letter-spacing:0.14em;color:var(--fg-3);" }, (i + 1) + " · " + r.k),
          el("div", { style: "font-size:15px;line-height:1.4;margin-top:3px;" }, r.v)
        ])
      ]);
      list.appendChild(row);
    });
    $("#sheet-evening-body").appendChild(list);
    $("#sheet-evening-body").appendChild(el("div", {
      style: "margin-top:14px;padding:12px;border:1px dashed var(--border-strong);font-family:var(--ff-mono);font-size:11px;color:var(--fg-2);line-height:1.5;"
    }, "Rytuał najlepiej odpalać o 20:00 wieczorem dnia poprzedniego — NIE rano w aucie. Status zmienia się warunkowo; rano już za późno."));

    // Weather
    $("#sheet-weather-body").innerHTML = "";
    T.weatherScenarios.forEach(s => {
      $("#sheet-weather-body").appendChild(el("div", {
        style: "padding:12px 14px;border-bottom:1px solid var(--border);"
      }, [
        el("div", { style: "font-family:var(--ff-mono);font-size:11px;letter-spacing:0.12em;color:var(--amber-2);text-transform:uppercase;margin-bottom:4px;" }, "◈ " + s.k),
        el("div", { style: "font-size:14px;line-height:1.5;color:var(--fg);" }, s.v)
      ]));
    });

    // Packing
    const pb = $("#sheet-packing-body");
    pb.innerHTML = "";
    pb.appendChild(el("div", { class: "label", style: "margin-bottom:10px;color:var(--cinnabar);" }, "△ KRYTYCZNE"));
    T.packing.critical.forEach(i => pb.appendChild(packingItem(i, "critical")));
    pb.appendChild(el("div", { class: "label", style: "margin:18px 0 10px;" }, "◦ NA KAŻDY DZIEŃ"));
    T.packing.daily.forEach(i => pb.appendChild(packingItem(i, "daily")));

    // Costs + links
    const cb = $("#sheet-costs-body");
    cb.innerHTML = "";
    cb.appendChild(el("div", { class: "label", style: "margin-bottom:10px;" }, "KOSZTY POTWIERDZONE"));
    T.costs.forEach(c => {
      cb.appendChild(el("div", { style: "display:grid;grid-template-columns:1fr auto;gap:10px;padding:10px 0;border-bottom:1px dashed var(--border);align-items:baseline;" }, [
        el("div", {}, [
          el("div", { style: "font-size:14px;color:var(--fg);" }, c.k),
          el("div", { class: "sub", style: "font-family:var(--ff-mono);font-size:10px;color:var(--fg-3);margin-top:2px;" }, c.note)
        ]),
        el("div", { class: "mono", style: "font-size:14px;font-weight:600;" }, c.v)
      ]));
    });

    // Links
    const lb = $("#sheet-links-body");
    lb.innerHTML = "";
    T.links.forEach(l => {
      lb.appendChild(el("a", {
        href: l.url, target: "_blank", rel: "noopener",
        class: "nav-btn",
        style: "display:flex;justify-content:space-between;padding:12px 14px;margin-bottom:6px;text-transform:none;letter-spacing:0.02em;"
      }, [
        el("div", {}, [
          el("div", { class: "mono", style: "font-size:10px;letter-spacing:0.14em;color:var(--fg-3);text-transform:uppercase;" }, l.k),
          el("div", { style: "font-size:14px;" }, l.label)
        ]),
        el("span", { style: "color:var(--amber-2);" }, "↗")
      ]));
    });
    lb.appendChild(el("div", {
      style: "margin-top:18px;padding:14px;border:1px solid var(--border);background:var(--bg-2);"
    }, [
      el("div", { class: "label", style: "margin-bottom:8px;" }, "AUTO · ZASADY"),
      el("ul", { style: "list-style:none;padding:0;margin:0;display:grid;gap:6px;" },
        T.carRules.map(r => el("li", { style: "font-size:13px;line-height:1.4;padding-left:14px;position:relative;color:var(--fg-2);", html: `<span style="position:absolute;left:0;color:var(--fg-3);">—</span>${r}` })))
    ]));

    // Map
    const mf = $("#sheet-map-body");
    mf.innerHTML = "";
    mf.appendChild(el("iframe", {
      class: "map-frame",
      src: T.meta.myMapEmbed,
      loading: "lazy",
      title: "Mapa wyjazdu Madera 2026"
    }));
    mf.appendChild(el("div", { style: "margin-top:10px;" }, [
      el("a", { class: "nav-btn", href: T.meta.myMapUrl, target: "_blank", rel: "noopener" }, "◈ OTWÓRZ W GOOGLE MAPS")
    ]));
  }

  function packingItem(label, tone) {
    const id = "pk_" + label.replace(/[^a-z0-9]/gi, "").slice(0, 20);
    const checked = LS.get("mad2026.pk." + id, false);
    const cb = el("input", {
      type: "checkbox",
      onchange: (e) => LS.set("mad2026.pk." + id, e.target.checked),
      style: "margin-top:4px;width:18px;height:18px;accent-color:var(--amber);flex-shrink:0;"
    });
    cb.checked = checked;
    return el("label", {
      style: "display:flex;gap:12px;padding:10px 0;border-bottom:1px dashed var(--border);cursor:pointer;align-items:flex-start;"
    }, [
      cb,
      el("div", { style: "font-size:14px;line-height:1.4;color:" + (tone === "critical" ? "var(--fg)" : "var(--fg-2)") + ";" }, label)
    ]);
  }

  // ---------- EVENING PILL ----------
  function updateEveningPill() {
    const h = new Date().getHours();
    const pill = $("#evening-pill");
    if (h >= 18 && h < 24) pill.classList.add("show");
    else pill.classList.remove("show");
  }

  // ---------- TWEAKS ----------
  function bindTweaks() {
    // density
    document.documentElement.classList.remove("density-compact", "density-comfort");
    document.documentElement.classList.add("density-" + state.density);
    $$("[data-tweak='density'] button").forEach(b => {
      b.classList.toggle("active", b.dataset.val === state.density);
      b.onclick = () => {
        state.density = b.dataset.val; save();
        document.documentElement.classList.remove("density-compact", "density-comfort");
        document.documentElement.classList.add("density-" + state.density);
        bindTweaks();
      };
    });
    // variant
    $$("[data-tweak='variant'] button").forEach(b => {
      b.classList.toggle("active", b.dataset.val === state.variant);
      b.onclick = () => {
        state.variant = b.dataset.val; save();
        bindTweaks();
        $("#variant-note").textContent = variantNote(state.variant);
      };
    });
    $("#variant-note").textContent = variantNote(state.variant);
  }
  function variantNote(v) {
    if (v === "relax") return "RELAKS · Areeiro tylko viewpointy, PR8 krótki, więcej dni miękkich. Wybieraj Plan C częściej.";
    if (v === "iconic") return "IKONICZNE · Areeiro z pełnym priorytetem pogody, PR8 ambitniej, zachód foto-first. Plan A domyślnie.";
    return "REKOMENDOWANY · Jedna baza, 2 mocne poranki na starcie, recovery w środku, stabilna końcówka.";
  }

  // ---------- INIT ----------
  function init() {
    renderHeader();
    renderTimeline();
    renderDayCard();
    renderSheets();
    bindTweaks();
    updateEveningPill();
    setInterval(updateEveningPill, 60 * 1000);

    // Default: jeśli dziś jest dzień wyjazdu, skocz na niego
    const todayN = getTodayDayN();
    if (todayN && !LS.get("mad2026.activeDay")) {
      state.activeDay = todayN; save();
      renderTimeline(); renderDayCard();
    }

    // Scroll do karty po wyborze
    $("#timeline [data-day='" + state.activeDay + "']")?.scrollIntoView({ behavior: "auto", block: "nearest", inline: "center" });

    // Sheet close bindings
    $("#sheet-backdrop").addEventListener("click", sheets.close);
    $$(".sheet-close").forEach(b => b.addEventListener("click", sheets.close));
    document.addEventListener("keydown", e => {
      if (e.key === "Escape") { sheets.close(); $("#tweaks-panel").classList.remove("open"); }
      if (e.key === "ArrowLeft" && state.activeDay > 1) selectDay(state.activeDay - 1);
      if (e.key === "ArrowRight" && state.activeDay < 8) selectDay(state.activeDay + 1);
    });

    // Bottom nav
    $("#btn-evening").onclick = () => sheets.open("sheet-evening");
    $("#btn-weather").onclick = () => sheets.open("sheet-weather");
    $("#btn-packing").onclick = () => sheets.open("sheet-packing");
    $("#btn-costs").onclick = () => sheets.open("sheet-costs");
    $("#btn-links").onclick = () => sheets.open("sheet-links");
    $("#btn-map").onclick = () => sheets.open("sheet-map");
    $("#evening-pill").onclick = () => sheets.open("sheet-evening");

    $("#btn-tweaks").onclick = () => $("#tweaks-panel").classList.toggle("open");

    // Periodic re-render sun times (countdown)
    setInterval(() => {
      // Only re-render if day card is in view
      if (!document.hidden) renderDayCard();
    }, 60 * 1000);

    // Service worker
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("./sw.js").catch(() => {});
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
