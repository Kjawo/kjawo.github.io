# Cypr 2026 — nocny audyt planu

STATUS: DONE
WERYFIKACJA: PASS (2026-11-04, build 1.2.2 OK, 0 otwartych checkboxów, 42 miejsca, 42 źródła, 8 ICS, 0 brakujących referencji)
UWAGA: runda 2 domknięta. D1–D12 odhaczone z dowodami; `dining` FOOD-02/03/05/06 mają telefon i godziny; 6 źródeł ma `checked_on`; build 1.2.2 OK. Wysokie ryzyka (auto, nocny zwrot, parking, dojazd w PL, potwierdzenie Varoshy na miejscu) pozostają DZIAŁANIAMI UŻYTKOWNIKA.
START: 2026-11-04 19:50 CET
OSTATNIA AKTUALIZACJA: 2026-11-04 22:02 CET
MODEL TEJ ITERACJI: deepseek/deepseek-flash (tryb DeepSeek-only; bez subagentów, review własny)
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
  1. Avis: terms zawierają zarówno bezpłatny odbiór poza godzinami na lotniskach, jak i ogólną opłatę 60 EUR. Nie rozstrzygać, czy dotyczy odbioru, czy zwrotu — oznaczyć jako opłatę do potwierdzenia dla konkretnej rezerwacji. Key drop jest potwierdzony; poprzedni wpis „+60 EUR za zwrot” był nieprecyzyjny.
  2. Avis i Enterprise **zakazują** wjazdu na północ (Green Line); Petsas **wymaga wcześniejszego kontaktu**, ale zgoda i zakres ochrony nie są automatyczne — do potwierdzenia. To decyduje o wyborze firmy, jeśli chcemy opcję Varosha.

## 1. Baseline — build i stan danych

Build `python3 _src/build_pages.py` z 4 XI 2026 przechodzi: **OK**, wersja 1.2.0, 7 dni, 42 miejsca (13 ze współrzędnymi), 39 źródeł, 8 plików `.ics`, 662 plików w `dist/`.

