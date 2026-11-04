"""Photo manifest loading, validation and rendering for Cypr 2026.

The manifest is data/photos.json.  Every rendered photo must have a complete
provenance record; a missing field stops the build rather than shipping an
uncredited image.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ALLOWED_LICENSES = {
    "CC0", "Public domain", "CC BY 2.0", "CC BY 3.0", "CC BY 4.0",
    "CC BY-SA 2.0", "CC BY-SA 3.0", "CC BY-SA 4.0",
}
REQUIRED = {
    "id", "slot", "kind", "target", "title", "location", "gps", "author",
    "license", "license_url", "source_url", "original_url", "date",
    "description", "caption", "alt", "credit", "verification",
    "focal_point", "aspect", "files", "width", "height",
}
KINDS = {"hero", "day", "place", "route"}
WIDTHS = {480, 800, 1280, 1920}
FORMATS = {"avif", "webp", "jpeg"}
MAX_BYTES = {
    ("hero", 480): 180 * 1024,
    ("hero", 800): 180 * 1024,
    ("hero", 1280): 180 * 1024,
    ("hero", 1920): 180 * 1024,
    ("day", 1280): 120 * 1024,
    ("day", 1920): 120 * 1024,
    ("route", 1280): 120 * 1024,
    ("route", 1920): 120 * 1024,
    ("place", 480): 45 * 1024,
}


class PhotoError(Exception):
    pass


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


_MONTHS_PL = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
              "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]


def _date_pl(value: str) -> str:
    try:
        year, month, day = value[:10].split("-")
        return f"{int(day)} {_MONTHS_PL[int(month) - 1]} {year}"
    except (ValueError, IndexError):
        return value


_EVIDENCE_LABELS = {
    "commons-file-page": "strona pliku",
    "geotag-osm": "geotag / OSM",
    "commons-category-or-usage": "kategoria lub użycie",
}


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
        self.target = data["target"]
        self.title = str(data["title"])
        self.location = data["location"]
        self.gps = data["gps"]
        self.author = str(data["author"]).strip()
        self.license = str(data["license"]).strip()
        self.license_url = str(data["license_url"]).strip()
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
        self.files = data["files"]
        self.width = int(data["width"])
        self.height = int(data["height"])
        self.offline = data.get("offline")
        self.reverse = data.get("reverse_search", {})

    def validate(self) -> None:
        if self.kind not in KINDS:
            _fail(f"photos[{self.index}] {self.slot}: nieznany kind {self.kind!r}")
        if self.target.get("type") != self.kind:
            _fail(f"photos[{self.index}] {self.slot}: target.type musi być {self.kind!r}")
        if not self.author:
            _fail(f"photos[{self.index}] {self.slot}: pusty autor")
        if self.license not in ALLOWED_LICENSES:
            _fail(f"photos[{self.index}] {self.slot}: niedozwolona licencja {self.license!r}")
        if not self.license_url.startswith("https://creativecommons.org/"):
            _fail(f"photos[{self.index}] {self.slot}: brak poprawnego license_url")
        if not self.source_url.startswith("https://commons.wikimedia.org/wiki/File:"):
            _fail(f"photos[{self.index}] {self.slot}: source_url musi wskazywać stronę pliku Commons")
        if not self.original_url.startswith("https://upload.wikimedia.org/"):
            _fail(f"photos[{self.index}] {self.slot}: original_url musi wskazywać Wikimedia")
        if not self.date:
            _fail(f"photos[{self.index}] {self.slot}: brak daty")
        if not self.description:
            _fail(f"photos[{self.index}] {self.slot}: brak opisu")
        if len(self.caption) < 20:
            _fail(f"photos[{self.index}] {self.slot}: podpis zbyt krótki")
        if not any(word in self.caption.lower() for word in ("widok", "detal", "kadr", "panorama", "mozaika", "wnętrze", "droga", "ścieżka", "terminal")):
            _fail(f"photos[{self.index}] {self.slot}: podpis musi mówić, czym jest kadr")
        if "listopad" not in self.caption.lower() and "2026" not in self.caption:
            _fail(f"photos[{self.index}] {self.slot}: podpis musi uczciwie oddzielić kadr od listopada 2026")
        alt = self.alt.lower()
        if not (20 <= len(self.alt) <= 240):
            _fail(f"photos[{self.index}] {self.slot}: alt musi mieć 20–240 znaków")
        if alt.startswith(("zdjęcie", "fotografia", "photo", "image")):
            _fail(f"photos[{self.index}] {self.slot}: alt nie może zaczynać się od „zdjęcie”")
        if self.focal.get("x") is None or self.focal.get("y") is None:
            _fail(f"photos[{self.index}] {self.slot}: brak focal_point")
        if not (0 <= float(self.focal["x"]) <= 1 and 0 <= float(self.focal["y"]) <= 1):
            _fail(f"photos[{self.index}] {self.slot}: focal_point poza 0–1")
        if len(self.verification) < 2:
            _fail(f"photos[{self.index}] {self.slot}: potrzebne są co najmniej 2 dowody weryfikacji")
        for evidence in self.verification:
            if not isinstance(evidence, dict) or not evidence.get("type") or not evidence.get("url") or not evidence.get("note"):
                _fail(f"photos[{self.index}] {self.slot}: niepełny dowód weryfikacji")
        if not self.reverse.get("url"):
            _fail(f"photos[{self.index}] {self.slot}: brak linku reverse search")
        got_widths, got_formats = set(), set()
        for variant in self.files:
            width = int(variant.get("width", 0))
            got_widths.add(width)
            if width not in WIDTHS:
                _fail(f"photos[{self.index}] {self.slot}: nieoczekiwana szerokość {width}")
            for fmt in FORMATS:
                rel = variant.get(fmt)
                if not rel:
                    _fail(f"photos[{self.index}] {self.slot}: brak wariantu {fmt} dla {width}")
                path = Path(__file__).resolve().parent.parent / rel
                if not path.exists():
                    _fail(f"photos[{self.index}] {self.slot}: brak pliku {rel}")
                if path.stat().st_size == 0:
                    _fail(f"photos[{self.index}] {self.slot}: pusty plik {rel}")
                got_formats.add(fmt)
            budget = MAX_BYTES.get((self.kind, width))
            if budget:
                # Hero and place budgets apply to every delivered format; lead
                # budgets are enforced on the primary AVIF variant.
                check_formats = FORMATS if self.kind in {"hero", "place"} else {"avif"}
                for fmt in check_formats:
                    file_path = Path(__file__).resolve().parent.parent / variant[fmt]
                    if file_path.stat().st_size > budget:
                        _fail(
                            f"photos[{self.index}] {self.slot}: {fmt.upper()} {width}px ma "
                            f"{file_path.stat().st_size // 1024} KB, limit {budget // 1024} KB"
                        )
        if got_widths != WIDTHS:
            _fail(f"photos[{self.index}] {self.slot}: brakuje wariantów szerokości {sorted(WIDTHS - got_widths)}")
        if got_formats != FORMATS:
            _fail(f"photos[{self.index}] {self.slot}: brakuje formatów {sorted(FORMATS - got_formats)}")
        if self.offline:
            offline_path = Path(__file__).resolve().parent.parent / self.offline
            if not offline_path.exists():
                _fail(f"photos[{self.index}] {self.slot}: brak pliku offline {self.offline}")


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
        self.by_kind = {}
        for p in self.photos:
            self.by_kind.setdefault(p.kind, []).append(p)
        self.hero = self.by_slot.get("hero")
        if not self.hero:
            _fail("data/photos.json: brak slotu hero")
        self._check_targets()

    def _check_targets(self) -> None:
        for p in self.photos:
            if p.kind == "hero":
                continue
            target = p.target.get("id")
            if not target:
                _fail(f"{p.slot}: target bez id")
        for day in range(1, 8):
            if f"day-{day:02d}" not in self.by_slot:
                _fail(f"Brak zdjęcia lead dla dnia day-{day:02d}")

    def for_day(self, day_id: str) -> Photo | None:
        num = day_id.rsplit("-", 1)[-1]
        return self.by_slot.get(f"day-{num}")

    def for_place(self, place_id: str) -> Photo | None:
        for p in self.by_kind.get("place", []):
            if p.target.get("id") == place_id:
                return p
        return None

    def for_route(self, route_id: str) -> Photo | None:
        for p in self.by_kind.get("route", []):
            if p.target.get("id") == route_id:
                return p
        return None

    def render(self, photo: Photo, variant: str, *, sizes: str, loading: str = "lazy",
               fetchpriority: str | None = None, caption: bool = True) -> str:
        files = sorted(photo.files, key=lambda item: int(item["width"]))
        avif = ", ".join(f'{item["avif"]} {item["width"]}w' for item in files)
        webp = ", ".join(f'{item["webp"]} {item["width"]}w' for item in files)
        jpeg = ", ".join(f'{item["jpeg"]} {item["width"]}w' for item in files)
        fallback = next((item for item in files if int(item["width"]) == 800), files[-1])
        fallback_jpeg = fallback["jpeg"]
        fp = f' fetchpriority="{_esc(fetchpriority)}"' if fetchpriority else ""
        caption_html = ""
        if caption:
            caption_html = f"""
        <figcaption class="photo__caption">
          <span class="photo__desc">{_esc(photo.caption)}</span>
          <span class="photo__credit"><a href="{_esc(photo.source_url)}">{_esc(photo.author)}</a> · <a href="{_esc(photo.license_url)}">{_esc(photo.license)}</a></span>
        </figcaption>"""
        return f"""
      <figure class="photo photo--{_esc(variant)}" data-photo="{_esc(photo.slot)}">
        <picture>
          <source type="image/avif" srcset="{avif}" sizes="{_esc(sizes)}">
          <source type="image/webp" srcset="{webp}" sizes="{_esc(sizes)}">
          <img src="{_esc(fallback_jpeg)}" srcset="{jpeg}" sizes="{_esc(sizes)}" width="{photo.width}" height="{photo.height}" alt="{_esc(photo.alt)}" loading="{_esc(loading)}"{fp} decoding="async">
        </picture>{caption_html}
      </figure>"""

    def render_hero_preload(self) -> str:
        hero = self.hero
        files = sorted(hero.files, key=lambda item: int(item["width"]))
        srcset = ", ".join(f'{item["avif"]} {item["width"]}w' for item in files)
        href = next(item["avif"] for item in files if int(item["width"]) == 1280)
        return (
            f'<link rel="preload" as="image" type="image/avif" '
            f'href="{_esc(href)}" '
            f'imagesrcset="{srcset}" imagesizes="(min-width: 900px) 44vw, 100vw" fetchpriority="high">'
        )

    def render_credits(self) -> str:
        rows = []
        for p in self.photos:
            verify = p.verification
            loc_name = p.location.get("name", "")
            rev_url = p.reverse.get("url", "")
            date_pl = _date_pl(p.date)
            rows.append(f"""
        <li class="photo-credit" id="credit-{_esc(p.slot)}" data-photo-kind="{_esc(p.kind)}">
          <p class="photo-credit__title">{_esc(p.title)}</p>
          <p class="photo-credit__meta"><span class="photo-credit__place">{_esc(loc_name)}</span><span class="photo-credit__byline">{_esc(p.author)} · <a href="{_esc(p.license_url)}">{_esc(p.license)}</a><span class="photo-credit__source-wrap"> · <a class="photo-credit__source" href="{_esc(p.source_url)}">Commons</a></span><span class="photo-credit__print"> · {_esc(date_pl)}</span></span></p>
          <p class="photo-credit__date">{_esc(p.caption)}</p>
        </li>""")
        groups = {}
        for p in self.photos:
            key = (p.author, p.license, p.license_url)
            groups.setdefault(key, []).append(p)
        print_rows = []
        for (author, license_name, license_url), items in groups.items():
            titles = "; ".join(f"{item.title} ({item.date[:4]})" for item in items)
            print_rows.append(
                f'<p class="print-credit"><strong>{_esc(author)}</strong> · '
                f'<a href="{_esc(license_url)}">{_esc(license_name)}</a><br>'
                f'<span>{_esc(titles)}</span></p>'
            )
        return f"""
    <section class="section section--photos" id="zdjecia" aria-labelledby="zdjecia-title">
      <div class="page-width">
        <header class="section-head">
          <p class="section-index"><span>10</span> / ZDJĘCIA</p>
          <div class="section-head__body">
            <h2 id="zdjecia-title">Zdjęcia i licencje</h2>
            <p class="section-lede">20 kadrów z Wikimedia Commons: hero, po jednym leadzie każdego dnia, zdjęcia miejsc i tras. Każdy wpis ma autora, licencję, datę i trzy dowody; pełne linki i reverse search są w manifeście. To widoki ogólne lub detale, nie zdjęcia z listopada 2026.</p>
          </div>
        </header>
        <div class="photo-index" role="group" aria-label="Filtruj zdjęcia">
          <button type="button" data-photo-filter="all" aria-pressed="true">Wszystkie <span>{len(self.photos)}</span></button>
          <button type="button" data-photo-filter="hero" aria-pressed="false">Hero <span>1</span></button>
          <button type="button" data-photo-filter="day" aria-pressed="false">Dni <span>7</span></button>
          <button type="button" data-photo-filter="place" aria-pressed="false">Miejsca <span>9</span></button>
          <button type="button" data-photo-filter="route" aria-pressed="false">Trasy <span>3</span></button>
        </div>
        <ul class="photo-credits">{''.join(rows)}</ul>
        <div class="photo-credits-print" role="group" aria-label="Skrócony spis zdjęć do druku">{''.join(print_rows)}</div>
        <p class="photo-credits__note">Każdy wpis ma 3 dowody: stronę pliku, geotag/OSM i kategorię/usage. Pełne linki, daty i reverse search: <a href="data/photos.json">data/photos.json</a> i <a href="CREDITS.md">CREDITS.md</a>. Licencje CC BY-SA zachowują share-alike.</p>
        <p class="fine-print">Licencje CC BY i CC BY-SA zachowują attribution; warianty CC BY-SA są udostępniane na tej samej licencji. Pełny manifest: <a href="data/photos.json">data/photos.json</a>. Kopia tekstowa: <a href="CREDITS.md">CREDITS.md</a>. Reverse search wykonano w Yandex Images; linki przy każdym kadrze. Drobne, nieidentyfikowalne sylwetki w tle nie są portretami.</p>
        {_section_next("Na koniec", [("#zrodla", "Źródła i wersja"), ("#top", "Wróć na początek")])}
      </div>
    </section>
    """

    def offline_files(self) -> list[str]:
        files = []
        for p in self.photos:
            if p.kind not in {"hero", "day"}:
                continue
            for variant in sorted(p.files, key=lambda item: int(item["width"])):
                width = int(variant["width"])
                if width in {480, 800}:
                    files.append("./" + variant["avif"])
                    files.append("./" + variant["webp"])
                if width == 800:
                    files.append("./" + variant["jpeg"])
        return files

    def credits_markdown(self) -> str:
        lines = [
            "# Cypr 2026 — zdjęcia i licencje",
            "",
            "Wszystkie zdjęcia pochodzą z Wikimedia Commons. Kadry przycięto i przeskalowano; nie użyto AI, generative fill ani podmiany nieba. Podpisy mówią wprost, że są to widoki ogólne lub detale, a nie zdjęcia z listopada 2026.",
            "",
            "| Slot | Kadr | Miejsce | Autor | Licencja | Data | Źródło |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for p in self.photos:
            lines.append(
                f"| `{p.slot}` | {p.title} | {p.location.get('name','')} | {p.author} | "
                f"[{p.license}]({p.license_url}) | {_date_pl(p.date)} | [Commons]({p.source_url}) |"
            )
        lines += [
            "",
            "## Weryfikacja",
            "",
            "Każdy wpis w `data/photos.json` zawiera stronę pliku, geotag/OSM, kategorię Commons lub użycie w innych wiki oraz link do reverse search. Reverse search wykonano w Yandex Images; wyniki mogą zawierać kopie w serwisach zewnętrznych, ale źródłem pozostaje plik Commons z pełną metryką.",
            "",
            "## Modyfikacje",
            "",
            "Kadrowanie do formatów 4:5 (hero), 3:2 (dni), 4:3 (miejsca) i 16:9 (trasy), zmiana rozmiaru do 480/800/1280/1920 px oraz konwersja do AVIF/WebP/JPEG. Bez upscalingu: największy wariant nie przekracza szerokości źródła 1920 px.",
            "",
        ]
        return "\n".join(lines)
