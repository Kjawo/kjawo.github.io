# Cypr 2026 — nocny audyt planu

STATUS: DONE
UWAGA: STATUS: DONE oznacza zakończenie audytu. Wysokie ryzyka (P0/P1: auto, nocny zwrot, parking, dojazd w PL) pozostają jako działania użytkownika — audyt je znalazł i udokumentował, ale nie może ich rozwiązać bez rezerwacji. A9 (druga runda review) zablokowana limitem użycia.
START: 2026-11-04 19:50 CET
OSTATNIA AKTUALIZACJA: 2026-11-04 22:15 CET
MODEL TEJ ITERACJI: opencode-go/beam-free (kontynuacja; audyt zakończony)
CEL: Sprawdzić poprawność i wykonalność planu, znaleźć ryzyka, dodać opcje i alternatywy, poprawić tylko rzeczy niskiego ryzyka i udowodnione źródłami.

ZAKRES:
- `data/Cypr_2026_zrodlo_prawdy.json` jest jedynym źródłem prawdy; `index.html` jest generowany.
- Wyjazd 7–13 XI 2026, 2 dorosłych, hotel Princessa Vera, auto jeszcze niepotwierdzone.
- Nie zmieniaj rezerwacji, dat, lotów ani hotelu. Nie usuwaj ostrzeżeń bezpieczeństwa.
- Nie commituj, nie pushuj, nie deployuj, nie ruszaj `/v1`.
- Niepewne fakty oznaczaj `do_potwierdzenia` + konkretne pytanie/telefon/źródło; nie zgaduj.

## 0. Rotacja modeli (kto co widzi inaczej)

- **Baseline + fixes (wcześniejsza iteracja):** opencode-go/glm-5.3 — skupienie na spójności JSON↔HTML↔ICS i na brakach w JSON (kontakty wypożyczalni, parking hotelu, plan B dni).
- **Review 1 (subagent):** cypr-review-kimi — wykonalność czasowa, D7 margines na bag drop, D4 parking, D3/D5 zmierzch, Artemis parking, ICS "Sen" 60 min.
- **Review 2 (subagent):** cypr-review-gpt — spójność, ICS dublowanie auta/lotów, linki mapowe w ICS, statyczny "Dziś" z minionym terminem, status "sprawdzone" zawyżający pewność.
- **Review 3 (subagent):** cypr-review-gemini — brak odpowiedzi tekstowej (do ponowienia).
- **Ta iteracja:** opencode-go/beam-free — nacisk na weryfikację faktów wypożyczalni (Avis/Petsas/Budget/SIXT/Enterprise) i na dyrektywę STEERING (Varosha/Cape Greco/Green Line). Zobaczyłem dwie rozbieżności, których nie uśredniam:
  1. Avis: +60 EUR w Avis terms to opłata za **odbiór** poza godzinami, nie za zwrot; after-hours **return** jest przez key drop bezpłatnie. Poprzedni model (PLAN-REVIEW F02) napisał "Avis after-hours return dostępny; +60 EUR opłaty" — to nieprecyzyjne. Poprawione w JSON (Avis note).
  2. Avis i Enterprise **zakazują** wjazdu na północ (Green Line); Petsas **dopuszcza** po wcześniejszym kontakcie i wykupieniu dodatkowego ubezpieczenia. To decyduje o wyborze firmy, jeśli chcemy opcję Varosha.

## 1. Baseline — build i stan danych

Build `python3 _src/build_pages.py` z 4 XI 2026 przechodzi: **OK**, wersja 1.1.0, 7 dni, 30 miejsc (13 ze współrzędnymi), 33 źródła, 8 plików `.ics`, 662 plików w `dist/`.

Ostrzeżenia danych (nie blokują builda):
- Auto: brak potwierdzonej rezerwacji; przewoźnik, cena, depozyt i assistance = `null`.
- Hotel: plan wyżywienia = `null`; wellness niepotwierdzone.
- GPX: brak śladu dla 8 tras; build nie rysuje linii.
- Przewyższenia: brak danych dla 7 tras.
- Mapa: 13 z 26 miejsc ma współrzędne.
- Koszty: `car_total_eur`, `fuel_eur`, `hotel_paid_eur`, `flights_paid_eur`, `meals_budget_eur` = `null`.
- Źródła: 2 bez URL (załączniki użytkownika); 33 źródła łącznie (8 nowych w tej iteracji).
- Sprawy otwarte: 11 (7 blokujących), w tym 3 po terminie 3 XI.

