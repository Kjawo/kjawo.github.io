#!/usr/bin/env python3
"""Build the generated site and package it for Cloudflare Pages.

The GitHub Pages build stays the source of truth. This wrapper runs the normal
build with Cloudflare-specific canonical/link values, copies only the public
files into ``dist/`` and adds the Cloudflare Pages control files
(``_headers``, ``_redirects``, ``404.html``).

Usage:
    python3 _src/build_pages.py
    python3 _src/build_pages.py --canonical https://example.com/ --zip
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent
DIST = ROOT / "dist"
ZIP_FILE = ROOT / "cypr2026-pages.zip"

DEFAULT_CANONICAL = json.loads((ROOT / "data" / "Cypr_2026_zrodlo_prawdy.json").read_text(encoding="utf-8")).get("publication_contract", {}).get("primary_url", "https://kjawo.github.io/cypr2026/")
DEFAULT_JOURNAL = "https://kjawo.github.io/"
DEFAULT_ARCHIVE = "https://kjawo.github.io/v1/"

PUBLIC_FILES = [
    "index.html",
    "styles.min.css",
    "app.min.js",
    "sw.js",
    "manifest.json",
    "cypr2026-print.pdf",
    "cypr2026-handbook.pdf",
    "cypr2026-handbook.html",
    "CREDITS.md",
]
PUBLIC_DIRS = ["assets", "cal", "data"]

HEADERS = """\
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: geolocation=(), camera=(), microphone=()

/index.html
  Cache-Control: public, max-age=0, must-revalidate

