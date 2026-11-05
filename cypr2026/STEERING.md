# Dyrektywy użytkownika — Cypr 2026

Ten plik jest **nadrzędny** wobec `PLAN-REVIEW.md`. Agent czyta go przed każdą iteracją.

## KOREKTY PO REVIEW (PRIORYTET)

Zachowaj dotychczasowe zmiany, ale **nie używaj planu na wyjeździe**, dopóki C1–C9 z `PLAN-REVIEW.md` (sekcja 11) nie są zamknięte lub świadomie odłożone.

- **C1 (pilne):** rozdziel „lot opóźniony” i „lot odwołany”. Bag drop 05:20 według planowej godziny; nie przesuwać go bez pisemnej informacji przewoźnika.
- **C2 (pilne):** przelicz Varosha: TF-22 150–195 min + Green Line 30–60 min; obecne 09:00–09:30 jest nierealne. Wskaż przejście, polisę i bufor powrotu.
- **C3:** Petsas „wymaga kontaktu; zgoda i zakres ochrony do potwierdzenia”, nie „dopuszcza po kontakcie”. Udział własny 700–1000 EUR ≠ blokada karty 500 EUR.
- **C4:** Avis 60 EUR — nie rozstrzygaj, czy dotyczy odbioru, czy zwrotu; oznacz jako do potwierdzenia dla rezerwacji.
- **C5:** parking WAW licz na 7 dób: P45/P46 210 PLN, P44 230 PLN — nie 190/210.
- **C6:** rozdziel Kamara tou Koraka, Love Bridge (Ayia Napa) i Drzewo Kochanków; osobne pinezki; usuń „160+ lat” bez źródła.
- **C7:** „Sen” 23:59 vs pobudka 02:15 — podziel na dwa zdarzenia lub obsłuż przejście przez północ; spójność ICS.
- **C8:** `nearest_issue` nie może pomijać zaległych blokad auto/zwrot/parking.
- **C9:** po poprawkach build, walidacja, ICS/HTML i aktualizacja raportu.

## NOWE POMYSŁY (dodatkowa dyrektywa)

- Zaproponuj **8–10 nowych, realnych, ładnych/ciekawych miejsc**, których nie ma w planie.
- Kategorie: widoki i klify, plaże/zatoczki, wioski, klasztory, geologia, punkty fotograficzne, jedzenie/wino, zachód słońca, plan B na deszcz.
- Dla każdego: dlaczego warto, dojazd z Pafos, czas, parking, wstęp, godziny, najlepsze światło, sezon, ryzyka, źródło.
- Podziel: po drodze / mały objazd / tylko osobny dzień lub nocleg; wskaż **3 najlepsze**.
- Nie powtarzaj: Varosha, Cape Greco, Drzewo Kochanków, Grobowce, Aphrodite, Artemis, Akamas, Troodos, Pafos.
- Nie zmieniaj planu bazowego — dodaj jako `alternatives`, `optional_stops` lub `places`; brak twardych danych = `do_potwierdzenia`.

## Aktywne dyrektywy