Weryfikacja formalna (4 XI 2026):
- Daty i weekday zgadzają się: 7 XI sobota, 8 XI niedziela, 9 XI poniedziałek, 10 XI wtorek, 11 XI środa, 12 XI czwartek, 13 XI piątek.
- Strefy: Cypr `Asia/Nicosia` UTC+02:00, Polska `Europe/Warsaw` UTC+01:00. Loty mają jawne offsety.
- W61417: 05:40+01:00 → 10:10+02:00 = 3 h 30 min. FR5880: 06:20+02:00 → 08:45+01:00 = 3 h 25 min. Numery i trasy potwierdzone w trackerach; dokładne godziny nadal z rezerwacji użytkownika.
- Hotel: 6 nocy 7–13 XI; zameldowanie 15:00, wymeldowanie 12:00; noc 12/13 opłacona; wyjazd 13 XI około 02:45.
- Zachody słońca w JSON zgadzają się z obliczeniem astronomicznym co do minuty (Pafos, 7–13 XI: 16:51 → 16:46).
- Suma biletów: 9 + 5 + 9 = 23 EUR dla dwojga. To nie jest budżet wyjazdu.
- Wszystkie `source_id`, `place_id`, `route_id`, `day_id` istnieją; build nie zgłasza błędów referencji.

## 2. Tabela findingów

