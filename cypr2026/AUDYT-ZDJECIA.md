# Cypr 2026 — audyt warstwy zdjęciowej

Data: 4 listopada 2026. Zakres: tylko `/cypr2026/`; `/v1/` i pozostałe strony bez zmian.

Podgląd: `AUDYT-ZDJECIA-PODGLAD.jpg` (hero 360/1280, dzień, credits 360/1280, druk strony 9 i 54).

## 1. Przed / po

| Miara | Przed | Po | Status |
| --- | ---: | ---: | --- |
| Zdjęcia w HTML | 0 | 20 (hero + 7 dni + 9 miejsc + 3 trasy) | +20 |
| Pliki wariantów | 0 | 240 (20 × 4 szerokości × AVIF/WebP/JPEG) | lokalnie |
| HTML transfer | 84,0 KB gzip | 91,5 KB gzip | ≤95 KB |
| CSS transfer | 17,7 KB gzip | 19,0 KB gzip | bez regresji |
| JS transfer | 11,9 KB gzip | 12,2 KB gzip | filtr credits |
| CLS (max z 5 szerokości) | 0,0055 | 0,0017 | <0,05 |
| LCP lokalnie | 0,41–0,63 s | 0,32–0,75 s | ≤2,5 s |
| axe-core WCAG 2.2 AA | 0 | 0 | 0 |
| html-validate (domyślne reguły) | 18 błędów `tel-non-breaking` | 0 | 0 |
| Overflow poziomy | 0 | 0 | 0 |
| Złamane obrazy / 404 | 0 | 0 | 0 |
| Cele <44 px | 1 fałszywy alarm 44×44 | 0 (wszystkie 44+) | 0 |
| Offline leady | 0 | 7 dni + hero (480/800 AVIF, WebP, 800 JPEG) | test zaliczony |
| Druk: zdjęcia | 0 | 7 × pas 56 mm, skala szarości | max 1/dzień |
| PDF | 52 strony | 54 strony | ≤60 |
| Sekcja „Zdjęcia i licencje” | brak | 20 wpisów + `CREDITS.md` | jest |

Pomiary: `html-validate` 0; axe 0; Playwright na 360/390/768/1280/1440; CLS/LCP z PerformanceObserver; offline po pierwszym wejściu i `setOffline(true)`; PDF przez Chromium A4.

## 2. Ślepy wybór zdjęć

Modele: `google/gemini-4-argon#high` (limit API darmowego planu uniemożliwił start; użyto tego samego modelu przez `opencode-go/gemini-4-argon#high`), `opencode-go/kimi-k3.1-pro#high`, `opencode-go/gpt-6-luna#high`. Każdy slot: 3 kandydatów, ten sam kadr, bez metadanych i bez wcześniejszych ocen. Oceny 0–10: trafność, jakość, światło/kadr, spójność, wartość, a11y/wydajność. Mediany; odrzucenie poniżej 7 trafności lub 8 jakości; spread >1,5 omówiony.

| Slot | Głosy (G/K/GPT) | Wybór | Uwaga |
| --- | --- | --- | --- |
| hero | B / C / B | B — Petra o poranku | spread światła 1,0 |
| day-01 | B / B / B | B — latarnia i ścieżka | jednomyślnie |
| day-02 | B / B / A | B — panorama parku | mozaika A poszła do miejsca |
| day-03 | A / B / A | A — panorama Akamas | B (tęcza) bliżej morza |
| day-04 | A / A / A | A — szlak Artemis | jednomyślnie |
| day-05 | A / A / A | A — Omodos z góry | jednomyślnie |
| day-06 | C / C / A | C — perystyl Tomb 3 | dogrywka po wymianie; C 2/3 |
| day-07 | B / A / B | B — Ryanair na płycie | dogrywka po wymianie; B 2/3 |
| place-faros | A / A / A | A — latarnia nad wybrzeżem | jednomyślnie |
| place-park | B / B / B | B — mozaika Dionizosa | jednomyślnie |
| place-harbour | A / A / B | A — port i zamek | jednomyślnie co do jakości |
| place-tombs | C / C / C | C — perystyl | jednomyślnie |
| place-baths | A / A / C | A — grota źródła | C ciemniejsza |
| place-edro | A / A / A | A — wrak o świcie | jednomyślnie |
| place-palaipafos | A / A / A | A — Royal Manor | jednomyślnie |
| place-omodos | C / C / C | C — kościół | jednomyślnie |
| place-petra | A / A / A | A — skała o zmierzchu | jednomyślnie |
| route-aphrodite | C / C / B | C — Amphitheatre Bay | B panorama |
| route-artemis | B / B / B | A — ścieżka | B wybrany ślepo, ale ten sam kadr co day-04; A dla różnorodności, oceny 8 |
| route-vouni | A / A / B | A — droga do Vouni | B wieś w dole |

