# Cypr 2026 — pakowanie i późniejsza publikacja

Stan 6 XI 2026, wersja **1.3.0**: komplet przygotowany lokalnie. Nie wykonano commita, pushowania ani wdrożenia. Wyrównanie działających wersji GitHub Pages i Cloudflare pozostaje do publikacji.

## Adresy

Adres główny HTML, ICS i obu PDF-ów: **https://kjawo.github.io/cypr2026/**. Mirror: https://cypr2026.pages.dev/. Konfiguracja: `publication_contract.primary_url` i `mirror_urls` w JSON-ie planu. Wspólny canonical jest celowy; linki do Photo Journal i archiwum v1 są absolutne i działają na obu hostach.

Zmiana adresu głównego wymaga ponownego wygenerowania HTML, ICS i obu PDF-ów. Samo przeniesienie paczki na mirror nie zmienia konfiguracji. Nie traktuj przygotowanej paczki jako dowodu opublikowania aktualizacji.

## Budowanie lokalne

Wymagania i konfiguracja Windows: README. Z folderu `cypr2026/`:

```powershell
npm install
npm run build
npm run test:data
npm test
python _src/build_pages.py --skip-build --zip
```

Pełny build generuje HTML, ICS i oba PDF-y, po czym pakuje publiczne pliki do `dist/`. Osobne pakowanie sprawdza linki lokalne, adresy kalendarzy i zgodność SHA-256 eksportów z HTML według `data/exports.json`. Nieaktualny PDF zatrzymuje pakowanie.

Do paczki trafiają HTML, zminifikowany CSS/JS, service worker, manifest, PDF-y, `CREDITS.md`, `assets/`, `cal/`, `data/`, a także `_headers`, `_redirects` i `404.html`. Kod generatorów, dokumentacja robocza i archiwum v1 nie trafiają do `dist/`.

Podgląd paczki bez publikacji:

```powershell
python -m http.server 8000 --directory dist
# http://localhost:8000/
```

Wariant z odrębnym canonicalem wymaga wykonania wszystkich kroków z tym samym adresem:

```powershell
python _src/build.py --canonical https://example.com/
npm run pdf
python _src/build_pages.py --skip-build --canonical https://example.com/ --zip
```

## Publikacja — poza zakresem wykonanych prac

Po osobnym zleceniu publikacji można użyć istniejącego projektu Cloudflare `cypr2026`, gałąź `gh-pages`, przez Wrangler albo ręcznie wgrać zawartość `dist/` / przygotowany ZIP. Skrypt `npm run deploy` przebudowuje materiały i wywołuje publikację; nie jest potrzebny do podglądu ani pakowania lokalnego.

Po publikacji trzeba sprawdzić na **obu** adresach numer wersji, osadzony JSON, godziny auta i powrotu, PDF-y, ICS oraz przełączenie service workera na nowy cache. Wyczyszczenie cache nie potwierdza aktualizacji drugiego hostingu. Checklisty są oddzielne dla każdego adresu.

Service worker i HTML wymagają odświeżania; `_headers` ustawia dla `sw.js` `no-cache`. Kafelki OSM nie trafiają do cache. Poprzedni cache planu jest usuwany po udanej instalacji nowego; klucz checklist nie zmienia się. Nie zapisuj tokenów i danych osobowych w publicznej paczce.