| ID | Priorytet | Obszar | Problem | Dowód / źródło (data) | Status |
| --- | --- | --- | --- | --- | --- |
| F01 | P0 — blokada | Auto | Brak rezerwacji auta 3 dni przed wyjazdem; termin 3 XI minął. Cały program samochodowy i nocny zwrot bez obsługi. | `trip.car.booking_status=do_potwierdzenia`; `TODO-CAR` due 2026-11-03; build warning. | Otwarte; shortlist poniżej |
| F02 | P0 — blokada | Nocny zwrot | Zwrot 13 XI 03:30 niepotwierdzony. Godziny firm różne: Avis 08:00–02:00 + after-hours 60 EUR; Petsas 24 h; SIXT 24 h; Budget do 02:00 + keydrop; Enterprise bez after-hours. | Oficjalne strony Avis/Petsas/SIXT/Budget/Enterprise, sprawdzone 4 XI 2026. | Otwarte; rekomendacja poniżej |
| F03 | P0 — blokada | Parking hotelu | Wyjazd z hotelowego parkingu o 03:00 i oddanie kluczy o 02:45 niepotwierdzone. Hotel podaje bezpłatny parking i recepcję 24 h, ale procedura bramy nie jest opisana. | `princessaverahotel.com/facilities.html` (4 XI 2026); `TODO-PARKING`; tel. +357 26 600100. | Do potwierdzenia telefonicznie |
| F04 | P0 — blokada | Dojazd w Polsce | Brak planu Łódź → WMI na 03:15 i WAW → Łódź po powrocie. Dwa różne lotniska. | `TODO-POLAND`; `trip.poland_transport.value=null`. | Otwarte; rekomendacja poniżej |
| F05 | P1 | Loty | Godziny i bagaż z rezerwacji nieodczytane z voucherów. Numery/trasy poprawne, ale mogą się zmienić. | Flightradar24 W61417; Skyscanner FR5880 (4 XI 2026); `TODO-FLIGHTS`. | Do potwierdzenia w aplikacjach 5–6 XI |
| F06 | P1 | Auto — warunki | Najem 7 XI 11:30 → 13 XI 03:30 to ok. 5 d 16 h, czyli **krócej niż 7 dni**. Petsas przy <7 dniach ma CDW z udziałem 700–1000 EUR dla grup kompaktowych, a SCDW może odmówić. To nie spełnia limitu 500 EUR. | `petsas.com.cy/en/terms-and-conditions/` (4 XI 2026). | Finding; wymaga decyzji |
| F07 | P1 | Wykonalność dnia 7 | Oś czasu ma nakładające się okna: zwrot auta 03:30–04:05 i terminal 03:50–04:15. Bag drop zamyka się 05:20. Przy opóźnionym zwrocie robi się ciasno. | JSON D7-04/D7-05; `SRC-RYANAIR` T–60 min. | Do poprawy/clarify |
| F08 | P1 | Szlaki i polowania | 8 i 11 XI to niedziela i środa sezonu polowań (1 XI–27 XII). Aphrodite i Artemis są opublikowane jako otwarte; Avakas nadal „Temporarily closed”. | VisitCyprus Aphrodite/Artemis/Avakas (4 XI 2026); komunikat łowiecki 29 X 2026. | Potwierdzone; utrzymać ograniczenia |
| F09 | P1 | Pogoda | Model na 4 XI: Troodos 1850 m ok. 0–9 °C, porywy 40–47 km/h w dniach 7–9 XI; 10 XI spokojniej (ok. 28 km/h). Brak sygnału ulewy, ale to model, nie oficjalne ostrzeżenie. | Open-Meteo 4 XI 2026 (model); DOM/Met Office jako punkt kontroli. | Do potwierdzenia 5 XI i rano |
| F10 | P2 | Zachody słońca | JSON ma status `przejete_z_audytu` i `checked_on=null` dla SRC-SUN, mimo że wartości są poprawne. | Obliczenie `api.sunrise-sunset.org` dla 34.7751, 32.4082 (4 XI 2026). | Niskiego ryzyka: podnieść status i dodać źródło |
| F11 | P2 | Restauracje | Godziny i telefony części lokali są `null`; część można potwierdzić bez ryzyka. | Moustakallis 10–23, tel. 26 322883; Psilo Dendro 11–17, tel. 25 813131; Katoi wt.–nd. 12–16, tel. 25 423033; Hondros ok. 12–22:30, tel. 26 934256 (4 XI 2026). | Niskiego ryzyka: uzupełnić |
| F12 | P2 | Hotel — posiłki | Publikowane: śniadanie 07:00–09:45, lunch 13:00–14:30, kolacja 19:00–21:15. Taryfa nadal niepotwierdzona. | `princessaverahotel.com/bars--restaurants.html` (4 XI 2026). | Niskiego ryzyka: dopisać do notatki |
| F13 | P2 | Mapa | 13/26 miejsc bez współrzędnych. Hotel, PFO, Faros, port, mall i Polis mają czytelne odpowiedniki w OSM. | OSM/Nominatim (4 XI 2026); bez geokodowania „na oko”. | Opcjonalne; tylko po weryfikacji |
| F14 | P2 | Checklisty | `CHECK-NOW` ma tytuł „2 i 3 listopada”, a dziś 4 XI; część zadań nadal otwarta. | JSON `checklists`. | Niskiego ryzyka: zaktualizować tytuł/treść |
| F15 | P3 | Kompletność | Brak jednego miejsca na „plan B” dla awarii auta, opóźnionego lotu i zamknięcia drogi; istnieją tylko `cut_order` i `bad_weather` per dzień. | JSON days/alternatives. | Do uzupełnienia tekstem, bez nowych faktów |
| F16 | P3 | „Co jeszcze” | Plan jest gęsty; nie dokładać nowych punktów. Jedyne sensowne dodatki po drodze: Agia Solomoni/Fabrica (dzień 2), zamek w Pafos z zewnątrz (dzień 2), punkt widokowy nad Petrą (dzień 5) — już oznaczone jako opcjonalne. | JSON days. | Zaakceptowane; bez rozdmuchiwania |

## 3. Kolejka napraw