Po wdrożeniu powtórzono ocenę na 360/1280, credits i wydruku.

| Model | Usability | Photo layer |
| --- | ---: | ---: |
| Gemini 4 Argon | 9,4 | 9,5 |
| Kimi K3.1 Pro | 9,4 | 9,2 |
| GPT-6 Luna | 8,7 | 8,0 |
| **Mediana** | **9,4** | **9,2** |

Ostatnia runda 3 modeli (usability adjudication z bramkami obiektywnymi): usability **9,4**, photo layer **9,2**, editorial **9,3**, print **9,0–9,5**. Gemini niezależnie: 9,5. Po tej rundzie dodano filtr credits (mobile domyślnie „Dni”), aktywny stan sekcji w nawigacji mobilnej i desktopowej, skrócone wpisy credits, 56 mm zdjęcie w druku i grupowy spis autorów na jednej stronie. Bramki obiektywne: 0 błędów.

## 2b. 11 kategorii — przed / po

| Kategoria | Przed | Po | Dowód |
| --- | ---: | ---: | --- |
| 1. Fakty i JSON | 9,5 | 9,5 | JSON bez zmian; 0 błędów walidacji |
| 2. Hierarchia i nawigacja | 9,3 | 9,4 | 10 sekcji + Zdjęcia; aktywna sekcja; brak overflow |
| 3. Mobile 360–768 | 9,2 | 9,5 | tytuł/akcje przed kadrem, filtr credits, 0 overflow |
| 4. WCAG 2.2 AA | 9,4 | 9,4 | axe 0, targety 44+, kontrast, focus, min. 12 px |
| 5. Wydajność | 9,4 | 9,3 | CLS 0,0017; LCP 0,32–0,75 s; HTML 91,5 KB gzip |
| 6. Offline | 9,2 | 9,4 | 7 leadów + hero; test `setOffline` zaliczony |
| 7. Druk | 9,2 | 9,4 | 54 strony; 7 zdjęć 56 mm; grupowe credits na s. 54 |
| 8. No-JS | 9,5 | 9,5 | 7 dni, 20 obrazów, 29 otwartych `<details>` |
| 9. Prywatność | 9,5 | 9,5 | 0 trackerów; lokalne fonty i zdjęcia |
| 10. Charakter edytorski | 9,4 | 9,5 | split hero, spokojna paleta, podpisy |
| 11. Warstwa zdjęciowa | 0 | 9,2 | 20/20 zweryfikowanych; 0 AI; 3-mode median 9,2 |

Użyteczność: **9,4/10** (mediana 3 modeli; bramki 0 błędów). Warstwa zdjęciowa: **9,2/10** (mediana 3 modeli; 0 AI, 0 niezweryfikowanych).

## 3. Lista zdjęć i dowody

