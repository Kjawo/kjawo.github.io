# Cypr 2026 — plan podróży

Statyczna, jednotygodniowa podstrona pod adresem:

**https://cypr2026.pages.dev/** (mirror: https://kjawo.github.io/cypr2026/)

To niezależny folder w repo `kjawo/kjawo.github.io`, gałąź `gh-pages`. Nie zmienia motywu, globalnego CSS, `_config.yml`, głównego `index.html` ani nawigacji. Link do strony można dodać później — po akceptacji.

## Najważniejsza zasada

`data/Cypr_2026_zrodlo_prawdy.json` jest jedynym źródłem prawdy. `index.html` jest generowany i **nie wolno go edytować ręcznie**. Zmiany wprowadzaj do JSON-a, potem uruchom build i sprawdź ostrzeżenia.

Plik źródłowy został skopiowany 1:1. SHA-256:

```text
c33fd05e805ecf3869489aea480d36614ded6ec00dcd7d19e8819fecbc8405be
```

## Build

Wymagany jest Python 3.10+ (użyto `zoneinfo`); biblioteki zewnętrzne nie są potrzebne.

```bash
python3 cypr2026/_src/build.py
```

Build:

- wczytuje JSON i buduje słowniki `places`, `routes`, `sources`, `days`, `alternatives`,
- sprawdza referencje, daty, godziny, statusy, unikalność ID i format danych,
- zatrzymuje się z błędem, gdy walidacja nie przechodzi,
- wypisuje ostrzeżenia dla `null` i braków, ale ich nie blokuje,
- renderuje `index.html` z `_src/template.html`,
- osadza JSON w `<script type="application/json" id="cypr-data">` do funkcji interaktywnych,
- tworzy zminifikowane `styles.min.css` i `app.min.js` (źródła pozostają czytelne),
- generuje `cal/cypr2026-*.ics` — cały wyjazd i osobne dni,
- wstrzykuje wersję, `updated_on` i hash assetów do `?v=`,
- aktualizuje wersję cache i listę precache w `sw.js`.

Dwa uruchomienia dają identyczny wynik (nie ma timestampów w treści).

## Cloudflare Pages

Wersja produkcyjna jest publikowana na **https://cypr2026.pages.dev/**. Build i pakowanie tylko publicznych plików:

```bash
python3 _src/build_pages.py
```

Deploy (po jednorazowym `npx wrangler login --device`):

```bash
npm run deploy
```

`dist/` zawiera wyłącznie to, co trafia na Pages; `_headers`, `_redirects` i `404.html` są dodawane przez `_src/build_pages.py`. Canonical i linki w `.ics` wskazują na `cypr2026.pages.dev`, a linki „Photo Journal” i „Archiwum v1” pozostają na GitHub Pages. Pełna instrukcja, cache, redirecty i rollback: [`DEPLOY-CLOUDFLARE.md`](DEPLOY-CLOUDFLARE.md).

## Archiwum wersji 1

Stara wersja strony jest zachowana bez zmian funkcjonalnych pod adresem **https://kjawo.github.io/v1/** (lokalnie `http://localhost:8000/v1/`). Katalog `v1/` jest zamrożoną kopią z `noindex`, własnym manifestem, assetami i service workerem o odrębnej nazwie cache. Nowa wersja pozostaje pod `/cypr2026/`; link do archiwum jest też w stopce nowej strony.

## Podgląd

Z katalogu głównego repo:

```bash
python3 -m http.server 8000
# http://localhost:8000/cypr2026/
```

Do testów widoku „Dziś”:

```text
?date=2026-11-06   # przed wyjazdem
?date=2026-11-09   # w trakcie
?date=2026-11-14   # po wyjeździe
```

Parametr zmienia tylko datę logiczną widoku i jest ignorowany, jeśli nie jest prawidłową datą ISO. Zegar nadal pokazuje bieżący czas w `Asia/Nicosia`.

## Struktura