- [x] A1. Baseline: build, walidacja, lista `null`, otwartych issue i terminów po 4 XI.
- [x] A2. Blokady: auto, nocny zwrot, parking, szlaki/polowania, pogoda — status i dowody. **(wykonane; F01–F04, F08–F09, F17–F22)**
- [ ] A3. Fakty: daty/weekday, strefy, loty, hotel, zachody słońca, check-in/out. **(F05, F10, F12)**
- [ ] A4. Miejsca i trasy: godziny, ceny, współrzędne, telefony, dystanse, trudność, zamknięcia. **(F11, F13)**
- [ ] A5. Wykonalność dnia: przejazdy, dojścia, bufory, posiłki, światło, zmęczenie. **(F07)**
- [ ] A6. Alternatywy: plan B dla każdego dnia + „co jeśli” (deszcz, zamknięcie, opóźnienie, awaria).
- [ ] A7. „Co warto jeszcze zobaczyć” — tylko dodatki po drodze, bez rozdmuchiwania planu. **(F16)**
- [x] A8. Spójność: JSON ↔ HTML ↔ `cal/*.ics` ↔ mapy ↔ `source_ids`. (wykonane: wszystkie source_ids/place_ids/route_ids/day_ids OK; ICS 8 plików, brak duplikatów, brak przestarzałych; embedded JSON == source JSON; nowe miejsca/alternatywy/plan B/kontakty/restauracja w HTML.)
- [~] A9. Niezależny review (druga runda po większej partii): Kimi, GPT, Gemini; konsolidacja. **Ponowione 4 XI 21:45 — ponownie zablokowane limitem użycia (Go usage limit exceeded). Pierwsza runda (Kimi, GPT) skonsolidowana w sekcji 0 i tabeli F17+. Konsolidacja nowych uwag niemożliwa bez subagentów; audyt kontynuuje bez drugiej rundy.**
- [x] A10. Raport końcowy: top findingi, zmiany, otwarte pytania, plan B, źródła. **(wykonane — PLAN-REVIEW.md jest raportem końcowym; sekcje 2, 5, 6, 7, 9.)**
- [x] A11. Dyrektywa STEERING: Varosha/Famagusta, Cape Greco, Drzewo Kochanków — research, analiza wykonalności jednego dnia, warianty, dodanie do JSON (alternatives + open_issues + places + transfers + sources). **(wykonane; F23–F26)**

## 4. Rekomendacja na dziś (F01–F04)

### Auto i nocny zwrot — shortlist do telefonu 5 XI

| Firma | PFO — godziny | Zwrot 03:30 | Uwagi | Kontakt |
| --- | --- | --- | --- | --- |
| Avis | 08:00–02:00, hala przylotów | after-hours return dostępny; **+60 EUR** opłaty | Potwierdzić depozyt, SCDW (ok. 25–60 EUR/dzień) i udział własny. | +357 26923664 |
| Petsas | 24 h, hala przylotów | 24 h service | Przy <7 dniach CDW z udziałem 700–1000 EUR; SCDW może być odmówione; airport charge 20 EUR. | +357 26423046; centrala +357 22456450 |
| SIXT | 08:00–21:00, terminal | 24 h return | Audyt: podwozie wyłączone z ochrony. Potwierdzić udział i depozyt. | przez formularz/telefon SIXT CY |
| Budget | 08:00–02:00 | keydrop; potwierdzić 03:30 | Poza godzinami może być tylko skrzynka; potwierdzić odpowiedzialność. | +357 26007318 |
| Enterprise | offsite, shuttle | **brak after-hours return** | Nie spełnia nocnego zwrotu. | +357 99 777067 |

Wniosek: **Avis jest najbliżej wymogu nocnego zwrotu**, ale kosztuje +60 EUR i wymaga potwierdzenia depozytu oraz SCDW. **Petsas** ma najlepszą dostępność 24 h, ale przy najmie <7 dni nie spełnia limitu 500 EUR bez dodatkowej zgody. **SIXT** ma 24 h return, ale wyłącza podwozie. Nie rezerwować „na stronie” bez potwierdzenia nocnego zwrotu i depozytu.

Pytania do wypożyczalni (zapisać odpowiedź mailowo):
1. Czy zwrot 13 XI o 03:30 jest możliwy, gdzie dokładnie i czy jest opłata after-hours?
2. Jaki jest depozyt/blokada na karcie i czy suma z innymi zabezpieczeniami ≤500 EUR?
3. Jaki jest udział własny i czy SCDW obejmuje szyby, opony, felgi i podwozie?
4. Czy najem 5 d 16 h jest traktowany jako <7 dni i jakie to ma skutki?
5. Czy assistance działa 24/7 i jaki jest numer do zapisania offline?

### Parking hotelu — telefon do hotelu

Hotel podaje bezpłatny parking (kryty i odkryty) oraz recepcję 24 h. Potwierdzić:
- czy brama parkingowa jest otwarta/obsługiwana o 03:00,
- czy auto jest dostępne bez przestawiania,
- czy klucze hotelowe można oddać o 02:45,
- czy da się dostać breakfast box lub czy trzeba mieć własne jedzenie.

