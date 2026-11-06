# Cypr 2026 — plan podróży

Wersja **1.3.0**, 6 XI 2026. Implementacja zaakceptowanego audytu projektu. Zakres tych prac jest lokalny: **bez commita, pushowania i publikacji**.

SHA-256 źródłowego planu: `28302c7f09fa3a6f5b450d2cbeaaf43db9b8b3a8497d160dd40fc26fd88a90ea`.

Adres główny materiałów: **https://kjawo.github.io/cypr2026/**. Mirror: https://cypr2026.pages.dev/. Konfigurację zapisano w `publication_contract.primary_url` i `mirror_urls` w danych. Wyrównanie opublikowanych wersji wymaga osobnej publikacji; nie zostało wykonane w tym zadaniu. Paczka lokalna ma wspólny canonical, a odnośniki do dziennika i archiwum są absolutne, więc działają również na mirrorze.

## Edycja i budowanie

Treść planu pochodzi z `data/Cypr_2026_zrodlo_prawdy.json`, zdjęcia z `data/photos.json`. Nie edytuj ręcznie HTML, zminifikowanych plików, ICS ani PDF. Generator sprawdza referencje, godziny, statusy i lokalne warianty zdjęć.

Wymagania: Python 3.10+, Node.js, Chrome oraz `npm install`. Windows potrzebuje pakietu `tzdata`; Pillow jest potrzebne tylko do odtwarzania wariantów nowych zdjęć.

```powershell
# Jeśli aliasy Windows kierują do Microsoft Store, wskaż rzeczywisty Python:
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python313;$env:PATH"
python -m pip install tzdata
npm install
npm run build
npm run test:data
npm test
```

`npm run build` kolejno generuje stronę i kalendarze, oba PDF-y, a następnie pakuje publiczne materiały do `dist/`. Chrome jest domyślną przeglądarką do eksportu i testów; opcjonalna zmienna `CHROME_PATH` wskazuje inny plik wykonywalny Chromium.

Kroki można uruchamiać oddzielnie:

```powershell
python _src/build.py
npm run pdf
python _src/build_pages.py --skip-build --zip
```

Pakowanie kontroluje SHA-256 wejściowego HTML i obu PDF-ów według `data/exports.json`. Nieaktualny PDF zatrzymuje pakowanie. Zmiana canonical przez `--canonical` wymaga przebudowania HTML, kalendarzy i PDF przed pakowaniem z tym samym adresem. Zwykły build używa adresu głównego z danych.

Podgląd z katalogu nadrzędnego repo:

```powershell
python -m http.server 8000
# http://localhost:8000/cypr2026/
```

`?date=2026-11-09` zmienia logiczny dzień widoku „Dziś”; zegar nadal pokazuje rzeczywisty czas na Cyprze. Testy korzystają z zegara Playwright, aby sprawdzić pełne przejścia czasu i wznowienie strony.

## Gotowe materiały

- `index.html`, `styles.min.css`, `app.min.js`, `sw.js`, `manifest.json` i `assets/` — strona z lokalnymi zasobami;
- `cal/` — osiem ICS: cały wyjazd i siedem dni;
- `cypr2026-handbook.pdf` — **14 stron**, skrót podręczny;
- `cypr2026-handbook.html` — generowane wejście do skrótu PDF;
- `cypr2026-print.pdf` — pełna wersja, **108 stron**;
- `CREDITS.md` — źródła, autorzy i licencje 142 fotografii;
- `dist/` i `cypr2026-pages.zip` — lokalny komplet publiczny do późniejszej publikacji.

Dane rezerwacji: W61417 7 XI WMI 05:40 → PFO 10:10; FR5880 13 XI PFO 06:20 → WAW 08:45; Princessa Vera 7–13 XI; Petsas C3 automat, odbiór umówiony 7 XI 10:30, zwrot 13 XI 03:30, prepaid 325,50 EUR. Godziny lotów są lokalne dla lotnisk. Prowizoryczne okna obsługi nie zmieniają terminów umówionych.

Powrót: wyjazd hotel 02:40; cel sektora 03:15–03:25; zwrot umówiony 03:30; cel stanowiska 04:20 i nadania 04:20–04:45; granica nadania 05:20, zamknięcie bramki 05:50. Procedury Petsas i hotelowej bramy nadal do potwierdzenia.

## Offline, checklisty i dostępność

Po instalacji service workera strona sprawdza komplet plików i zgodność wersji z dokumentem. Dopiero wtedy pokazuje **„Plan zapisany offline”**. Niepełny zapis, błąd instalacji lub stara wersja nie otrzymują tego potwierdzenia. Przycisk umożliwia sprawdzenie i ponowienie zapisu.