```text
cypr2026/
  index.html                  # GENEROWANY
  styles.css                  # źródło arkusza, mobile-first
  styles.min.css              # GENEROWANY, serwowany
  app.js                      # źródło progresywnych ulepszeń, vanilla JS
  app.min.js                  # GENEROWANY, serwowany
  cal/                        # GENEROWANE pliki .ics (cały wyjazd + dni)
  cypr2026-print.pdf          # statyczny PDF z tego samego builda (54 strony)
  sw.js                       # cache powłoki; build wpisuje wersję i listę plików
  manifest.json
  data/Cypr_2026_zrodlo_prawdy.json
  data/photos.json            # manifest zdjęć: slot, autor, licencja, dowody, pliki
  data/photo-selection.json   # ślepy wybór 3 modeli: głosy, wybór, dogrywki
  AUDYT-ZDJECIA.md            # przed/po, 11 kategorii, lista zdjęć i ograniczenia
  AUDYT-ZDJECIA-PODGLAD.jpg   # kontakt: hero 360/1280, dzień, credits, druk
  CREDITS.md                  # GENEROWANY tekstowy spis zdjęć i licencji
  assets/
    fonts/                    # Inter + Newsreader, lokalnie, OFL
    icons/                    # SVG + PNG 180/192/512
    photos/                   # 20 kadrów × 4 szerokości × AVIF/WebP/JPEG
    vendor/leaflet/           # Leaflet 1.9.4, vendored
  _src/
    build.py
    template.html
  README.md
```

Zdjęć użytkownika nie było, więc warstwa zdjęciowa korzysta wyłącznie z Wikimedia Commons. Hero jest edytorskim splitem z kadrem Petry tou Romiou; każdy dzień ma lead, a 9 miejsc i 3 trasy mają własne kadry. Nie użyto stocku, AI ani podmiany nieba. Ikony strony są inline SVG; PNG służą tylko manifestowi/PWA.

## Zdjęcia i licencje

- **20 kadrów:** 1 hero, 7 leadów dni, 9 miejsc i 3 trasy. Dzień 7 ma kadr Ryanaira na płycie PFO — jest to widok ogólny, nie zdjęcie z listopada 2026.
- **Manifest:** `data/photos.json` zawiera slot, dzień/miejsce/trasę, pliki, autora, licencję, źródło, datę, GPS, opis, podpis, alt, focal point i dowody. Brak pola albo pliku zatrzymuje build.
- **Źródła:** Wikimedia Commons, wyłącznie CC0/PD/CC BY/CC BY-SA. Autorzy i linki są w sekcji „Zdjęcia i licencje”, w `CREDITS.md` i w druku.
- **Uczciwe podpisy:** każdy kadr mówi „widok ogólny” lub „detal” i podaje datę wykonania; żaden nie udaje listopada 2026. Alt jest opisowy, nie zaczyna się od „zdjęcie”.
- **Warianty:** AVIF + WebP + JPEG w 480/800/1280/1920 px; hero 4:5, dzień 3:2, miejsce 4:3, trasa 16:9. Bez upscalingu — największy wariant nie przekracza 1920 px.
- **Budżety:** hero ≤180 KB (wszystkie formaty), lead ≤120 KB (AVIF), thumb ≤45 KB (wszystkie formaty). Hero 1920 AVIF to 145 KB, najcięższy lead 1920 AVIF to 116 KB, najcięższy thumb 480 to 42 KB.
- **Weryfikacja:** strona pliku (autor, licencja, data, opis), geotag/OSM albo współrzędne miejsca, kategoria Commons lub użycie w innych wiki, oraz reverse search w Yandex Images. Linki są przy każdym kadrze w manifeście i w sekcji licencji. Wątpliwy kadr nie wszedł.
- **Offline:** service worker cache’uje dla hero i 7 leadów warianty 480/800 AVIF oraz WebP i 800 JPEG; po pierwszym wejściu online zdjęcia działają bez sieci.
- **Druk:** maksymalnie jedno małe zdjęcie na dzień (pas 56 mm, skala szarości), plus spis autorów i licencji na stronie 54. PDF ma 54 strony.
- **Ograniczenia:** brak zdjęć użytkownika; reverse search może znajdować kopie w serwisach podróżniczych, ale źródłem pozostaje plik Commons z pełną metryką. Kadry są widokami ogólnymi lub detalami, nie dokumentacją konkretnego przejścia szlaku.

## Prywatność i `noindex`

Strona domyślnie jest publiczna i nie zawiera numerów rezerwacji, danych karty, paszportu ani polisy. Numery lotów i daty pochodzą z JSON-a.

Jeśli strona ma być tylko dla rodziny, zbuduj ją z metą `robots`:

```bash
python3 cypr2026/_src/build.py --noindex
```

To dodaje:

```html
<meta name="robots" content="noindex, nofollow">
```

Aby wrócić do wersji publicznej, uruchom build bez flagi. `--noindex` zmienia też hash cache, więc service worker nie poda starej wersji.

Sam `noindex` nie zastępuje ochrony dostępu. GitHub Pages jest publiczny; jeśli potrzebna jest prawdziwa prywatność, użyj innego hostingu z autoryzacją albo osobnego, prywatnego repozytorium.

