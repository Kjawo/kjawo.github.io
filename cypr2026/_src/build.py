#!/usr/bin/env python3
"""Build and validate the static Cypr 2026 travel page.

Only the Python standard library is required.  The JSON is the single source
of truth; this script never writes to the source JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, time
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "Cypr_2026_zrodlo_prawdy.json"
TEMPLATE_FILE = ROOT / "_src" / "template.html"
STYLES_FILE = ROOT / "styles.css"
APP_FILE = ROOT / "app.js"
SW_FILE = ROOT / "sw.js"
MANIFEST_FILE = ROOT / "manifest.json"
INDEX_FILE = ROOT / "index.html"
ASSETS_DIR = ROOT / "assets"

CY_TZ = "Asia/Nicosia"
PL_TZ = "Europe/Warsaw"
HUNTING_DATES = {"2026-11-08", "2026-11-11"}

MONTHS = [
    "stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
    "lipca", "sierpnia", "września", "października", "listopada", "grudnia",
]
MONTHS_SHORT = [
    "sty", "lut", "mar", "kwi", "maj", "cze",
    "lip", "sie", "wrz", "paź", "lis", "gru",
]
MONTHS_ROMAN = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
    7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII",
}
WEEKDAYS = {
    "poniedziałek": "poniedziałek",
    "wtorek": "wtorek",
    "środa": "środa",
    "czwartek": "czwartek",
    "piątek": "piątek",
    "sobota": "sobota",
    "niedziela": "niedziela",
}

# Human labels and tones for every status or readiness code used by the plan.
# They are deliberately explicit: unknown codes stop the build.
STATUS_LABELS = {
    "zarezerwowane_wg_uzytkownika": "Zarezerwowane według użytkownika",
    "zweryfikowane": "Zweryfikowane",
    "przejete_z_audytu": "Przejęte z audytu",
    "szacunek": "Szacunek",
    "do_potwierdzenia": "Do potwierdzenia",
    "decyzja_planu": "Decyzja planu",
    "planowane": "Planowane",
    "otwarte": "Otwarte",
    "do_przygotowania_i_weryfikacji": "GPX do przygotowania i weryfikacji",
    "orientacyjne_do_potwierdzenia": "Orientacyjne, do potwierdzenia",
    "do_sprawdzenia_przed_wyjsciem": "Do sprawdzenia przed wyjściem",
    "nie_dotyczy": "Nie dotyczy",
    "zalacznik_uzytkownika": "Załącznik użytkownika",
    "sprawdzone_2026_11_02": "Sprawdzone 2 listopada 2026",
    "link_kontrolny_z_audytu": "Link kontrolny z audytu",
    "czesciowy_kosztorys": "Częściowy kosztorys",
}

STATUS_MEANINGS = {
    "zarezerwowane_wg_uzytkownika": "Tak wynika z materiałów użytkownika; vouchery i rezerwacje nie zostały sprawdzone w tym opracowaniu.",
    "zweryfikowane": "Potwierdzone we wskazanym źródle. Nie jest to gwarancją przyszłej dostępności.",
    "przejete_z_audytu": "Informacja z audytu z 2 XI 2026, bez ponownej niezależnej kontroli.",
    "szacunek": "Wartość planistyczna, nie pomiar ani obietnica.",
    "do_potwierdzenia": "Brakuje danych, odpowiedzi usługodawcy lub bieżącej kontroli.",
    "decyzja_planu": "Wybór redakcyjny planu, nie twierdzenie o świecie.",
    "planowane": "Element planu bazowego; nie jest potwierdzoną rezerwacją.",
    "otwarte": "Sprawa nadal nierozwiązana.",
    "do_przygotowania_i_weryfikacji": "Ślad nie jest załączony; trzeba przygotować i sprawdzić konkretny przebieg.",
    "orientacyjne_do_potwierdzenia": "Punkt orientacyjny; dokładna lokalizacja wymaga potwierdzenia.",
    "do_sprawdzenia_przed_wyjsciem": "Gotowość terenowa zależy od bieżącej kontroli przed wyjściem.",
    "nie_dotyczy": "Dzień nie ma aktywnego trekkingu.",
    "zalacznik_uzytkownika": "Źródło przekazane przez użytkownika; brak publicznego URL.",
    "sprawdzone_2026_11_02": "Źródło sprawdzone 2 listopada 2026.",
    "przejete_z_audytu": "Ustalenie przejęte z audytu, bez ponownej kontroli.",
    "link_kontrolny_z_audytu": "Link kontrolny wskazany w audycie; nie sprawdzono treści przy budowie.",
    "czesciowy_kosztorys": "Znane są wyłącznie wskazane bilety. Pozostałe koszty mają brak danych.",
}

STATUS_TONE = {
    "zarezerwowane_wg_uzytkownika": "warning",
    "zweryfikowane": "ok",
    "przejete_z_audytu": "info",
    "szacunek": "info",
    "do_potwierdzenia": "warning",
    "decyzja_planu": "neutral",
    "planowane": "neutral",
    "otwarte": "warning",
    "do_przygotowania_i_weryfikacji": "warning",
    "orientacyjne_do_potwierdzenia": "warning",
    "do_sprawdzenia_przed_wyjsciem": "warning",
    "nie_dotyczy": "neutral",
    "zalacznik_uzytkownika": "neutral",
    "sprawdzone_2026_11_02": "ok",
    "przejete_z_audytu": "info",
    "link_kontrolny_z_audytu": "info",
    "czesciowy_kosztorys": "warning",
}

STATUS_ICON = {
    "ok": "check",
    "warning": "alert",
    "info": "info",
    "neutral": "dot",
}

PRIORITY_LABELS = {"wysoki": "Wysoki", "średni": "Średni", "niski": "Niski"}
PRIORITY_ORDER = {"wysoki": 0, "średni": 1, "niski": 2}
PRIORITY_TONE = {"wysoki": "warning", "średni": "info", "niski": "neutral"}

PLACE_TYPE_LABELS = {
    "hotel": "Hotel",
    "airport": "Lotnisko",
    "trailhead": "Start szlaku",
    "attraction": "Stanowisko",
    "museum": "Muzeum",
    "village": "Wieś",
    "coast": "Wybrzeże",
    "restaurant": "Restauracja",
    "town": "Miasto",
    "shopping": "Zakupy",
}

PLACE_GROUPS = [
    ("baza", "Baza i transport", {"hotel", "airport"}),
    ("szlaki", "Szlaki", {"trailhead"}),
    ("zwiedzanie", "Zwiedzanie", {"attraction", "museum", "village", "coast"}),
    ("jedzenie", "Jedzenie", {"restaurant"}),
    ("miasto", "Miasto", {"town", "shopping"}),
]

SOURCE_STATUS_ALLOWED = {
    "zalacznik_uzytkownika", "sprawdzone_2026_11_02",
    "przejete_z_audytu", "link_kontrolny_z_audytu",
}
GENERIC_STATUS_ALLOWED = {
    "zarezerwowane_wg_uzytkownika", "zweryfikowane", "przejete_z_audytu",
    "szacunek", "do_potwierdzenia", "decyzja_planu", "planowane", "otwarte",
    "do_przygotowania_i_weryfikacji", "orientacyjne_do_potwierdzenia",
}
READINESS_ALLOWED = {"nie_dotyczy", "do_sprawdzenia_przed_wyjsciem"}
BOOKING_ALLOWED = {"planowane", "zarezerwowane_wg_uzytkownika", "do_potwierdzenia"}
EFFORT_ALLOWED = {"szacunek"}
DISTANCE_STATUS_ALLOWED = {"zweryfikowane", "przejete_z_audytu", "szacunek", "do_potwierdzenia"}
ASCENT_STATUS_ALLOWED = {"do_potwierdzenia", "szacunek", "przejete_z_audytu", "zweryfikowane"}

# A decorative, simplified outline generated from Natural Earth public-domain
# geometry.  It is not used as a map, route or navigation aid.
CYPRUS_PATH = (
    "M407.2,247.3 L402.3,262.1 L401.7,276.4 L397.7,278.6 L394.8,286.0 "
    "L378.9,288.2 L370.9,297.5 L359.2,301.0 L351.7,304.6 L345.6,306.0 "
    "L341.7,301.3 L341.5,310.1 L334.2,314.7 L315.0,318.7 L305.6,324.2 "
    "L301.9,324.9 L283.3,322.8 L260.8,326.0 L245.2,339.7 L242.6,345.0 "
    "L230.7,345.8 L228.9,348.0 L227.1,346.8 L226.7,342.4 L229.7,339.6 "
    "L230.9,341.4 L235.9,341.4 L235.3,332.8 L226.8,331.5 L222.0,337.7 "
    "L217.2,334.7 L216.3,336.9 L208.7,334.9 L203.9,331.1 L202.5,328.3 "
    "L202.3,324.2 L195.3,324.1 L191.9,328.3 L188.5,328.9 L186.6,333.5 "
    "L178.4,331.9 L176.6,334.1 L176.8,339.1 L163.0,341.6 L152.3,339.5 "
    "L142.1,334.9 L124.2,324.6 L107.8,322.1 L103.3,320.2 L87.2,307.5 "
    "L84.4,294.0 L78.4,277.4 L67.7,268.8 L64.0,261.9 L63.8,257.8 "
    "L66.0,253.8 L61.1,245.6 L59.5,229.5 L51.8,214.9 L50.7,207.0 "
    "L51.5,201.2 L54.5,199.3 L59.7,203.0 L71.7,214.8 L76.6,216.8 "
    "L87.3,216.4 L96.6,211.4 L104.3,203.8 L110.0,195.5 L116.7,180.5 "
    "L120.8,177.5 L122.0,174.5 L123.5,173.8 L128.8,176.2 L140.3,171.7 "
    "L148.3,170.7 L172.8,173.8 L180.8,176.1 L187.3,180.4 L194.3,183.1 "
    "L203.8,180.5 L210.8,174.8 L216.5,166.7 L220.3,156.5 L221.7,144.7 "
    "L222.0,123.9 L221.0,114.6 L218.0,104.6 L224.2,105.7 L234.7,111.9 "
    "L256.5,116.9 L274.7,115.9 L306.2,119.9 L310.9,122.1 L348.8,126.3 "
    "L408.9,116.8 L440.6,98.7 L453.8,100.8 L505.7,81.5 L516.2,74.2 "
    "L530.3,68.9 L543.3,55.4 L579.0,45.3 L589.7,38.3 L636.9,16.3 "
    "L649.3,12.0 L645.8,16.3 L644.2,27.2 L636.4,29.2 L610.4,46.1 "
    "L587.4,65.9 L532.0,99.2 L524.6,105.7 L518.5,113.4 L511.7,127.8 "
    "L507.8,130.6 L501.6,130.9 L489.1,128.7 L484.0,131.8 L476.8,142.2 "
    "L473.8,148.0 L472.6,153.4 L470.7,178.1 L484.5,191.3 L491.0,202.4 "
    "L509.7,219.5 L515.4,233.7 L519.0,238.8 L522.1,240.9 L511.8,240.4 "
    "L505.4,238.6 L499.5,233.8 L485.5,235.6 L473.3,239.3 L468.6,243.1 "
    "L461.5,241.6 L456.7,242.6 L454.7,241.3 L457.9,238.4 L460.1,237.9 "
    "L460.1,232.5 L455.3,232.0 L452.5,229.5 L452.7,222.7 L450.7,220.4 "
    "L444.6,217.8 L446.0,214.3 L451.9,210.6 L455.5,213.8 L459.1,213.1 "
    "L465.6,206.9 L470.2,210.6 L474.4,206.9 L476.2,204.5 L474.2,201.3 "
    "L472.2,201.3 L470.4,195.6 L468.6,195.1 L468.0,192.4 L464.6,192.4 "
    "L463.4,203.0 L464.7,205.7 L458.7,211.6 L455.9,212.1 L451.1,208.9 "
    "L444.5,213.3 L443.4,217.3 L438.6,217.3 L436.2,220.0 L429.3,215.0 "
    "L423.9,219.7 L421.1,220.7 L424.1,210.1 L422.9,208.9 L420.5,208.9 "
    "L417.7,211.6 L413.6,212.3 L412.4,215.3 L412.8,218.2 L419.7,222.9 "
    "L420.5,225.1 L418.2,227.1 L419.0,229.1 L423.1,230.8 L422.1,234.5 "
    "L419.9,233.7 L419.5,238.5 L414.0,240.5 L407.2,247.3 Z"
)

ICON_PATHS = {
    "arrow": '<path d="M5 12h13M13 6l6 6-6 6"/>',
    "print": '<path d="M7 8V3h10v5M7 17H4a1 1 0 0 1-1-1v-6a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1h-3"/><rect x="7" y="13" width="10" height="8" rx="1"/><path d="M17 11h.01"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "pin": '<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    "foot": '<path d="M8 20c-2 0-3-2-2-4l2-5V5a2 2 0 0 1 4 0v4l2 3h2a2 2 0 0 1 0 4h-1l-2 3H8Z"/><path d="M6 9h1"/>',
    "car": '<path d="m5 16-1-5 2-4h12l2 4-1 5"/><path d="M3 16h18v4H3zM7 20v2M17 20v2M6 12h.01M18 12h.01"/>',
    "plane": '<path d="M22 2 9 15M22 2l-6 20-5-8-8-5 19-7Z"/>',
    "bed": '<path d="M3 18V7M3 12h18v6M21 18v-6a3 3 0 0 0-3-3h-7v3"/><path d="M3 20h18"/><circle cx="7" cy="10" r="2"/>',
    "trail": '<path d="M4 20c4-2 2-6 6-8s6-5 2-7M4 11c4 0 3 4 8 4s5-4 8-4"/><circle cx="18" cy="4" r="2"/>',
    "alert": '<path d="M10.3 3.4 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.4a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
    "check": '<path d="m5 12 4 4L19 6"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "dot": '<circle cx="12" cy="12" r="4"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2Z"/>',
    "map": '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z"/><path d="M9 3v15M15 6v15"/>',
    "source": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/>',
    "bag": '<path d="M6 7h12l1 14H5L6 7Z"/><path d="M9 7V5a3 3 0 0 1 6 0v2"/>',
    "ticket": '<path d="M3 9a2 2 0 0 0 0 4v5h18v-5a2 2 0 0 0 0-4V4H3v5Z"/><path d="M13 4v3M13 10v3M13 16v3"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    "camera": '<path d="M4 7h3l2-3h6l2 3h3a1 1 0 0 1 1 1v12H3V8a1 1 0 0 1 1-1Z"/><circle cx="12" cy="13" r="4"/>',
    "food": '<path d="M7 3v8a3 3 0 0 1-3 3V3M4 14v7M11 3v18M17 3c2 2 2 4 2 7s-1 3-3 3V3Z"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "download": '<path d="M12 3v12M7 10l5 5 5-5M4 21h16"/>',
    "wifi": '<path d="M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0M12 19.5h.01"/>',
}


class BuildError(Exception):
    pass


def fail(message: str) -> None:
    raise BuildError(message)


def icon(name: str, cls: str = "") -> str:
    body = ICON_PATHS.get(name, ICON_PATHS["dot"])
    extra = f" {cls}" if cls else ""
    return (
        f'<svg class="icon{extra}" viewBox="0 0 24 24" width="18" height="18" '
        f'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true" focusable="false">{body}</svg>'
    )


def esc(value: object) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def safe_url(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = urlparse(value)
    except ValueError:
        return None
    if parsed.scheme not in {"http", "https", "mailto", "tel"}:
        return None
    return value


def index_by(items: list[dict], label: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in items:
        item_id = item.get("id")
        if not item_id:
            fail(f"{label}: encja bez pola id")
        if item_id in result:
            fail(f"{label}: zduplikowane id {item_id}")
        result[item_id] = item
    return result


def parse_iso_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        fail(f"{label}: oczekiwano daty RRRR-MM-DD, otrzymano {value!r}")
    raise AssertionError("unreachable")


def parse_datetime(value: str, label: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        fail(f"{label}: oczekiwano daty ISO z offsetem, otrzymano {value!r}")
    if dt.tzinfo is None:
        fail(f"{label}: data ISO musi mieć offset: {value!r}")
    return dt


def parse_hhmm(value: str, label: str) -> time:
    if not isinstance(value, str) or not re.fullmatch(r"\d{2}:\d{2}", value):
        fail(f"{label}: oczekiwano godziny HH:MM, otrzymano {value!r}")
    try:
        return time(int(value[:2]), int(value[3:]))
    except ValueError:
        fail(f"{label}: nieprawidłowa godzina {value!r}")
    raise AssertionError("unreachable")


def validate_time_range(start: str, end: str | None, label: str) -> None:
    start_t = parse_hhmm(start, f"{label}.start_local")
    if end is not None:
        end_t = parse_hhmm(end, f"{label}.end_local")
        if end_t < start_t:
            fail(f"{label}: end_local {end} jest przed start_local {start}")


def format_date_pl(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def short_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS_SHORT[d.month - 1]} {d.year}"


def due_short(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS_ROMAN[d.month]}"


def format_number(value: int | float) -> str:
    if isinstance(value, bool):
        return str(int(value))
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        text = f"{value:.2f}".rstrip("0").rstrip(".")
        return text.replace(".", ",")
    return str(value)


def format_km(value) -> str:
    if value is None:
        return "brak danych"
    if isinstance(value, (list, tuple)):
        if len(value) == 2:
            a, b = value
            if a == b:
                return f"{format_number(a)} km"
            return f"{format_number(a)}–{format_number(b)} km"
    return f"{format_number(value)} km"


def format_metres(value) -> str:
    if value is None:
        return "brak danych"
    if isinstance(value, (list, tuple)) and len(value) == 2:
        a, b = value
        if a == b:
            return f"{format_number(a)} m"
        return f"{format_number(a)}–{format_number(b)} m"
    return f"{format_number(value)} m"


def format_coord(value: float) -> str:
    text = f"{float(value):.6f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def format_phone_display(value: str | None) -> str:
    if not value:
        return "brak danych"
    cleaned = re.sub(r"[^\d+]", "", str(value))
    if cleaned.startswith("+357") and len(cleaned) == 12:
        rest = cleaned[4:]
        return f"+357 {rest[:2]} {rest[2:5]} {rest[5:]}"
    return str(value)


def format_minutes_single(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes} min"
    if minutes % 30 == 0:
        return f"{format_number(minutes / 60)} h"
    hours, rest = divmod(minutes, 60)
    if rest == 0:
        return f"{hours} h"
    return f"{hours} h {rest:02d} min"


def format_duration(value) -> str:
    if value is None:
        return "brak danych"
    if isinstance(value, (list, tuple)):
        if len(value) != 2:
            return "brak danych"
        a, b = value
        if a == b:
            return format_minutes_single(a)
        if a < 60 and b < 60:
            return f"{a}–{b} min"
        if a >= 60 and b >= 60 and a % 30 == 0 and b % 30 == 0:
            return f"{format_number(a / 60)}–{format_number(b / 60)} h"
        if a >= 60 and b >= 60:
            ah, am = divmod(a, 60)
            bh, bm = divmod(b, 60)
            left = f"{ah} h" if am == 0 else f"{ah} h {am:02d}"
            right = f"{bh} h" if bm == 0 else f"{bh} h {bm:02d}"
            return f"{left}–{right}"
        return f"{format_minutes_single(a)}–{format_minutes_single(b)}"
    return format_minutes_single(int(value))


def format_money(value) -> str:
    if value is None:
        return "brak danych"
    if isinstance(value, int) and value == 0:
        return "0 €"
    if isinstance(value, float) and value == 0:
        return "0 €"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:.2f}".replace(".", ",") + " €"
    return f"{format_number(value)} €"


def format_time_range(start: str, end: str | None) -> str:
    if end is None:
        return f"od {start}"
    return f"{start}–{end}"


def status_label(code: str) -> str:
    return STATUS_LABELS.get(code, code.replace("_", " ").capitalize())


def status_chip(code: str | None, *, extra_class: str = "", compact: bool = False) -> str:
    if not code:
        return ""
    label = status_label(code)
    tone = STATUS_TONE.get(code, "neutral")
    meaning = STATUS_MEANINGS.get(code, "")
    icon_name = STATUS_ICON.get(tone, "dot")
    classes = f"status status--{tone} status--{code}"
    if compact:
        classes += " status--compact"
    if extra_class:
        classes += f" {extra_class}"
    title = f' title="{esc(meaning)}"' if meaning else ""
    return (
        f'<span class="{classes}"{title}>{icon(icon_name)}'
        f'<span>{esc(label)}</span></span>'
    )


def source_chips(plan: "Plan", source_ids: list[str] | None, *, prefix: str = "Źródło") -> str:
    if not source_ids:
        return ""
    chips = []
    for source_id in source_ids:
        source = plan.sources.get(source_id)
        title = source["title"] if source else source_id
        chips.append(
            f'<a class="source-chip" href="#src-{esc(source_id)}" '
            f'title="{esc(title)}">{icon("source")}<span>{esc(source_id)}</span></a>'
        )
    label = f'<span class="source-chips__label">{esc(prefix)}:</span>' if prefix else ""
    return '<span class="source-chips">' + label + "".join(chips) + "</span>"


def nowrap(text: str) -> str:
    return f'<span class="nowrap">{text}</span>'


def plural_pl(count: int, one: str, few: str, many: str) -> str:
    if count == 1:
        return one
    if count % 10 in {2, 3, 4} and count % 100 not in {12, 13, 14}:
        return few
    return many


def zone_label(zone: str) -> str:
    return "CY" if zone == CY_TZ else "PL" if zone == PL_TZ else zone


def airport_zone(code: str) -> str:
    return CY_TZ if code == "PFO" else PL_TZ if code in {"WMI", "WAW"} else CY_TZ


def local_time_in(iso: str, zone: str) -> str:
    dt = datetime.fromisoformat(iso).astimezone(ZoneInfo(zone))
    return dt.strftime("%H:%M")


def time_in_zone(date_iso: str, time_text: str, from_zone: str, to_zone: str) -> str:
    dt = datetime.fromisoformat(f"{date_iso}T{time_text}:00").replace(tzinfo=ZoneInfo(from_zone))
    return dt.astimezone(ZoneInfo(to_zone)).strftime("%H:%M")


class Plan:
    def __init__(self, data: dict):
        self.raw = data
        self.meta = data["meta"]
        self.trip = data["trip"]
        self.status_legend = data.get("status_legend", [])
        self.decisions = data.get("decisions", [])
        self.sources = index_by(data["sources"], "sources")
        self.days = index_by(data["days"], "days")
        self.day_list = data["days"]
        self.routes = index_by(data["routes"], "routes")
        self.route_list = data["routes"]
        self.excluded = index_by(data["excluded"], "excluded")
        self.excluded_list = data["excluded"]
        self.alternatives = index_by(data["alternatives"], "alternatives")
        self.alternative_list = data["alternatives"]
        self.places = index_by(data["places"], "places")
        self.place_list = data["places"]
        self.transfers = data["transfers"]
        self.transfer_method = data.get("transfer_method", "")
        self.dining = data["dining"]
        self.costs = data["costs"]
        self.safety = data["safety"]
        self.sunsets = data["sunsets"]
        self.sunset_note = data.get("sunset_note", "")
        self.open_issues = data["open_issues"]
        self.checklists = data["checklists"]
        self.packing = data["packing"]
        self.publication_contract = data.get("publication_contract", {})
        self.revision_log = data.get("revision_log", [])
        self.flights = self.trip.get("flights", [])
        self.primary_days: dict[str, list[dict]] = defaultdict(list)
        for day in self.day_list:
            rid = day.get("primary_route_id")
            if rid:
                self.primary_days[rid].append(day)
        self.alternatives_by_day: dict[str, list[dict]] = defaultdict(list)
        for alt in self.alternative_list:
            self.alternatives_by_day[alt["day_id"]].append(alt)
        self.coord_places = [p for p in self.place_list if p.get("coordinates")]
        self.total_places = len(self.place_list)
        self.coord_count = len(self.coord_places)
        self.blocking_issues = [i for i in self.open_issues if i.get("blocking")]
        self.total_check_items = sum(len(g.get("items", [])) for g in self.checklists)


def walk_values(node, key: str):
    if isinstance(node, dict):
        for k, value in node.items():
            if k == key:
                yield value
            yield from walk_values(value, key)
    elif isinstance(node, list):
        for value in node:
            yield from walk_values(value, key)


def validate_statuses(plan: Plan) -> None:
    def check(code, allowed: set[str], path: str):
        if code is None:
            return
        if not isinstance(code, str) or code not in allowed:
            fail(f"{path}: nieznany status {code!r}. Dodaj jawne mapowanie w build.py.")

    def walk(node, path: str = ""):
        if isinstance(node, dict):
            for key, value in node.items():
                child = f"{path}.{key}" if path else key
                if key == "plan_status":
                    pass
                elif key == "status":
                    if path == "costs":
                        check(value, {"częściowy kosztorys"}, child)
                    else:
                        check(value, GENERIC_STATUS_ALLOWED, child)
                elif key == "verification_status":
                    check(value, SOURCE_STATUS_ALLOWED, child)
                elif key == "booking_status":
                    check(value, BOOKING_ALLOWED, child)
                elif key == "effort_status":
                    check(value, EFFORT_ALLOWED, child)
                elif key == "field_readiness":
                    check(value, READINESS_ALLOWED, child)
                elif key == "distance_status":
                    check(value, DISTANCE_STATUS_ALLOWED, child)
                elif key == "ascent_status":
                    check(value, ASCENT_STATUS_ALLOWED, child)
                walk(value, child)
        elif isinstance(node, list):
            for idx, value in enumerate(node):
                walk(value, f"{path}[{idx}]")

    walk(plan.raw)
    for entry in plan.status_legend:
        code = entry.get("id")
        if code not in STATUS_LABELS and code not in STATUS_MEANINGS:
            fail(f"status_legend: brak etykiety dla {code!r}")


def validate(plan: Plan) -> None:
    data = plan.raw
    for required in ["meta", "trip", "days", "routes", "places", "sources", "alternatives",
                     "transfers", "dining", "costs", "safety", "sunsets", "open_issues",
                     "checklists", "packing"]:
        if required not in data:
            fail(f"JSON: brak wymaganego klucza {required!r}")

    meta = plan.meta
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(meta.get("version", ""))):
        fail("meta.version: oczekiwano wersji semantycznej, np. 1.0.0")
    parse_iso_date(meta.get("updated_on", ""), "meta.updated_on")

    trip = plan.trip
    start = parse_iso_date(trip.get("start_date", ""), "trip.start_date")
    end = parse_iso_date(trip.get("end_date", ""), "trip.end_date")
    if end < start:
        fail("trip.end_date jest przed trip.start_date")
    if (end - start).days + 1 != len(plan.day_list):
        fail("Liczba dni nie odpowiada zakresowi trip.start_date–trip.end_date")
    if trip.get("nights") != (end - start).days:
        fail("trip.nights nie odpowiada różnicy dat")
    if trip.get("adults") != 2:
        fail("trip.adults: ten widok jest przygotowany dla 2 osób")
    expected_dates = [date.fromordinal(start.toordinal() + i) for i in range(len(plan.day_list))]
    actual_dates = [parse_iso_date(d["date"], f"{d['id']}.date") for d in plan.day_list]
    if actual_dates != expected_dates:
        fail("Dni muszą następować kolejno po sobie, bez luk i duplikatów dat.")
    if len(plan.alternative_list) != 2:
        fail("Oczekiwano dwóch wariantów dnia (ALT-SUNDAY, ALT-THURSDAY).")

    # Globally unique identifiers make chipless cross-references unambiguous.
    seen: dict[str, str] = {}
    collections = [
        ("day", plan.day_list), ("route", plan.route_list), ("place", plan.place_list),
        ("source", plan.raw["sources"]), ("alternative", plan.alternative_list),
        ("excluded", plan.excluded_list), ("transfer", plan.transfers),
        ("dining", plan.dining), ("issue", plan.open_issues), ("checklist", plan.checklists),
        ("decision", plan.decisions), ("revision", plan.revision_log),
        ("flight", plan.flights),
    ]
    for label, items in collections:
        for item in items:
            item_id = item.get("id")
            if not item_id:
                fail(f"{label}: encja bez id")
            if item_id in seen:
                fail(f"Zduplikowane ID {item_id} ({seen[item_id]} i {label})")
            seen[item_id] = label
    for day in plan.day_list:
        for event in day.get("timeline", []):
            item_id = event.get("id")
            if not item_id:
                fail(f"{day['id']}: punkt osi bez id")
            if item_id in seen:
                fail(f"Zduplikowane ID {item_id} w osi dnia {day['id']}")
            seen[item_id] = "timeline"

    # References: sources, places, routes and days.
    valid_sources = set(plan.sources)
    for source_id in walk_values(data, "source_id"):
        if source_id not in valid_sources:
            fail(f"Nieistniejące source_id: {source_id}")
    for source_ids in walk_values(data, "source_ids"):
        if not isinstance(source_ids, list):
            fail(f"source_ids powinno być listą, otrzymano {type(source_ids).__name__}")
        for source_id in source_ids:
            if source_id not in valid_sources:
                fail(f"Nieistniejące source_id: {source_id}")

    valid_places = set(plan.places)
    for key in ["place_id", "start_place_id", "origin_id", "destination_id"]:
        for place_id in walk_values(data, key):
            if place_id is not None and place_id not in valid_places:
                fail(f"Nieistniejące {key}: {place_id}")
    for place_ids in walk_values(data, "place_ids"):
        if not isinstance(place_ids, list):
            fail("place_ids powinno być listą")
        for place_id in place_ids:
            if place_id not in valid_places:
                fail(f"Nieistniejące place_id w osi dnia: {place_id}")

    for day in plan.day_list:
        route_id = day.get("primary_route_id")
        if route_id is not None and route_id not in plan.routes:
            fail(f"{day['id']}: nieistniejący primary_route_id {route_id}")
    for route in plan.route_list:
        if route.get("start_place_id") not in valid_places:
            fail(f"{route['id']}: nieistniejący start_place_id")
    for alt in plan.alternative_list:
        if alt.get("day_id") not in plan.days:
            fail(f"{alt['id']}: nieistniejący day_id {alt.get('day_id')}")
        route_id = alt.get("route_id")
        if route_id is not None and route_id not in plan.routes:
            fail(f"{alt['id']}: nieistniejący route_id {route_id}")

    # Times, dates, day order.
    for day in plan.day_list:
        day_date = parse_iso_date(day["date"], f"{day['id']}.date")
        if not start <= day_date <= end:
            fail(f"{day['id']}: data poza zakresem wyjazdu")
        if day.get("weekday") not in WEEKDAYS:
            fail(f"{day['id']}: nieznany weekday {day.get('weekday')!r}")
        if day.get("timezone") != CY_TZ:
            fail(f"{day['id']}: podstawowa strefa dnia musi mieć Asia/Nicosia")
        for event in day.get("timeline", []):
            validate_time_range(event.get("start_local"), event.get("end_local"), f"{day['id']}.{event.get('id')}")
            event_zone = event.get("timezone", CY_TZ)
            assert_zone(event_zone, f"{day['id']}.{event['id']}.timezone")

    for route in plan.route_list:
        for key in ["planned_duration_minutes", "reserve_duration_minutes"]:
            if route.get(key) is None:
                fail(f"{route['id']}: brak {key}")
        if route["reserve_duration_minutes"] < max(route["planned_duration_minutes"]):
            fail(f"{route['id']}: rezerwa krótsza niż planowany czas")
        if route.get("gpx", {}).get("status") not in {"do_przygotowania_i_weryfikacji", "zweryfikowane"}:
            fail(f"{route['id']}: nieznany gpx.status")
        if route.get("gpx", {}).get("path"):
            url = safe_url(route["gpx"]["path"])
            if not url:
                fail(f"{route['id']}: nieprawidłowy URL GPX")

    for transfer in plan.transfers:
        if transfer.get("duration_minutes") is not None:
            dur = transfer["duration_minutes"]
            if not (isinstance(dur, list) and len(dur) == 2 and 0 <= dur[0] <= dur[1]):
                fail(f"{transfer['id']}: nieprawidłowy duration_minutes")
        if transfer.get("status") not in {"szacunek"}:
            fail(f"{transfer['id']}: oczekiwano statusu szacunek")

    for sunset in plan.sunsets:
        parse_iso_date(sunset["date"], f"sunset {sunset['date']}")
        parse_hhmm(sunset["sunset_local"], f"sunset {sunset['date']}.sunset_local")
        parse_hhmm(sunset["civil_twilight_end_local"], f"sunset {sunset['date']}.civil_twilight_end_local")
        if not start <= date.fromisoformat(sunset["date"]) <= end:
            fail(f"sunset: data {sunset['date']} poza wyjazdem")

    for flight in plan.flights:
        dep = parse_datetime(flight["departure_at"], f"{flight['id']}.departure_at")
        arr = parse_datetime(flight["arrival_at"], f"{flight['id']}.arrival_at")
        if arr <= dep:
            fail(f"{flight['id']}: przylot nie jest po odlocie")
        for code_key in ("departure_airport", "arrival_airport"):
            if flight.get(code_key) not in {"WMI", "WAW", "PFO"}:
                fail(f"{flight['id']}: nieznane lotnisko {flight.get(code_key)!r}")

    hotel = plan.trip.get("hotel", {})
    if hotel.get("place_id") not in valid_places:
        fail("trip.hotel.place_id nie istnieje")
    parse_hhmm(hotel["published_check_in"], "hotel.published_check_in")
    parse_hhmm(hotel["published_check_out"], "hotel.published_check_out")
    breakfast = hotel.get("breakfast_hours", {}).get("value", "")
    match = re.fullmatch(r"(\d{2}:\d{2})[–-](\d{2}:\d{2})", breakfast)
    if not match:
        fail("hotel.breakfast_hours.value: oczekiwano HH:MM–HH:MM")
    validate_time_range(match.group(1), match.group(2), "hotel.breakfast_hours")
    if plan.trip.get("car", {}).get("pickup_target_at"):
        parse_datetime(plan.trip["car"]["pickup_target_at"], "car.pickup_target_at")
    if plan.trip.get("car", {}).get("return_target_at"):
        parse_datetime(plan.trip["car"]["return_target_at"], "car.return_target_at")

    for cost in plan.costs.get("known_admissions", []):
        if cost.get("place_id") not in valid_places:
            fail(f"costs: nieistniejący place_id {cost.get('place_id')}")
        if cost.get("source_id") not in valid_sources:
            fail(f"costs: nieistniejący source_id {cost.get('source_id')}")

    for checklist in plan.checklists:
        if not checklist.get("items"):
            fail(f"{checklist['id']}: pusta checklista")
    for issue in plan.open_issues:
        if issue.get("priority") not in PRIORITY_ORDER:
            fail(f"{issue['id']}: nieznany priorytet {issue.get('priority')!r}")
        parse_iso_date(issue.get("due_on", ""), f"{issue['id']}.due_on")

    validate_statuses(plan)


def assert_zone(zone: str, label: str) -> None:
    try:
        ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError):
        fail(f"{label}: nieznana strefa czasowa {zone!r}")


def collect_warnings(plan: Plan) -> list[str]:
    warnings = []
    car = plan.trip.get("car", {})
    if car.get("booking_status") != "zarezerwowane_wg_uzytkownika":
        warnings.append("Auto: brak potwierdzonej rezerwacji (zgodnie z danymi).")
    null_routes = [r["id"] for r in plan.route_list if not r.get("gpx", {}).get("path")]
    if null_routes:
        warnings.append(f"GPX: brak śladu dla {len(null_routes)} tras; build nie rysuje linii.")
    if plan.coord_count < plan.total_places:
        warnings.append(
            f"Mapa: współrzędne ma {plan.coord_count} z {plan.total_places} miejsc; "
            "pozostałe są linkowane do Maps, bez geokodowania."
        )
    missing_ascent = [r["id"] for r in plan.route_list if r.get("ascent_m") is None]
    if missing_ascent:
        warnings.append(f"Przewyższenia: brak danych dla {len(missing_ascent)} tras.")
    hotel = plan.trip.get("hotel", {})
    if hotel.get("meal_plan", {}).get("value") is None:
        warnings.append("Hotel: plan wyżywienia ma null — pokazano brak danych / do potwierdzenia.")
    if hotel.get("wellness", {}).get("status") == "do_potwierdzenia":
        warnings.append("Wellness: niepotwierdzone; żaden dzień nie zależy od basenów ani sauny.")
    if car.get("provider") is None or car.get("total_price_eur") is None:
        warnings.append("Auto: przewoźnik, cena, depozyt i assistance mają null.")
    for key in ["car_total_eur", "fuel_eur", "hotel_paid_eur", "flights_paid_eur", "meals_budget_eur"]:
        if plan.costs.get(key) is None:
            warnings.append(f"Koszty: {key} = null (brak danych, nie zero).")
    null_urls = [s["id"] for s in plan.raw["sources"] if not s.get("url")]
    if null_urls:
        warnings.append(f"Źródła: {len(null_urls)} bez URL — oznaczone jako załączniki użytkownika.")
    if plan.open_issues:
        warnings.append(f"Sprawy otwarte: {len(plan.open_issues)} ({len(plan.blocking_issues)} blokujących).")
    return warnings


# === SECTION RENDERERS ===


def render_cyprus_art() -> str:
    return f"""
    <figure class="hero-art" aria-labelledby="hero-art-caption">
      <svg class="hero-art__svg" viewBox="0 0 700 360" role="img" aria-label="Dekoracyjny kontur Cypru">
        <defs>
          <linearGradient id="sea-wash" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#0C5C6B" stop-opacity=".10"/>
            <stop offset="1" stop-color="#D9A441" stop-opacity=".03"/>
          </linearGradient>
          <clipPath id="cyprus-clip"><path d="{CYPRUS_PATH}"/></clipPath>
          <filter id="paper-grain">
            <feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" stitchTiles="stitch" result="noise"/>
            <feColorMatrix in="noise" type="saturate" values="0" result="gray"/>
            <feComponentTransfer in="gray"><feFuncA type="table" tableValues="0 .055"/></feComponentTransfer>
          </filter>
        </defs>
        <circle cx="514" cy="120" r="106" fill="url(#sea-wash)"/>
        <path d="{CYPRUS_PATH}" fill="#FFFDF8" stroke="#0C5C6B" stroke-width="1.15"/>
        <g clip-path="url(#cyprus-clip)" fill="none" stroke="#0C5C6B" stroke-width=".65" opacity=".38">
          <path d="M20 302C122 264 198 291 276 270s145-84 243-61 107 18 174 2"/>
          <path d="M14 285C120 246 200 273 282 250s145-80 239-56 108 18 176 1"/>
          <path d="M18 268C126 230 203 254 286 231s143-74 235-50 110 18 174 1"/>
          <path d="M22 251C130 214 207 236 291 213s141-69 231-45 111 17 172 0"/>
          <path d="M24 234C134 198 210 218 296 195s139-64 227-40 112 16 170 0"/>
          <path d="M25 217C136 182 212 200 300 177s137-58 222-35 113 15 168 0"/>
          <path d="M25 200C136 166 214 183 302 160s134-51 218-29 114 14 166 0"/>
          <path d="M24 183C134 150 215 168 303 145s132-44 214-22 115 12 164 0"/>
          <path d="M22 166C129 135 212 153 301 130s130-37 210-16 115 11 162 0"/>
          <path d="M21 149C126 119 210 138 299 115s128-30 206-10 115 10 160 0"/>
          <path d="M21 132C123 105 208 122 296 100s127-23 202-5 114 9 158 0"/>
          <path d="M20 115C120 90 206 107 294 85s125-16 198 1 114 8 156 0"/>
        </g>
        <path d="{CYPRUS_PATH}" fill="none" stroke="#B85C3E" stroke-width=".6" opacity=".32" transform="translate(8,8)"/>
        <path d="{CYPRUS_PATH}" fill="none" stroke="#5C6B4A" stroke-width=".5" opacity=".22" transform="translate(15,15)"/>
        <rect width="700" height="360" filter="url(#paper-grain)" opacity=".6"/>
      </svg>
      <figcaption id="hero-art-caption" class="hero-art__caption">
        <span>Jedna wyspa</span><span>jeden tydzień</span>
      </figcaption>
    </figure>
    """


def render_hero(plan: Plan) -> str:
    version = esc(plan.meta["version"])
    updated = format_date_pl(plan.meta["updated_on"])
    blocking = len(plan.blocking_issues)
    plan_status = esc(plan.trip.get("plan_status", "Plan bazowy"))
    return f"""
    <div class="hero__inner page-width">
      <div class="hero__copy">
        <div class="hero__utility">
          <a class="back-link" href="/">KJ <span>/</span> Photo Journal</a>
          <span class="hero__edition">Wydanie {version}</span>
        </div>
        <p class="eyebrow">PODRÓŻ · CYPR · 2026</p>
        <h1 class="hero__title">Cypr <span>bez pośpiechu</span></h1>
        <p class="hero__dates">7–13 listopada 2026 <span aria-hidden="true">·</span> 2 osoby <span aria-hidden="true">·</span> 6 nocy <span aria-hidden="true">·</span> Pafos</p>
        <p class="hero__lede">Dwa widokowe trekkings, Pafos, Troodos, Omodos i Petra. Jedna baza, spokojne tempo i miejsce na światło.</p>
        <div class="hero__actions">
          <a class="button button--primary" href="#dzis">Dziś {icon("arrow")}</a>
          <button class="button button--ghost js-print" type="button">{icon("print")} Drukuj</button>
          <a class="button button--text" href="#tydzien">Zobacz plan {icon("chevron")}</a>
        </div>
        <p class="hero__footnote">Plan bazowy. Rezerwacje lotów i hotelu według użytkownika; auto, wellness i warunki terenowe wymagają potwierdzenia.</p>
      </div>
      {render_cyprus_art()}
    </div>
    <div class="hero__status">
      <div class="page-width">
        <dl class="status-bar" aria-label="Status planu">
          <div><dt>Wersja</dt><dd>{version}</dd></div>
          <div><dt>Aktualizacja</dt><dd>{esc(updated)}</dd></div>
          <div><dt>Status</dt><dd>Plan bazowy</dd></div>
          <div><dt>Auto</dt><dd><a href="#auto">Do potwierdzenia</a></dd></div>
          <div class="status-bar__wide"><dt>Do potwierdzenia</dt><dd><a href="#todo">{blocking} zadań blokujących</a></dd></div>
          <div class="status-bar__offline"><dt>Tryb</dt><dd><span class="connection connection--hero" data-connection role="status" aria-live="polite">{icon("wifi")}<span class="connection__text">sprawdzam</span></span></dd></div>
        </dl>
        <p class="hero__plan-note">{plan_status}</p>
      </div>
    </div>
    """


def render_nav(plan: Plan) -> str:
    nav = [
        ("#top", "Start"),
        ("#tydzien", "Tydzień"),
        ("#dzis", "Dziś"),
        ("#dni", "Dni"),
        ("#trasy", "Trasy"),
        ("#mapa", "Mapa"),
        ("#praktyka", "Praktyka"),
        ("#checklisty", "Checklisty"),
        ("#todo", "Do potwierdzenia"),
        ("#zrodla", "Źródła"),
    ]
    items = "".join(f'<li><a href="{href}">{esc(label)}</a></li>' for href, label in nav)
    return f"""
    <nav class="subnav" aria-label="Sekcje planu">
      <div class="page-width subnav__inner">
        <a class="subnav__brand" href="#top" aria-label="Cypr 2026 — początek strony"><span>CYPR</span> <b>2026</b></a>
        <div class="subnav__scroll">
          <ul class="subnav__list">{items}</ul>
        </div>
        <div class="subnav__tools">
          <a class="emergency-mini" href="tel:112" aria-label="Numer alarmowy 112">{icon("phone")}<span>112</span></a>
          <span class="connection connection--nav" data-connection role="status" aria-live="polite">{icon("wifi")}<span class="connection__text">sprawdzam</span></span>
        </div>
      </div>
    </nav>
    """


def render_week_card(plan: Plan, day: dict) -> str:
    day_no = day["id"].split("-")[-1]
    walk = format_km(day.get("walk_km_estimate"))
    drive = format_km(day.get("drive_km_estimate"))
    hunt = ' <span class="hunting-micro">bez trekkingu</span>' if day["date"] in HUNTING_DATES else ""
    return f"""
      <a class="week-card" href="#day-{day_no}" data-day-date="{esc(day['date'])}"
         aria-label="{esc(day['id'])} · {esc(format_date_pl(day['date']))} · {esc(day['title'])}">
        <span class="week-card__number">{esc(day_no)}</span>
        <span class="week-card__today">Dziś</span>
        <time class="week-card__date" datetime="{esc(day['date'])}">{esc(format_date_pl(day['date']))}</time>
        <span class="week-card__weekday">{esc(day['weekday'])}{hunt}</span>
        <h3 class="week-card__title">{esc(day['title'])}</h3>
        <p class="week-card__mode">{esc(day['mode'])}</p>
        <p class="week-card__summary">{esc(day['summary'])}</p>
        <span class="week-card__metrics">
          <span>Pieszo <b>{esc(walk)}</b></span>
          <span>Auto <b>{esc(drive)}</b></span>
        </span>
        <span class="week-card__arrow" aria-hidden="true">{icon("arrow")}</span>
      </a>
    """


def render_week(plan: Plan) -> str:
    cards = "".join(render_week_card(plan, day) for day in plan.day_list)
    return f"""
    <section class="section section--week" id="tydzien" aria-labelledby="tydzien-title">
      <div class="page-width">
        <header class="section-head">
          <p class="section-index"><span>01</span> / PRZEGLĄD</p>
          <div class="section-head__body">
            <h2 id="tydzien-title">Tydzień w skrócie</h2>
            <p class="section-lede">Siedem dni, jedna baza i dwa główne trekkings. Karty są skrótem; pełny plan z godzinami znajduje się <a href="#dni">niżej</a>.</p>
          </div>
        </header>
        <div class="week-strip" aria-label="Siedem dni wyjazdu">
          {cards}
        </div>
        <p class="section-footnote">{icon("alert")} <span>8 i 11 listopada to dni polowań — bez trekkingu. Szczegóły w sekcji <a href="#bezpieczenstwo">Bezpieczeństwo</a>.</span></p>
      </div>
    </section>
    """


def nearest_issue(plan: Plan) -> dict | None:
    if not plan.open_issues:
        return None
    return sorted(plan.open_issues, key=lambda item: (item.get("due_on") or "9999", PRIORITY_ORDER.get(item.get("priority"), 9)))[0]


def render_today(plan: Plan) -> str:
    hotel = plan.places.get(plan.trip["hotel"]["place_id"], {})
    hotel_phone_raw = hotel.get("phone")
    hotel_phone = re.sub(r"[^\d+]", "", hotel_phone_raw or "")
    issue = nearest_issue(plan)
    nearest = ""
    if issue:
        nearest = (
            f'<p>Najbliższy termin: <strong>{esc(format_date_pl(issue["due_on"]))}</strong> — '
            f'{esc(issue["title"])}.</p>'
        )
    return f"""
    <section class="section section--today" id="dzis" aria-labelledby="dzis-title">
      <div class="page-width">
        <header class="section-head section-head--compact">
          <p class="section-index"><span>02</span> / TERAZ</p>
          <div class="section-head__body">
            <h2 id="dzis-title">Dziś</h2>
            <p class="section-lede">Jeden spokojny punkt widzenia: zegar Cypru, bieżący dzień i następny krok. Bez automatycznej pogody i bez przewijania strony.</p>
          </div>
        </header>
        <div class="today-card" data-today>
          <div class="today-card__main">
            <p class="today-kicker"><span class="live-dot" aria-hidden="true"></span> <span data-today-kicker>Widok planu</span></p>
            <h3 class="today-title" data-today-title>Plan na 7–13 listopada 2026</h3>
            <div class="today-body" data-today-body>
              <p>Ten widok dopasuje się do daty po włączeniu JavaScript. Pełny plan, kontakty i druk działają także bez niego.</p>
              {nearest}
            </div>
            <div class="today-actions" data-today-actions>
              <a class="text-link" href="#tydzien">Tydzień w skrócie {icon("arrow")}</a>
              <a class="text-link" href="#todo">Zadania do potwierdzenia {icon("arrow")}</a>
            </div>
            <p class="date-override" data-date-override hidden></p>
            <noscript><p class="noscript-note">Widok „Dziś” wymaga JavaScript. Cały plan bazowy jest widoczny poniżej, a wydruk obejmuje wszystkie dni.</p></noscript>
          </div>
          <aside class="today-card__aside" aria-label="Szybkie kontakty">
            <div class="clock-block">
              <span class="clock" data-cyprus-clock>--:--</span>
              <span class="clock-label">Czas na Cyprze<br><small>Asia/Nicosia · UTC+2</small></span>
            </div>
            <ul class="quick-links">
              <li><a href="tel:{esc(hotel_phone)}">{icon("phone")} <span><small>Hotel</small>{esc(format_phone_display(hotel_phone_raw))}</span></a></li>
              <li><a class="quick-links__emergency" href="tel:112">{icon("phone")} <span><small>Alarmowy</small>112</span></a></li>
              <li><a href="#mapa">{icon("map")} <span><small>Mapa</small>Punkty i Maps</span></a></li>
            </ul>
          </aside>
        </div>
      </div>
    </section>
    """


def render_flight_band(plan: Plan, day: dict) -> str:
    flights = []
    for flight in plan.flights:
        dep_date = flight["departure_at"][:10]
        if dep_date != day["date"]:
            continue
        dep_zone = airport_zone(flight["departure_airport"])
        arr_zone = airport_zone(flight["arrival_airport"])
        dep_local = local_time_in(flight["departure_at"], dep_zone)
        arr_local = local_time_in(flight["arrival_at"], arr_zone)
        cy_dep = local_time_in(flight["departure_at"], CY_TZ)
        pl_dep = local_time_in(flight["departure_at"], PL_TZ)
        cy_arr = local_time_in(flight["arrival_at"], CY_TZ)
        pl_arr = local_time_in(flight["arrival_at"], PL_TZ)
        bagdrop = ""
        if flight["id"] == "FL-IN":
            bagdrop = '<p class="flight-band__alert">Bag drop zamyka się o <strong>05:20 czasu Cypru</strong>. Bagaż ma być przyjęty; stanie w kolejce nie wystarczy.</p>'
        flights.append(f"""
          <div class="flight-band__item">
            <span class="flight-band__icon">{icon("plane")}</span>
            <div class="flight-band__copy">
              <p><strong>{esc(flight["flight_no"])}</strong> · {esc(flight["carrier"])}</p>
              <p>{esc(flight["departure_airport"])} {esc(dep_local)} ({zone_label(dep_zone)}) <span aria-hidden="true">→</span> {esc(flight["arrival_airport"])} {esc(arr_local)} ({zone_label(arr_zone)})</p>
              <p class="flight-band__zones">Cypr: {esc(cy_dep)} start / {esc(cy_arr)} przylot · Polska: {esc(pl_dep)} start / {esc(pl_arr)} przylot</p>
              {bagdrop}
            </div>
            {status_chip(flight.get("status"), compact=True)}
          </div>
        """)
    if not flights:
        return ""
    return f'<div class="flight-band" aria-label="Lot w tym dniu">{"".join(flights)}</div>'


def render_dual_zone(day: dict, event: dict) -> str:
    event_zone = event.get("timezone", day.get("timezone", CY_TZ))
    if event_zone == day.get("timezone", CY_TZ) and event.get("kind") != "flight":
        return ""
    other_zone = PL_TZ if event_zone == CY_TZ else CY_TZ
    other = time_in_zone(day["date"], event["start_local"], event_zone, other_zone)
    place_phrase = "w Polsce" if other_zone == PL_TZ else "na Cyprze"
    return (
        f'<span class="event-tz">'
        f'<span class="tz-code">{zone_label(event_zone)}</span>'
        f'<span class="tz-alt">{place_phrase}: {esc(other)}</span>'
        f'</span>'
    )


def place_links(plan: Plan, place_ids: list[str]) -> str:
    links = []
    for place_id in place_ids:
        place = plan.places.get(place_id)
        if not place:
            continue
        links.append(
            f'<a class="place-link" href="#place-{esc(place_id)}">{icon("pin")}{esc(place["name"])}</a>'
        )
    return " ".join(links)


def place_usage(plan: Plan, place_id: str) -> list[str]:
    usage = []
    for day in plan.day_list:
        if any(place_id in event.get("place_ids", []) for event in day.get("timeline", [])):
            usage.append(day["id"])
    for route in plan.route_list:
        if route.get("start_place_id") == place_id:
            label = f'{route["id"]} — start'
            if label not in usage:
                usage.append(label)
    for transfer in plan.transfers:
        if place_id in {transfer.get("origin_id"), transfer.get("destination_id")}:
            label = f'{transfer["id"]} — przejazd'
            if label not in usage:
                usage.append(label)
    return usage


def render_timeline(plan: Plan, day: dict) -> str:
    items = []
    for event in day.get("timeline", []):
        time_text = format_time_range(event["start_local"], event.get("end_local"))
        optional = '<span class="optional-badge">opcjonalne</span>' if event.get("optional") else ""
        zone_note = render_dual_zone(day, event)
        basis = esc(event.get("time_basis", ""))
        places = place_links(plan, event.get("place_ids", []))
        items.append(f"""
          <li class="timeline__item timeline__item--{esc(event.get('kind', 'plan'))}">
            <div class="timeline__time">
              <time datetime="{esc(day['date'])}T{esc(event['start_local'])}">{esc(time_text)}</time>
              {zone_note}
            </div>
            <span class="timeline__dot" aria-hidden="true"></span>
            <div class="timeline__content">
              <div class="timeline__top">
                <h5>{esc(event["title"])}</h5>
                {optional}
              </div>
              <p>{esc(event["description"])}</p>
              <p class="timeline__meta">
                {places}
                {'<span class="meta-dot" aria-hidden="true">·</span>' if places and basis else ''}
                <span class="time-basis">{esc(basis)}</span>
              </p>
            </div>
          </li>
        """)
    return f'<ol class="timeline" aria-label="Oś czasu dnia">{"".join(items)}</ol>'


def render_alternative(plan: Plan, alt: dict) -> str:
    anchor = "alt-" + alt["id"].replace("ALT-", "").lower()
    conditions = "".join(f"<li>{esc(item)}</li>" for item in alt.get("conditions", []))
    replaces = ", ".join(alt.get("replaces", []))
    day = plan.days[alt["day_id"]]
    return f"""
      <aside class="variant-card" id="{esc(anchor)}" aria-labelledby="{esc(anchor)}-title">
        <div class="variant-card__head">
          <p class="variant-kicker">WARIANT · OPCJA · NIE PLAN BAZOWY</p>
          <h3 id="{esc(anchor)}-title">{esc(alt["name"])}</h3>
          <p>Przy dniu <a href="#day-{day['id'].split('-')[-1]}">{esc(day['id'])} · {esc(day['title'])}</a></p>
        </div>
        <dl class="variant-facts">
          <div><dt>Co zastępuje</dt><dd>{esc(replaces)}</dd></div>
          <div><dt>Harmonogram</dt><dd>{esc(alt["schedule"])}</dd></div>
        </dl>
        <div class="variant-columns">
          <div>
            <h4>Warunki</h4>
            <ul>{conditions}</ul>
          </div>
          <div>
            <h4>Fallback</h4>
            <p>{esc(alt["fallback"])}</p>
          </div>
        </div>
        <p class="variant-card__foot">{icon("info")} Domyślnie obowiązuje plan bazowy. Wariant nie jest dodatkowym obowiązkiem.</p>
      </aside>
    """


def render_day(plan: Plan, day: dict) -> str:
    day_no = day["id"].split("-")[-1]
    alt_cards = "".join(render_alternative(plan, alt) for alt in plan.alternatives_by_day.get(day["id"], []))
    hunt = day["date"] in HUNTING_DATES
    hunt_note = ""
    if hunt:
        hunt_note = f"""
          <div class="day-alert day-alert--hunting">
            {icon("alert")}
            <div><strong>Dzień polowań — bez trekkingu.</strong>
            <p>Zgodnie z sekcją bezpieczeństwa 8 i 11 XI nie planujemy tras terenowych. Pozostań w programie miejskim i kulturowym. Jaskrawa odzież nie zastępuje kontroli obszaru.</p></div>
          </div>
        """
    primary_route = plan.routes.get(day.get("primary_route_id")) if day.get("primary_route_id") else None
    route_link = ""
    if primary_route:
        route_link = (
            f'<a class="route-jump" href="#trasa-{esc(primary_route["id"].replace("TR-", "").lower())}">'
            f'{icon("trail")} Trasa: {esc(primary_route["name"])} {icon("arrow")}</a>'
        )
    cut = "".join(f"<li>{esc(item)}</li>" for item in day.get("cut_order", []))
    sources = source_chips(plan, day.get("source_ids", []))
    flight_band = render_flight_band(plan, day)
    timezone_note = "Czasy w Asia/Nicosia (UTC+2)." if day["date"] not in {"2026-11-07", "2026-11-13"} else "Czasy w Asia/Nicosia (UTC+2); loty w czasie lokalnym lotnisk, z obiema strefami."
    return f"""
      <article class="day-card" id="day-{esc(day_no)}" data-day-date="{esc(day['date'])}" aria-labelledby="day-{esc(day_no)}-title">
        <header class="day-card__head">
          <p class="day-label">DAY-{esc(day_no)} <span>/</span> {esc(format_date_pl(day['date']))}</p>
          <div class="day-card__title-row">
            <div>
              <p class="day-weekday">{esc(day['weekday'])}</p>
              <h3 id="day-{esc(day_no)}-title">{esc(day["title"])}</h3>
            </div>
            <p class="day-summary">{esc(day["summary"])}</p>
          </div>
          <div class="chip-row">
            <span class="chip">{icon("calendar")}{esc(day['mode'])}</span>
            <span class="chip">{icon("foot")}Pieszo: <b>{esc(format_km(day.get("walk_km_estimate")))}</b></span>
            <span class="chip">{icon("car")}Auto: <b>{esc(format_km(day.get("drive_km_estimate")))}</b></span>
            {status_chip(day.get("effort_status"), compact=True)}
          </div>
          <p class="timezone-note">{icon("clock")} {timezone_note}</p>
        </header>
        {flight_band}
        {hunt_note}
        <details class="day-disclosure" open data-day-disclosure>
          <summary><span>Oś czasu, notatki i źródła</span>{icon("chevron")}</summary>
          <div class="day-card__body">
            <div class="timeline-wrap">
              <h4 class="subheading">Oś czasu</h4>
              {render_timeline(plan, day)}
            </div>
            <div class="day-notes">
              <section class="day-note">
                <h4>{icon("alert")} Jeśli się opóźni</h4>
                <ol>{cut}</ol>
              </section>
              <section class="day-note">
                <h4>{icon("sun")} Zła pogoda</h4>
                <p>{esc(day.get("bad_weather", ""))}</p>
              </section>
              <section class="day-note">
                <h4>{icon("camera")} Fotografia</h4>
                <p>{esc(day.get("photography", ""))}</p>
              </section>
              <section class="day-note">
                <h4>{icon("check")} Domknięcie dnia</h4>
                <p>{esc(day.get("return_note", ""))}</p>
              </section>
            </div>
            <div class="day-card__foot">
              {route_link}
              <details class="source-note" open data-collapse-on-load>
                <summary>{icon("source")} Źródła dnia</summary>
                <div class="source-note__body">{sources}</div>
              </details>
            </div>
          </div>
        </details>
      </article>
      {alt_cards}
    """


def render_days(plan: Plan) -> str:
    blocks = []
    for day in plan.day_list:
        blocks.append(
            f'<div class="day-block" data-block-date="{esc(day["date"])}">'
            + render_day(plan, day)
            + '</div>'
        )
    return f"""
    <section class="section section--days" id="dni" aria-labelledby="dni-title">
      <div class="page-width">
        <header class="section-head">
          <p class="section-index"><span>03</span> / DZIENNIK</p>
          <div class="section-head__body">
            <h2 id="dni-title">Dni</h2>
            <p class="section-lede">Każdy dzień ma własną oś czasu, plan awaryjny, notatkę fotograficzną i źródła. Warianty są osobnymi kartami i nigdy nie mieszają się z planem bazowym.</p>
          </div>
        </header>
        {''.join(blocks)}
      </div>
    </section>
    """


def route_anchor(route_id: str) -> str:
    return "trasa-" + route_id.replace("TR-", "").lower().replace("_", "-")


def route_day_links(plan: Plan, route: dict) -> str:
    links = []
    for day in plan.primary_days.get(route["id"], []):
        links.append(f'<a class="day-link" href="#day-{day["id"].split("-")[-1]}">{esc(day["id"])} · {esc(day["title"])}</a>')
    for alt in plan.alternative_list:
        if alt.get("route_id") == route["id"] and alt["day_id"] not in {d["id"] for d in plan.primary_days.get(route["id"], [])}:
            day = plan.days[alt["day_id"]]
            anchor = "alt-" + alt["id"].replace("ALT-", "").lower()
            links.append(
                f'<a class="day-link" href="#{esc(anchor)}">{esc(day["id"])} · wariant {esc(alt["id"])}</a>'
            )
    if not links:
        return '<span class="muted">Brak dnia w planie bazowym; trasa jest wyłącznie opcją rezerwową.</span>'
    return '<span class="route-links">' + " ".join(links) + "</span>"


def render_route_body(plan: Plan, route: dict) -> str:
    start = plan.places.get(route["start_place_id"], {})
    activation = "".join(f"<li>{esc(item)}</li>" for item in route.get("activation", []))
    cancel = "".join(f"<li>{esc(item)}</li>" for item in route.get("cancel", []))
    risks = "".join(f"<li>{esc(item)}</li>" for item in route.get("risks", []))
    notes = "".join(f"<li>{esc(item)}</li>" for item in route.get("notes", []))
    gpx = route.get("gpx", {})
    gpx_path = safe_url(gpx.get("path"))
    gpx_link = (
        f'<a class="button button--small button--ghost" href="{esc(gpx_path)}">Otwórz GPX {icon("download")}</a>'
        if gpx_path else ""
    )
    ascent_value = format_metres(route.get("ascent_m"))
    if route.get("ascent_m") is None:
        ascent_value = "brak danych"
    difficulty = route.get("official_difficulty")
    difficulty_text = f"{difficulty} / 3" if difficulty is not None else "brak danych"
    stats = f"""
      <dl class="route-stats">
        <div><dt>Dystans</dt><dd>{esc(format_km(route.get("distance_km")))}<span class="stat-status">{status_chip(route.get("distance_status"), compact=True)}</span></dd></div>
        <div><dt>Czas planowany</dt><dd>{esc(format_duration(route.get("planned_duration_minutes")))}<span class="stat-note">z fotografią i przerwami</span></dd></div>
        <div><dt>Rezerwa</dt><dd>{esc(format_duration(route.get("reserve_duration_minutes")))}<span class="stat-note">maksymalny margines</span></dd></div>
        <div><dt>Trudność oficjalna</dt><dd>{esc(difficulty_text)}<span class="stat-note">skala źródłowa</span></dd></div>
        <div><dt>Przewyższenie</dt><dd>{esc(ascent_value)}<span class="stat-status">{status_chip(route.get("ascent_status"), compact=True)}</span></dd></div>
        <div><dt>Start</dt><dd><a href="#place-{esc(route['start_place_id'])}">{esc(start.get('name', route['start_place_id']))}</a><span class="stat-note">punkt orientacyjny, nie ślad</span></dd></div>
      </dl>
    """
    return f"""
      <div class="route-chips">
        {status_chip(route.get("field_readiness"))}
        {status_chip(gpx.get("status"))}
      </div>
      {stats}
      <div class="route-columns">
        <section class="route-conditions">
          <h4>{icon("check")} Warunki wejścia</h4>
          <ul>{activation}</ul>
        </section>
        <section class="route-conditions route-conditions--cancel">
          <h4>{icon("alert")} Odwołanie</h4>
          <ul>{cancel}</ul>
        </section>
      </div>
      <div class="route-columns">
        <section class="route-notes">
          <h4>Ryzyka</h4>
          <ul>{risks}</ul>
        </section>
        <section class="route-notes">
          <h4>Notatki planistyczne</h4>
          <ul>{notes}</ul>
        </section>
      </div>
      <div class="gpx-box">
        <div class="gpx-box__top">
          <span class="gpx-box__label">{icon("source")} GPX</span>
          {status_chip(gpx.get("status"), compact=True)}
        </div>
        <p>{esc(gpx.get("note", ""))}</p>
        {gpx_link}
        <p class="gpx-box__warning">To nie jest gotowy ślad. Nie rysujemy linii trasy z punktów orientacyjnych.</p>
      </div>
      <div class="route-footer">
        {route_day_links(plan, route)}
        {source_chips(plan, route.get("source_ids", []))}
      </div>
    """


def render_route_card(plan: Plan, route: dict, *, reserve: bool = False) -> str:
    anchor = route_anchor(route["id"])
    body = render_route_body(plan, route)
    if reserve:
        return f"""
          <article class="route-card route-card--reserve" id="{esc(anchor)}" aria-labelledby="{esc(anchor)}-title">
            <header class="route-card__head">
              <div>
                <p class="route-role">REZERWA · {esc(route["role"])}</p>
                <h3 id="{esc(anchor)}-title">{esc(route["name"])}</h3>
              </div>
              <span class="reserve-stamp">To nie plan bazowy</span>
            </header>
            <p class="route-card__summary">{esc(route.get("description", ""))}</p>
            <div class="reserve-facts">
              <span>{esc(format_km(route.get("distance_km")))}</span>
              <span>{esc(format_duration(route.get("planned_duration_minutes")))}</span>
              <span>rezerwa {esc(format_duration(route.get("reserve_duration_minutes")))}</span>
            </div>
            <details class="route-details" open data-collapse-on-load>
              <summary>Pokaż parametry, warunki i źródła {icon("chevron")}</summary>
              <div class="route-details__body">{body}</div>
            </details>
          </article>
        """
    return f"""
      <article class="route-card" id="{esc(anchor)}" aria-labelledby="{esc(anchor)}-title">
        <header class="route-card__head">
          <div>
            <p class="route-role">{esc(route["role"])}</p>
            <h3 id="{esc(anchor)}-title">{esc(route["name"])}</h3>
          </div>
          <span class="route-id">{esc(route["id"])}</span>
        </header>
        <p class="route-card__summary">{esc(route.get("description", ""))}</p>
        {body}
      </article>
    """


def render_routes(plan: Plan) -> str:
    active_ids = ["TR-APHRODITE", "TR-ARTEMIS"]
    conditional_ids = ["TR-VOUNI"]
    reserve_ids = [route["id"] for route in plan.route_list if route["id"] not in active_ids + conditional_ids]
    active = "".join(render_route_card(plan, plan.routes[rid]) for rid in active_ids if rid in plan.routes)
    conditional = "".join(render_route_card(plan, plan.routes[rid]) for rid in conditional_ids if rid in plan.routes)
    reserve = "".join(render_route_card(plan, plan.routes[rid], reserve=True) for rid in reserve_ids)
    excluded = []
    for item in plan.excluded_list:
        excluded.append(f"""
          <article class="excluded-card">
            <div>
              <p class="excluded-card__label">POZA PLANEM</p>
              <h4>{esc(item["name"])}</h4>
              <p>{esc(item["reason"])}</p>
              {source_chips(plan, item.get("source_ids", []))}
            </div>
            {icon("alert")}
          </article>
        """)
    return f"""
    <section class="section section--routes" id="trasy" aria-labelledby="trasy-title">
      <div class="page-width">
        <header class="section-head">
          <p class="section-index"><span>04</span> / TEREN</p>
          <div class="section-head__body">
            <h2 id="trasy-title">Trasy</h2>
            <p class="section-lede">Aphrodite i Artemis są aktywne w planie bazowym. Vouni jest warunkową zamianą czwartku. Pozostałe trasy to rezerwy — nie obowiązki.</p>
            <p class="section-aside">{esc(plan.trip.get("distance_exception", ""))}</p>
          </div>
        </header>
        <section class="route-group" aria-labelledby="trasy-aktywne">
          <div class="group-head">
            <h3 id="trasy-aktywne">Aktywne</h3>
            <span>2 trasy</span>
          </div>
          <div class="route-stack">{active}</div>
        </section>
        <section class="route-group" aria-labelledby="trasy-warunkowe">
          <div class="group-head">
            <h3 id="trasy-warunkowe">Warunkowa</h3>
            <span>tylko po pełnej kontroli</span>
          </div>
          <div class="route-stack">{conditional}</div>
        </section>
        <section class="route-group" aria-labelledby="trasy-rezerwowe">
          <div class="group-head">
            <h3 id="trasy-rezerwowe">Rezerwowe</h3>
            <span>zwinięte · to nie plan bazowy</span>
          </div>
          <p class="group-note">{icon("info")} Rezerwy nie są dodatkowymi celami. Dotyczą wyłącznie świadomej zamiany, po sprawdzeniu warunków i czasu.</p>
          <div class="route-stack route-stack--reserve">{reserve}</div>
        </section>
        <section class="excluded" aria-labelledby="poza-planem">
          <div class="group-head">
            <h3 id="poza-planem">Poza planem</h3>
            <span>świadomie pominięte</span>
          </div>
          <div class="excluded-grid">{''.join(excluded)}</div>
        </section>
      </div>
    </section>
    """


def render_coordinate_status(status: str | None) -> str:
    return status_chip(status, compact=True) if status else ""


def render_place(plan: Plan, place: dict) -> str:
    coord = place.get("coordinates") or {}
    usage = place_usage(plan, place["id"])
    if usage:
        usage_text = ", ".join(usage)
    else:
        usage_text = "brak bezpośredniego użycia w osi czasu"
    coords_text = (
        f'{format_coord(coord.get("lat"))}, {format_coord(coord.get("lon"))}'
        if coord else "brak współrzędnych"
    )
    coords_html = (
        f'<span class="place-coords">{icon("pin")}<code>{esc(coords_text)}</code>{render_coordinate_status(coord.get("status"))}</span>'
        if coord else
        f'<span class="place-coords place-coords--none">{icon("pin")}brak współrzędnych; otwórz w Maps</span>'
    )
    map_url = safe_url(place.get("map_url"))
    map_link = (
        f'<a class="text-link" href="{esc(map_url)}">Otwórz w Maps {icon("arrow")}</a>'
        if map_url else ""
    )
    facts = []
    if place.get("address"):
        facts.append(f'<div><dt>Adres</dt><dd>{esc(place["address"])}</dd></div>')
    if place.get("phone"):
        tel = re.sub(r"[^\d+]", "", place["phone"])
        facts.append(f'<div><dt>Telefon</dt><dd><a href="tel:{esc(tel)}">{esc(format_phone_display(place["phone"]))}</a></dd></div>')
    facts.append(f'<div><dt>Godziny</dt><dd>{esc(place.get("published_hours") or "brak danych")}</dd></div>')
    if place.get("fee_eur_per_adult") is None:
        fee = "brak danych"
    elif place.get("fee_eur_per_adult") == 0:
        fee = "0 €"
    else:
        fee = f'{format_money(place["fee_eur_per_adult"])}/os.'
    facts.append(f'<div><dt>Wstęp</dt><dd>{esc(fee)}</dd></div>')
    return f"""
      <article class="place-card" id="place-{esc(place["id"])}">
        <header class="place-card__head">
          <p class="place-type">{esc(PLACE_TYPE_LABELS.get(place.get("type"), place.get("type", "miejsce")))}</p>
          <h4>{esc(place["name"])}</h4>
          {coords_html}
        </header>
        <p class="place-notes">{esc(place.get("notes", ""))}</p>
        <dl class="place-facts">{''.join(facts)}</dl>
        <p class="place-usage"><span>W planie:</span> {esc(usage_text)}</p>
        {map_link}
      </article>
    """


def render_map(plan: Plan) -> str:
    groups = []
    for group_id, group_name, types in PLACE_GROUPS:
        places = [place for place in plan.place_list if place.get("type") in types]
        if not places:
            continue
        cards = "".join(render_place(plan, place) for place in places)
        groups.append(f"""
          <section class="place-group" aria-labelledby="place-group-{group_id}">
            <div class="group-head"><h3 id="place-group-{group_id}">{esc(group_name)}</h3><span>{len(places)}</span></div>
            <div class="place-grid">{cards}</div>
          </section>
        """)
    return f"""
    <section class="section section--map" id="mapa" aria-labelledby="mapa-title">
      <div class="page-width">
        <header class="section-head">
          <p class="section-index"><span>05</span> / ORIENTACJA</p>
          <div class="section-head__body">
            <h2 id="mapa-title">Mapa i miejsca</h2>
            <p class="section-lede">Punkty orientacyjne; to nie jest ślad GPS. {plan.coord_count} z {plan.total_places} miejsc ma współrzędne. Pozostałe otwierają wyszukiwanie w Maps — bez zgadywania lokalizacji.</p>
          </div>
        </header>
        <div class="map-frame">
          <div class="map-canvas" id="map-canvas" role="region" aria-label="Interaktywna mapa miejsc z planu">
            <div class="map-placeholder">
              {icon("map")}
              <p>Mapa jest ładowana dopiero przy tej sekcji. Pełna lista miejsc znajduje się poniżej i działa bez JavaScriptu.</p>
            </div>
          </div>
          <div class="map-legend" aria-label="Legenda statusu współrzędnych">
            <span class="legend-title">Status punktu</span>
            <span class="map-key"><i class="map-dot map-dot--ok"></i>zweryfikowane</span>
            <span class="map-key"><i class="map-dot map-dot--audit"></i>przejęte z audytu</span>
            <span class="map-key"><i class="map-dot map-dot--approx"></i>orientacyjne, do potwierdzenia</span>
            <span class="map-key"><i class="map-dot map-dot--cluster">3</i>grupa bliskich miejsc</span>
          </div>
        </div>
        <div class="map-notes">
          <p>{icon("info")} Kafelki OpenStreetMap nie są cache’owane przez service worker. Po pierwszym wejściu plan działa offline, ale mapa może pokazać tylko szare tło. Do nawigacji offline użyj Organic Maps lub Guru Maps.</p>
          <p>{icon("alert")} Markery pokazują miejsca, nie przebieg szlaku. Nie rysujemy linii z punktów orientacyjnych. Bliskie punkty łączą się w jeden marker — kliknij go, aby zobaczyć pełną listę.</p>
        </div>
        <div class="places">
          {''.join(groups)}
        </div>
      </div>
    </section>
    """


def subsection_head(number: str, title: str, intro: str = "", *, icon_name: str = "") -> str:
    icon_html = icon(icon_name) if icon_name else ""
    intro_html = f'<p class="subsection-lede">{esc(intro)}</p>' if intro else ""
    return f"""
      <header class="subsection-head">
        <p class="subsection-index">{esc(number)}</p>
        <div><h3>{icon_html}{esc(title)}</h3>{intro_html}</div>
      </header>
    """


def utc_offset_text(dt: datetime) -> str:
    offset = dt.utcoffset()
    if offset is None:
        return "UTC"
    total = int(offset.total_seconds() // 60)
    sign = "+" if total >= 0 else "−"
    total = abs(total)
    hours, minutes = divmod(total, 60)
    return f"UTC{sign}{hours}" + (f":{minutes:02d}" if minutes else "")


def render_flight_card(plan: Plan, flight: dict) -> str:
    dep = datetime.fromisoformat(flight["departure_at"])
    arr = datetime.fromisoformat(flight["arrival_at"])
    dep_zone = airport_zone(flight["departure_airport"])
    arr_zone = airport_zone(flight["arrival_airport"])
    dep_local = dep.astimezone(ZoneInfo(dep_zone))
    arr_local = arr.astimezone(ZoneInfo(arr_zone))
    other_dep = dep.astimezone(ZoneInfo(PL_TZ if dep_zone == CY_TZ else CY_TZ))
    other_arr = arr.astimezone(ZoneInfo(PL_TZ if arr_zone == CY_TZ else CY_TZ))
    other_dep_zone = PL_TZ if dep_zone == CY_TZ else CY_TZ
    other_arr_zone = PL_TZ if arr_zone == CY_TZ else CY_TZ
    return f"""
      <article class="flight-card">
        <header class="flight-card__head">
          <div>
            <p class="flight-route"><strong>{esc(flight["departure_airport"])}</strong> {icon("arrow")} <strong>{esc(flight["arrival_airport"])}</strong></p>
            <h4>{esc(flight["flight_no"])} <span>· {esc(flight["carrier"])}</span></h4>
          </div>
          {status_chip(flight.get("status"), compact=True)}
        </header>
        <table class="flight-times">
          <caption>Godziny lotu {esc(flight["flight_no"])} — czas lokalny lotnisk</caption>
          <thead><tr><th scope="col">Moment</th><th scope="col">Czas lotniska</th><th scope="col">Ten sam moment</th></tr></thead>
          <tbody>
            <tr>
              <th scope="row">Odlot · {esc(flight["departure_airport"])}</th>
              <td><time datetime="{esc(flight["departure_at"])}">{dep_local.strftime("%H:%M")}</time> <span class="zone-tag">{zone_label(dep_zone)} · {utc_offset_text(dep)}</span></td>
              <td><span class="secondary-time">{other_dep.strftime("%H:%M")} {zone_label(other_dep_zone)}</span></td>
            </tr>
            <tr>
              <th scope="row">Przylot · {esc(flight["arrival_airport"])}</th>
              <td><time datetime="{esc(flight["arrival_at"])}">{arr_local.strftime("%H:%M")}</time> <span class="zone-tag">{zone_label(arr_zone)} · {utc_offset_text(arr)}</span></td>
              <td><span class="secondary-time">{other_arr.strftime("%H:%M")} {zone_label(other_arr_zone)}</span></td>
            </tr>
          </tbody>
        </table>
        <p class="flight-card__date">{icon("calendar")} {esc(format_date_pl(flight["departure_at"][:10]))}</p>
        <p class="flight-card__recheck"><strong>Recheck:</strong> {esc(flight.get("recheck", ""))}</p>
        <div class="flight-card__sources">{source_chips(plan, flight.get("source_ids", []))}</div>
      </article>
    """


def render_flights(plan: Plan) -> str:
    cards = "".join(render_flight_card(plan, flight) for flight in plan.flights)
    baggage = plan.trip.get("baggage", {})
    bag_value = baggage.get("value") or {}
    transport = plan.trip.get("poland_transport", {})
    transport_note = transport.get("note") or "brak danych"
    transport_status = transport.get("status")
    return f"""
      <div id="loty" class="subsection">
        {subsection_head("06.1", "Loty", "Dwie osobne rezerwacje i dwa różne lotniska w Polsce. Godziny lotów są lokalne dla każdego lotniska.", icon_name="plane")}
        <div class="flight-grid">{cards}</div>
        <div class="lot-alerts">
          <div class="alert alert--urgent">
            {icon("alert")}
            <div><strong>Powrót: bag drop zamyka się o 05:20 czasu Cypru.</strong>
            <p>Przy odlocie 06:20 bagaż musi być już przyjęty. To nie jest cel obecności w kolejce.</p></div>
          </div>
          <div class="alert alert--warning">
            {icon("bag")}
            <div><strong>Bagaż według danych użytkownika</strong>
            <p>{bag_value.get("personal_items", "brak danych")} małe przedmioty osobiste i {bag_value.get("checked_bags", "brak danych")} bagaż {bag_value.get("checked_bag_kg", "brak danych")} kg. {esc(baggage.get("note", ""))}</p>
            <div>{status_chip(baggage.get("status"), compact=True)}</div></div>
          </div>
          <div class="alert alert--neutral">
            {icon("car")}
            <div><strong>Dojazd w Polsce: {esc(status_label(transport_status) if transport_status else "brak danych")}</strong>
            <p>{esc(transport_note)}</p>
            <div>{source_chips(plan, transport.get("source_ids", []))}</div></div>
          </div>
        </div>
        <p class="status-disclaimer">{icon("info")} „Zarezerwowane według użytkownika” nie znaczy „zweryfikowane”. Voucherów i rezerwacji nie sprawdzono w tym opracowaniu.</p>
      </div>
    """


def render_hotel(plan: Plan) -> str:
    hotel = plan.trip["hotel"]
    place = plan.places.get(hotel["place_id"], {})
    phone_raw = place.get("phone")
    phone = re.sub(r"[^\d+]", "", phone_raw or "")
    meal = hotel.get("meal_plan", {})
    wellness = hotel.get("wellness", {})
    breakfast = hotel.get("breakfast_hours", {})
    return f"""
      <div id="hotel" class="subsection">
        {subsection_head("06.2", "Hotel", "Jedna baza w Pafos. Publikowane godziny obiektu nie są potwierdzeniem warunków Twojej taryfy.", icon_name="bed")}
        <article class="hotel-card">
          <div class="hotel-card__intro">
            <div>
              <p class="place-type">Baza · Pafos</p>
              <h4>{esc(hotel["name"])}</h4>
              <p class="hotel-address">{icon("pin")} {esc(place.get("address") or "brak danych")}</p>
              <p class="hotel-phone">{icon("phone")} <a href="tel:{esc(phone)}">{esc(format_phone_display(phone_raw))}</a></p>
            </div>
            {status_chip(hotel.get("booking_status"), compact=True)}
          </div>
          <dl class="hotel-facts">
            <div><dt>Zameldowanie</dt><dd>{esc(format_date_pl(hotel["check_in_date"]))}, od {esc(hotel["published_check_in"])}</dd></div>
            <div><dt>Wymeldowanie</dt><dd>{esc(format_date_pl(hotel["check_out_date"]))}, do {esc(hotel["published_check_out"])}</dd></div>
            <div><dt>Śniadanie</dt><dd>{esc(breakfast.get("value") or "brak danych")} {status_chip(breakfast.get("status"), compact=True)}</dd></div>
            <div><dt>Wyżywienie</dt><dd>{esc(meal.get("value") or "brak danych")} {status_chip(meal.get("status"), compact=True)}</dd></div>
          </dl>
          <div class="hotel-warning">
            {icon("alert")}
            <div><strong>Wellness: do potwierdzenia.</strong>
            <p>{esc(wellness.get("value", ""))}</p>
            <p>{esc(wellness.get("note", ""))}</p></div>
          </div>
          <div class="hotel-night">
            <h4>{icon("clock")} Nocny wyjazd</h4>
            <p>{esc(hotel.get("night_departure", ""))}</p>
            <p><strong>Do potwierdzenia:</strong> wjazd na parking, dostęp do auta przed 03:00 i oddanie kluczy hotelowych. Voucher ma pierwszeństwo.</p>
          </div>
          <div class="hotel-card__foot">{source_chips(plan, hotel.get("source_ids", []))}</div>
        </article>
      </div>
    """


def render_car(plan: Plan) -> str:
    car = plan.trip["car"]
    reqs = "".join(f"<li>{esc(item)}</li>" for item in car.get("requirements", []))
    checks = "".join(f"<li>{esc(item)}</li>" for item in car.get("pickup_check", []))
    pickup = datetime.fromisoformat(car["pickup_target_at"])
    return_ = datetime.fromisoformat(car["return_target_at"])
    return f"""
      <div id="auto" class="subsection">
        {subsection_head("06.3", "Auto", "Warunek całego programu samochodowego — nie rezerwacja.", icon_name="car")}
        <div class="alert alert--urgent alert--large">
          {icon("alert")}
          <div><strong>Brak potwierdzonej rezerwacji auta.</strong>
          <p>Nie ma zatwierdzonej firmy, ceny, depozytu ani numeru assistance. Nie traktuj żadnej marki jako zarezerwowanej. Program obowiązuje dopiero po uzyskaniu pisemnej oferty i potwierdzeniu nocnego zwrotu na PFO.</p></div>
          {status_chip(car.get("booking_status"), compact=True)}
        </div>
        <dl class="car-facts">
          <div><dt>Odbiór — cel</dt><dd>7 XI 2026, {pickup.astimezone(ZoneInfo(CY_TZ)).strftime("%H:%M")} <span class="zone-tag">CY</span></dd></div>
          <div><dt>Zwrot — cel</dt><dd>13 XI 2026, {return_.astimezone(ZoneInfo(CY_TZ)).strftime("%H:%M")} <span class="zone-tag">CY</span></dd></div>
          <div><dt>Przewoźnik</dt><dd>{esc(car.get("provider") or "brak danych")}</dd></div>
          <div><dt>Cena łączna</dt><dd>{esc(format_money(car.get("total_price_eur")))}</dd></div>
          <div><dt>Depozyt</dt><dd>{esc(format_money(car.get("deposit_eur")))}</dd></div>
          <div><dt>Miejsce zwrotu</dt><dd>{esc(car.get("return_location") or "brak danych")}</dd></div>
          <div><dt>Assistance</dt><dd>{esc(car.get("assistance_phone") or "brak danych")}</dd></div>
        </dl>
        <div class="car-columns">
          <section>
            <h4>{icon("check")} Wymagania oferty</h4>
            <ul>{reqs}</ul>
          </section>
          <section>
            <h4>{icon("camera")} Przy odbiorze</h4>
            <ul>{checks}</ul>
            <p class="fine-print">Wymaganie: łączna blokada na karcie najwyżej 500 EUR. To nie jest potwierdzona kwota depozytu.</p>
          </section>
        </div>
        <div class="route-columns route-columns--single">
          <section class="route-notes">
            <h4>Jazda</h4>
            <p>{esc(car.get("use_rule", ""))}</p>
          </section>
          <section class="route-notes">
            <h4>Zwrot i odpowiedzialność</h4>
            <p>{esc(car.get("return_rule", ""))}</p>
          </section>
        </div>
        <details class="selection-note" open data-collapse-on-load>
          <summary>Notatka o wyborze firmy (bez rekomendacji rezerwacji) {icon("chevron")}</summary>
          <p>{esc(car.get("selection_note", ""))}</p>
        </details>
        <div class="source-line">{source_chips(plan, car.get("source_ids", []))}</div>
      </div>
    """


def render_transfer_table(plan: Plan, rows: list[dict], title: str, caption: str) -> str:
    body = []
    mode_labels = {"auto": "auto", "pieszo": "pieszo"}
    for transfer in rows:
        origin = plan.places.get(transfer["origin_id"], {})
        destination = plan.places.get(transfer["destination_id"], {})
        body.append(f"""
          <tr>
            <td data-label="Relacja"><span class="transfer-pair"><b>{esc(origin.get("name", transfer["origin_id"]))}</b>{icon("arrow")}<b>{esc(destination.get("name", transfer["destination_id"]))}</b></span></td>
            <td data-label="Tryb">{esc(mode_labels.get(transfer.get("mode"), transfer.get("mode", "")))}</td>
            <td data-label="Dystans">{esc(format_km(transfer.get("distance_km")))}</td>
            <td data-label="Czas">{esc(format_duration(transfer.get("duration_minutes")))}</td>
            <td data-label="Status">{status_chip(transfer.get("status"), compact=True)}</td>
            <td data-label="Uwagi">{esc(transfer.get("notes", ""))}</td>
          </tr>
        """)
    return f"""
      <section class="transfer-table-wrap" aria-labelledby="{esc(title)}-title">
        <h4 id="{esc(title)}-title">{esc(caption)}</h4>
        <div class="table-scroll">
          <table class="data-table transfer-table">
            <caption>{esc(caption)} — {len(rows)} {plural_pl(len(rows), "przejazd", "przejazdy", "przejazdów")}. Czasy i dystanse to szacunki planistyczne.</caption>
            <thead><tr><th scope="col">Relacja</th><th scope="col">Tryb</th><th scope="col">Dystans</th><th scope="col">Czas</th><th scope="col">Status</th><th scope="col">Uwagi</th></tr></thead>
            <tbody>{''.join(body)}</tbody>
          </table>
        </div>
      </section>
    """


def render_transfers(plan: Plan) -> str:
    auto = [t for t in plan.transfers if t.get("mode") == "auto"]
    walking = [t for t in plan.transfers if t.get("mode") == "pieszo"]
    from_hotel = [t for t in auto if t.get("origin_id") == "POI-HOTEL"]
    between = [t for t in auto if t.get("origin_id") != "POI-HOTEL"]
    return f"""
      <div id="przejazdy" class="subsection">
        {subsection_head("06.4", "Przejazdy", "21 relacji z audytu. To nie jest pomiar od drzwi do drzwi.", icon_name="trail")}
        <p class="method-note">{icon("info")} {esc(plan.transfer_method)}</p>
        {render_transfer_table(plan, from_hotel, "from-hotel", "Z hotelu")}
        {render_transfer_table(plan, between, "between-places", "Między punktami")}
        {render_transfer_table(plan, walking, "walking", "Pieszo")}
        <div class="source-line">{source_chips(plan, ["SRC-AUDIT"])}</div>
      </div>
    """


def render_costs(plan: Plan) -> str:
    costs = plan.costs
    rows = []
    for cost in costs.get("known_admissions", []):
        place = plan.places.get(cost["place_id"], {})
        rows.append(f"""
          <tr>
            <th scope="row">{esc(place.get("name", cost["place_id"]))}</th>
            <td data-label="Za osobę">{esc(format_money(cost["per_adult"]))}/os.</td>
            <td data-label="Za dwoje">{esc(format_money(cost["for_two"]))}</td>
            <td data-label="Źródło">{source_chips(plan, [cost["source_id"]], prefix="")}</td>
          </tr>
        """)
    unknown = [
        ("Auto", costs.get("car_total_eur")),
        ("Paliwo", costs.get("fuel_eur")),
        ("Hotel", costs.get("hotel_paid_eur")),
        ("Loty", costs.get("flights_paid_eur")),
        ("Jedzenie", costs.get("meals_budget_eur")),
    ]
    unknown_html = "".join(
        f'<div class="cost-unknown"><dt>{esc(label)}</dt><dd>{esc(format_money(value))}</dd></div>'
        for label, value in unknown
    )
    return f"""
      <div id="koszty" class="subsection">
        {subsection_head("06.5", "Koszty", "Tylko znane bilety. To nie budżet wyjazdu.", icon_name="ticket")}
        <div class="alert alert--warning">
          {icon("alert")}
          <div><strong>23 € to wyłącznie trzy bilety dla dwojga.</strong>
          <p>Park, Grobowce i Palaipafos według publikowanych cen. Bez transportu, paliwa, hotelu, lotów i jedzenia. „brak danych” nie znaczy „zero”.</p></div>
        </div>
        <div class="cost-highlight">
          <div><span>Trzy bilety / dwoje</span><strong>{esc(format_money(costs.get("base_admissions_for_two_eur")))}</strong></div>
          <div><span>Bez Palaipafos</span><strong>{esc(format_money(costs.get("if_palaipafos_omitted_eur")))}</strong></div>
          <div><span>Muzeum dystryktu</span><strong>{esc(format_money(costs.get("museum_eur")))}</strong></div>
        </div>
        <div class="table-scroll">
          <table class="data-table cost-table">
            <caption>Znane bilety wstępu — ceny publikowane, bez zniżek</caption>
            <thead><tr><th scope="col">Miejsce</th><th scope="col">Za osobę</th><th scope="col">Za dwoje</th><th scope="col">Źródło</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
        <dl class="cost-unknown-grid">{unknown_html}</dl>
        <p class="fine-print">{esc(costs.get("note", ""))}</p>
        {status_chip("czesciowy_kosztorys", compact=True)}
      </div>
    """


def render_dining(plan: Plan) -> str:
    cards = []
    for item in plan.dining:
        url = safe_url(item.get("url"))
        link = f'<a class="text-link" href="{esc(url)}">Strona lokalu {icon("arrow")}</a>' if url else '<span class="muted">brak linku w danych</span>'
        cards.append(f"""
          <article class="dining-card">
            <header><div><p class="dining-when">{esc(item.get("when", ""))}</p><h4>{esc(item["name"])}</h4></div>{status_chip(item.get("status"), compact=True)}</header>
            <p>{esc(item.get("note", ""))}</p>
            <dl class="dining-facts">
              <div><dt>Godziny</dt><dd>{esc(item.get("published_hours") or "brak danych")}</dd></div>
              <div><dt>Link</dt><dd>{link}</dd></div>
            </dl>
          </article>
        """)
    return f"""
      <div id="jedzenie" class="subsection">
        {subsection_head("06.6", "Jedzenie", "Restauracje są opcjami, nie rezerwacjami. Prowiant pozostaje planem awaryjnym.", icon_name="food")}
        <div class="dining-grid">{''.join(cards)}</div>
      </div>
    """


def source_link(plan: Plan, source_id: str, label: str | None = None) -> str:
    source = plan.sources.get(source_id)
    if not source:
        return ""
    url = safe_url(source.get("url"))
    text = label or source.get("title", source_id)
    if url:
        return f'<a class="official-link" href="{esc(url)}">{icon("source")}{esc(text)}</a>'
    return f'<span class="official-link official-link--offline">{icon("source")}{esc(text)} <small>(załącznik)</small></span>'


def render_safety(plan: Plan) -> str:
    safety = plan.safety
    emergency = safety.get("emergency", {})
    no_go = "".join(f"<li>{esc(item)}</li>" for item in safety.get("no_go", []))
    route_gate = "".join(f"<li>{esc(item)}</li>" for item in safety.get("route_gate", []))
    swaps = "".join(f"<li>{esc(item)}</li>" for item in safety.get("swaps", []))
    return f"""
      <div id="bezpieczenstwo" class="subsection">
        {subsection_head("06.7", "Bezpieczeństwo", "Trzy zasady widoczne od razu. Reszta to brama decyzyjna, a nie formalność.", icon_name="shield")}
        <div class="safety-rules">
          <article class="safety-rule safety-rule--alert">
            <span class="safety-rule__number">01</span>
            <h4>8 i 11 XI — bez trekkingu</h4>
            <p>To dni głównego sezonu polowań. Zostajemy w mieście i w programie kulturowym. Inne dni też nie są automatycznie wolne od polowań.</p>
          </article>
          <article class="safety-rule">
            <span class="safety-rule__number">02</span>
            <h4>Koniec 14:30–15:00</h4>
            <p>Górna rezerwa 15:30 nie jest celem ani zgodą na przedłużenie. W górach światło kończy się wcześniej. Czołówka jest zapasem, nie planem.</p>
          </article>
          <article class="safety-rule">
            <span class="safety-rule__number">03</span>
            <h4>Woda, jedzenie, 112</h4>
            <p>Każda osoba ma wodę i jedzenie na całą trasę, nawet gdy lunch jest w restauracji. Około 2 l wody na osobę to założenie wyjściowe.</p>
            <a class="inline-emergency" href="tel:112">{icon("phone")} 112</a>
          </article>
        </div>
        <div class="emergency-panel">
          <div class="emergency-panel__number"><span>Numer alarmowy</span><strong>112</strong></div>
          <div>
            <p>{esc(emergency.get("procedure", ""))}</p>
            <p class="fine-print">Numer hotelu: <a href="tel:+35726600100">+357 26 600 100</a> · assistance auta: {esc(emergency.get("car_assistance_phone") or "brak danych")} · assistance polisy: {esc(emergency.get("insurance_assistance_phone") or "brak danych")}</p>
            {source_chips(plan, [emergency.get("source_id")] if emergency.get("source_id") else [])}
          </div>
        </div>
        <p class="confidence-note">{icon("alert")} Żadna prognoza ani link nie jest zgodą na wejście na szlak. Decyzja należy do osób na miejscu.</p>

        <details class="safety-details" open>
          <summary>{icon("shield")} Brama decyzyjna przed trasą {icon("chevron")}</summary>
          <ol class="decision-gate">{route_gate}</ol>
        </details>
        <details class="safety-details" open>
          <summary>{icon("alert")} Pogoda i zamknięcia — tylko oficjalne linki {icon("chevron")}</summary>
          <p>{esc(safety.get("weather_checks", ""))}</p>
          <div class="official-links">
            {source_link(plan, "SRC-WEATHER", "Pogoda i ostrzeżenia")}
            {source_link(plan, "SRC-FORESTS", "Komunikaty leśników")}
            {source_link(plan, "SRC-HUNT-MAP", "Mapy i dekrety polowań")}
            {source_link(plan, "SRC-ROAD", "Roboty drogowe")}
            {source_link(plan, "SRC-HUNT", "Komunikat o sezonie polowań")}
          </div>
          <p class="fine-print">W tym planie nie ma automatycznej prognozy. Linki wymagają internetu; najważniejsze kontakty i plan działają offline.</p>
        </details>
        <details class="safety-details" open>
          <summary>{icon("alert")} NO-GO i światło {icon("chevron")}</summary>
          <ul class="no-go-list">{no_go}</ul>
          <p>{esc(safety.get("daylight_rule", ""))}</p>
        </details>
        <details class="safety-details" open>
          <summary>{icon("trail")} Zamiany, jedzenie i nawigacja {icon("chevron")}</summary>
          <h4>Zamiany</h4>
          <ul>{swaps}</ul>
          <h4>Woda i jedzenie</h4>
          <p>{esc(safety.get("food_water", ""))}</p>
          <h4>Nawigacja</h4>
          <p>{esc(safety.get("navigation", ""))}</p>
        </details>
      </div>
    """


def render_sunsets(plan: Plan) -> str:
    rows = []
    for item in plan.sunsets:
        rows.append(f"""
          <tr>
            <th scope="row"><time datetime="{esc(item["date"])}">{esc(format_date_pl(item["date"]))}</time></th>
            <td data-label="Zachód"><time datetime="{esc(item["date"])}T{esc(item["sunset_local"])}">{esc(item["sunset_local"])}</time></td>
            <td data-label="Koniec zmierzchu cywilnego">{esc(item["civil_twilight_end_local"])}</td>
            <td data-label="Status">{status_chip(item.get("status"), compact=True)}</td>
            <td data-label="Źródło">{source_chips(plan, item.get("source_ids", []), prefix="")}</td>
          </tr>
        """)
    return f"""
      <div id="zachody" class="subsection">
        {subsection_head("06.8", "Zachody słońca", "Pafos, astronomiczny horyzont. W górach użyteczne światło kończy się wcześniej.", icon_name="sun")}
        <div class="table-scroll">
          <table class="data-table sunset-table">
            <caption>Zachód i koniec zmierzchu cywilnego w Pafos</caption>
            <thead><tr><th scope="col">Data</th><th scope="col">Zachód</th><th scope="col">Koniec zmierzchu cywilnego</th><th scope="col">Status</th><th scope="col">Źródło</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
        <p class="fine-print">{esc(plan.sunset_note)}</p>
      </div>
    """


def render_packing(plan: Plan) -> str:
    icons = {"hike": "foot", "documents": "source", "photography": "camera"}
    labels = {"hike": "Trekking", "documents": "Dokumenty", "photography": "Fotografia"}
    cards = []
    for key in ["hike", "documents", "photography"]:
        items = "".join(f"<li>{esc(item)}</li>" for item in plan.packing.get(key, []))
        cards.append(f"""
          <article class="packing-card">
            <h4>{icon(icons[key])} {esc(labels[key])}</h4>
            <ul>{items}</ul>
          </article>
        """)
    return f"""
      <div id="pakowanie" class="subsection">
        {subsection_head("06.9", "Pakowanie", "Trzy zestawy, które warto przygotować osobno. Checklisty poniżej zapisują stan lokalnie.", icon_name="bag")}
        <div class="packing-grid">{''.join(cards)}</div>
        <details class="offline-note" open data-collapse-on-load>
          <summary>{icon("wifi")} Offline, mapa i ekran główny {icon("chevron")}</summary>
          <p>Po pierwszym wejściu service worker zapisuje powłokę strony, CSS, JavaScript, JSON, fonty i ikony. Kafelki OpenStreetMap nie są cache’owane. Mapa offline wymaga osobnej aplikacji.</p>
          <p>Do nawigacji offline użyj <strong>Organic Maps</strong> lub <strong>Guru Maps</strong> i wcześniej pobierz obszar zachodniego Cypru i Troodos. Strona ma manifest PWA — możesz dodać ją do ekranu głównego z menu przeglądarki.</p>
          <p>Ustawienia checklist są lokalne (<code>localStorage</code>) i nie zmieniają faktów w planie. Po wyczyszczeniu danych przeglądarki znikną.</p>
        </details>
      </div>
    """


def render_practice(plan: Plan) -> str:
    return f"""
    <section class="section section--practice" id="praktyka" aria-labelledby="praktyka-title">
      <div class="page-width">
        <header class="section-head">
          <p class="section-index"><span>06</span> / PRAKTYKA</p>
          <div class="section-head__body">
            <h2 id="praktyka-title">Praktyka</h2>
            <p class="section-lede">Loty, hotel, auto, przejazdy, koszty, jedzenie, bezpieczeństwo, światło i pakowanie. Fakty mają swoje statusy; brak danych nie jest zerem.</p>
          </div>
        </header>
        {render_flights(plan)}
        {render_hotel(plan)}
        {render_car(plan)}
        {render_transfers(plan)}
        {render_costs(plan)}
        {render_dining(plan)}
        {render_safety(plan)}
        {render_sunsets(plan)}
        {render_packing(plan)}
      </div>
    </section>
    """


def render_checklists(plan: Plan) -> str:
    groups = []
    for group in plan.checklists:
        items = []
        for index, text in enumerate(group["items"]):
            check_id = f'{group["id"]}-{index}'
            items.append(f"""
              <label class="check-item" for="chk-{esc(check_id.lower())}">
                <input type="checkbox" id="chk-{esc(check_id.lower())}" data-check-id="{esc(check_id)}">
                <span class="check-item__box" aria-hidden="true"></span>
                <span class="check-item__text">{esc(text)}</span>
              </label>
            """)
        groups.append(f"""
          <article class="checklist-card" data-checklist-group="{esc(group["id"])}">
            <header class="checklist-card__head">
              <div><p class="checklist-id">{esc(group["id"])}</p><h3>{esc(group["title"])}</h3></div>
              <span class="checklist-count" data-group-count="{esc(group["id"])}">0 / {len(group["items"])}</span>
            </header>
            <progress class="check-progress" max="{len(group["items"])}" value="0" aria-label="Postęp: {esc(group["title"])}" data-group-progress="{esc(group["id"])}">0 / {len(group["items"])}</progress>
            <div class="check-items">{''.join(items)}</div>
          </article>
        """)
    return f"""
    <section class="section section--checklists" id="checklisty" aria-labelledby="checklisty-title">
      <div class="page-width">
        <header class="section-head">
          <p class="section-index"><span>07</span> / PRZYGOTOWANIE</p>
          <div class="section-head__body">
            <h2 id="checklisty-title">Checklisty</h2>
            <p class="section-lede">Siedem grup roboczych. Zaznaczenia zapisują się tylko w tej przeglądarce. Druk zostawia puste pola do użycia na papierze.</p>
          </div>
        </header>
        <div class="checklist-toolbar">
          <div class="global-progress">
            <span>Całość</span>
            <progress max="{plan.total_check_items}" value="0" aria-label="Postęp wszystkich checklist" data-global-progress>0 / {plan.total_check_items}</progress>
            <strong data-global-count>0 / {plan.total_check_items}</strong>
          </div>
          <button type="button" class="button button--ghost button--small" data-reset-checklist>Reset checklisty</button>
        </div>
        <p class="local-note">{icon("info")} Stan checklisty jest lokalny i nie zmienia faktów w planie. Klucz zapisu: <code>cypr2026.checklist.v1</code>.</p>
        <div class="checklist-grid">{''.join(groups)}</div>
      </div>
    </section>
    """


def sorted_issues(plan: Plan) -> list[dict]:
    return sorted(
        plan.open_issues,
        key=lambda item: (
            0 if item.get("blocking") else 1,
            item.get("due_on") or "9999-99-99",
            PRIORITY_ORDER.get(item.get("priority"), 9),
            item.get("id", ""),
        ),
    )


def todo_summary(plan: Plan) -> str:
    due_counts = Counter(issue["due_on"] for issue in plan.blocking_issues)
    parts = []
    for index, due in enumerate(sorted(due_counts)):
        count = due_counts[due]
        if index == 0:
            parts.append(f'{count} {plural_pl(count, "blokujące", "blokujące", "blokujących")} do {due_short(due)}')
        else:
            parts.append(f'{count} do {due_short(due)}')
    return ", ".join(parts)


def render_todo(plan: Plan) -> str:
    issues = sorted_issues(plan)
    cards = []
    for issue in issues:
        blocking = '<span class="blocking-badge">blokujące</span>' if issue.get("blocking") else ""
        priority = issue.get("priority", "")
        cards.append(f"""
          <article class="issue-card{' issue-card--blocking' if issue.get("blocking") else ''}" id="issue-{esc(issue["id"])}">
            <header class="issue-card__head">
              <div>
                <p class="issue-id">{esc(issue["id"])}</p>
                <h3>{esc(issue["title"])}</h3>
              </div>
              {blocking}
            </header>
            <div class="issue-tags">
              <span class="priority priority--{esc(priority)}">{esc(PRIORITY_LABELS.get(priority, priority))} priorytet</span>
              <span class="issue-due">{icon("calendar")}termin: <time datetime="{esc(issue["due_on"])}">{esc(format_date_pl(issue["due_on"]))}</time></span>
              {status_chip(issue.get("status"), compact=True)}
            </div>
            <div class="issue-body">
              <p><strong>Działanie:</strong> {esc(issue.get("action", ""))}</p>
              <p><strong>Wpływ:</strong> {esc(issue.get("impact", ""))}</p>
            </div>
            <footer class="issue-card__foot"><span>Odpowiedzialność: {esc(issue.get("owner", ""))}</span><span>bez lokalnego „done”</span></footer>
          </article>
        """)
    return f"""
    <section class="section section--todo" id="todo" aria-labelledby="todo-title">
      <div class="page-width">
        <header class="section-head">
          <p class="section-index"><span>08</span> / OPERACJE</p>
          <div class="section-head__body">
            <h2 id="todo-title">Sprawy do potwierdzenia</h2>
            <p class="section-lede">{esc(todo_summary(plan))}. To lista operacyjna, nie checklista. Zmiana stanu w planie wymaga zmiany JSON-a i ponownego builda.</p>
          </div>
        </header>
        <div class="issue-grid">{''.join(cards)}</div>
      </div>
    </section>
    """


def render_status_legend(plan: Plan) -> str:
    legend_cards = []
    legend_ids = [entry.get("id") for entry in plan.status_legend]
    for entry in plan.status_legend:
        legend_cards.append(f"""
          <div class="legend-card">
            {status_chip(entry.get("id"), compact=True)}
            <p>{esc(entry.get("meaning", ""))}</p>
          </div>
        """)
    extra_codes = [
        "planowane", "otwarte", "do_przygotowania_i_weryfikacji",
        "orientacyjne_do_potwierdzenia", "do_sprawdzenia_przed_wyjsciem",
        "nie_dotyczy", "zalacznik_uzytkownika", "sprawdzone_2026_11_02",
        "link_kontrolny_z_audytu",
    ]
    extra = "".join(
        f'<li>{status_chip(code, compact=True)} <span>{esc(STATUS_MEANINGS.get(code, ""))}</span></li>'
        for code in extra_codes if code not in legend_ids
    )
    return f"""
      <div class="status-legend-block">
        <h3>Statusy</h3>
        <p class="section-lede">Kolor nigdy nie jest jedynym nośnikiem znaczenia. Każdy status ma tekst, a w treści także podpowiedź.</p>
        <div class="legend-grid">{''.join(legend_cards)}</div>
        <details class="legend-more" open data-collapse-on-load>
          <summary>Pozostałe oznaczenia {icon("chevron")}</summary>
          <ul>{extra}</ul>
        </details>
      </div>
    """


def render_sources(plan: Plan) -> str:
    rows = []
    for source in plan.raw["sources"]:
        url = safe_url(source.get("url"))
        if url:
            link = f'<a class="source-open" href="{esc(url)}">Otwórz źródło {icon("arrow")}</a><span class="print-url">{esc(url)}</span>'
        else:
            filename = source.get("filename") or "brak nazwy pliku"
            link = f'<span class="attachment">Załącznik użytkownika</span><span class="print-url">{esc(filename)}</span>'
        checked = format_date_pl(source["checked_on"]) if source.get("checked_on") else "brak daty kontroli"
        checked_html = (
            f'<time datetime="{esc(source["checked_on"])}">{esc(checked)}</time>'
            if source.get("checked_on") else f'<span class="muted">{esc(checked)}</span>'
        )
        rows.append(f"""
          <tr id="src-{esc(source["id"])}">
            <th scope="row"><a class="source-id-link" href="#src-{esc(source["id"])}">{esc(source["id"])}</a></th>
            <td data-label="Tytuł"><strong>{esc(source["title"])}</strong></td>
            <td data-label="Zakres">{esc(source.get("scope", ""))}</td>
            <td data-label="Weryfikacja">{status_chip(source.get("verification_status"), compact=True)}</td>
            <td data-label="Data kontroli">{checked_html}</td>
            <td data-label="Link / załącznik">{link}</td>
          </tr>
        """)
    revisions = "".join(
        f'<li><article><p class="change-id">{esc(item["id"])}</p><p><b>{esc(item["from"])}</b> <span aria-hidden="true">→</span> {esc(item["to"])}</p><p>{esc(item["reason"])}</p></article></li>'
        for item in plan.revision_log
    )
    decisions = "".join(
        f'<li><p class="decision-id">{esc(item["id"])}</p><p><b>{esc(item["decision"])}</b></p><p>{esc(item["reason"])}</p></li>'
        for item in plan.decisions
    )
    return f"""
    <section class="section section--sources" id="zrodla" aria-labelledby="zrodla-title">
      <div class="page-width">
        <header class="section-head">
          <p class="section-index"><span>09</span> / ŹRÓDŁA</p>
          <div class="section-head__body">
            <h2 id="zrodla-title">Źródła i wersja</h2>
            <p class="section-lede">24 źródła, statusy weryfikacji i dziennik zmian. JSON jest dokumentem nadrzędnym; ta strona jest jego widokiem.</p>
          </div>
        </header>
        {render_status_legend(plan)}
        <div class="table-scroll source-table-wrap">
          <table class="data-table source-table">
            <caption>Źródła planu Cypr 2026 — {len(plan.sources)} pozycji</caption>
            <thead><tr><th scope="col">ID</th><th scope="col">Tytuł</th><th scope="col">Zakres</th><th scope="col">Weryfikacja</th><th scope="col">Data kontroli</th><th scope="col">Link / załącznik</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
        <div class="source-details">
          <details class="change-log" open data-collapse-on-load>
            <summary>{icon("source")} Dziennik zmian — {len(plan.revision_log)} wpisów {icon("chevron")}</summary>
            <ol class="change-list">{revisions}</ol>
          </details>
          <details class="change-log" open data-collapse-on-load>
            <summary>{icon("check")} Decyzje planu — {len(plan.decisions)} {icon("chevron")}</summary>
            <ol class="decision-list">{decisions}</ol>
          </details>
        </div>
        {render_print_source_urls(plan)}
      </div>
    </section>
    """


def render_print_source_urls(plan: Plan) -> str:
    items = []
    for source in plan.raw["sources"]:
        url = safe_url(source.get("url"))
        if url:
            items.append(
                f'<li><b>{esc(source["id"])}</b> <span>{esc(url)}</span></li>'
            )
    return f"""
        <section class="print-source-urls" aria-label="Adresy źródeł do wydruku">
          <h3>Kluczowe adresy źródeł</h3>
          <ul>{''.join(items)}</ul>
        </section>
    """


def render_print_cover(plan: Plan) -> str:
    return f"""
    <section class="print-cover" aria-label="Okładka wydruku">
      <p class="print-cover__kicker">PLAN PODRÓŻY · WYDANIE {esc(plan.meta["version"])}</p>
      <h1>Cypr 2026</h1>
      <p class="print-cover__subtitle">bez pośpiechu</p>
      <div class="print-cover__rule"></div>
      <dl class="print-cover__facts">
        <div><dt>Termin</dt><dd>7–13 listopada 2026</dd></div>
        <div><dt>Ludzie</dt><dd>2 osoby</dd></div>
        <div><dt>Noclegi</dt><dd>6 nocy · Pafos</dd></div>
        <div><dt>Wersja</dt><dd>{esc(plan.meta["version"])}</dd></div>
        <div><dt>Aktualizacja</dt><dd>{esc(format_date_pl(plan.meta["updated_on"]))}</dd></div>
        <div><dt>Strefa</dt><dd>Cypr: Asia/Nicosia UTC+2 · Polska UTC+1</dd></div>
        <div><dt>Alarmowy</dt><dd>112</dd></div>
      </dl>
      <p class="print-cover__note">Wydruk widoku JSON-a. Statusy „do potwierdzenia” i „szacunek” pozostają widoczne. Auto nie jest zarezerwowane. Avakas jest poza planem.</p>
      <p class="print-cover__source">https://kjawo.github.io/cypr2026/ · data/Cypr_2026_zrodlo_prawdy.json</p>
    </section>
    """


def render_footer(plan: Plan) -> str:
    return f"""
    <div class="page-width footer-grid">
      <div>
        <p class="footer-mark">KJ <span>/</span> Photo Journal</p>
        <p class="footer-note">Spokojny plan podróży. Bez analityki, cookies i trackerów. Źródłem prawdy jest plik JSON; strona jest generowanym widokiem.</p>
        <p class="footer-back"><a href="#top">Do początku {icon("arrow")}</a> · <a href="#zrodla">Źródła</a></p>
      </div>
      <div class="footer-meta">
        <p><span>Wersja</span> <strong>{esc(plan.meta["version"])}</strong></p>
        <p><span>Aktualizacja</span> <strong>{esc(format_date_pl(plan.meta["updated_on"]))}</strong></p>
        <p><span>Dane</span> <a href="data/Cypr_2026_zrodlo_prawdy.json">Cypr_2026_zrodlo_prawdy.json {icon("download")}</a></p>
        <p><span>Strefa</span> Asia/Nicosia, UTC+2</p>
        <p class="footer-version">Plan bazowy · 7 dni / 6 nocy · Pafos</p>
      </div>
    </div>
    """


def compute_asset_hash(raw_json: bytes, *, noindex: bool) -> str:
    digest = hashlib.sha256()
    digest.update(b"cypr2026-asset-hash-v1\0")
    digest.update(b"noindex=1\0" if noindex else b"noindex=0\0")
    digest.update(raw_json)
    paths = [TEMPLATE_FILE, Path(__file__).resolve(), STYLES_FILE, APP_FILE, MANIFEST_FILE]
    for path in paths:
        if path.exists():
            digest.update(path.name.encode("utf-8") + b"\0")
            digest.update(path.read_bytes())
    if ASSETS_DIR.exists():
        for path in sorted(p for p in ASSETS_DIR.rglob("*") if p.is_file()):
            digest.update(path.relative_to(ROOT).as_posix().encode("utf-8") + b"\0")
            digest.update(path.read_bytes())
    return digest.hexdigest()[:10]


def write_if_changed(path: Path, content: str) -> None:
    encoded = content.encode("utf-8")
    if path.exists() and path.read_bytes() == encoded:
        return
    path.write_bytes(encoded)


def render_page(plan: Plan, asset_hash: str, data_json: str, *, noindex: bool) -> str:
    if not TEMPLATE_FILE.exists():
        fail("Brak _src/template.html")
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    replacements = {
        "{{NOINDEX}}": '<meta name="robots" content="noindex, nofollow">' if noindex else "",
        "{{VERSION}}": esc(plan.meta["version"]),
        "{{HASH}}": esc(asset_hash),
        "{{HERO}}": render_hero(plan),
        "{{NAV}}": render_nav(plan),
        "{{PRINT_COVER}}": render_print_cover(plan),
        "{{WEEK}}": render_week(plan),
        "{{TODAY}}": render_today(plan),
        "{{DAYS}}": render_days(plan),
        "{{ROUTES}}": render_routes(plan),
        "{{MAP}}": render_map(plan),
        "{{PRACTICE}}": render_practice(plan),
        "{{CHECKLISTS}}": render_checklists(plan),
        "{{TODO}}": render_todo(plan),
        "{{SOURCES}}": render_sources(plan),
        "{{FOOTER}}": render_footer(plan),
        "{{DATA_JSON}}": data_json,
    }
    output = template
    for token, value in replacements.items():
        output = output.replace(token, value)
    if re.search(r"\{\{[A-Z_]+\}\}", output):
        fail("Szablon zawiera niewypełniony placeholder")
    return output


def build_service_worker(plan: Plan, asset_hash: str) -> str:
    sw = SW_FILE.read_text(encoding="utf-8")
    version = plan.meta["version"]
    cache_name = f"cypr-2026-{version}-{asset_hash}"
    precache = [
        "./",
        f"./index.html",
        f"./styles.css?v={asset_hash}",
        f"./app.js?v={asset_hash}",
        f"./manifest.json?v={asset_hash}",
        "./data/Cypr_2026_zrodlo_prawdy.json",
    ]
    if ASSETS_DIR.exists():
        for path in sorted(p for p in ASSETS_DIR.rglob("*") if p.is_file()):
            rel = path.relative_to(ROOT).as_posix()
            if rel.endswith(".png") or rel.endswith(".svg") or rel.endswith(".woff2") or rel.endswith(".js") or rel.endswith(".css"):
                precache.append(f"./{rel}")
    # Keep the list stable and free of duplicates.
    seen = set()
    final = []
    for url in precache:
        if url not in seen:
            seen.add(url)
            final.append(url)
    cache_line = f'const CACHE_VERSION = "{cache_name}";'
    precache_js = "const PRECACHE_URLS = [\n" + "".join(f'  {json.dumps(url)},\n' for url in final) + "];"
    sw = re.sub(r'const CACHE_VERSION = "[^"]*";', cache_line, sw, count=1)
    sw = re.sub(r"const PRECACHE_URLS = \[.*?\];", precache_js, sw, flags=re.S, count=1)
    if cache_name not in sw or "PRECACHE_URLS" not in sw:
        fail("Nie udało się wstrzyknąć wersji cache do sw.js")
    return sw


def main() -> int:
    parser = argparse.ArgumentParser(description="Zbuduj statyczną stronę Cypr 2026 z JSON-a.")
    parser.add_argument("--noindex", action="store_true", help="Dodaj meta robots noindex, nofollow.")
    args = parser.parse_args()

    try:
        try:
            raw_bytes = DATA_FILE.read_bytes()
        except FileNotFoundError:
            fail(f"Brak pliku źródłowego: {DATA_FILE.relative_to(ROOT)}. Wstaw JSON 1:1 i uruchom build ponownie.")
        except OSError as exc:
            fail(f"Nie można odczytać JSON-a: {exc}")
        try:
            data = json.loads(raw_bytes.decode("utf-8"))
        except UnicodeDecodeError as exc:
            fail(f"JSON nie jest poprawny (UTF-8): {exc}")
        except json.JSONDecodeError as exc:
            fail(f"JSON nie jest poprawny: {exc}")
        plan = Plan(data)
        validate(plan)
        warnings = collect_warnings(plan)

        for path in [TEMPLATE_FILE, STYLES_FILE, APP_FILE, MANIFEST_FILE, SW_FILE]:
            if not path.exists():
                fail(f"Brak pliku wymaganego do builda: {path.relative_to(ROOT)}")

        asset_hash = compute_asset_hash(raw_bytes, noindex=args.noindex)
        version = str(plan.meta["version"])
        data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        rendered = render_page(plan, asset_hash, data_json, noindex=args.noindex)
        write_if_changed(INDEX_FILE, rendered)
        sw_text = build_service_worker(plan, asset_hash)
        write_if_changed(SW_FILE, sw_text)

        print(f"OK  Cypr 2026 {version} · {asset_hash}")
        print(f"    index.html: {INDEX_FILE.stat().st_size:,} B")
        print(f"    dni: {len(plan.day_list)} · miejsca: {plan.total_places} "
              f"(współrzędne: {plan.coord_count}) · źródła: {len(plan.sources)}")
        print(f"    blokujące zadania: {len(plan.blocking_issues)} · checklisty: {plan.total_check_items} pozycji")
        if warnings:
            print("\nOstrzeżenia danych (nie blokują builda):")
            for item in warnings:
                print(f"  ! {item}")
        return 0
    except BuildError as exc:
        print(f"BŁĄD BUILD: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