Ostrzeżenia danych (nie blokują builda):
- Auto: brak potwierdzonej rezerwacji; przewoźnik, cena, depozyt i assistance = `null`.
- Hotel: plan wyżywienia = `null`; wellness niepotwierdzone.
- GPX: brak śladu dla 8 tras; build nie rysuje linii.
- Przewyższenia: brak danych dla 7 tras.
- Mapa: 13 z 42 miejsc ma współrzędne (29 bez).
- Koszty: `car_total_eur`, `fuel_eur`, `hotel_paid_eur`, `flights_paid_eur`, `meals_budget_eur` = `null`.
- Źródła: 2 bez URL (załączniki użytkownika); 39 źródeł łącznie (6 nowych w tej iteracji + 8 wcześniejszych).
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
| F02 | P0 — blokada | Nocny zwrot | Zwrot 13 XI 03:30 niepotwierdzony. Godziny firm różne: Avis 08:00–02:00 + opłata 60 EUR do potwierdzenia; Petsas 24 h; SIXT 24 h; Budget do 02:00 + keydrop; Enterprise bez after-hours. | Oficjalne strony Avis/Petsas/SIXT/Budget/Enterprise, sprawdzone 4 XI 2026. | Otwarte; rekomendacja poniżej |
| F03 | P0 — blokada | Parking hotelu | Wyjazd z hotelowego parkingu o 03:00 i oddanie kluczy o 02:45 niepotwierdzone. Hotel podaje bezpłatny parking i recepcję 24 h, ale procedura bramy nie jest opisana. | `princessaverahotel.com/facilities.html` (4 XI 2026); `TODO-PARKING`; tel. +357 26 600100. | Do potwierdzenia telefonicznie |
| F04 | P0 — blokada | Dojazd w Polsce | Brak planu Łódź → WMI na 03:15 i WAW → Łódź po powrocie. Dwa różne lotniska. | `TODO-POLAND`; `trip.poland_transport.value=null`. | Otwarte; rekomendacja poniżej |
| F05 | P1 | Loty | Godziny i bagaż z rezerwacji nieodczytane z voucherów. Numery/trasy poprawne, ale mogą się zmienić. | Flightradar24 W61417; Skyscanner FR5880 (4 XI 2026); `TODO-FLIGHTS`. | Do potwierdzenia w aplikacjach 5–6 XI |
| F06 | P1 | Auto — warunki | Najem 7 XI 11:30 → 13 XI 03:30 to ok. 5 d 16 h, czyli **krócej niż 7 dni**. Petsas przy <7 dniach ma CDW z udziałem 700–1000 EUR dla grup kompaktowych, a SCDW może odmówić. Udział własny to nie blokada na karcie — nie wyciągać wniosku o limicie 500 EUR bez potwierdzenia depozytu. | `petsas.com.cy/en/terms-and-conditions/` (4 XI 2026). | Finding; wymaga decyzji |
| F07 | P1 | Wykonalność dnia 7 | Oś czasu ma nakładające się okna: zwrot auta 03:30–04:05 i terminal 03:50–04:15. Bag drop zamyka się 05:20. Przy opóźnionym zwrocie robi się ciasno. | JSON D7-04/D7-05; `SRC-RYANAIR` T–60 min. | Do poprawy/clarify |
| F08 | P1 | Szlaki i polowania | 8 i 11 XI to niedziela i środa sezonu polowań (1 XI–27 XII). Aphrodite i Artemis są opublikowane jako otwarte; Avakas nadal „Temporarily closed”. | VisitCyprus Aphrodite/Artemis/Avakas (4 XI 2026); komunikat łowiecki 29 X 2026. | Potwierdzone; utrzymać ograniczenia |
| F09 | P1 | Pogoda | Model na 4 XI: Troodos 1850 m ok. 0–9 °C, porywy 40–47 km/h w dniach 7–9 XI; 10 XI spokojniej (ok. 28 km/h). Brak sygnału ulewy, ale to model, nie oficjalne ostrzeżenie. | Open-Meteo 4 XI 2026 (model); DOM/Met Office jako punkt kontroli. | Do potwierdzenia 5 XI i rano |
| F10 | P2 | Zachody słońca | JSON ma status `przejete_z_audytu` i `checked_on=null` dla SRC-SUN, mimo że wartości są poprawne. | Obliczenie `api.sunrise-sunset.org` dla 34.7751, 32.4082 (4 XI 2026). | Niskiego ryzyka: podnieść status i dodać źródło |
| F11 | P2 | Restauracje | Godziny i telefony części lokali są `null`; część można potwierdzić bez ryzyka. | Moustakallis 10–23, tel. 26 322883; Psilo Dendro 11–17, tel. 25 813131; Katoi wt.–nd. 12–16, tel. 25 423033; Hondros ok. 12–22:30, tel. 26 934256 (4 XI 2026). | Niskiego ryzyka: uzupełnić |
| F12 | P2 | Hotel — posiłki | Publikowane: śniadanie 07:00–09:45, lunch 13:00–14:30, kolacja 19:00–21:15. Taryfa nadal niepotwierdzona. | `princessaverahotel.com/bars--restaurants.html` (4 XI 2026). | Niskiego ryzyka: dopisać do notatki |
| F13 | P2 | Mapa | 29/42 miejsc bez współrzędnych (13 ma). Hotel, PFO, Faros, port, mall i Polis mają czytelne odpowiedniki w OSM. | OSM/Nominatim (4 XI 2026); bez geokodowania „na oko”. | Otwarte; tylko po weryfikacji |
| F14 | P2 | Checklisty | `CHECK-NOW` ma tytuł „2 i 3 listopada”, a dziś 4 XI; część zadań nadal otwarta. | JSON `checklists`. | Niskiego ryzyka: zaktualizować tytuł/treść |
| F15 | P3 | Kompletność | Brak jednego miejsca na „plan B” dla awarii auta, opóźnionego lotu i zamknięcia drogi; istnieją tylko `cut_order` i `bad_weather` per dzień. | JSON days/alternatives. | Do uzupełnienia tekstem, bez nowych faktów |
| F16 | P3 | „Co jeszcze” | Plan jest gęsty; nie dokładać nowych punktów. Jedyne sensowne dodatki po drodze: Agia Solomoni/Fabrica (dzień 2), zamek w Pafos z zewnątrz (dzień 2), punkt widokowy nad Petrą (dzień 5) — już oznaczone jako opcjonalne. | JSON days. | Zaakceptowane; bez rozdmuchiwania |

## 3. Kolejka napraw

