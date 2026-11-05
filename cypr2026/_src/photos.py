"""Photo manifest loading, validation and rendering for Cypr 2026.

The manifest is data/photos.json.  Every rendered photo must have a complete
provenance record: source page, real date, place proof and local files.  A
missing field stops the build rather than shipping an uncredited image.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

KINDS = {"hero", "strip", "day", "place", "route"}
ROLES = {"hero", "strip", "lead", "extra"}
REQUIRED = {
    "id", "slot", "kind", "role", "order", "lead", "target", "title",
    "location", "gps", "author", "source_url", "original_url", "date",
    "description", "caption", "alt", "credit", "verification",
    "focal_point", "aspect", "files", "source_width", "source_height",
    "width", "height",
}
WIDTHS = {480, 800, 1280, 1920}
FORMATS = {"avif", "webp", "jpeg"}
ASPECTS = {"4:5": 4 / 5, "3:2": 3 / 2, "4:3": 4 / 3, "16:9": 16 / 9}
MAX_BYTES = {
    ("hero", 480): 45 * 1024,
    ("hero", 800): 130 * 1024,
    ("hero", 1280): 180 * 1024,
    ("day", 480): 45 * 1024,
    ("place", 480): 45 * 1024,
    ("route", 480): 45 * 1024,
    ("strip", 480): 45 * 1024,
    ("day", 800): 70 * 1024,
    ("place", 800): 70 * 1024,
    ("route", 800): 70 * 1024,
    ("strip", 800): 70 * 1024,
    ("day", 1280): 120 * 1024,
    ("place", 1280): 120 * 1024,
    ("route", 1280): 120 * 1024,
    ("strip", 1280): 120 * 1024,
    ("day", 1920): 180 * 1024,
    ("place", 1920): 180 * 1024,
    ("route", 1920): 180 * 1024,
    ("strip", 1920): 180 * 1024,
}
THUMB_FORMATS = {"avif", "webp", "jpeg"}
MONTHS_PL = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
             "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]


class PhotoError(Exception):
    pass


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _photo_plural(count: int) -> str:
    if count == 1:
        return "kadr"
    if count % 10 >= 2 and count % 10 <= 4 and (count % 100 < 12 or count % 100 > 14):
        return "kadry"
    return "kadrów"


def _date_pl(value: str) -> str:
    try:
        year, month, day = value[:10].split("-")
        return f"{int(day)} {MONTHS_PL[int(month) - 1]} {year}"
    except (ValueError, IndexError):
        return value


def _fail(message: str) -> None:
    raise PhotoError(message)


def _section_next(label: str, links: list[tuple[str, str]]) -> str:
    anchors = "".join(f'<a href="{_esc(href)}">{_esc(text)}</a>' for href, text in links)
    return f'<nav class="section-next" aria-label="{_esc(label)}"><span>{_esc(label)}</span>{anchors}</nav>'


class Photo:
    def __init__(self, data: dict, index: int):
        self.data = data
        self.index = index
        for key in REQUIRED:
            if key not in data:
                _fail(f"photos[{index}]: brak pola {key!r} (slot {data.get('slot', '?')})")
        self.id = str(data["id"])
        self.slot = str(data["slot"])
        self.kind = str(data["kind"])
        self.role = str(data["role"])
        self.order = int(data["order"])
        self.lead = bool(data["lead"])
        self.target = data["target"]
        self.title = str(data["title"]).strip()
        self.location = data["location"]
        self.gps = data["gps"]
        self.author = str(data["author"]).strip()
        self.license = str(data.get("license") or "").strip()
        self.license_url = str(data.get("license_url") or "").strip()
        self.source_url = str(data["source_url"]).strip()
        self.original_url = str(data["original_url"]).strip()
        self.date = str(data["date"]).strip()
        self.description = str(data["description"]).strip()
        self.caption = str(data["caption"]).strip()
        self.alt = str(data["alt"]).strip()
        self.credit = str(data["credit"]).strip()
        self.verification = data["verification"]
        self.focal = data["focal_point"]
        self.aspect = str(data["aspect"])
        self.files = sorted(data["files"], key=lambda item: int(item["width"]))
        self.source_width = int(data["source_width"])
        self.source_height = int(data["source_height"])
        self.width = int(data["width"])
        self.height = int(data["height"])
        self.offline = data.get("offline")
        self.category_url = data.get("category_url", "")
        self.source_title = data.get("source_title", "")
        self.credit_short = data.get("credit_short", self.credit)

    def validate(self) -> None:
        if self.kind not in KINDS:
            _fail(f"photos[{self.index}] {self.slot}: nieznany kind {self.kind!r}")
        if self.role not in ROLES:
            _fail(f"photos[{self.index}] {self.slot}: nieznana rola {self.role!r}")
        if self.target.get("type") != self.kind:
            _fail(f"photos[{self.index}] {self.slot}: target.type musi być {self.kind!r}")
        if not self.target.get("id") or not self.target.get("label"):
            _fail(f"photos[{self.index}] {self.slot}: target bez id/label")
        if self.order < 1:
            _fail(f"photos[{self.index}] {self.slot}: order musi być >= 1")
        if self.lead != (self.role in {"lead", "hero"}):
            _fail(f"photos[{self.index}] {self.slot}: lead musi odpowiadać roli lead/hero")
        if self.lead and self.order != 1:
            _fail(f"photos[{self.index}] {self.slot}: lead musi mieć order 1")
        if not self.author:
            _fail(f"photos[{self.index}] {self.slot}: pusty autor")
        if self.license_url and not self.license_url.startswith("https://creativecommons.org/"):
            _fail(f"photos[{self.index}] {self.slot}: niepoprawny license_url")
        if not self.source_url.startswith("https://commons.wikimedia.org/wiki/File:"):
            _fail(f"photos[{self.index}] {self.slot}: source_url musi wskazywać stronę pliku Commons")
        if not self.original_url.startswith("https://upload.wikimedia.org/"):
            _fail(f"photos[{self.index}] {self.slot}: original_url musi wskazywać Wikimedia")
        if not re.fullmatch(r"20\d\d-\d\d-\d\d", self.date):
            _fail(f"photos[{self.index}] {self.slot}: data musi być w formacie ISO")
        if not self.description:
            _fail(f"photos[{self.index}] {self.slot}: brak opisu")
        if len(self.caption) < 20:
            _fail(f"photos[{self.index}] {self.slot}: podpis zbyt krótki")
        if _date_pl(self.date) not in self.caption:
            _fail(f"photos[{self.index}] {self.slot}: podpis musi zawierać prawdziwą datę ({_date_pl(self.date)})")
        practical = ("widok", "detal", "kadr", "panorama", "mozaika", "wnętrze", "ścieżka",
                     "droga", "tablica", "zejście", "wejście", "plaża", "wrak", "ruiny",
                     "taras", "grota", "sanktuarium", "klasztor", "dziedziniec", "ulica",
                     "port", "marina", "terminal", "strefa", "samolot", "latarnia", "zamek",
                     "kościół", "dachy", "wieś", "brama", "schody", "kolumny", "mury")
        if not any(word in self.caption.lower() for word in practical):
            _fail(f"photos[{self.index}] {self.slot}: podpis musi mówić, czym jest kadr")
        if "listopada 2026" in self.caption.lower() and not self.date.startswith("2026-11"):
            _fail(f"photos[{self.index}] {self.slot}: podpis nie może udawać listopada 2026")
        alt = self.alt.lower()
        if not (20 <= len(self.alt) <= 240):
            _fail(f"photos[{self.index}] {self.slot}: alt musi mieć 20–240 znaków")
        if alt.startswith(("zdjęcie", "fotografia", "photo", "image")):
            _fail(f"photos[{self.index}] {self.slot}: alt nie może zaczynać się od „zdjęcie”")
        loc = self.location
        if not loc.get("name") or not (-90 <= float(loc.get("lat", 999)) <= 90) or not (-180 <= float(loc.get("lon", 999)) <= 180):
            _fail(f"photos[{self.index}] {self.slot}: niepełna lokalizacja")
        if self.focal.get("x") is None or self.focal.get("y") is None:
            _fail(f"photos[{self.index}] {self.slot}: brak focal_point")
        if not (0 <= float(self.focal["x"]) <= 1 and 0 <= float(self.focal["y"]) <= 1):
            _fail(f"photos[{self.index}] {self.slot}: focal_point poza 0–1")
        if self.aspect not in ASPECTS:
            _fail(f"photos[{self.index}] {self.slot}: nieznany aspect {self.aspect!r}")
        if len(self.verification) < 2:
            _fail(f"photos[{self.index}] {self.slot}: potrzebne są co najmniej 2 dowody weryfikacji")
        evidence_types = set()
        for evidence in self.verification:
            if not isinstance(evidence, dict) or not evidence.get("type") or not evidence.get("url") or not evidence.get("note"):
                _fail(f"photos[{self.index}] {self.slot}: niepełny dowód weryfikacji")
            if not str(evidence["url"]).startswith("https://"):
                _fail(f"photos[{self.index}] {self.slot}: dowód bez https")
            evidence_types.add(evidence["type"])
        if "commons-file-page" not in evidence_types:
            _fail(f"photos[{self.index}] {self.slot}: brak dowodu strony pliku")
        if not ({"geotag-osm", "commons-category-or-usage"} & evidence_types):
            _fail(f"photos[{self.index}] {self.slot}: brak dowodu miejsca")
        if self.source_width < self.width or self.source_height < self.height:
            _fail(f"photos[{self.index}] {self.slot}: wariant większy od źródła (upscaling)")
        got_widths = set()
        for variant in self.files:
            width = int(variant.get("width", 0))
            got_widths.add(width)
            if width not in WIDTHS:
                _fail(f"photos[{self.index}] {self.slot}: nieoczekiwana szerokość {width}")
            for fmt in THUMB_FORMATS:
                if width in {480, 800} and not variant.get(fmt):
                    _fail(f"photos[{self.index}] {self.slot}: brak wariantu {fmt} dla {width}")
            for fmt in FORMATS:
                rel = variant.get(fmt)
                if not rel:
                    continue
                path = Path(__file__).resolve().parent.parent / rel
                if not path.exists():
                    _fail(f"photos[{self.index}] {self.slot}: brak pliku {rel}")
                if path.stat().st_size == 0:
                    _fail(f"photos[{self.index}] {self.slot}: pusty plik {rel}")
                budget = MAX_BYTES.get((self.kind, width))
                if budget and fmt == "avif" and path.stat().st_size > budget:
                    _fail(f"photos[{self.index}] {self.slot}: AVIF {width}px ma {path.stat().st_size // 1024} KB, limit {budget // 1024} KB")
                if width == 480 and path.stat().st_size > 45 * 1024:
                    _fail(f"photos[{self.index}] {self.slot}: {fmt.upper()} 480px ma {path.stat().st_size // 1024} KB, limit 45 KB")
            for fmt in ("webp", "jpeg"):
                if width in {480, 800} and variant.get(fmt):
                    path = Path(__file__).resolve().parent.parent / variant[fmt]
                    if path.stat().st_size > (150 * 1024 if self.kind == "hero" else 120 * 1024):
                        _fail(f"photos[{self.index}] {self.slot}: {fmt.upper()} {width}px przekracza budżet")
            ratio = ASPECTS[self.aspect]
            if abs((int(variant["width"]) / int(variant["height"])) - ratio) > 0.02:
                _fail(f"photos[{self.index}] {self.slot}: proporcje {width}px niezgodne z {self.aspect}")
        if 480 not in got_widths or 800 not in got_widths:
            _fail(f"photos[{self.index}] {self.slot}: brakuje wariantów 480/800")
        max_file = max(self.files, key=lambda item: int(item["width"]))
        if int(max_file["width"]) != self.width or int(max_file["height"]) != self.height:
            _fail(f"photos[{self.index}] {self.slot}: width/height muszą opisywać największy wariant")
        if self.offline:
            offline_path = Path(__file__).resolve().parent.parent / self.offline
            if not offline_path.exists():
                _fail(f"photos[{self.index}] {self.slot}: brak pliku offline {self.offline}")

    def variants(self, fmt: str, max_width: int | None = None) -> list[dict]:
        items = [item for item in self.files if item.get(fmt)]
        if max_width:
            items = [item for item in items if int(item["width"]) <= max_width]
        return sorted(items, key=lambda item: int(item["width"]))

    def srcset(self, fmt: str, max_width: int | None = None) -> str:
        return ", ".join(f'{item[fmt]} {item["width"]}w' for item in self.variants(fmt, max_width))

    def best(self, fmt: str) -> dict | None:
        items = self.variants(fmt)
        return items[-1] if items else None

    def fallback(self) -> dict:
        for width in (800, 480):
            for fmt in ("jpeg", "webp", "avif"):
                for item in self.files:
                    if int(item["width"]) == width and item.get(fmt):
                        return item
        return self.files[0]

    def full_href(self) -> str:
        item = self.best("jpeg") or self.best("webp") or self.best("avif")
        return item["jpeg"] if item and item.get("jpeg") else (item["webp"] if item and item.get("webp") else item["avif"])


class PhotoLibrary:
    def __init__(self, root: Path):
        self.root = root
        manifest = root / "data" / "photos.json"
        if not manifest.exists():
            _fail("Brak data/photos.json — warstwa zdjęciowa wymaga manifestu.")
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            _fail(f"data/photos.json nie jest poprawnym JSON: {exc}")
        if not isinstance(data.get("photos"), list) or not data["photos"]:
            _fail("data/photos.json: brak listy photos")
        self.meta = data.get("meta", {})
        self.photos = [Photo(item, i) for i, item in enumerate(data["photos"])]
        for photo in self.photos:
            photo.validate()
        self.by_slot = {p.slot: p for p in self.photos}
        if len(self.by_slot) != len(self.photos):
            _fail("data/photos.json: zduplikowany slot")
        self.by_id = {p.id: p for p in self.photos}
        if len(self.by_id) != len(self.photos):
            _fail("data/photos.json: zduplikowany id")
        self.by_kind: dict[str, list[Photo]] = {}
        self.by_target: dict[tuple[str, str], list[Photo]] = {}
        for p in self.photos:
            self.by_kind.setdefault(p.kind, []).append(p)
            self.by_target.setdefault((p.kind, str(p.target["id"])), []).append(p)
        for group in self.by_target.values():
            group.sort(key=lambda p: p.order)
        self.hero = self.by_kind.get("hero", [None])[0] if self.by_kind.get("hero") else None
        self.strip = sorted(self.by_kind.get("strip", []), key=lambda p: p.order)
        self._check_targets()

    def _check_targets(self) -> None:
        if not self.hero or len(self.by_kind.get("hero", [])) != 1:
            _fail("data/photos.json: potrzebny dokładnie jeden hero")
        if len(self.strip) != 3:
            _fail(f"data/photos.json: pasek pod hero musi mieć 3 kadry, jest {len(self.strip)}")
        for day in range(1, 8):
            key = ("day", f"DAY-{day:02d}")
            group = self.by_target.get(key, [])
            if not (3 <= len(group) <= 4):
                _fail(f"{key[1]}: musi mieć 3–4 zdjęcia, jest {len(group)}")
            self._check_lead(key, group)
        for kind in ("place", "route"):
            for key, group in self.by_target.items():
                if key[0] != kind:
                    continue
                if not (3 <= len(group) <= 4):
                    _fail(f"{key[1]}: musi mieć 3–4 zdjęcia, jest {len(group)}")
                self._check_lead(key, group)

    def _check_lead(self, key: tuple[str, str], group: list[Photo]) -> None:
        leads = [p for p in group if p.lead]
        if len(leads) != 1:
            _fail(f"{key[1]}: potrzebny dokładnie jeden lead, jest {len(leads)}")
        if leads[0].order != 1:
            _fail(f"{key[1]}: lead musi być pierwszy")
        orders = [p.order for p in group]
        if len(set(orders)) != len(orders):
            _fail(f"{key[1]}: zduplikowany order")

    def check_plan_targets(self, day_ids: set[str], place_ids: set[str], route_ids: set[str]) -> None:
        for p in self.photos:
            target = str(p.target["id"])
            allowed = {"day": day_ids, "place": place_ids, "route": route_ids}.get(p.kind)
            if allowed is not None and target not in allowed:
                _fail(f"{p.slot}: target {target} nie istnieje w planie")

    def for_day(self, day_id: str) -> list[Photo]:
        return list(self.by_target.get(("day", day_id), []))

    def for_place(self, place_id: str) -> list[Photo]:
        return list(self.by_target.get(("place", place_id), []))

    def for_route(self, route_id: str) -> list[Photo]:
        return list(self.by_target.get(("route", route_id), []))

    def warnings(self) -> list[str]:
        items = []
        recent = sum(1 for p in self.photos if p.date[:4] >= "2024")
        pct = recent / len(self.photos) * 100
        if pct < 70:
            items.append(f"zdjęcia: tylko {pct:.1f}% dat >= 2024 (cel 70%)")
        for p in self.photos:
            if p.lead and p.date[:4] < "2025":
                items.append(f"zdjęcia: lead {p.slot} ma datę {p.date} (wyjątek od 2025)")
        return items

    def render(self, photo: Photo, variant: str, *, sizes: str, loading: str = "lazy",
               fetchpriority: str | None = None, caption: str = "full",
               max_width: int = 800, link: bool = True, extra_class: str = "") -> str:
        avif = photo.srcset("avif", max_width)
        webp = photo.srcset("webp", max_width)
        jpeg = photo.srcset("jpeg", max_width)
        fallback = photo.fallback()
        fallback_jpeg = fallback.get("jpeg") or fallback.get("webp") or fallback["avif"]
        fp = f' fetchpriority="{_esc(fetchpriority)}"' if fetchpriority else ""
        sources = []
        if avif:
            sources.append(f'<source type="image/avif" srcset="{avif}" sizes="{_esc(sizes)}">')
        if webp:
            sources.append(f'<source type="image/webp" srcset="{webp}" sizes="{_esc(sizes)}">')
        img = (f'<img src="{_esc(fallback_jpeg)}" srcset="{jpeg}" sizes="{_esc(sizes)}" '
               f'width="{photo.width}" height="{photo.height}" alt="{_esc(photo.alt)}" '
               f'loading="{_esc(loading)}"{fp} decoding="async">')
        picture = f'<picture>{"".join(sources)}{img}</picture>'
        if link:
            picture = (f'<a class="photo__link" href="{_esc(photo.full_href())}" '
                       f'data-lightbox="{_esc(photo.slot)}" aria-label="Powiększ: {_esc(photo.title)}">{picture}</a>')
        caption_html = ""
        if caption != "none":
            desc = photo.caption if caption == "full" else photo.title
            source = (f'<span class="photo__source-wrap"> · <a class="photo__source" href="{_esc(photo.source_url)}">źródło</a></span>'
                      if caption == "full" else "")
            caption_html = f"""
        <figcaption class="photo__caption">
          <span class="photo__desc">{_esc(desc)}</span>
          <span class="photo__meta"><time datetime="{_esc(photo.date)}">{_esc(_date_pl(photo.date))}</time> · {_esc(photo.location.get("name", ""))}{source}</span>
        </figcaption>"""
        classes = f"photo photo--{_esc(variant)}" + (f" {extra_class}" if extra_class else "")
        return f"""
      <figure class="{classes}" data-photo="{_esc(photo.slot)}" data-photo-kind="{_esc(photo.kind)}" data-photo-target="{_esc(photo.target.get("id", ""))}" data-photo-date="{_esc(photo.date)}">
        {picture}{caption_html}
      </figure>"""

    def render_hero_preload(self) -> str:
        hero = self.hero
        items = hero.variants("avif", 1280)
        srcset = ", ".join(f'{item["avif"]} {item["width"]}w' for item in items)
        href = next((item["avif"] for item in items if int(item["width"]) == 1280), items[-1]["avif"])
        return (
            f'<link rel="preload" as="image" type="image/avif" '
            f'href="{_esc(href)}" '
            f'imagesrcset="{srcset}" imagesizes="(min-width: 900px) 44vw, 100vw" fetchpriority="high">'
        )

    def render_strip(self) -> str:
        cards = "".join(
            self.render(p, "strip", sizes="(min-width: 900px) 30vw, 100vw", caption="compact", max_width=800)
            for p in self.strip
        )
        return f"""
    <aside class="photo-strip" aria-label="Trzy kadry z wyjazdu">
      <div class="page-width photo-strip__grid">{cards}</div>
    </aside>"""

    def render_gallery(self) -> str:
        counts = {kind: len(self.by_kind.get(kind, [])) for kind in ("day", "place", "route")}
        cards = []
        for p in self.photos:
            cards.append(
                f'<li class="gallery-card" data-photo-kind="{_esc(p.kind)}" data-photo-target="{_esc(p.target.get("id", ""))}" data-photo-slot="{_esc(p.slot)}">'
                + self.render(p, "thumb", sizes="(min-width: 1100px) 240px, (min-width: 700px) 30vw, 45vw", caption="compact", max_width=800)
                + '</li>'
            )
        return f"""
    <section class="section section--photos" id="galeria" aria-labelledby="galeria-title">
      <div class="page-width">
        <header class="section-head">
          <p class="section-index"><span>10</span> / GALERIA</p>
          <div class="section-head__body">
            <h2 id="galeria-title">Galeria: czego się spodziewać</h2>
            <p class="section-lede">{len(self.photos)} kadrów z dni, miejsc i tras. Każdy podpis podaje prawdziwą datę i miejsce; pełny kadr otwiera się w lightboxie. To zdjęcia dokumentacyjne, nie obietnica listopada 2026.</p>
          </div>
        </header>
        <div class="gallery-controls" role="group" aria-label="Filtruj galerię">
          <button type="button" data-gallery-filter="all" aria-pressed="true" aria-controls="photo-gallery">Wszystkie <span>{len(self.photos)}</span></button>
          <button type="button" data-gallery-filter="day" aria-pressed="false" aria-controls="photo-gallery">Dni <span>{counts["day"]}</span></button>
          <button type="button" data-gallery-filter="place" aria-pressed="false" aria-controls="photo-gallery">Miejsca <span>{counts["place"]}</span></button>
          <button type="button" data-gallery-filter="route" aria-pressed="false" aria-controls="photo-gallery">Trasy <span>{counts["route"]}</span></button>
        </div>
        <p class="gallery-status" id="gallery-status" role="status" aria-live="polite"><span id="gallery-status-text">Wszystkie: {len(self.photos)} {_photo_plural(len(self.photos))}</span> <button class="gallery-clear" id="gallery-clear" type="button" hidden>Wyczyść filtr</button></p>
        <ul class="gallery-grid" id="photo-gallery">{''.join(cards)}</ul>
        <p class="gallery-note">Źródła: Wikimedia Commons. Data i miejsce są w podpisie; pełny podpis i link „źródło” są w lightboxie. Wszystkie pliki lokalne; bez AI, bez stocku z innego miejsca. Pełny manifest: <a href="data/photos.json">data/photos.json</a>.</p>
        {_section_next("Na koniec", [("#zrodla", "Źródła i wersja"), ("#top", "Wróć na początek")])}
      </div>
    </section>"""

    def render_lightbox(self) -> str:
        data = []
        for p in self.photos:
            avif = p.best("avif")
            webp = p.best("webp")
            jpeg = p.best("jpeg")
            data.append({
                "slot": p.slot,
                "title": p.title,
                "caption": p.caption,
                "alt": p.alt,
                "date": _date_pl(p.date),
                "place": p.location.get("name", ""),
                "source": p.source_url,
                "author": p.author,
                "license": p.license,
                "avif": avif["avif"] if avif else "",
                "webp": webp["webp"] if webp else "",
                "jpeg": jpeg["jpeg"] if jpeg else "",
                "width": int((avif or p.files[-1])["width"]),
                "height": int((avif or p.files[-1])["height"]),
            })
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        return f"""
    <dialog class="lightbox" id="photo-lightbox" aria-labelledby="photo-lightbox-title" aria-describedby="photo-lightbox-caption">
      <div class="lightbox__inner">
        <div class="lightbox__bar">
          <p class="lightbox__counter" id="photo-lightbox-counter"></p>
          <button class="lightbox__button lightbox__close" type="button" data-lightbox-close aria-label="Zamknij powiększenie">Zamknij</button>
        </div>
        <div class="lightbox__media">
          <picture>
            <source id="photo-lightbox-avif" type="image/avif">
            <source id="photo-lightbox-webp" type="image/webp">
            <img id="photo-lightbox-img" src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=" alt="Powiększenie zdjęcia" width="1280" height="853" decoding="async">
          </picture>
        </div>
        <div class="lightbox__footer">
          <div>
            <h3 id="photo-lightbox-title">Powiększenie zdjęcia</h3>
            <p id="photo-lightbox-caption"></p>
            <p class="lightbox__meta" id="photo-lightbox-meta"></p>
            <a class="lightbox__source" id="photo-lightbox-source" href="#">źródło</a>
          </div>
          <div class="lightbox__nav">
            <button class="lightbox__button" type="button" data-lightbox-prev aria-label="Poprzedni kadr">← Poprzedni</button>
            <button class="lightbox__button" type="button" data-lightbox-next aria-label="Następny kadr">Następny →</button>
          </div>
        </div>
      </div>
    </dialog>
    <script type="application/json" id="photo-lightbox-data">{payload}</script>"""

    def offline_files(self) -> list[str]:
        files = []
        for p in self.photos:
            for width, formats in ((480, ("avif", "webp")), (800, ("avif", "webp", "jpeg"))):
                if not p.lead and width == 800:
                    continue
                for fmt in formats:
                    item = next((v for v in p.files if int(v["width"]) == width and v.get(fmt)), None)
                    if item:
                        files.append("./" + item[fmt])
        hero = self.hero
        item = next((v for v in hero.files if int(v["width"]) == 1280 and v.get("avif")), None)
        if item:
            files.append("./" + item["avif"])
        seen, unique = set(), []
        for path in files:
            if path not in seen:
                seen.add(path)
                unique.append(path)
        return unique

    def credits_markdown(self) -> str:
        lines = [
            "# Cypr 2026 — zdjęcia, źródła i daty",
            "",
            f"{len(self.photos)} zweryfikowanych kadrów z Wikimedia Commons. Każdy wpis ma stronę pliku, prawdziwą datę, miejsce i lokalne warianty. Nie użyto AI, generative fill ani podmiany nieba.",
            "",
            "| Slot | Kadr | Miejsce | Autor | Licencja | Data | Źródło |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for p in self.photos:
            lines.append(
                f"| `{p.slot}` | {p.title} | {p.location.get('name','')} | {p.author} | "
                f"{p.license} | {_date_pl(p.date)} | [Commons]({p.source_url}) |"
            )
        lines += [
            "",
            "## Weryfikacja",
            "",
            "Każdy wpis w `data/photos.json` zawiera stronę pliku, geotag/OSM lub kategorię miejsca oraz datę. Wątpliwe kadry odrzucono przed wdrożeniem.",
            "",
            "## Modyfikacje",
            "",
            "Kadrowanie do formatów 4:5 (hero), 3:2 (dni i pasek), 4:3 (miejsca) i 16:9 (trasy), zmiana rozmiaru do 480/800/1280/1920 px oraz konwersja do AVIF/WebP/JPEG. Bez upscalingu: największy wariant nie przekracza szerokości źródła.",
            "",
        ]
        return "\n".join(lines)