## Offline

- Service worker rejestruje się tylko na HTTPS albo `localhost`/`127.0.0.1`.
- Cache-first dotyczy powłoki, CSS, JS, JSON, fontów, ikon, plików `.ics` i vendored Leaflet.
- Na górze strony jest zwijana instrukcja „Offline w skrócie: 3 kroki”; pełna sekcja jest w Praktyce.
- Kafelki OpenStreetMap **nie są cache’owane**. Po odcięciu internetu mapa pokaże szare tło, a strona wyświetli uczciwy komunikat.
- Do nawigacji offline używaj Organic Maps lub Guru Maps i wcześniej pobierz zachodni Cypr oraz Troodos.
- „Dodaj do ekranu głównego” jest dostępne z menu przeglądarki dzięki `manifest.json` (`start_url: "./"`, `scope: "./"`, `display: "standalone"`).
- Pierwsze pełne wejście musi się odbyć online. Cache ma nazwę zaczynającą się od `cypr-2026-<wersja>-<hash>`.

## Druk

Strona ma arkusz `@media print`:

- okładka z terminem, wersją, strefą czasu i numerem 112,
- jednokartkowa „Karta podręczna” z lotami, hotelem, alarmem, zadaniami blokującymi i tygodniem światła,
- tydzień w skrócie i dni płynące kolejno, bez osieroconych nagłówków,
- trasy, praktyka, kontakty, checklisty i źródła,
- puste checkboxy do użycia ołówkiem,
- ukryta mapa i interaktywne elementy, ale pełna tekstowa lista miejsc,
- otwieranie zwiniętych `<details>` przez `beforeprint` i przywracanie stanu po `afterprint`,
- pełne adresy URL źródeł na końcu wydruku,
- czytelność w skali szarości; statusy są tekstowe, nie tylko kolorowe.

Do PDF: `Ctrl/Cmd + P` → A4 → marginesy domyślne → bez grafiki tła. Strona nie wymaga JavaScriptu do odczytu i wydruku treści; JS otwiera dodatkowe zwinięte przypisy przed drukiem.

## Testowanie

Sprawdzone szerokości: **360, 390, 768, 1280 i 1440 px**. Widok „Dziś” sprawdzono dla dat 2026-11-06, 2026-11-09 i 2026-11-14, a zegar dla stref urządzenia: UTC, `Europe/Warsaw` i `Asia/Nicosia`.

Audyt axe-core 4.10 (WCAG 2.2 AA): 0 naruszeń; 0 elementów tekstowych interfejsu poniżej 12 px (poza dekoracyjnym 7 px licznikiem klastra mapy) i 0 elementów interaktywnych poniżej 44 px (także linki autorów/licencji mają powiększony obszar klikalny). CLS w testach: 0,0003–0,0018. LCP lokalnie: 0,32–0,75 s. `html-validate` 0 błędów. Build waliduje 20 zdjęć, 240 plików, budżety i dowody; 0 brakujących plików i 0 błędów 404 obrazów.

Funkcje zależne od danych: pasek „światła dnia” (start/koniec trekkingu, zachód, zmierzch, zapas), filtr „Dzień na mapie” (markery i lista miejsc), pliki `.ics` oraz jednokartkowa karta do druku.

Na wąskim ekranie oś czasu i notatki dnia są zwinięte w `<details>`, z wyjątkiem bieżącego dnia podróży. Tydzień jest listą na telefonie i siatką 2 / 3 / 4 kolumn na większych ekranach — bez siedmiu ściśniętych kolumn i bez ucinania opisów. Bez JavaScriptu i w druku wszystkie dni są otwarte. Link do `#day-XX` automatycznie otwiera właściwy dzień.

Checklisty zapisują się jako:

```json
{
  "items": { "CHECK-NOW-0": true },
  "planVersion": "1.0.0"
}
```

Klucz: `cypr2026.checklist.v1`. Reset czyści wpis w `localStorage` po potwierdzeniu. Zaznaczenia nie zmieniają żadnego faktu w planie.

## Wydajność