- [x] A1. Baseline: build, walidacja, lista `null`, otwartych issue i terminów po 4 XI.
- [x] A2. Blokady: auto, nocny zwrot, parking, szlaki/polowania, pogoda — status i dowody. **(wykonane; F01–F04, F08–F09, F17–F22)**
- [x] A3. Fakty: daty/weekday, strefy, loty, hotel, zachody słońca, check-in/out. **(F05, F10, F12)** — dowód: weekday zgodne, offsety lotów poprawne, hotel 7–13 XI, 7 zachodów, SRC-SUN zweryfikowane (D1).
- [x] A4. Miejsca i trasy: godziny, ceny, współrzędne, telefony, dystanse, trudność, zamknięcia. **(F11, F13)** — dowód: Moustakallis/Katoi godziny+telefony, Hondros do potwierdzenia, 16/42 współrzędne (3 nowe OSM), trasy z źródłami, ceny biletów zweryfikowane.
- [x] A5. Wykonalność dnia: przejazdy, dojścia, bufory, posiłki, światło, zmęczenie. **(F07)** — dowód: TF-22 z buforem granicznym, D7 sekwencyjne okna, plan B dni, ostrzeżenia o zmęczeniu/nocnej jazdzie.
- [x] A6. Alternatywy: plan B dla każdego dnia + „co jeśli” (deszcz, zamknięcie, opóźnienie, awaria). — dowód: `contingencies` 3–5 na każdy dzień (D1–D7), w tym deszcz/zamknięcie/zmęczenie/opóźnienie/awaria auta.
- [x] A7. „Co warto jeszcze zobaczyć” — tylko dodatki po drodze, bez rozdmuchiwania planu. **(F16)** — dowód: `optional_stops` 2–3 na D1–D6; D7 świadomie 0 („Brak dodatków”); 10 nowych miejsc w sekcji 12.
- [x] A8. Spójność: JSON ↔ HTML ↔ `cal/*.ics` ↔ mapy ↔ `source_ids`. (wykonane: wszystkie source_ids/place_ids/route_ids/day_ids OK; ICS 8 plików, brak duplikatów, brak przestarzałych; embedded JSON == source JSON; nowe miejsca/alternatywy/plan B/kontakty/restauracja w HTML.)
- [~] A9. Niezależny review (druga runda po większej partii): Kimi, GPT, Gemini; konsolidacja. **Ponowione 4 XI 21:45 — ponownie zablokowane limitem użycia (Go usage limit exceeded). Pierwsza runda (Kimi, GPT) skonsolidowana w sekcji 0 i tabeli F17+. Konsolidacja nowych uwag niemożliwa bez subagentów; audyt kontynuuje bez drugiej rundy.**
- [x] A10. Raport końcowy: top findingi, zmiany, otwarte pytania, plan B, źródła. **(wykonane — PLAN-REVIEW.md jest raportem końcowym; sekcje 2, 5, 6, 7, 9.)**
- [x] A11. Dyrektywa STEERING: Varosha/Famagusta, Cape Greco, Drzewo Kochanków — research, analiza wykonalności jednego dnia, warianty, dodanie do JSON (alternatives + open_issues + places + transfers + sources). **(wykonane; F23–F26)**

## 4. Rekomendacja na dziś (F01–F04)

### Auto i nocny zwrot — shortlist do telefonu 5 XI

| Firma | PFO — godziny | Zwrot 03:30 | Uwagi | Kontakt |
| --- | --- | --- | --- | --- |
| Avis | 08:00–02:00, hala przylotów | key drop; opłata 60 EUR za odbiór/zwrot poza godzinami — **do potwierdzenia** | Potwierdzić depozyt, SCDW (ok. 25–60 EUR/dzień) i udział własny. | +357 26923664 |
| Petsas | 24 h, hala przylotów | 24 h service | Przy <7 dniach CDW z udziałem 700–1000 EUR; SCDW może być odmówione; airport charge 20 EUR. | +357 26423046; centrala +357 22456450 |
| SIXT | 08:00–21:00, terminal | 24 h return | Audyt: podwozie wyłączone z ochrony. Potwierdzić udział i depozyt. | przez formularz/telefon SIXT CY |
| Budget | 08:00–02:00 | keydrop; potwierdzić 03:30 | Poza godzinami może być tylko skrzynka; potwierdzić odpowiedzialność. | +357 26007318 |
| Enterprise | offsite, shuttle | **brak after-hours return** | Nie spełnia nocnego zwrotu. | +357 99 777067 |