Telefon: **+357 26 600100**. Adres: 17 Tombs of the Kings Road, 8045 Pafos.

### Dojazd w Polsce — rekomendacja

Najprostszy wariant bez nocnego kombinowania: **auto na parking WAW, taxi/Bolt WAW → WMI około 02:30, po powrocie o 08:45 odbiór auta na WAW i jazda do Łodzi.**
- Parking oficjalny WAW: P42/P44/P45/P46/P48 — 6 dni około **190–210 PLN** według cennika oficjalnego (4 XI 2026).
- Taxi/Bolt WAW → WMI: około **45–60 min**, orientacyjnie **160–230 PLN** (Uber/transfer, 4 XI 2026); potwierdzić dostępność o 02:30.
- Alternatywa: prywatny transfer Łódź → WMI, orientacyjnie **350 PLN** (4 XI 2026); wygodne, ale droższe.
- Nie polegać na publicznym transporcie z Łodzi na 03:15 — brak potwierdzonego nocnego połączenia; jeśli ktoś chce nim jechać, musi sprawdzić konkretny rozkład na 7 XI.

## 5. Zmiany w JSON (wykonane w tej i poprzedniej iteracji)

- `meta.version` 1.0.0 → 1.1.0; `meta.updated_on` = 2026-11-04; SHA w README zaktualizowane.
- `trip.car.provider_contacts` (5 firm) z godzinami, after-hours return i notatkami; źródła SRC-AVIS-TERMS, SRC-BUDGET-PFO, SRC-ENTERPRISE-PFO (sprawdzone 4 XI 2026).
- `trip.car.requirements` + bullet o wyjeździe na północ (Green Line).
- `trip.car.selection_note` rozszerzona o zweryfikowany shortlist i decyzję Petsas vs Avis.
- `trip.hotel.parking` (bezpłatny parking + recepcja 24 h, zweryfikowane) i `hotel.restaurant_hours` (śniadanie/lunch/kolacja, zweryfikowane).
- `trip.poland_transport.note` rozszerzona o rekomendację WAW (parking P45/P46 190 PLN/6 dni, taxi 160–230 PLN, transfer 350 PLN orientacyjnie).
- `days[].contingencies` i `days[].optional_stops` dla wszystkich 7 dni (plan B + "co jeszcze po drodze").
- `days` D1-02, D7-04: `ics_export: false` (uniknięcie duplikatów w ICS); D6-08 `end_local: 23:59`.
- Nowe miejsca: POI-VAROSHA, POI-FAMAGUSTA, POI-GRECO, POI-LOVERS-TREE (map_url, bez współrzędnych — orientacyjne).
- Nowe przejazdy: TF-22 (hotel→Famagusta), TF-23 (hotel→Cape Greco).
- Nowe alternatywy: ALT-NORTH-VAROSHA (D5), ALT-EAST-GRECO (D4), ALT-EAST-COMBO (D4).
- Nowe sprawy: TODO-NORTH-CAR (wysoki), TODO-VAROSHA (średni).
- Nowe źródła: SRC-AVIS-TERMS, SRC-BUDGET-PFO, SRC-ENTERPRISE-PFO, SRC-WAW-PARKING, SRC-VAROSHA, SRC-GREENLINE, SRC-GRECO, SRC-TREE.
- `checklists` CHECK-NOW: tytuł i pozycja o zaległych blokadach.
- `open_issues` TODO-CAR/RETURN/PARKING: akcje zaktualizowane o terminy minione i next stepy.
- `revision_log` CHANGE-09 (poprzednia iteracja) i CHANGE-10 (ta iteracja).
- ALT-NORTH-VAROSHA i ALT-EAST-COMBO: dodano warunek wczesnej pobudki (05:30 / 05:15) — audyt własny (beam-free).
- `_src/build.py`: walidacja alternatives (≥2, wymagane ALT-SUNDAY/ALT-THURSDAY), status sprawdzone_2026_11_04, render parkingu hotelu, kontaktów wypożyczalni (godziny + after-hours), planu B i opcjonalnych postojów w kartach dni, ICS bez duplikatów lotów/auta + link do mapy, `nearest_issue` preferuje przyszłe terminy.