Zapis obejmuje treść, kontakty, fonty, ICS, oba PDF-y i małe zdjęcia każdej fotografii. Powiększenie wcześniej nieotwartego zdjęcia wybiera dostępny wariant z cache; przy błędzie dużego pliku korzysta z małego JPEG. Pobranie dużych JPEG-ów jest osobną opcją z postępem i komunikatem zakończenia/przerwania.

Kafelki OSM, zewnętrzne strony, prognoza i nawigacja nie są pobierane. Mapy zachodniego Cypru i Troodos należy pobrać osobno, np. w Organic Maps. Przeglądarka może usunąć zapis przy braku miejsca.

Checklisty zachowują klucz `cypr2026.checklist.v1`; aktualizacja planu/cache ich nie kasuje. Odhaczenie zadania nie potwierdza warunków umowy. Zapis jest lokalny dla przeglądarki i adresu strony.

„Dziś” korzysta z `Asia/Nicosia`, odświeża wydarzenia w ciągu dnia oraz po powrocie do karty, `pageshow` i odzyskaniu fokusu okna. Nie otwiera ponownie ani nie zamyka sekcji dnia. Podstawowy harmonogram, kontakty i rezerwacje są renderowane podczas builda i dostępne bez JavaScriptu. Druk otwiera szczegóły i przywraca ich wcześniejszy stan. Historia bez JavaScriptu jest dostępna w pełnym PDF.

## Mapa i zdjęcia

Wszystkie cypryjskie punkty bazowej osi dni mają pinezki. Łącznie 31 z 50 miejsc ma współrzędne; pozostałe to głównie alternatywy oraz polskie lotniska, z uczciwie oznaczonym wyszukiwaniem Maps. Nowe punkty mają źródło i kontekst: obiekt, wejście, ulica piesza, restauracja lub początek szlaku. Punkt hotelu nie potwierdza bramy parkingowej; Troodos Square nie zastępuje startu Artemis.

Manifest zawiera **142 fotografie i 1479 wskazanych plików wariantów**. Zachowano istniejące autorstwo i licencje; nowe kadry obejrzano przed przypisaniem. Przeniesiono Alykes oraz wieś Choirokoitia do osobnych zestawów. Zastąpiono grafikę PFO fotografią terminala; dodano zatokę Pissouri, rekonstrukcje domów i schody w Choirokoitii oraz drogę przy punkcie obserwacyjnym Vouni. Nowych wiarygodnych zdjęć samej trasy Pouziaris nie znaleziono; zachowano kontekst rejonu startu. Nie dopisano nieznanego GPS stanowiska aparatu.

Odtwarzanie nowych wariantów z oryginału wskazanego w manifeście:

```powershell
python -m pip install Pillow
python _src/photo_variants.py SLOT SCIEZKA_DO_ORYGINALU
python _src/build.py
```

Historyczne głosy w `photo-selection.json` pozostają zachowane; pole korekt audytu wskazuje późniejsze zmiany. Wyjątek świeżości zdjęć opisany w `V8-EXCEPTION.md` pozostaje historią decyzji użytkownika; nie fabrykowano nowych dat.

## Kontrole i ograniczenia

`_src/verify_data.py` sprawdza JSON osadzony w HTML, rezerwacje, 67 zdarzeń w ośmiu ICS, unikalność UID, poprawność końców zdarzeń, strefy, zgodność linków, bazową mapę i manifest/cache zdjęć. UID pozostały stabilne; ICS otrzymuje rosnące `SEQUENCE` z wersji planu, również przy zmianach tego samego dnia.

`_src/verify.cjs` sprawdza przejścia wydarzeń i wznowienie w czterech strefach, checklisty/fokus/sekcje, szerokości 360/390/768/1440 i tekst 200%, mapę, galerię, klawiaturę, brak JavaScriptu, druk, axe WCAG 2.2 AA, instalację offline, błąd instalacji, naprawę cache, wcześniej nieotwarte powiększenia, opcjonalne duże zdjęcia i aktualizację service workera. Zrzuty i wyniki JSON zapisuje w katalogu tymczasowym; `CYPR_TEST_OUTPUT` pozwala wskazać inny katalog.

Build nadal uczciwie ostrzega o brakujących GPX, sumach podejść i niepotwierdzonych usługach/kosztach. Brak testów na fizycznym iPhonie i importu do Apple/Google Calendar. Otwarte sprawy Petsas, hotelu i transportu WMI/WAW nie zostały rozwiązane zmianą treści. Szczegóły wykonania i rzeczywiste wyniki: `IMPLEMENTACJA-2026-11-06.md`.