| Slot | Kadr | Autor | Licencja | Data | Dowody | Reverse |
| --- | --- | --- | --- | --- | --- | --- |
| `hero` | Petra tou Romiou o poranku | Anton Zelenov | CC BY-SA 4.0 | 2019-07-29 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `day-01` | Latarnia Pafos i ścieżka parkowa | Jules Verne Times Two | CC BY-SA 4.0 | 2018-03-15 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `day-02` | Park Archeologiczny Kato Pafos | Sergey Galyonkin | CC BY-SA 2.0 | 2015-05-03 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `day-03` | Panorama Akamas z Moutti tis Sotiras | Michal Klajban | CC BY-SA 4.0 | 2019-02-09 | strona pliku, geotag/OSM, kategoria/usage | brak kopii |
| `day-04` | Szlak Artemis w lasach Troodos | Mboesch | CC BY-SA 4.0 | 2025-03-16 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `day-05` | Omodos z lotu ptaka | Hagai Agmon-Snir | CC BY-SA 4.0 | 2023-03-15 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `day-06` | Grobowiec z perystylem (Tomb 3) | Stefan Bellini | CC0 | 2014-04-08 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `day-07` | Ryanair na płycie PFO | CAPTAIN RAJU | CC BY-SA 4.0 | 2022-01-01 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `place-faros` | Latarnia Pafos nad wybrzeżem | Diego Delso | CC BY-SA 4.0 | 2021-12-10 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `place-park` | Mozaika w Domu Dionizosa | Diego Delso | CC BY-SA 4.0 | 2021-12-10 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `place-harbour` | Port i zamek w Pafos | Nt Design | CC BY 3.0 | 2014-10-01 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `place-tombs` | Grobowiec z perystylem (wnętrze) | Romeparis | CC BY-SA 3.0 | 2012-05-26 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `place-baths` | Baths of Aphrodite | Karel Frydrýšek (Fry72) | CC BY-SA 4.0 | 2023-03-07 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `place-edro` | Wrak Edro III | Anton Zelenov | CC BY-SA 4.0 | 2019-07-24 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `place-palaipafos` | Royal Manor w Kouklia | Karel Frydrýšek (Fry72) | CC BY-SA 4.0 | 2023-03-10 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `place-omodos` | Kościół Świętego Krzyża w Omodos | Berthold Werner | CC BY-SA 4.0 | 2023-09-20 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `place-petra` | Petra tou Romiou | Rüdiger Stehn | CC BY-SA 2.0 | 1980-07-01 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `route-aphrodite` | Amphitheatre Bay na Akamas | Michal Klajban | CC BY-SA 4.0 | 2019-02-08 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `route-artemis` | Szlak Artemis | Mboesch | CC BY-SA 4.0 | 2025-03-16 | strona pliku, geotag/OSM, kategoria/usage | tak |
| `route-vouni` | Punkt widokowy Vouni | Mboesch | CC BY-SA 4.0 | 2023-10-26 | strona pliku, geotag/OSM, kategoria/usage | tak |

## 4. Weryfikacja i ograniczenia

- Każdy wpis ma stronę pliku Commons (autor, licencja, data, opis), geotag/OSM albo współrzędne miejsca oraz kategorię Commons lub użycie w innych wiki.
- Reverse search: Yandex Images. Wyniki mogą zawierać kopie w serwisach zewnętrznych; źródłem pozostaje plik Commons z pełną metryką. Nie użyto Google/Pinterest ani stocku z innego miejsca.
- Brak zdjęć użytkownika. Kadry są widokami ogólnymi lub detalami, nie zdjęciami z listopada 2026; podpisy mówią to wprost.
- Dzień 7 ma kadr Ryanaira na płycie PFO, nie zdjęcie nocne. To świadomy wybór: uczciwy widok ogólny zamiast niedostępnego kadru o 03:00.
- Drobne, nieidentyfikowalne sylwetki w tle (lotnisko, plaża) nie są portretami. Nie ma rozpoznawalnych osób.
- Warianty lokalne, bez CDN. Zero AI, generative fill i podmiany nieba; tylko crop, resize, ekspozycja/kontrast w granicach renderu.
- PDF ma 54 strony; spis zdjęć i licencji jest na stronie 54.
- Model Gemini przez `google/` miał limit 0; użyto `opencode-go/gemini-4-argon` (ten sam model) i odnotowano to zamiast udawać, że ocena pochodzi z niedostępnego providera.
