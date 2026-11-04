# Cypr 2026 na Cloudflare Pages

Ta strona jest statyczna. Cloudflare Pages nie buduje jej z JSON-a — dostaje gotowy katalog `dist/` z `index.html`, assetami i plikami kontrolnymi. Dzięki temu build pozostaje lokalny i powtarzalny, a deploy jest szybki.

## Co jest wysyłane

`python3 _src/build_pages.py`:

1. uruchamia normalny `_src/build.py` z canonical `https://cypr2026.pages.dev/`,
2. kopiuje do `dist/` tylko publiczne pliki:
   - `index.html`, `styles.min.css`, `app.min.js`, `sw.js`, `manifest.json`,
   - `cypr2026-print.pdf`, `CREDITS.md`,
   - `assets/`, `cal/`, `data/`,
3. dodaje `_headers`, `_redirects` i `404.html`,
4. sprawdza, czy wszystkie lokalne linki z `index.html` prowadzą do istniejących plików.

Nie są wysyłane: `_src/`, `README.md`, `AUDYT-*` ani archiwum `v1/`. Katalog `data/` jest kopiowany w całości, bo service worker precache’uje źródłowy JSON.

## Wymagania

- Python 3.10+ (bez zewnętrznych bibliotek),
- Node.js 20+ i `npx wrangler` (Wrangler 4.x),
- konto Cloudflare z dostępem do Pages.

## Build i podgląd lokalny

Z katalogu `cypr2026/`:

```bash
python3 _src/build_pages.py
npx wrangler pages dev dist
```

`wrangler pages dev` uruchamia lokalny serwer na `http://localhost:8788` i czyta `_headers`/`_redirects` podobnie jak produkcja. Sam podgląd bez Cloudflare:

```bash
python3 -m http.server 8000 --directory dist
```

## Pierwszy deploy

Jednorazowa autoryzacja (w kontenerze/SSH użyj device flow):

```bash
npx wrangler login --device
```

Wrangler wypisze adres i kod. Otwórz adres w przeglądarce, zaloguj się i zatwierdź dostęp. Potem:

```bash
cd /home/konrad/projects/kjawo.github.io/cypr2026
npm run build
npx wrangler pages project create cypr2026 --production-branch gh-pages --force
npx wrangler pages deploy dist --project-name cypr2026 --branch gh-pages
```

Pierwszy deploy tworzy projekt `cypr2026` i adres `https://cypr2026.pages.dev/`. Kolejne deploye:

```bash
npm run deploy
```

albo bez npm:

```bash
python3 _src/build_pages.py
npx wrangler pages deploy dist --project-name cypr2026 --branch gh-pages
```

## Canonical i linki

Build dla Cloudflare używa:

- canonical: `https://cypr2026.pages.dev/`,
- „KJ / Photo Journal”: `https://kjawo.github.io/`,
- „Archiwum v1”: `https://kjawo.github.io/v1/`.

Linki w `.ics` również prowadzą do `https://cypr2026.pages.dev/`. GitHub Pages pozostaje osobnym, działającym adresem; jeśli ma przestać być kanoniczny, nie commituj lokalnego `index.html` wygenerowanego z canonicalem Pages albo uruchom ponownie `python3 _src/build.py` bez flag.

Zmiana domeny:

```bash
python3 _src/build_pages.py --canonical https://cypr2026.kjawo.pl/ --journal-url https://kjawo.pl/ --archive-url https://kjawo.github.io/v1/
npx wrangler pages deploy dist --project-name cypr2026 --branch gh-pages
```

Po podpięciu własnej domeny w Cloudflare Pages (Custom domains) ustaw ją też jako canonical i przebuduj stronę.

## Cache i nagłówki

`dist/_headers` ustawia:

- `index.html`: zawsze rewalidowany (`max-age=0, must-revalidate`),
- `sw.js`: bez cache,
- `assets/*`: roczny cache immutable (nazwy plików są stałe, ale wersjonowane przez `?v=hash`; przy zmianie zdjęć/fontów podnieś wersję lub użyj nowej nazwy),
- `cal/*`: 1 dzień,
- podstawowe nagłówki bezpieczeństwa (`nosniff`, `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy`).

Service worker ma własny cache `cypr-2026-<wersja>-<hash>` i czyści stare wersje przy aktywacji. Po deployu odśwież stronę dwukrotnie albo wyczyść dane witryny, jeśli przeglądarka trzyma stary shell.

## Redirecty

`dist/_redirects`:

- `/cypr2026/*` → `/:splat` (stare adresy z GitHub Pages),
- `/cypr2026/` → `/`,
- `/v1/*` → `https://kjawo.github.io/v1/:splat` (archiwum zostaje na GitHub Pages).

## Rollback

```bash
npx wrangler pages deployment list --project-name cypr2026
npx wrangler pages deployment rollback <deployment-id> --project-name cypr2026
```

Albo w dashboardzie: **Workers & Pages → cypr2026 → Deployments → … → Rollback**.

## Typowe problemy

- **`You are not authenticated`** — uruchom `npx wrangler login --device` i dokończ autoryzację.
- **`Your user email must been verified`** — Cloudflare wymaga weryfikacji e-maila konta. Wejdź w dashboard → **My Profile → Email Address → Send verification email**, kliknij link z wiadomości i wróć do deployu.
- **`Delegating to the latest version of Cloudflare Pages` / `Missing entry-point`** — Wrangler 4.157+ próbuje przekierować Pages do Workers. Dodaj `--force` do `wrangler pages project create` i `wrangler pages deploy`.
- **`Project not found`** — najpierw `npx wrangler pages project create cypr2026 --production-branch gh-pages --force`.
- **Stara wersja po deployu** — odśwież z pominięciem cache; service worker czyści stare cache przy nowym hashu, ale pierwsze wejście musi pobrać nowy `sw.js`.
- **404 na `/v1/`** — to zamierzone; archiwum jest na `https://kjawo.github.io/v1/`, a `_redirects` przekierowuje tam stare linki.
- **Brak mapy offline** — kafelki OpenStreetMap nie są cache’owane; to zachowanie zgodne z README, nie błąd deployu.

## Bezpieczeństwo

W repo nie ma tokenów ani sekretów. Nie commituj `.env`, tokena API ani plików z danymi rezerwacji. Jeśli w przyszłości deploy ma iść z GitHub Actions, token Cloudflare trzymaj wyłącznie w sekretach repozytorium.