- **Nowy cel opcjonalny (nie zmieniaj planu bazowego):** dodaj jako alternatywę wyjazd na stronę turecką (Cypr Północny). Główny cel: **Varosha / Famagusta**.
- **Cape Greco nie leży na stronie tureckiej** — to Republika Cypryjska, południowo-wschodni kraniec wyspy (Ayia Napa / Protaras). Nie łącz go z „stroną turecką” bez wyjaśnienia; przeanalizuj osobno.
- **Drzewo Kochanków (Lovers' Tree)** — dodaj jako punkt opcjonalny przy Cape Greco / Ayia Napa, nie na stronie tureckiej. To wiekowe drzewo (jałowiec) w rejonie Cape Greco, popularne do zdjęć; sprawdź dokładną lokalizację, parking, dojście i nie myl go z „Mostem Kochanków” (Kamara tou Koraka).
- **Rotacja modeli (tylko w trybie rotate):** runner podaje model tej iteracji. Zapisuj w `PLAN-REVIEW.md`, który model pracował, i zbieraj różne punkty widzenia. Nie uśredniaj rozbieżności bez wyjaśnienia. W trybie DeepSeek-only nie dotyczy — jest tylko `deepseek-flash`.
- Zbadaj, czy **Varosha + Cape Greco da się zrobić w jednym dniu z Pafos**. Policz realny czas jazdy, przekroczenia granicy, światło, zmęczenie i koszt. Jeśli nie — zaproponuj warianty:
  1. dzień tylko Varosha / Famagusta (Pafos → Nicosia → Famagusta),
  2. dzień tylko Cape Greco / Ayia Napa (południe),
  3. nocleg 1 noc na wschodzie (Larnaka / Ayia Napa / Famagusta) i oba punkty,
  4. inne propozycje północy: Kyrenia, Bellapais, St. Hilarion, Salamis, Othello, dzielona Nicosia.
- Dla każdego wariantu podaj: czas jazdy w obie strony, km, checkpointy, wymagane dokumenty (dowód/paszport), czy auto z wypożyczalni może przekroczyć granicę, ubezpieczenie, opłaty, godziny otwarcia Varoshy, parking, światło, ryzyka i czy pasuje do 7–13 XI.
- Nie zakładaj, że auto z wypożyczalni może wjechać na północ — to często zabronione; sprawdź to jawnie.
- Nie zmieniaj rezerwacji ani planu bazowego. Dodaj wpisy do `alternatives` i `open_issues`; każdy fakt ze źródłem i datą sprawdzenia.
- Priorytet: najpierw wykonalność i bezpieczeństwo, potem propozycje.

## NOWE ZADANIE — 2026-11-05 (priorytet nadrzędny)

Wykonuj **`cypr2026/ZADANIE-2026-11-05.md`** przed wszystkimi starszymi dyrektywami z tego pliku. Skrót:

- Zweryfikuj **wszystkie** informacje i źródła w `cypr2026`; każdy fakt z datą sprawdzenia, bez fikcji i cichych `null`.
- Sprawdź nowe miejsca (Varosha/Famagusta, Cape Greco/Drzewo Kochanków/Love Bridge/Kamara, Kourion/Kolossi/Neofytos/Chrysorrogiatissa/Geroskipou/Pissouri/Lefkara/Larnaka/Choirokoitia/Coral Bay) na oficjalnych stronach.
- Zaproponuj 5–10 nowych realnych rzeczy, z dojazdem, parkingiem, godzinami, światłem, ryzykiem i źródłem; dodaj jako opcje, nie zmieniaj planu bazowego.
- Zaudytuj **wszystkie 71 zdjęć** i uzupełnij braki: nowe miejsca i wszystkie trasy po 3–4 zweryfikowane kadry, jeden lead; scenic/praktyczne miejsca w miarę możliwości.
- Preferuj **najnowsze** zdjęcia (2025–2026, potem 2024); cel ≥75% dat ≥2024; wymień stare kadry, gdzie jest nowszy odpowiednik.
- Tylko prawdziwe zdjęcia: zero AI, stocku i „podobnych” miejsc; źródło Commons, data, miejsce, 2 dowody, lokalne warianty 480/800/1280/1920 AVIF/WebP/JPEG.
- Utwórz `cypr2026/ZDJECIA-AUDYT.md` z macierzą pokrycia wszystkich dni, miejsc i tras.
- `STATUS: DONE` dopiero po odhaczeniu sekcji 16 w `PLAN-REVIEW.md` i przejściu runnera (`photo_check`).

## Jak pisać

- Jedna dyrektywa = jedna linia, konkretnie: „najpierw…”, „nie zmieniaj…”, „dodaj tylko…”.
- Nie usuwaj nagłówka; dopisuj pod `## Aktywne dyrektywy`.
- Agent ma nadal zakaz commitowania, pushowania i deployowania.