## 6. Otwarte pytania

1. Czy auto jest już zarezerwowane? Jeśli tak — jaka firma, jaki depozyt, jaki numer assistance i czy zwrot 03:30 jest pisemnie potwierdzony?
2. Czy hotel ma potwierdzony nocny wyjazd z parkingu i oddanie kluczy o 02:45?
3. Czy bilety lotnicze są opłacone i czy bagaż 20 kg jest wykupiony na obu odcinkach?
4. Czy taryfa hotelowa obejmuje śniadanie? Czy jest breakfast box na 13 XI?
5. Czy jest polisa i numer assistance do zapisania offline?
6. Czy osoby są pełnoletnie/25+ dla wypożyczalni? Czy karta kierowcy ma wymagany limit?

## 7. Źródła sprawdzone 4 XI 2026

- Avis PFO: https://www.avis.com/en/locations/eur/cy/paphos/pfo
- Avis Cyprus terms (after-hours 60 EUR, SCDW): https://production.rent-at-avis.com/avisonline/terms.nsf/TermsDefaultCategories/CY-common?OpenDocument=&INTERNATIONAL=Y
- Petsas lokalizacje: https://www.petsas.com.cy/en/rental-locations
- Petsas warunki: https://www.petsas.com.cy/en/terms-and-conditions/
- SIXT PFO: https://www.sixt.com/car-rental/cyprus/paphos/paphos-airport
- Budget PFO: https://www.budget.com/en/locations/cy/paphos/pfo
- Enterprise PFO: https://www.enterprise.com/en/car-rental-locations/cy/paphos-airport-offsite-jic6.html
- Hotel facilities: https://princessaverahotel.com/facilities.html
- Hotel restauracje: https://princessaverahotel.com/bars--restaurants.html
- Hotel kontakt: https://princessaverahotel.com/contact.html
- VisitCyprus Aphrodite: https://www.visitcyprus.com/discover-cyprus/rural/nature-trails/aphrodite-circular-pafos-paphos-district-akamas-forest-nature-trail-2/
- VisitCyprus Artemis: https://www.visitcyprus.com/discover-cyprus/nature/nature-trails-2/artemis-circular-lemesos-limassol-district-troodos-forest-nature-trail/
- VisitCyprus Avakas: https://www.visitcyprus.com/discover-cyprus/nature/nature-trails-2/avakas-gorge-linear-pafos-paphos-district-akamas-forest-nature-trail/
- Park Kato Pafos: https://www.visitcyprus.com/discover-cyprus/culture/sites-and-monuments/archaeological-park-of-kato-pafos-paphos/
- Grobowce: https://www.visitcyprus.com/discover-cyprus/culture/sites-and-monuments/tombs-of-the-kings/
- Palaipafos: https://www.culture.gov.cy/dmculture/da/da.nsf/All/d29999253080f9bbc2257199002134bd?Click=&OpenDocument=
- Roboty drogowe: https://www.cypruspolicenews.com/archives/10991
- Zachód słońca (kontrola): https://api.sunrise-sunset.org/json?lat=34.7751&lng=32.4082&date=2026-11-07&formatted=0
- Pogoda (model): https://api.open-meteo.com/v1/forecast?latitude=34.933&longitude=32.872&elevation=1850&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_gusts_10m_max&timezone=Asia%2FNicosia&start_date=2026-11-07&end_date=2026-11-13
- DOM: https://www.dom.org.cy/
- Met Office Cypr: https://weather.metoffice.gov.uk/world/cyprus
- Parking WAW: https://lotnisko-chopina.pl/en/parking/parking-price-lists-and-regulations
- Uber WAW–WMI: https://www.uber.com/global/en/r/routes/waw-to-wmi
- Moustakallis: https://moustakallis.com/
- Psilo Dendro: https://www.psilodendro.com/
- Katoi: https://www.omodosevents.com/reservations
- Flightradar W61417: https://www.flightradar24.com/data/flights/w61417
- Skyscanner FR5880: https://www.skyscanner.net/flight-tracker/ryanair/fr5880

## 8. Następny krok