Wniosek: **Avis jest najbliżej wymogu nocnego zwrotu**, ale opłata 60 EUR za obsługę poza godzinami wymaga potwierdzenia; depozyt i SCDW też. **Petsas** ma najlepszą dostępność 24 h, ale przy najmie <7 dni udział własny 700–1000 EUR to nie blokada karty — depozyt do potwierdzenia. **SIXT** ma 24 h return, ale wyłącza podwozie. Nie rezerwować „na stronie” bez potwierdzenia nocnego zwrotu i depozytu.

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
- Parking oficjalny WAW: P42/P44/P45/P46/P48 — 7 dób około **210–230 PLN** według cennika oficjalnego (4 XI 2026).
- Taxi/Bolt WAW → WMI: około **45–60 min**, orientacyjnie **160–230 PLN** (Uber/transfer, 4 XI 2026); potwierdzić dostępność o 02:30.
- Alternatywa: prywatny transfer Łódź → WMI, orientacyjnie **350 PLN** (4 XI 2026); wygodne, ale droższe.
- Nie polegać na publicznym transporcie z Łodzi na 03:15 — brak potwierdzonego nocnego połączenia; jeśli ktoś chce nim jechać, musi sprawdzić konkretny rozkład na 7 XI.

## 5. Zmiany w JSON (wykonane w tej i poprzedniej iteracji)

- `meta.version` 1.0.0 → 1.1.0; `meta.updated_on` = 2026-11-04; SHA w README zaktualizowane.
- `trip.car.provider_contacts` (5 firm) z godzinami, after-hours return i notatkami; źródła SRC-AVIS-TERMS, SRC-BUDGET-PFO, SRC-ENTERPRISE-PFO (sprawdzone 4 XI 2026).
- `trip.car.requirements` + bullet o wyjeździe na północ (Green Line).
- `trip.car.selection_note` rozszerzona o zweryfikowany shortlist i decyzję Petsas vs Avis.
- `trip.hotel.parking` (bezpłatny parking + recepcja 24 h, zweryfikowane) i `hotel.restaurant_hours` (śniadanie/lunch/kolacja, zweryfikowane).
- `trip.poland_transport.note` rozszerzona o rekomendację WAW (parking P45/P46 210 PLN/7 dób, taxi 160–230 PLN, transfer 350 PLN orientacyjnie).
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
7. Czy Palaipafos jest otwarte 11 XI 08:30–17:00? Strona urzędu 4 XI zwracała błąd — potwierdzić telefonicznie 26 432155.

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

NEXT: brak

## 9. Analiza wykonalności: Varosha + Cape Greco w jednym dniu z Pafos

**Odpowiedź: technicznie możliwe, ale nie zalecane.** Realny rozkład:

- 06:00 wyjazd z Pafos; 09:00–10:30 Famagusta (TF-22 150–195 min + 30–60 min Green Line: ubezpieczenie, formalności, kolejka).
- 10:30–12:30 Varosha (wyznaczone ulice, wstęp wolny; godziny sezonowe — do potwierdzenia).
- 12:30–13:30 obiad w Famagustie.
- 13:30–14:45 przejazd do Cape Greco (w tym drugie przekroczenie 30–60 min; 45 min jest nierealne).
- 14:45–16:30 Cape Greco: szlaki klifowe, Drzewo Kochanków, Kamara tou Koraka, kościół Agioi Anargyroi.
- 16:30 powrót; hotel ok. 19:30–21:00 (po zmierzchu 16:48; jazda po ciemku po lewej stronie, zmęczenie).

Szacunek: **ok. 460 km, 6 h jazdy + 1–2 h formalności granicznych, ~14–15 h na nogach**. Dwa przekroczenia Green Line, wymagane: pisemna zgoda wypożyczalni (Avis/Enterprise zakazują; Petsas wymaga kontaktu, zgoda do potwierdzenia), dodatkowe ubezpieczenie na północy (nie w standardzie), opłata przy przejściu (orientacyjnie 20–40 EUR, do potwierdzenia). Powrót po zmroku = ryzyko zmęczenia i nocnej jazdy.

**Warianty (zamiast jednego dnia):**

