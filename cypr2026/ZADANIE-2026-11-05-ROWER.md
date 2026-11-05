# Cypr 2026 — zadanie 2026-11-05: sekcja wycieczek rowerowych

## Jedyny cel

Rozbuduj publiczną stronę Cypr 2026 o **samodzielną, niedatowaną sekcję „Wycieczki rowerowe”** z maksymalnie trzema propozycjami z rejonu Pafos. Nie przypisuj ich do konkretnego dnia. To opcjonalne pomysły, nie zmiana planu bazowego, rezerwacja ani obietnica, że trasa jest gotowa do przejazdu.

To zadanie dotyczy wyłącznie rowerów: nie wykonuj ponownego audytu pozostałych atrakcji, zdjęć, rezerwacji ani całego planu. Nie zmieniaj planu dni, trekkingów, lotów, hotelu, auta, kalendarzy ani niezwiązanych sekcji strony.
To zadanie zastępuje wszystkie wcześniejsze cele merytoryczne; nie traktuj ich jako aktywnych punktów `NEXT`, TODO ani kryteriów akceptacji.

## Dane i implementacja

- Zachowaj `data/Cypr_2026_zrodlo_prawdy.json` jako źródło danych. Dodaj osobną strukturę rowerową (np. `cycling_options`) i źródła potrzebne tylko dla tych propozycji.
- Pokaż ją jako niezależną sekcję na stronie, bez przypisania do dnia. Użyj tylko powierzchni edycji dozwolonych przez runnera: JSON, `app.js`, `_src/template.html`, `styles.css` oraz krótki zapis dowodów dla tego zadania w `PLAN-REVIEW.md`.
- Nie dopisuj wycieczek rowerowych do `routes[]`: obecne trasy są piesze i podlegają oddzielnej bramce zdjęć. Nie dodawaj zdjęć ani GPX.
- `index.html`, `dist/` i assety generowane są wyłącznie wynikiem builda; nie edytuj ich ręcznie.
- Zachowaj dostępność klawiaturową, mobilną i druk. Nie osłabiaj istniejącej obsługi bez JavaScriptu. Jeśli sekcji nie da się poprawnie wyrenderować z kanonicznych danych bez edycji chronionego `_src/build.py` albo zmiany polityk runnera, **zatrzymaj się i opisz blocker**. Nie obchodź ochrony i nie duplikuj treści po cichu między JSON-em a szablonem.

## Zawartość propozycji

Preferuj trzy wyraźnie różne poziomy dystansu/wysiłku (krótka, średnia, dłuższa/wymagająca), ale jeśli nie da się rzetelnie potwierdzić trzech sensownych opcji, pokaż mniej i wyjaśnij dlaczego. Nie zakładaj doświadczenia rowerowego użytkowników.

Każda opcja ma podać, o ile źródła to potwierdzają:

1. Nazwę i przebieg, start/metę oraz informację, czy to pętla czy trasa liniowa.
2. Oficjalny dystans i sumę podejść; czas jazdy wyłącznie jako jawny szacunek z wyjaśnionymi założeniami.
3. Nawierzchnię, zalecany typ roweru i wymagany poziom doświadczenia.
4. Ruch drogowy, ścieżki rowerowe i ograniczenia bezpieczeństwa; nie nazywaj drogi bezpieczną bez dowodu.
5. Logistykę dotarcia z Pafos i powrotu. Nie przedstawiaj trasy jednokierunkowej jako praktycznej bez potwierdzonego powrotu z rowerem.
6. Najciekawsze postoje oraz istotne ryzyka, zamknięcia i ograniczenia.
7. Wypożyczenie (typ, dostępność w okresie podróży, godziny, koszt) tylko z wiarygodnym źródłem; resztę oznacz `do_potwierdzenia`. Nie dzwoń i niczego nie rezerwuj.
8. Linki do oficjalnych źródeł/GPX i rzeczywistą datę sprawdzenia.

Oddziel fakty źródłowe od szacunków i niewiadomych. Nie wymyślaj tras, dystansów, przewyższeń, czasów, cen, godzin, śladów ani zapewnień o bezpieczeństwie. Ponieważ sekcja jest niedatowana, zaznacz, że pogodę, zamknięcia i ograniczenia terenowe trzeba sprawdzić przed wyborem.

## Źródła — wstępne tropy do weryfikacji

Korzystaj z oficjalnych, publicznych stron dostępnych w allowliście źródeł runnera (`www.visitcyprus.com` jest już w źródłach planu). Nie rozszerzaj allowlisty i nie obchodź blokad. Poniższe strony to tropy, nie gotowe rekomendacje:

- Pafos 2 — Kato Pafos–Timi Forest: <https://www.visitcyprus.com/discover-cyprus/nature/cycling/kato-pafos-paphos-timi-forest-cycling-route/>. Opis podaje 16,6 km, 76 m, trasę płaską/asfaltową i liniową oraz GPX.
- Druga oficjalna strona o Kato Pafos–Timi podaje 12 km, nawierzchnie mieszane i MTB: <https://www.visitcyprus.com/discover-cyprus/rural/cycling-rural/kato-pafos-paphos-timi-forest-cycling-route-2/>. Ustal, czy to odrębny wariant; nie łącz parametrów obu stron.
- Pafos 1 — przez Agia Varvara, Episkopi, Tsada i Armou: <https://www.visitcyprus.com/discover-cyprus/nature/cycling/pafos-1-pafos-castle-agia-varvara-episkopi-tsada-armou-agia-varvara-pafos-castle-cycling-route/>. Strona zawiera GPX, ale nie podaje w tekście podstawowych statystyk; nie dopisuj ich bez dowodu.
- Main 16 — Pafos–Pegeia–Polis: <https://www.visitcyprus.com/discover-cyprus/nature/cycling/main-16-pafos-paphos-polis-cycling-route/>. Opis podaje 43,8 km, 775 m podejść, trudną asfaltową trasę liniową do Polis; nie polecaj jej jako praktycznej bez potwierdzenia powrotu.

## Kryteria akceptacji

- Na stronie jest oddzielna sekcja rowerowa z maksymalnie trzema niedatowanymi propozycjami; plan bazowy i pozostała treść nie zmieniają się.
- Każda liczba i twierdzenie o trasie ma źródło lub jest wyraźnie oznaczonym szacunkiem; braki są jawne.
- Sekcja działa w ramach istniejącego builda, jest dostępna, responsywna i nadaje się do druku. Jeśli wymaga chronionych zmian w Pythonie/politykach lub narusza obsługę bez JavaScriptu, zakończ raportem o blockerze zamiast obchodzić ograniczenia.
- Nie oznaczaj historycznego audytu jako ponownie zweryfikowanego ani nie ustawiaj `STATUS: DONE`; stan końcowy runnera należy do Cypr Night.