- HTML jest duży, bo zawiera cały plan i osadzony JSON; w transferze na GitHub Pages jest kompresowany. Transfer: **91,5 KB gzip**.
- CSS: **19,0 KB gzip** (serwowany `styles.min.css`, źródło `styles.css`).
- JS bez Leafleta: **12,2 KB gzip** (serwowany `app.min.js`, źródło `app.js`).
- Fonty: około 152 KB łącznie, lokalne, tylko potrzebne podzbiory. Minimalny rozmiar tekstu na ekranie to 12 px; wszystkie elementy interaktywne mają co najmniej 44 px wysokości i szerokości (także linki inline). Ikony mapy grupują bliskie punkty, żeby pozostały klikalne na telefonie.
- Leaflet, CSS Leafleta i kafelki są ładowane dopiero przy sekcji mapy; kafelki nigdy nie trafiają do cache offline.
- Zdjęcia: 20 kadrów / 240 plików lokalnych (27 MB w repo). W pierwszym ekranie tylko hero; pozostałe mają `loading="lazy"`. Brak analityki, cookie bannerów i zewnętrznych trackerów.

## Decyzje i ograniczenia

- **Auto:** brak potwierdzonej rezerwacji i firmy. Cena, depozyt, miejsce zwrotu i assistance = `null` → „brak danych”. Wymagania i terminy są widoczne osobno.
- **Wellness:** niepotwierdzone; żaden dzień nie zależy od basenów, jacuzzi ani sauny.
- **Lot i hotel:** „zarezerwowane według użytkownika”; voucherów nie sprawdzono.
- **GPX:** brak plików. Nie rysujemy śladów ani linii mapy. Karty tras pokazują status i notkę weryfikacyjną.
- **Mapa:** 13 z 26 miejsc ma współrzędne. Pozostałe nie są geokodowane na oko; mają link do wyszukiwania Maps.
- **Pogoda:** tylko oficjalne linki i checklista. Brak automatycznej prognozy i „zielonego światła” na trekking.
- **Avakas:** wyłączony, tylko w „Poza planem” z powodem „Temporarily closed”.
- **Koszty:** 23 € to wyłącznie trzy bilety dla dwojga. Brak budżetu całościowego.
- **Mobile:** dni inne niż bieżący są domyślnie zwinięte przez JS; bez JS wszystkie są otwarte. Ważne ostrzeżenia (auto, 112, polowania, bag drop) pozostają poza zwiniętymi blokami.
- **Statusy współrzędnych:** `zweryfikowane`, `przejete_z_audytu`, `orientacyjne_do_potwierdzenia`.
- Niektóre serwisy (Ryanair, Wizz Air, timeanddate, SIXT) blokują automatyczne zapytania HTTP 403, choć linki są źródłami z JSON-a. Nie usuwaj ich tylko z powodu błędu bota.
- Print jest obszerny (**54 strony A4**), bo zawiera wszystkie dni, warianty, trasy, miejsca, checklisty i źródła; dni płyną kolejno, a tabele źródłowe mają powtarzany nagłówek. Druga strona to jednokartkowa „Karta podręczna”, żeby nie trzeba było drukować całego planu do szybkiego użycia. Ten sam PDF jest linkowany w stopce i w banerze no-JS; po zmianie JSON wygeneruj go ponownie z aktualnego builda.

## Edycja

1. Zmień `data/Cypr_2026_zrodlo_prawdy.json` (to jedyne miejsce zmian treści).
2. Uruchom build.
3. Napraw błędy walidacji albo świadomie zaakceptuj ostrzeżenia o `null`.
4. Sprawdź widok na 360 px, wydruk i offline.
5. Nie commituj ręcznie zmodyfikowanego `index.html`; commituj raczej JSON + wynik builda.
6. Zdjęcia zmieniaj w `data/photos.json`; build sprawdza komplet pól, pliki i budżety. Nowe warianty muszą istnieć w `assets/photos/` w AVIF/WebP/JPEG dla 480/800/1280/1920 px.

## Licencje i źródła

- Leaflet 1.9.4 — BSD-2-Clause, pliki w `assets/vendor/leaflet/`; nagłówek licencji pozostaje w plikach.
- Inter i Newsreader — SIL Open Font License 1.1; pliki licencji: `assets/fonts/OFL-Inter.txt`, `assets/fonts/OFL-Newsreader.txt`.
- Kontur Cypru w hero/ikonie: uproszczona geometria z Natural Earth (public domain), wyłącznie dekoracja.
- Kafelki mapy: © OpenStreetMap contributors, ODbL; atrybucja jest w mapie.
- Zdjęcia: Wikimedia Commons, CC BY / CC BY-SA / CC0 / PD; pełna lista autorów, licencji i linków w sekcji „Zdjęcia i licencje” oraz w `CREDITS.md`. Warianty CC BY-SA są udostępniane na tej samej licencji.
- Plan i dane: materiały użytkownika oraz audyt wskazany w JSON-ie.