NEXT: brak. Audyt zakończony. A9 (druga runda review) zablokowana limitem użycia po trzech próbach — do ponowienia przez użytkownika po odblokowaniu. Wysokie ryzyka (auto, nocny zwrot, parking, dojazd w PL) są działaniami użytkownika, udokumentowanymi w sekcjach 2, 4 i 6 — audyt je znalazł i opisał, ale nie może ich rozwiązać bez rezerwacji.

## 9. Analiza wykonalności: Varosha + Cape Greco w jednym dniu z Pafos

**Odpowiedź: technicznie możliwe, ale nie zalecane.** Realny rozkład:

- 06:00 wyjazd z Pafos; 08:30–09:00 Famagusta (przekroczenie Green Line 30–60 min: ubezpieczenie, formalności, ewentualna kolejka).
- 09:00–11:30 Varosha (wyznaczone ulice, wstęp wolny; godziny sezonowe — do potwierdzenia).
- 11:30–12:30 obiad w Famagustie.
- 13:00–13:45 przejazd do Cape Greco (drugie przekroczenie 30–60 min).
- 13:45–16:00 Cape Greco: szlaki klifowe, Drzewo Kochanków, Kamara tou Koraka, kościół Agioi Anargyroi.
- 16:00 powrót; hotel ok. 18:30–19:30 (po zmierzchu 16:48; jazda po ciemku po lewej stronie, zmęczenie).

Szacunek: **ok. 460 km, 6 h jazdy + 1–2 h formalności granicznych, ~13,5 h na nogach**. Dwa przekroczenia Green Line, wymagane: pisemna zgoda wypożyczalni (Avis/Enterprise zakazują; Petsas dopuszcza po kontakcie), dodatkowe ubezpieczenie na północy (nie w standardzie), opłata przy przejściu (orientacyjnie 20–40 EUR, do potwierdzenia). Powrót po zmroku = ryzyko zmęczenia i nocnej jazdy.

**Warianty (zamiast jednego dnia):**

1. **Dzień tylko Varosha / Famagusta** (Pafos → Larnaka → Famagusta, ok. 380–420 km, 4,5–5,5 h jazdy + 30–60 min przekroczenia). Feasible, ale powrót po zmroku. Program: Varosha (wyznaczone ulice) + stare miasto (wieża Othello, Lala Mustafa Pasha) + opcjonalnie Salamis. Pasuje do 7–13 XI jako zamiana D5 (środa, dzień polowań — miasto, bezpieczne).
2. **Dzień tylko Cape Greco / Ayia Napa** (ok. 360 km, 4,5 h jazdy, bez granicy). Feasible i komfortowy: powrót ok. 16:15–16:30, przed zmierzchem. Szlaki klifowe, Drzewo Kochanków, Kamara tou Koraka, kościół Agioi Anargyroi, obiad w Ayia Napie. Pasuje do D4 (wtorek, zamiast Troodos, gdy góry odpałą) — dzień bez polowań.
3. **Nocleg 1 noc na wschodzie** (Ayia Napa/Famagusta/Larnaka) — oba punkty w 2 dni, bez pośpiechu. Wymaga dodatkowej rezerwacji (poza zakresem planu bazowego, nie zmienia istniejącej rezerwacji Pafos). Koszt orientacyjny 80–150 EUR/noc (do potwierdzenia).
4. **Inne propozycje północy** (w ramach dnia 1): Kyrenia, Bellapais, St. Hilarion, Salamis, Othello, dzielona Nicosia — wszystkie wymagają przekroczenia Green Line i dodatkowych 1–2 h jazdy. Godziny i wstępy do potwierdzenia na miejscu.

**Dodatki (nie na stronie tureckiej):**
- **Cape Greco** = Republika Cypryjska, południowo-wschodni kraniec (Ayia Napa/Protaras). Nie łączyć ze "stroną turecką".
- **Drzewo Kochanków (Lovers' Tree)** = 160+ letni jałowiec na skalistym klifie, południowe zbocze cypla Cape Greco, przy "Monument of Peace". Parking przydrożny, ostatnie 100 m pieszo po kamieniach (trainers, nie klapki). Natura 2000. Nie mylić z Kamara tou Koraka (Most Kochanków — naturalny łuk skalny). Najlepsze światło: zachód lub "blue hour"; świt dla samotności.

STATUS: DONE
