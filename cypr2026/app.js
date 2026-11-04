/* Cypr 2026 — progressive enhancement. Vanilla JS, no analytics. */
(function () {
  "use strict";

  var dataEl = document.getElementById("cypr-data");
  if (!dataEl) return;

  var data;
  try {
    data = JSON.parse(dataEl.textContent || "{}");
  } catch (error) {
    console.warn("Nie udało się odczytać danych planu.", error);
    return;
  }

  var CY_TZ = "Asia/Nicosia";
  var PL_TZ = "Europe/Warsaw";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var HUNTING_DATES = { "2026-11-08": true, "2026-11-11": true };
  var CHECK_KEY = "cypr2026.checklist.v1";
  var allDays = data.days || [];
  var allPlaces = data.places || [];
  var dayByDate = {};
  var placeById = {};
  var typeLabels = {
    hotel: "Hotel", airport: "Lotnisko", trailhead: "Start szlaku",
    attraction: "Stanowisko", museum: "Muzeum", village: "Wieś",
    coast: "Wybrzeże", restaurant: "Restauracja", town: "Miasto", shopping: "Zakupy"
  };
  var coordStatusLabels = {
    zweryfikowane: "współrzędne zweryfikowane",
    przejete_z_audytu: "współrzędne przejęte z audytu",
    orientacyjne_do_potwierdzenia: "orientacyjne, do potwierdzenia"
  };
  allDays.forEach(function (day) { dayByDate[day.date] = day; });
  allPlaces.forEach(function (place) { placeById[place.id] = place; });

  function $(selector, context) { return (context || document).querySelector(selector); }
  function $all(selector, context) {
    return Array.prototype.slice.call((context || document).querySelectorAll(selector));
  }
  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function pad(value) { return String(value).padStart(2, "0"); }
  function pluralDays(count) {
    if (count === 1) return "dzień";
    if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 12 || count % 100 > 14)) return "dni";
    return "dni";
  }
  function pluralTasks(count) {
    if (count === 1) return "zadanie";
    if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 12 || count % 100 > 14)) return "zadania";
    return "zadań";
  }
  function blockingLabel(count) {
    var noun = pluralTasks(count);
    var adjective = count === 1 ? "blokujące" : (noun === "zadania" ? "blokujące" : "blokujących");
    return count + " " + noun + " " + adjective;
  }

  function cyprusNow() {
    var parts = new Intl.DateTimeFormat("en-GB", {
      timeZone: CY_TZ, year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hourCycle: "h23"
    }).formatToParts(new Date());
    var map = {};
    parts.forEach(function (part) { if (part.type !== "literal") map[part.type] = part.value; });
    return {
      date: map.year + "-" + map.month + "-" + map.day,
      hour: Number(map.hour),
      minute: Number(map.minute)
    };
  }
  function dateLabel(iso) {
    var p = iso.split("-").map(Number);
    return new Intl.DateTimeFormat("pl-PL", {
      day: "numeric", month: "long", year: "numeric", timeZone: "UTC"
    }).format(new Date(Date.UTC(p[0], p[1] - 1, p[2], 12)));
  }
  function weekdayLabel(iso) {
    var p = iso.split("-").map(Number);
    return new Intl.DateTimeFormat("pl-PL", { weekday: "long", timeZone: "UTC" })
      .format(new Date(Date.UTC(p[0], p[1] - 1, p[2], 12)));
  }
  function dayDiff(fromIso, toIso) {
    var a = fromIso.split("-").map(Number);
    var b = toIso.split("-").map(Number);
    return Math.round((Date.UTC(b[0], b[1] - 1, b[2]) - Date.UTC(a[0], a[1] - 1, a[2])) / 86400000);
  }
  function minutes(value) {
    var parts = String(value || "").split(":");
    return Number(parts[0]) * 60 + Number(parts[1]);
  }
  function wallTimeToUtc(dateIso, timeText, zone) {
    var d = dateIso.split("-").map(Number);
    var t = timeText.split(":").map(Number);
    var guess = Date.UTC(d[0], d[1] - 1, d[2], t[0], t[1]);
    var parts = new Intl.DateTimeFormat("en-US", {
      timeZone: zone, year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hourCycle: "h23"
    }).formatToParts(new Date(guess));
    var map = {};
    parts.forEach(function (part) { if (part.type !== "literal") map[part.type] = part.value; });
    var shown = Date.UTC(Number(map.year), Number(map.month) - 1, Number(map.day), Number(map.hour), Number(map.minute));
    return new Date(guess - (shown - guess));
  }
  function eventMinuteInCyprus(day, event) {
    var zone = event.timezone || day.timezone || CY_TZ;
    if (zone === CY_TZ) return minutes(event.start_local);
    var time = new Intl.DateTimeFormat("en-GB", {
      timeZone: CY_TZ, hour: "2-digit", minute: "2-digit", hourCycle: "h23"
    }).format(wallTimeToUtc(day.date, event.start_local, zone));
    return minutes(time);
  }
  function zoneCode(zone) { return zone === PL_TZ ? "PL" : zone === CY_TZ ? "CY" : zone; }

  var initialNow = cyprusNow();
  var params = new URLSearchParams(window.location.search);
  var queryDate = params.get("date");
  var overrideDate = null;
  if (queryDate && /^\d{4}-\d{2}-\d{2}$/.test(queryDate)) {
    var parsed = new Date(queryDate + "T12:00:00Z");
    if (!isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === queryDate) overrideDate = queryDate;
  }
  var activeDate = overrideDate || initialNow.date;
  var startDate = data.trip.start_date;
  var endDate = data.trip.end_date;

  // Clock --------------------------------------------------------------------
  var clockEl = $("[data-cyprus-clock]");
  function drawClock() {
    var now = cyprusNow();
    if (clockEl) {
      clockEl.textContent = pad(now.hour) + ":" + pad(now.minute);
      clockEl.setAttribute("datetime", now.date + "T" + pad(now.hour) + ":" + pad(now.minute) + "+02:00");
    }
    return now;
  }
  drawClock();
  var clockDate = initialNow.date;

  // Connection status --------------------------------------------------------
  function updateConnection() {
    var online = navigator.onLine !== false;
    $all("[data-connection]").forEach(function (el) {
      var text = el.querySelector(".connection__text");
      if (!text) {
        Array.prototype.slice.call(el.childNodes).forEach(function (node) {
          if (node.nodeType === 3) node.remove();
        });
        text = document.createElement("span");
        text.className = "connection__text";
        el.appendChild(text);
      }
      text.textContent = online ? "Online" : "Offline";
      el.classList.toggle("is-offline", !online);
      el.setAttribute("title", online
        ? "Połączenie internetowe aktywne"
        : "Brak połączenia. Plan działa offline; kafelki mapy nie.");
    });
    var mapOffline = $("[data-map-offline]");
    if (mapOffline) mapOffline.hidden = online;
  }
  window.addEventListener("online", updateConnection);
  window.addEventListener("offline", updateConnection);
  updateConnection();

  // Print and disclosure controls -------------------------------------------
  $all(".js-print").forEach(function (button) {
    button.addEventListener("click", function () { window.print(); });
  });
  var printState = [];
  window.addEventListener("beforeprint", function () {
    printState = [];
    $all("details").forEach(function (details) {
      printState.push([details, details.open]);
      details.open = true;
    });
  });
  window.addEventListener("afterprint", function () {
    printState.forEach(function (entry) { entry[0].open = entry[1]; });
    printState = [];
  });
  function syncDetails(details) {
    var summary = details.querySelector("summary");
    if (summary) summary.setAttribute("aria-expanded", details.open ? "true" : "false");
  }
  $all("details").forEach(function (details) {
    syncDetails(details);
    details.addEventListener("toggle", function () { syncDetails(details); });
  });
  // Content is open by default so that no-JS printing keeps every note.
  // With JS, secondary disclosures start collapsed for a calmer screen page.
  $all("details[data-collapse-on-load]").forEach(function (details) {
    details.open = false;
    syncDetails(details);
  });

  // Today --------------------------------------------------------------------
  var todayKicker = $("[data-today-kicker]");
  var todayTitle = $("[data-today-title]");
  var todayBody = $("[data-today-body]");
  var todayActions = $("[data-today-actions]");
  var dateOverrideNote = $("[data-date-override]");
  var hotelPlace = placeById[data.trip.hotel.place_id] || {};
  var hotelTel = String(hotelPlace.phone || "").replace(/[^\d+]/g, "");
  function phoneDisplay(value) {
    var cleaned = String(value || "").replace(/[^\d+]/g, "");
    if (cleaned.indexOf("+357") === 0 && cleaned.length === 12) {
      return "+357 " + cleaned.slice(4, 6) + " " + cleaned.slice(6, 9) + " " + cleaned.slice(9);
    }
    return value || "brak danych";
  }

  function issueLink(issue) {
    return '<a class="text-link" href="#issue-' + esc(issue.id) + '">Otwórz zadanie →</a>';
  }
  function renderBeforeTrip() {
    var days = dayDiff(activeDate, startDate);
    var blocking = (data.open_issues || []).filter(function (issue) { return issue.blocking; });
    var sortedBlocking = blocking.slice().sort(function (a, b) {
      return String(a.due_on).localeCompare(String(b.due_on));
    });
    var upcoming = sortedBlocking.filter(function (issue) { return issue.due_on >= activeDate; });
    var overdue = sortedBlocking.filter(function (issue) { return issue.due_on < activeDate; });
    var nearest = upcoming[0];
    if (todayKicker) todayKicker.textContent = "Przed wyjazdem";
    if (todayTitle) todayTitle.textContent = days === 1 ? "Jutro zaczynamy" : "Za " + days + " " + pluralDays(days);
    var html = '<p class="today-bigline">' + esc(dateLabel(startDate)) + " · " + esc(data.trip.nights) + " nocy w Pafos</p>";
    html += "<p>Plan bazowy jest gotowy. Do potwierdzenia: <strong>" + blockingLabel(blocking.length) + "</strong>. Auto nie jest zarezerwowane.</p>";
    if (overdue.length && nearest) {
      html += '<p class="today-overdue">' + esc(overdue.length + " " + pluralTasks(overdue.length) + " z minionym terminem — sprawdź, co udało się potwierdzić.") + "</p>";
    }
    if (nearest) {
      html += '<div class="today-task"><span class="today-task__label">Najbliższy termin · ' + esc(dateLabel(nearest.due_on)) + "</span><strong>" + esc(nearest.title) + "</strong>" + issueLink(nearest) + "</div>";
    } else if (overdue.length) {
      html += '<div class="today-task today-task--late"><span class="today-task__label">Terminy minęły · ' + overdue.length + " zadań blokujących</span><strong>Sprawdź, co udało się potwierdzić</strong><a class=\"text-link\" href=\"#todo\">Otwórz listę zadań →</a></div>";
    }
    if (todayBody) todayBody.innerHTML = html;
    if (todayActions) {
      todayActions.innerHTML = '<a class="text-link" href="#todo">Wszystkie zadania →</a>' +
        '<a class="text-link" href="#dni">Dni i warianty →</a>';
    }
  }
  function renderInTrip(day) {
    var now = cyprusNow();
    var nowMinutes = now.hour * 60 + now.minute;
    var events = (day.timeline || []).map(function (event, index, list) {
      var start = eventMinuteInCyprus(day, event);
      var end = null;
      if (event.end_local) {
        var endZone = event.timezone || day.timezone || CY_TZ;
        if (endZone === CY_TZ) end = minutes(event.end_local);
        else {
          var endCy = new Intl.DateTimeFormat("en-GB", {
            timeZone: CY_TZ, hour: "2-digit", minute: "2-digit", hourCycle: "h23"
          }).format(wallTimeToUtc(day.date, event.end_local, endZone));
          end = minutes(endCy);
        }
      }
      return { event: event, start: start, end: end, index: index };
    });
    events.forEach(function (item) {
      if (item.end == null) {
        var next = events[item.index + 1];
        item.end = next ? next.start : 24 * 60 + 30;
      }
    });
    var active = null;
    events.forEach(function (item) {
      if (item.start <= nowMinutes && nowMinutes < item.end) active = item;
    });
    var next = null;
    if (!active) {
      events.some(function (item) {
        if (item.start > nowMinutes) { next = item; return true; }
        return false;
      });
    }
    var current = active || next;
    if (todayKicker) todayKicker.textContent = "Dzień " + Number(day.id.slice(-2)) + " z " + allDays.length + " · w trakcie";
    if (todayTitle) todayTitle.textContent = day.title;
    var html = '<p class="today-bigline">Dzień ' + Number(day.id.slice(-2)) + " · " + esc(weekdayLabel(day.date)) + " · " + esc(dateLabel(day.date)) + "</p>";
    (data.trip.flights || []).filter(function (flight) {
      return flight.departure_at.slice(0, 10) === day.date;
    }).forEach(function (flight) {
      var dep = new Date(flight.departure_at);
      var arr = new Date(flight.arrival_at);
      var fmt = function (dateObj, zone) {
        return new Intl.DateTimeFormat("pl-PL", { timeZone: zone, hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(dateObj);
      };
      var depZone = flight.departure_airport === "PFO" ? CY_TZ : PL_TZ;
      var arrZone = flight.arrival_airport === "PFO" ? CY_TZ : PL_TZ;
      html += '<p class="today-flight">' + esc(flight.flight_no) + " · " + esc(flight.departure_airport) + " " + fmt(dep, depZone) + " " + (depZone === CY_TZ ? "CY" : "PL") + " / " + fmt(dep, depZone === CY_TZ ? PL_TZ : CY_TZ) + " " + (depZone === CY_TZ ? "PL" : "CY") + " → " + esc(flight.arrival_airport) + " " + fmt(arr, arrZone) + " " + (arrZone === CY_TZ ? "CY" : "PL") + " / " + fmt(arr, arrZone === CY_TZ ? PL_TZ : CY_TZ) + " " + (arrZone === CY_TZ ? "PL" : "CY") + "</p>";
    });
    if (day.date in HUNTING_DATES) {
      html += '<div class="today-hunt">Dzień polowań — bez trekkingu. Trzymaj się programu miejskiego.</div>';
    }
    if (!current) {
      html += "<p>Dzisiejsze punkty osi czasu dobiegły końca. Zachowaj czas na odpoczynek i sprawdź plan na jutro.</p>";
    } else {
      var eventZone = current.event.timezone || day.timezone || CY_TZ;
      var eventTime = current.event.start_local + " " + zoneCode(eventZone);
      if (eventZone !== CY_TZ) {
        var converted = new Intl.DateTimeFormat("en-GB", {
          timeZone: CY_TZ, hour: "2-digit", minute: "2-digit", hourCycle: "h23"
        }).format(wallTimeToUtc(day.date, current.event.start_local, eventZone));
        eventTime += " · " + converted + " CY";
      }
      var names = (current.event.place_ids || []).map(function (id) {
        return placeById[id] ? placeById[id].name : id;
      });
      html += '<div class="today-point">' +
        '<span class="today-point__tag">' + (active ? "Teraz w planie" : "Następnie") + "</span>" +
        '<p class="today-point__time">' + esc(eventTime) + "</p>" +
        "<h4>" + esc(current.event.title) + "</h4>" +
        "<p>" + esc(current.event.description) + "</p>" +
        (names.length ? '<p class="today-places">' + names.map(esc).join(" · ") + "</p>" : "") +
        "</div>";
    }
    var sunset = (data.sunsets || []).filter(function (item) { return item.date === day.date; })[0];
    html += '<dl class="today-facts">';
    if (sunset) {
      html += "<div><dt>Zachód</dt><dd>" + esc(sunset.sunset_local) + "</dd></div>" +
        "<div><dt>Zmierzch</dt><dd>" + esc(sunset.civil_twilight_end_local) + "</dd></div>";
    }
    html += '<div><dt>Hotel</dt><dd><a href="tel:' + esc(hotelTel) + '">' + esc(phoneDisplay(hotelPlace.phone)) + "</a></dd></div>" +
      '<div><dt>Alarm</dt><dd><a href="tel:112">112</a></dd></div></dl>';
    if (todayBody) todayBody.innerHTML = html;
    if (todayActions) {
      todayActions.innerHTML = '<a class="text-link" href="#day-' + esc(day.id.slice(-2)) + '">Pełny dzień →</a>' +
        '<a class="text-link" href="#mapa">Mapa i miejsca →</a>';
    }
  }
  function renderAfterTrip() {
    if (todayKicker) todayKicker.textContent = "Po wyjeździe";
    if (todayTitle) todayTitle.textContent = "Plan zakończony";
    if (todayBody) {
      todayBody.innerHTML = '<p class="today-bigline">7–13 listopada 2026 · Pafos</p><p>Wyjazd minął, ale cały plan, źródła i checklisty pozostają dostępne. Nic nie zostało automatycznie oznaczone jako wykonane.</p>';
    }
    if (todayActions) {
      todayActions.innerHTML = '<a class="text-link" href="#dni">Wróć do dni →</a>' +
        '<a class="text-link" href="#zrodla">Źródła i wersja →</a>';
    }
  }
  function refreshToday() {
    if (activeDate < startDate) renderBeforeTrip();
    else if (activeDate > endDate) renderAfterTrip();
    else if (dayByDate[activeDate]) renderInTrip(dayByDate[activeDate]);
    if (overrideDate) {
      if (dateOverrideNote) {
        dateOverrideNote.hidden = false;
        dateOverrideNote.textContent = "Widok testowy: ?date=" + overrideDate + ". Zegar pokazuje bieżący czas na Cyprze.";
      }
    } else if (dateOverrideNote) {
      dateOverrideNote.hidden = true;
    }
  }
  refreshToday();

  function updateWeekHighlight(iso) {
    $all(".week-card").forEach(function (card) {
      var current = card.getAttribute("data-day-date") === iso;
      card.classList.toggle("is-today", current);
      if (current) card.setAttribute("aria-current", "date");
      else card.removeAttribute("aria-current");
    });
    $all(".day-card").forEach(function (card) {
      var current = card.getAttribute("data-day-date") === iso;
      card.classList.toggle("is-current", current);
      if (current) card.setAttribute("aria-current", "date");
      else card.removeAttribute("aria-current");
    });
  }
  updateWeekHighlight(activeDate);

  // Days are open by default (no-JS and print). On narrow screens collapse
  // secondary day content, keeping the current test/travel day open.
  var dayMobileQuery = window.matchMedia("(max-width: 759px)");
  function applyDayDisclosures() {
    var currentDay = dayByDate[activeDate];
    var hashMatch = /^#day-\d{2}$/.test(window.location.hash);
    $all("[data-day-disclosure]").forEach(function (disclosure) {
      var card = disclosure.closest(".day-card");
      var dayDate = card ? card.getAttribute("data-day-date") : "";
      if (!dayMobileQuery.matches) {
        disclosure.open = true;
      } else {
        disclosure.open = !!(currentDay && dayDate === currentDay.date);
      }
      var summary = disclosure.querySelector("summary");
      if (summary) summary.setAttribute("aria-expanded", disclosure.open ? "true" : "false");
    });
    if (hashMatch) {
      var target = document.querySelector(window.location.hash);
      var disclosure = target ? target.querySelector("[data-day-disclosure]") : null;
      if (disclosure) {
        disclosure.open = true;
        var summary = disclosure.querySelector("summary");
        if (summary) summary.setAttribute("aria-expanded", "true");
      }
    }
  }
  function openDayFromLink(link) {
    var href = link.getAttribute("href") || "";
    if (!/^#day-\d{2}$/.test(href)) return;
    var card = document.getElementById(href.slice(1));
    var disclosure = card ? card.querySelector("[data-day-disclosure]") : null;
    if (disclosure) {
      disclosure.open = true;
      var summary = disclosure.querySelector("summary");
      if (summary) summary.setAttribute("aria-expanded", "true");
    }
  }
  function openDayFromHash() {
    if (!/^#day-\d{2}$/.test(window.location.hash)) return;
    var card = document.getElementById(window.location.hash.slice(1));
    var disclosure = card ? card.querySelector("[data-day-disclosure]") : null;
    if (disclosure) {
      disclosure.open = true;
      var summary = disclosure.querySelector("summary");
      if (summary) summary.setAttribute("aria-expanded", "true");
    }
  }
  applyDayDisclosures();
  openDayFromHash();
  window.addEventListener("hashchange", openDayFromHash);
  window.addEventListener("load", openDayFromHash);
  document.addEventListener("click", function (event) {
    var link = event.target.closest ? event.target.closest('a[href^="#day-"]') : null;
    if (link) openDayFromLink(link);
  });
  if (dayMobileQuery.addEventListener) {
    dayMobileQuery.addEventListener("change", applyDayDisclosures);
  } else if (dayMobileQuery.addListener) {
    dayMobileQuery.addListener(applyDayDisclosures);
  }

  window.setInterval(function () {
    var now = drawClock();
    if (now.date !== clockDate) {
      clockDate = now.date;
      if (!overrideDate) {
        activeDate = now.date;
        updateWeekHighlight(activeDate);
        applyDayDisclosures();
        refreshToday();
      }
    }
  }, 30000);

  // Checklist ----------------------------------------------------------------
  var checklistState = { items: {}, planVersion: data.meta.version };
  try {
    var saved = JSON.parse(window.localStorage.getItem(CHECK_KEY) || "null");
    if (saved && typeof saved === "object" && saved.items && typeof saved.items === "object") {
      checklistState.items = saved.items;
    }
    checklistState.planVersion = data.meta.version;
  } catch (error) {
    checklistState.storageBlocked = true;
  }
  var checklistInputs = $all("[data-check-id]");
  var liveRegion = document.createElement("span");
  liveRegion.className = "visually-hidden";
  liveRegion.setAttribute("aria-live", "polite");
  var toolbar = $(".checklist-toolbar");
  if (toolbar) toolbar.appendChild(liveRegion);
  function announce(message) {
    if (liveRegion) liveRegion.textContent = message;
  }
  function saveChecklist() {
    checklistState.planVersion = data.meta.version;
    try {
      window.localStorage.setItem(CHECK_KEY, JSON.stringify({
        items: checklistState.items,
        planVersion: data.meta.version
      }));
    } catch (error) {
      announce("Nie udało się zapisać checklisty w tej przeglądarce.");
    }
  }
  function refreshChecklist() {
    var total = 0;
    var checked = 0;
    $all("[data-checklist-group]").forEach(function (group) {
      var inputs = $all("input[data-check-id]", group);
      var groupChecked = inputs.filter(function (input) { return input.checked; }).length;
      var count = group.querySelector("[data-group-count]");
      var progress = group.querySelector("[data-group-progress]");
      if (count) count.textContent = groupChecked + " / " + inputs.length;
      if (progress) {
        progress.value = groupChecked;
        progress.setAttribute("aria-valuetext", groupChecked + " z " + inputs.length);
      }
      group.classList.toggle("is-complete", inputs.length > 0 && groupChecked === inputs.length);
      total += inputs.length;
      checked += groupChecked;
    });
    var globalProgress = $("[data-global-progress]");
    var globalCount = $("[data-global-count]");
    if (globalProgress) {
      globalProgress.value = checked;
      globalProgress.setAttribute("aria-valuetext", checked + " z " + total);
    }
    if (globalCount) globalCount.textContent = checked + " / " + total;
    return { checked: checked, total: total };
  }
  checklistInputs.forEach(function (input) {
    var id = input.getAttribute("data-check-id");
    input.checked = checklistState.items[id] === true;
    input.addEventListener("change", function () {
      checklistState.items[id] = input.checked;
      saveChecklist();
      var totals = refreshChecklist();
      announce("Zapisano lokalnie: " + totals.checked + " z " + totals.total + ".");
    });
  });
  refreshChecklist();
  var resetButton = $("[data-reset-checklist]");
  if (resetButton) {
    resetButton.addEventListener("click", function () {
      if (!window.confirm("Wyczyścić wszystkie zaznaczenia checklisty? Stan zapisany lokalnie zostanie usunięty.")) return;
      checklistState.items = {};
      try { window.localStorage.removeItem(CHECK_KEY); } catch (error) {}
      checklistInputs.forEach(function (input) { input.checked = false; });
      refreshChecklist();
      announce("Checklista wyczyszczona.");
    });
  }
  if (checklistState.storageBlocked) {
    announce("Ta przeglądarka blokuje lokalny zapis checklisty.");
  }

  // Source references --------------------------------------------------------
  document.addEventListener("click", function (event) {
    var link = event.target.closest ? event.target.closest("a.source-chip") : null;
    if (!link) return;
    var href = link.getAttribute("href") || "";
    if (href.indexOf("#src-") !== 0) return;
    var row = document.getElementById(href.slice(1));
    if (!row) return;
    row.classList.remove("is-highlighted");
    void row.offsetWidth;
    row.classList.add("is-highlighted");
    row.setAttribute("tabindex", "-1");
    window.setTimeout(function () { row.focus({ preventScroll: true }); }, 30);
    window.setTimeout(function () { row.classList.remove("is-highlighted"); }, 2600);
  });

  // Navigation ---------------------------------------------------------------
  var navLinks = $all(".subnav__list a[href^='#']");
  var sections = navLinks.map(function (link) {
    return { link: link, section: document.getElementById(link.getAttribute("href").slice(1)) };
  }).filter(function (item) { return item.section; });
  var navTicking = false;
  var readingProgress = $("[data-reading-progress]");
  function updateReadingProgress() {
    if (!readingProgress) return;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var value = max > 0 ? Math.min(100, Math.max(0, (window.scrollY / max) * 100)) : 0;
    readingProgress.style.width = value.toFixed(2) + "%";
  }
  function updateNavCurrent() {
    var line = window.scrollY + 220;
    var current = sections[0];
    sections.forEach(function (item) {
      if (item.section.offsetTop <= line) current = item;
    });
    navLinks.forEach(function (link) {
      var active = current && link === current.link;
      link.classList.toggle("is-active", active);
      if (active) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
      if (active) {
        var scroller = link.closest(".subnav__scroll");
        if (scroller) {
          var box = scroller.getBoundingClientRect();
          var linkBox = link.getBoundingClientRect();
          var left = (linkBox.left - box.left) + scroller.scrollLeft;
          var right = left + link.offsetWidth + 40;
          if (left < scroller.scrollLeft || right > scroller.scrollLeft + scroller.clientWidth) {
            scroller.scrollTo({ left: Math.max(0, left), behavior: reduceMotion ? "auto" : "smooth" });
          }
        }
      }
    });
    updateReadingProgress();
    navTicking = false;
  }
  window.addEventListener("scroll", function () {
    if (navTicking) return;
    navTicking = true;
    window.requestAnimationFrame(updateNavCurrent);
  }, { passive: true });
  window.addEventListener("resize", updateReadingProgress, { passive: true });
  updateNavCurrent();

  // Lazy Leaflet map ---------------------------------------------------------
  var mapCanvas = document.getElementById("map-canvas");
  var mapLoaded = false;
  var mapLoading = false;
  var OSM_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var script = document.createElement("script");
      script.src = src;
      script.async = true;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }
  function loadStylesheet(href) {
    return new Promise(function (resolve, reject) {
      var link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = href;
      link.onload = resolve;
      link.onerror = reject;
      document.head.appendChild(link);
    });
  }
  function placeUsage(placeId) {
    var usage = [];
    allDays.forEach(function (day) {
      if ((day.timeline || []).some(function (event) {
        return (event.place_ids || []).indexOf(placeId) !== -1;
      })) usage.push("Dzień " + Number(day.id.slice(-2)));
    });
    (data.routes || []).forEach(function (route) {
      if (route.start_place_id === placeId) usage.push("start trasy " + route.name);
    });
    return usage;
  }
  function placesPlural(count) {
    if (count === 1) return "miejsce";
    if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 12 || count % 100 > 14)) return "miejsca";
    return "miejsc";
  }
  function feeLabel(value) {
    if (value == null) return "brak danych";
    if (value === 0) return "0 €";
    return String(value).replace(".", ",") + " €/os.";
  }
  function popupPlaceBlock(place) {
    var coord = place.coordinates || {};
    var use = placeUsage(place.id);
    var mapUrl = place.map_url || "";
    return "<h3>" + esc(place.name) + "</h3>" +
      '<p class="map-popup__type">' + esc(typeLabels[place.type] || place.type) + "</p>" +
      '<p class="map-popup__status">' + esc(coordStatusLabels[coord.status] || "brak danych o współrzędnych") + "</p>" +
      (place.published_hours ? "<p><strong>Godziny:</strong> " + esc(place.published_hours) + "</p>" : "") +
      "<p><strong>Wstęp:</strong> " + esc(feeLabel(place.fee_eur_per_adult)) + "</p>" +
      "<p><strong>Powiązania:</strong> " + esc(use.length ? use.join(", ") : "brak bezpośredniego użycia w osi czasu") + "</p>" +
      '<p><a href="#place-' + esc(place.id) + '">Opis w liście miejsc</a>' +
      (mapUrl ? ' · <a href="' + esc(mapUrl) + '">Otwórz w Maps</a>' : "") + "</p>";
  }
  function popupHtml(place) {
    return '<div class="map-popup">' + popupPlaceBlock(place) + "</div>";
  }
  function popupGroupHtml(places) {
    return '<div class="map-popup map-popup--group">' +
      '<p class="map-popup__type">W pobliżu · ' + places.length + ' ' + placesPlural(places.length) + '</p>' +
      places.map(function (place) {
        return '<div class="map-popup__group-item">' + popupPlaceBlock(place) + '</div>';
      }).join("") +
      "</div>";
  }
  function groupPlaces(places, map) {
    var groups = places.map(function (place) {
      var point = map.project([place.coordinates.lat, place.coordinates.lon], map.getZoom());
      return { x: point.x, y: point.y, places: [place] };
    });
    var merged = true;
    while (merged) {
      merged = false;
      for (var i = 0; i < groups.length && !merged; i += 1) {
        for (var j = i + 1; j < groups.length; j += 1) {
          if (Math.abs(groups[i].x - groups[j].x) < 46 && Math.abs(groups[i].y - groups[j].y) < 46) {
            groups[i].places = groups[i].places.concat(groups[j].places);
            groups[i].x = (groups[i].x + groups[j].x) / 2;
            groups[i].y = (groups[i].y + groups[j].y) / 2;
            groups.splice(j, 1);
            merged = true;
            break;
          }
        }
      }
    }
    return groups;
  }
  function initMap() {
    if (!mapCanvas || !window.L || mapLoaded) return;
    mapLoaded = true;
    mapCanvas.removeAttribute("aria-busy");
    var places = allPlaces.filter(function (place) {
      return place.coordinates && typeof place.coordinates.lat === "number" && typeof place.coordinates.lon === "number";
    });
    mapCanvas.innerHTML = "";
    var map = window.L.map(mapCanvas, {
      scrollWheelZoom: false,
      keyboard: true,
      zoomControl: false,
      attributionControl: true,
      zoomAnimation: !reduceMotion,
      fadeAnimation: !reduceMotion,
      markerZoomAnimation: !reduceMotion
    });
    window.L.control.zoom({ zoomInTitle: "Przybliż mapę", zoomOutTitle: "Oddal mapę" }).addTo(map);
    window.L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: OSM_ATTRIBUTION
    }).addTo(map);
    var bounds = places.map(function (place) {
      return [place.coordinates.lat, place.coordinates.lon];
    });
    var markerLayer = window.L.layerGroup().addTo(map);
    function renderMarkers() {
      markerLayer.clearLayers();
      var groups = groupPlaces(places, map);
      groups.forEach(function (group) {
        var members = group.places;
        var lat = members.reduce(function (sum, place) { return sum + place.coordinates.lat; }, 0) / members.length;
        var lon = members.reduce(function (sum, place) { return sum + place.coordinates.lon; }, 0) / members.length;
        var status = members[0].coordinates.status || "orientacyjne_do_potwierdzenia";
        var symbol = status === "zweryfikowane" ? "✓" : status === "przejete_z_audytu" ? "A" : "?";
        var className = members.length > 1 ? "poi-marker poi-marker--cluster" : "poi-marker poi-marker--" + status.replace(/_/g, "-");
        var label = members.length > 1
          ? members.length + " " + placesPlural(members.length) + " w pobliżu: " + members.map(function (place) { return place.name; }).join(", ")
          : members[0].name;
        var markerIcon = window.L.divIcon({
          className: "poi-marker-wrap",
          html: '<span class="' + className + '" aria-hidden="true">' + (members.length > 1 ? members.length : symbol) + "</span>",
          iconSize: [44, 44],
          iconAnchor: [22, 22],
          popupAnchor: [0, -14]
        });
        var marker = window.L.marker([lat, lon], {
          icon: markerIcon,
          title: label,
          alt: label,
          keyboard: true
        }).addTo(markerLayer);
        var markerEl = marker.getElement();
        if (markerEl) {
          markerEl.setAttribute("role", "button");
          markerEl.setAttribute("aria-label", label);
        }
        marker.bindPopup(members.length > 1 ? popupGroupHtml(members) : popupHtml(members[0]), { maxWidth: 340 });
      });
    }
    if (bounds.length) map.fitBounds(bounds, { padding: [34, 34], maxZoom: 11 });
    else map.setView([34.9, 32.75], 8);
    renderMarkers();
    map.on("zoomend", renderMarkers);
    map.on("popupopen", function (event) {
      var closeButton = event.popup.getElement() && event.popup.getElement().querySelector(".leaflet-popup-close-button");
      if (closeButton) closeButton.setAttribute("aria-label", "Zamknij opis miejsca");
    });
    var offline = document.createElement("p");
    offline.className = "map-offline-overlay";
    offline.setAttribute("data-map-offline", "");
    offline.textContent = "Offline: kafelki mapy są niedostępne. Lista miejsc poniżej pozostaje pełna.";
    offline.hidden = navigator.onLine !== false;
    mapCanvas.appendChild(offline);
    mapCanvas.classList.add("is-ready");
    updateConnection();
  }
  function loadMap() {
    if (!mapCanvas || mapLoading || mapLoaded) return;
    mapLoading = true;
    mapCanvas.classList.add("is-loading");
    mapCanvas.setAttribute("aria-busy", "true");
    var sourceScript = document.querySelector("script[data-version]");
    var version = sourceScript ? sourceScript.getAttribute("data-version") : "";
    var suffix = version ? "?v=" + version : "";
    Promise.all([
      loadStylesheet("assets/vendor/leaflet/leaflet.css" + suffix),
      loadScript("assets/vendor/leaflet/leaflet.js" + suffix)
    ]).then(initMap).catch(function () {
      mapLoading = false;
      mapCanvas.classList.remove("is-loading");
      mapCanvas.removeAttribute("aria-busy");
      mapCanvas.innerHTML = '<div class="map-placeholder map-placeholder--error"><p>Nie udało się wczytać mapy. Pełna lista miejsc poniżej jest kompletna i działa bez JavaScriptu.</p></div>';
    });
  }
  if (mapCanvas) {
    if ("IntersectionObserver" in window) {
      var mapObserver = new IntersectionObserver(function (entries) {
        if (entries.some(function (entry) { return entry.isIntersecting; })) {
          mapObserver.disconnect();
          loadMap();
        }
      }, { rootMargin: "650px 0px" });
      mapObserver.observe(mapCanvas);
    } else {
      loadMap();
    }
  }

  // Offline shell ------------------------------------------------------------
  if ("serviceWorker" in navigator && (window.location.protocol === "https:" ||
      window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("./sw.js").catch(function (error) {
        console.warn("Service worker nie został zarejestrowany.", error);
      });
    });
  }
})();
