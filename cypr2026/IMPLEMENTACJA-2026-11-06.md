# Wykonanie poprawek audytu — 6 XI 2026

**Wersja 1.3.0. Zmiany lokalne, bez commita, pushowania i publikacji.** Zachowano układ tygodnia, oba główne trekkingi, regeneracyjny czwartek i dane rezerwacji. HEAD pozostał `a60daccccaff75cae8555864881fd7bc97422604`.

## Wdrożono

- „Dziś” przechodzi między wydarzeniami oraz odświeża się po powrocie do karty/wznowieniu. Zegar używa Nikozji; aktualizacja zachowuje fokus, checklisty i otwarte sekcje.
- Rezerwacje i eksporty rozróżniają terminy umówione, okna planu i granice odprawy. Powrót: wyjazd 02:40, Petsas umówione 03:30, cel nadania 04:20–04:45, granica 05:20, zamknięcie bramki 05:50. UID zachowano; dodano `SEQUENCE`, aby aktualizacje tego samego dnia miały kolejną rewizję.
- Harmonogram uwzględnia bufory, prowiant, pogodę, kolejność rezygnacji, świadomy dodatek Moutti i właściwy start Artemis wraz z dodatkowym dojściem z Troodos Square. Alternatywy audytu są dodatkami lub zamiennikami wskazanych punktów; wariant Varosha + Cape Greco jest odradzany.
- Dodano źródłowe punkty hotelu, wejścia do parku, Artemis i pozostałych brakujących cypryjskich punktów bazowej osi dni. Łącznie mapa ma 31 z 50 miejsc; wejście, obiekt, parking i start szlaku mają jawny kontekst. Nie dopisano nieznanych współrzędnych alternatyw.
- Poprawiono wszystkie wskazane przypisania/podpisy galerii. Obejrzano i przypisano pięć nowych fotografii: terminal PFO, zatoka Pissouri, rekonstrukcje domów i schody Choirokoitii, droga przy punkcie obserwacyjnym Vouni. Alykes i wieś Choirokoitia mają osobne zestawy. Galeria: 142 fotografie, 1479 wskazanych wariantów. Nowych wiarygodnych zdjęć samej trasy Pouziaris nie znaleziono; zachowano uczciwy opis rejonu startu.
- Lightbox wybiera dostępny obraz z cache i ma fallback JPEG. Stan „Plan zapisany offline” wymaga kompletnego zapisu bieżącej wersji. Duże zdjęcia pobiera się opcjonalnie. Zapis podstawowy obejmuje oba PDF-y i ICS; mapy podkładowe oraz zewnętrzne strony pozostają poza nim.
- Każdy dzień zaczyna się od programu, wyjścia, nawigacji, decyzji pogodowej i kolejności rezygnacji. Scenariusze, warianty i szczegółowe źródła są rozwijane. Usunięto powielane karty auta i poprawiono zawijanie tekstu oraz nawigacji przy 200%.
- Przebudowano HTML, ICS, pełny PDF i nowy skrót. Dane rezerwacji w generatorach pochodzą z JSON-a. Pakowanie sprawdza metrykę SHA-256 HTML/PDF w `data/exports.json`. Zaktualizowano README, dokumentację i konfigurację adresów.

## Rzeczywiście wykonane kontrole

| Kontrola | Wynik |
|---|---|
| `npm run build` | Poprawny build i pakowanie `dist/` |
| `npm run test:data` | JSON zgodny z osadzeniem HTML; 67 unikalnych zdarzeń w ośmiu ICS, poprawne strefy i końce zdarzeń; rezerwacje, mapa i manifest/cache zdjęć zgodne |
| Zachowanie wcześniejszych UID | Wszystkie 56 UID wcześniejszego kalendarza całego wyjazdu zachowane; cztery nowe wpisy |
| `npm test` | Wszystkie 10 grup testów przeglądarki przeszło; wyniki w `VERIFICATION-2026-11-06.json` |
| Czas i wznowienie | Przejście wydarzeń, powrót do karty, `pageshow`, północ; UTC, Warszawa, Nikozja, Los Angeles; zachowanie fokusu, sekcji i checklist |
| Układ | 360, 390, 768 i 1440 px, zwykły tekst i 200%, również otwarte menu; bez poszerzania dokumentu i obcięcia badanego tekstu „Dziś” |
| Dostępność | axe WCAG 2.2 AA: 0 naruszeń przy 390 i 1440 px; klawiatura lightboxa i powrót fokusu |
| Offline | Pierwszy zapis; celowy błąd instalacji i ponowienie; wykrycie brakującego pliku i naprawa; wcześniej nieotwarte powiększenia; oba PDF-y i ICS; duże zdjęcia; aktualizacja cache bez utraty checklist |
| Bez JavaScriptu / druk | Podstawowy plan i rezerwacje dostępne; siedem dni otwartych; druk otwiera szczegóły i przywraca wcześniejszy stan |
| PDF | Skrót 14 stron, pełny 108; sprawdzono wersję, dane rezerwacji i godziny powrotu w wyeksportowanym tekście |
| Powtarzalność | Ponowny build dał identyczne SHA-256 14 generowanych plików HTML/CSS/JS/SW/ICS/credits |

Nie testowano fizycznego iPhone’a ani importu do Apple/Google Calendar. Brak GPX, nieznane sumy podejść, część kosztów i usług nadal wywołują uzasadnione ostrzeżenia builda. Zdjęcia historyczne mają rzeczywiste daty; nie podwyższano sztucznie wskaźnika świeżości.

## Gotowe materiały

- [Strona](index.html), [kalendarze](cal/cypr2026-caly-wyjazd.ics), [podręczny PDF — 14 stron](cypr2026-handbook.pdf), [pełny PDF — 108 stron](cypr2026-print.pdf).
- `dist/` oraz `cypr2026-pages.zip`: lokalny komplet publiczny. Przed publikacją oba hostingi wymagają rzeczywistego wyrównania. Canonical materiałów: `https://kjawo.github.io/cypr2026/`; Cloudflare jest mirrorem.
- Wyniki i zrzuty przeglądarki: `%LOCALAPPDATA%/Temp/cypr2026-tests-qGASET/`; kopia wyników JSON jest obok tego raportu.
- SHA-256 danych planu: `28302c7f09fa3a6f5b450d2cbeaaf43db9b8b3a8497d160dd40fc26fd88a90ea`.

## Nadal do rzeczywistego potwierdzenia

- **Petsas:** akceptacja przybycia po 10:30 przy lądowaniu 10:10, karencja/no-show i numer lotu; sektor zwrotu 03:30, klucze, transfer i koniec odpowiedzialności. Ponadto końcowa płatność, depozyt wraz z paliwem, udział własny, SCDW przy najmie krótszym niż siedem dni, pakiet szyb/opon/podwozia, drugi kierowca i assistance. Północ tylko po osobnym pisemnym uzgodnieniu zgody i ochrony.
- **Hotel / voucher:** wyżywienie, bagaż przed pokojem, nocne oddanie kluczy oraz dostęp do auta/bramy przed 02:40. Wellness i jedzenie na drogę, jeśli będą potrzebne.
- **Podróżni:** transport do WMI i powrót z WAW, w tym ewentualne odzyskanie auta spod innego lotniska.
- **Publikacja:** wyrównanie GitHub Pages i Cloudflare oraz kontrola działających wersji po publikacji.

Nie kontaktowano się z usługodawcami i nie zamykano tych spraw na podstawie samej zmiany strony.