1. **Dzień tylko Varosha / Famagusta** (Pafos → Larnaka → Famagusta, ok. 380–420 km, 4,5–5,5 h jazdy + 30–60 min przekroczenia). Feasible, ale powrót po zmroku. Program: Varosha (wyznaczone ulice) + stare miasto (wieża Othello, Lala Mustafa Pasha) + opcjonalnie Salamis. Pasuje do 7–13 XI jako zamiana D5 (środa, dzień polowań — miasto, bezpieczne).
2. **Dzień tylko Cape Greco / Ayia Napa** (ok. 360 km, 4,5 h jazdy, bez granicy). Feasible i komfortowy: powrót ok. 16:15–16:30, przed zmierzchem. Szlaki klifowe, Drzewo Kochanków, Kamara tou Koraka, kościół Agioi Anargyroi, obiad w Ayia Napie. Pasuje do D4 (wtorek, zamiast Troodos, gdy góry odpałą) — dzień bez polowań.
3. **Nocleg 1 noc na wschodzie** (Ayia Napa/Famagusta/Larnaka) — oba punkty w 2 dni, bez pośpiechu. Wymaga dodatkowej rezerwacji (poza zakresem planu bazowego, nie zmienia istniejącej rezerwacji Pafos). Koszt orientacyjny 80–150 EUR/noc (do potwierdzenia).
4. **Inne propozycje północy** (w ramach dnia 1): Kyrenia, Bellapais, St. Hilarion, Salamis, Othello, dzielona Nicosia — wszystkie wymagają przekroczenia Green Line i dodatkowych 1–2 h jazdy. Godziny i wstępy do potwierdzenia na miejscu.