/sw.js
  Cache-Control: no-cache

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/vendor/*
  Cache-Control: public, max-age=31536000, immutable

/assets/photos/*
  Cache-Control: public, max-age=86400

/assets/icons/*
  Cache-Control: public, max-age=604800

/cal/*
  Cache-Control: public, max-age=86400
"""

REDIRECTS = """\
# Stare adresy z GitHub Pages (subpath) -> nowy root projektu.
/cypr2026 https://cypr2026.pages.dev/ 301
/cypr2026/ / 301
/cypr2026/* /:splat 301

# Archiwum v1 nadal mieszka na GitHub Pages.
/v1 https://kjawo.github.io/v1/ 301
/v1/* https://kjawo.github.io/v1/:splat 301
"""

NOT_FOUND = """\
<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex">
  <title>Nie ma tej strony — Cypr 2026</title>
  <style>
    :root { color-scheme: light; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center;
      background: #F6F1E7; color: #173B3F;
      font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif; }
    main { max-width: 34rem; padding: 2rem; }
    h1 { margin: 0 0 .5rem; font-size: clamp(1.6rem, 5vw, 2.4rem); }
    p { margin: 0 0 1rem; }
    a { color: #0C5C6B; }
  </style>
</head>
<body>
  <main>
    <p><strong>404</strong></p>
    <h1>Nie ma tej strony</h1>
    <p>Ten adres nie istnieje w planie Cypr 2026. Wróć do początku planu.</p>
    <p><a href="/">Przejdź do planu Cypr 2026</a></p>
  </main>
</body>
</html>
"""


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.links.append(value)


def fail(message: str) -> None:
    print(f"BŁĄD PAKOWANIA: {message}", file=sys.stderr)
    raise SystemExit(2)


def run_build(canonical: str, journal: str, archive: str, noindex: bool) -> None:
    command = [
        sys.executable,
        str(ROOT / "_src" / "build.py"),
        "--canonical",
        canonical,
        "--journal-url",
        journal,
        "--archive-url",
        archive,
    ]
    if noindex:
        command.append("--noindex")
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def copy_public_files() -> None:
    # Resolve and constrain the only recursive removal to this project's dist.
    if DIST.resolve() != (ROOT.resolve() / "dist") or DIST.is_symlink():
        fail("dist musi być zwykłym katalogiem wewnątrz projektu")
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    for name in PUBLIC_FILES:
        source = ROOT / name
        if not source.is_file():
            fail(f"brak pliku publicznego: {source.relative_to(ROOT)}")
        shutil.copy2(source, DIST / name)

    for name in PUBLIC_DIRS:
        source = ROOT / name
        if not source.is_dir():
            fail(f"brak katalogu publicznego: {source.relative_to(ROOT)}")
        shutil.copytree(
            source,
            DIST / name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )

    (DIST / "_headers").write_text(HEADERS, encoding="utf-8")
    (DIST / "_redirects").write_text(REDIRECTS, encoding="utf-8")
    (DIST / "404.html").write_text(NOT_FOUND, encoding="utf-8")


def validate_dist(canonical: str) -> None:
    index = DIST / "index.html"
    if not index.is_file():
        fail("dist/index.html nie istnieje")

    html = index.read_text(encoding="utf-8")
    if "{{" in html:
        fail("dist/index.html zawiera niewypełniony placeholder")
    if f'<link rel="canonical" href="{canonical}">' not in html:
        fail("dist/index.html nie zawiera oczekiwanego canonical")

    parser = LinkParser()
    parser.feed(html)
    missing: list[str] = []
    for raw in parser.links:
        if not raw or raw.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
            continue
        parsed = urlsplit(raw)
        if parsed.scheme or parsed.netloc:
            continue
        path = unquote(parsed.path)
        if not path:
            continue
        target = DIST / path.lstrip("/") if path.startswith("/") else DIST / path
        if path.endswith("/"):
            target = target / "index.html"
        if not target.is_file():
            missing.append(raw)

    if missing:
        fail("linki prowadzą do brakujących plików: " + ", ".join(sorted(set(missing))))

    for path in sorted((DIST / "cal").glob("*.ics")):
        text = path.read_text(encoding="utf-8").replace("\n ", "")
        urls = [line[4:] for line in text.splitlines() if line.startswith("URL:")]
        if any(not value.startswith(canonical) for value in urls):
            fail(f"adres kalendarza nie zgadza się z canonical: {path.name}")

    export_file = DIST / "data" / "exports.json"
    if not export_file.is_file():
        fail("brak metryki PDF; uruchom npm run pdf przed pakowaniem")
    exports = json.loads(export_file.read_text(encoding="utf-8"))
    for filename, digest in exports["sha256"].items():
        if hashlib.sha256((DIST / filename).read_bytes()).hexdigest() != digest:
            fail(f"nieaktualny eksport PDF lub HTML: {filename}; uruchom npm run pdf")
    if exports["canonical"] != canonical:
        fail("PDF ma inny adres główny; wygeneruj PDF dla bieżącego canonical")

    required = [
        "_headers",
        "_redirects",
        "404.html",
        "index.html",
        "styles.min.css",
        "app.min.js",
        "sw.js",
        "manifest.json",
        "cypr2026-print.pdf",
        "cypr2026-handbook.pdf",
        "cypr2026-handbook.html",
        "CREDITS.md",
        "data/Cypr_2026_zrodlo_prawdy.json",
    ]
    for name in required:
        if not (DIST / name).is_file():
            fail(f"brak wymaganego pliku w dist: {name}")


def write_zip() -> None:
    if ZIP_FILE.exists():
        ZIP_FILE.unlink()
    with zipfile.ZipFile(ZIP_FILE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(DIST.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(DIST).as_posix())
    print(f"    ZIP: {ZIP_FILE} ({ZIP_FILE.stat().st_size:,} B)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Zbuduj i spakuj Cypr 2026 dla Cloudflare Pages.")
    parser.add_argument("--canonical", default=DEFAULT_CANONICAL, help="Docelowy adres strony.")
    parser.add_argument("--journal-url", default=DEFAULT_JOURNAL, help="Link do głównego dziennika.")
    parser.add_argument("--archive-url", default=DEFAULT_ARCHIVE, help="Link do archiwum v1.")
    parser.add_argument("--noindex", action="store_true", help="Dodaj meta robots noindex, nofollow.")
    parser.add_argument("--skip-build", action="store_true", help="Nie uruchamiaj build.py, tylko spakuj istniejące pliki.")
    parser.add_argument("--zip", action="store_true", help="Utwórz cypr2026-pages.zip do ręcznego wgrania.")
    args = parser.parse_args()

    canonical = args.canonical.strip().rstrip("/") + "/"
    if not canonical.startswith(("http://", "https://")):
        fail("--canonical musi być pełnym adresem http(s)")

    if not args.skip_build:
        run_build(canonical, args.journal_url, args.archive_url, args.noindex)
    elif args.noindex:
        fail("--noindex wymaga build.py; usuń --skip-build")

    copy_public_files()
    validate_dist(canonical)
    if args.zip:
        write_zip()

    file_count = sum(1 for path in DIST.rglob("*") if path.is_file())
    size = sum(path.stat().st_size for path in DIST.rglob("*") if path.is_file())
    print(f"OK  Cloudflare Pages · {file_count} plików · {size / 1024 / 1024:.1f} MB")
    print(f"    dist: {DIST}")
    print(f"    canonical: {canonical}")
    print(f"    journal: {args.journal_url}")
    print(f"    archiwum: {args.archive_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