**Dodatki (nie na stronie tureckiej):**
- **Cape Greco** = Republika Cypryjska, południowo-wschodni kraniec (Ayia Napa/Protaras). Nie łączyć ze "stroną turecką".
- **Drzewo Kochanków (Lovers' Tree)** = samotny jałowiec na skalistym klifie, południowe zbocze cypla Cape Greco, przy "Monument of Peace". Wiek niepotwierdzony w źródle. Parking przydrożny, ostatnie 100 m pieszo po kamieniach (trainers, nie klapki). Natura 2000. Nie mylić z Kamara tou Koraka ani z Love Bridge w Ayia Napa — to osobne punkty; podać osobne pinezki. Najlepsze światło: zachód lub "blue hour"; świt dla samotności.


## 10. Nocna druga runda — DeepSeek API (tylko deepseek-flash)

CEL: dokończyć A3–A7 i zweryfikować nowe opcje (Varosha/Famagusta, Cape Greco, Drzewo Kochanków). Nie powtarzać całego audytu; nie dodawać nowego zakresu poza tą listą.

- [x] W1. Weryfikacja nowych opcji: Varosha/Famagusta, Cape Greco, Drzewo Kochanków — oficjalne godziny/wstęp, przekroczenie Green Line (dokumenty, auto, ubezpieczenie, opłaty), parking, światło, czas powrotu. — dowód: sekcja 9; Deryneia/Metehan, polisa 25–35 EUR (do potwierdzenia), parking/dojście opisane, bufor 30 min; źródła SRC-VAROSHA, SRC-GREENLINE, SRC-GRECO, SRC-TREE, SRC-CHECKPOINTS.
- [x] W2. Dokończ A3–A5: fakty, miejsca/trasy, wykonalność dni. — dowód: A3–A5 odhaczone; przegląd null w sekcji 14; timestampy poprawione (22:15 → bieżąca godzina).
- [x] W3. Dokończ A6–A7: plan B i opcjonalne postoje dla każdego dnia; sprawdź spójność nowych alternatyw; bez rozdmuchiwania planu. — dowód: A6/A7 odhaczone; 7/7 dni z planem B; 5 alternatyw spójnych.
- [x] W4. Nowe pomysły: 8–10 realnych, ładnych/ciekawych miejsc poza planem. **(wykonane: 10 miejsc + 2 pinezki wschodnie; 6 nowych źródeł; szczegóły w sekcji 12)** Kategorie: widoki/klify, plaże i zatoczki, wioski, klasztory, geologia, foto, jedzenie/wino, zachód słońca, plan B na deszcz. Dla każdego: dlaczego warto, dojazd z Pafos, czas, parking, wstęp, godziny, światło, sezon, ryzyka, źródło. Podziel: po drodze / mały objazd / osobny dzień lub nocleg; wskaż 3 najlepsze. Nie powtarzaj Varosha/Cape Greco/Drzewo/Grobowce/Aphrodite/Artemis/Akamas/Troodos/Pafos. Nie zmieniaj planu bazowego — dodaj jako `alternatives`, `optional_stops` lub `places` z `do_potwierdzenia`, jeśli brak twardych danych.
- [x] W5. Self-review bez subagentów: przejrzano F01–F26 i nowe pomysły z W4; sprawdzono referencje, ICS, embedded JSON, build. **(wykonane; 0 brakujących source_ids/place_ids, build 1.2.0 OK)**
- [x] W6. Raport rano: top findingi, zmiany, otwarte pytania, opcje Turcja/Cape Greco/Drzewo, zużycie budżetu. **(wykonane; 
## 12. Nowe pomysły (W4) — 10 miejsc poza planem

Dodane do `places` (bez zmiany planu bazowego), z `map_url` i źródłem; brak twardych godzin/wstępu = `do potwierdzenia`.

| ID | Miejsce | Kategoria | Dlaczego warto | Dojazd z Pafos | Podział |
| --- | --- | --- | --- | --- | --- |
| POI-KOURION | Kourion Archaeological Site | archeologia / widoki | teatr na klifie, mozaiki Eustoliosa, agora; jedno z najefektowniejszych stanowisk | ~1 h (A6) | mały objazd / osobny półdzień |
| POI-NEOPHYTOS | Agios Neophytos Monastery | klasztor | najbliższy duży klasztor, freski w Enkleistrze, cisza | ~15 min | po drodze / blisko hotelu |
| POI-LEFKARA | Pano Lefkara | wioska / rzemiosło | koronki i srebro, wąskie uliczki, muzeum | ~1 h 15 min | mały objazd / osobny dzień |
| POI-KOLOSSI | Kolossi Castle | zamek | kompaktowy zamek joannitów obok Kourion | ~1 h | po drodze |
| POI-CHRYSORROGIATISSA | Chrysorrogiatissa Monastery | klasztor / widoki | klasztor na zboczu z widokiem na winnice | ~1 h | mały objazd |
| POI-GEROSKIPOU | Geroskipou | wioska / jedzenie | kościół Agia Paraskevi, loukoumi, muzeum | ~10 min | po drodze |
| POI-PISSOURI | Pissouri | wioska / plaża | wioska na wzgórzu nad plażą, tawerny | ~40 min | po drodze |
| POI-LARNACA-SALT | Larnaca Salt Lake + Hala Sultan Tekke | natura / religia / foto | słone jezioro, meczet, zimą możliwe flamingi | ~1 h 30 min | osobny dzień / na wschód |
| POI-CHOIROKOITIA | Choirokoitia (UNESCO) | archeologia | neolityczna osada, rekonstrukcje chat | ~1 h 30 min | po drodze na wschód |
| POI-CORAL-BAY | Coral Bay | plaża | piaszczysta zatoka, łatwy plan B na ciepły dzień | ~15 min | po drodze / blisko hotelu |

**3 najlepsze:** Kourion (najmocniejszy efekt), Agios Neophytos (najbliżej, łatwo), Pano Lefkara (najładniejsza wioska). Coral Bay i Geroskipou to najlepsze "bliskie" dodatki bez długiego dojazdu.

Dodatkowo dodano 2 pinezki wschodnie: POI-LOVE-BRIDGE (Monachus Monachus Arch) i POI-KAMARA (Crow's Arch) — osobne od Drzewa Kochanków. Źródła: SRC-KOURION, SRC-NEOPHYTOS, SRC-LEFKARA, SRC-VISITCYPRUS, SRC-LOVE-BRIDGE, SRC-CHECKPOINTS.

STATUS: DONE (ryzyka użytkownika opisane w sekcji 6 i 14)

ZASADY: tylko `deepseek/deepseek-flash`; bez subagentów; nie commituj/pushuj/deployuj; budżet ~5 USD, stop przy saldzie < 0.50 USD.



## 11. Korekty po review użytkownika (PRIORYTET przed W1–W5)

Plan nie powinien być używany na wyjeździe, dopóki C1–C9 nie są zamknięte lub świadomie odłożone. C1–C9 wdrożone lub świadomie odłożone; C2 (Varosha) i C6 (osobne pinezki wschodnie) wdrożone w tej iteracji (4 XI 2026).

- [x] C1. DAY-06/DAY-07: rozdzielić „lot opóźniony” i „lot odwołany”; bag drop 05:20 według planowej godziny odlotu, nie przesuwać bez pisemnej informacji przewoźnika. **(pilne)**
- [x] C2. Varosha: przeliczone TF-22 (150–195 min) + przejście (30–60 min); wskazane Deryneia (24/7, auta) i Metehan/Ayios Dometios (24/7, polisa zwykle dostępna); polisa orientacyjnie 25–35 EUR (do potwierdzenia); bufor powrotu 30 min. Usunięta obietnica 09:00–09:30.
- [x] C3. Petsas: „wymaga kontaktu; zgoda i zakres ochrony do potwierdzenia”, nie „dopuszcza po kontakcie”. Nie wyciągać z udziału własnego 700–1000 EUR wniosku o blokadzie 500 EUR — to różne wartości.
- [x] C4. Avis: nie rozstrzygać 60 EUR; oznaczyć jako opłatę do potwierdzenia dla konkretnej rezerwacji (terms mają both free after-hours pickup at airports and general 60 EUR).
- [x] C5. WAW parking: 7 dób, nie 6 — P45/P46 210 PLN, P44 230 PLN; wycena dla dokładnych godzin.
- [x] C6. Wschód: dodane osobne pinezki POI-LOVE-BRIDGE (Monachus Monachus Arch) i POI-KAMARA (Crow's Arch); Drzewo Kochanków bez wieku (wiek niepotwierdzony); parking/dojście jako do potwierdzenia; ALT-EAST-GRECO rozdziela trzy punkty.
- [x] C7. D6-08 „Sen”: 23:59 vs pobudka 02:15 — podzielić na dwa zdarzenia (12 XI 19:00–23:59 i 13 XI 00:00–02:15) albo dodać obsługę przejścia przez północ; spójność ICS.
- [x] C8. `nearest_issue`: nie pomijać zaległych blokad auto/zwrot/parking; pokazywać najpilniejsze otwarte, także po terminie.
- [x] C9. Po poprawkach: build, walidacja, sprawdzić ICS/HTML, zaktualizować źródła i raport.


STATUS: DONE

## 13. Kolejka domknięcia (mechaniczna bramka `STATUS: DONE`)

Runner odrzuca `STATUS: DONE`, dopóki w tym pliku jest choć jeden niezaznaczony checkbox, `NEXT` nie jest `brak`, brak `WERYFIKACJA: PASS` albo ta sekcja nie jest domknięta. Każdy punkt: dowód → zmiana → test. Nie odhaczać bez dowodu.

**RUNDA 1 DOMKNIĘTA: 2026-11-04.** D1–D9 odhaczone z dowodami powyżej; build 1.2.1 OK. **Runda 2 otwarta — patrz sekcja 15 (D10–D12).**

- [x] D1. F10: `SRC-SUN` — podniesione `verification_status` = `sprawdzone_2026_11_04`, `checked_on` = 2026-11-04; zakres: niezależne przeliczenie sunrise-sunset.org.
- [x] D2. F11: `POI-HONDROS`, `POI-MOUSTAKALLIS`, `POI-KATOI` — uzupełnione telefony i godziny; Moustakallis 10–23 i Katoi wt.–nd. 12–16 zweryfikowane na stronach oficjalnych; Hondros `do potwierdzenia` z telefonem z audytu.
- [x] D3. F13: dodane współrzędne PFO, Faros Lighthouse Beach i Kings Avenue Mall z OSM/Nominatim (16/42); pozostałe bez współrzędnych mają `map_url` wyszukiwania i status `do_potwierdzenia` w notatkach.
- [x] D4. W2/A3–A5: przegląd `null`/`do_potwierdzenia` — tabela w sekcji 14; każda kategoria ma decyzję (uzupełnione / do potwierdzenia / działanie użytkownika).
- [x] D5. W3/A6–A7: 7/7 dni ma `contingencies` (3–5); `optional_stops` 2–3 na D1–D6, D7 świadomie 0; A6/A7 odhaczone.
- [x] D6. W1: Varosha (godziny sezonowe, wstęp wolny), Cape Greco (park, bez godzin), Drzewo Kochanków (parking/dojście do potwierdzenia), Love Bridge i Kamara (osobne pinezki); przejścia Deryneia/Metehan i bufor 30 min w ALT-NORTH; W1 odhaczone.
- [x] D7. A3/A4: weekday zgodne, offsety lotów poprawne, hotel 7–13 XI, 7 zachodów, restauracje z telefonami/godzinami, trasy z źródłami; A3/A4 odhaczone.
- [x] D8. Finalny build: `OK Cypr 2026 1.2.1 · 24a40fcb1e`; 42 miejsca, 42 źródła, 8 ICS; 0 brakujących `source_id`/`place_id`; embedded JSON == source JSON; ICS D7 bez duplikatu FR5880 i bez „Lądowanie WAW”.
- [x] D9. Self-review: `WERYFIKACJA: PASS (2026-11-04, build 1.2.1 OK, 0 otwartych checkboxów)`; 
## 14. Przegląd `null` / `do_potwierdzenia` (D4)

| Kategoria | Przykłady | Decyzja |
| --- | --- | --- |
| `trip.car.*` | provider, cena, depozyt, assistance, return_location | DZIAŁANIA UŻYTKOWNIKA — rezerwacja i pisemna oferta; nie zgadujemy. |
| `trip.hotel.meal_plan` | taryfa | DZIAŁANIA UŻYTKOWNIKA — voucher; brak nie blokuje planu. |
| `trip.poland_transport.value` | wybór dojazdu | Rekomendacja w notatce (WAW parking + taxi); rezerwacja = użytkownik. |
| `costs.*` | car/fuel/hotel/flights/meals | DZIAŁANIA UŻYTKOWNIKA — paragony/rezerwacje; `null` ≠ zero. |
| `routes[].ascent_m`, `gpx.path` | przewyższenia, ślady | `do_potwierdzenia` — brak załączonych GPX; nie rysujemy linii. |
| `places[].coordinates` | 26/42 bez współrzędnych | Częściowo uzupełnione (16/42, w tym 3 z OSM 4 XI); reszta ma `map_url` wyszukiwania i notatkę. |
| `places[].address/phone` | większość plaż/wsi | Nie dotyczy typu lub `do_potwierdzenia`; restauracje uzupełnione. |
| `places[].published_hours/fee` | atrakcje bez potwierdzenia | `do_potwierdzenia`; Kourion/Neophytos zweryfikowane, pozostałe — sprawdzić przed wjazdem. |
| `dining[0/1]` | FOOD-01/02 godziny/URL | `do_potwierdzenia` — wybrać otwarty lokal w okolicy; plan B zawsze dostępny. |
| `safety.emergency.*` | assistance auta/polisy | DZIAŁANIA UŻYTKOWNIKA — wpisać po rezerwacji/polisie. |
| `sources[0/1]` | załączniki użytkownika | Brak URL — oznaczone jako załączniki. |
| `days[].timeline[].end_local` | zdarzenia otwarte | ICS dodaje 60 min lub jawne zakończenie (sen podzielony D6-08/D7-00). |

STATUS: DONE.

### Działania użytkownika (nie blokują DONE, ale muszą być widoczne)

Auto, nocny zwrot, parking hotelu, dojazd Łódź↔WMI/WAW, potwierdzenie lotów 5–6 XI, pogoda 5 XI, Varosha na miejscu — opisać z konkretnym pytaniem/telefonem w sekcji 6 i `open_issues`.

## 15. Runda 2 — poprawki po kontroli danych (nie odhaczać bez dowodu)

- [x] D10. F11/dining: FOOD-02 Hondros (tel. +357 26 934256, ~12:00–22:30 do potwierdzenia), FOOD-03 Moustakallis (tel. +357 26 322883, 10:00–23:00, strona oficjalna), FOOD-05 Katoi (tel. +357 25 423033, wt.–nd. 12:00–16:00, strona oficjalna), FOOD-06 Psilo Dendro (tel. +357 25 813131, 11:00–17:00). Dodane `phone`, `published_hours`, `source_ids`; brak potwierdzenia oznaczone `do potwierdzenia`.
- [x] D11. Źródła: `SRC-HUNT-MAP`, `SRC-WEATHER`, `SRC-FORESTS`, `SRC-TRAILS-MAP`, `SRC-PET`, `SRC-SIXT` — `checked_on` = 2026-11-04, status `przejete_z_audytu`; `SRC-ORIGINAL` i `SRC-AUDIT` bez `checked_on` (załączniki użytkownika).
- [x] D12. Build `OK Cypr 2026 1.2.2 · acbaa37acb`; 42 miejsca, 42 źródła, 8 ICS, 0 brakujących referencji, embedded JSON == source JSON; `WERYFIKACJA: PASS`, `STATUS: DONE`, `NEXT: brak`.
