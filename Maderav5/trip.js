// Madera 2026 — dane wyjazdu
// Wszystkie dane operacyjne w jednym miejscu; karty dni renderują się z tego.

window.TRIP = {
  meta: {
    title: "MADEIRA",
    subtitle: "PLAN OPERACYJNY",
    dateRange: "07.05 – 14.05.2026",
    base: "Ribeira Brava – Ponta do Sol",
    arrivalFlight: { code: "W6 1535", route: "WAW 11:40 → FNC 16:05", date: "2026-05-07" },
    departureFlight: { code: "W6 1536", route: "FNC 16:45 → WAW 22:50", date: "2026-05-14" },
    myMapUrl: "https://www.google.com/maps/d/u/0/edit?mid=1NtSuO52IGWeVbz_27JV7BOM1jsuU5mA&usp=sharing",
    myMapEmbed: "https://www.google.com/maps/d/u/0/embed?mid=1NtSuO52IGWeVbz_27JV7BOM1jsuU5mA"
  },

  // Statusy używane w planie
  statuses: {
    confirmed:   { label: "Potwierdzone", short: "CONF", color: "confirmed", desc: "Źródła oficjalne / operator." },
    check:       { label: "Sprawdzić",    short: "CHK",  color: "check",     desc: "Kontrola dzień wcześniej lub przy zakupie." },
    conditional: { label: "Warunkowe",    short: "COND", color: "conditional", desc: "Zależy od pogody / operatora / niespójnych komunikatów." }
  },

  // Rytuał 20:00
  eveningRitual: [
    { k: "IFCN",       v: "Status trasy na jutro." },
    { k: "SIMplifica", v: "Rezerwacja + QR, screen do galerii." },
    { k: "Pogoda",     v: "Wiatr, chmura, widoczność (IPMA — chmury orograficzne)." },
    { k: "Parking",    v: "Dojazd, alternatywa, godzina startu." },
    { k: "Sprzęt",     v: "Woda, kurtka wiatrowa, powerbank, gotówka." },
    { k: "Offline",    v: "Screeny rezerwacji, mapa offline, adres bazy." }
  ],

  // Checklist pakowania
  packing: {
    critical: [
      "Dry-bag / wodoszczelny plecak (PR8, Seixal, Porto Moniz)",
      "Pokrowiec przeciwdeszczowy na aparat",
      "Kurtka wiatrowa (Areeiro przed świtem = zimno)",
      "Gotówka na Carreiros do Monte (35 € / 2 os.)",
      "Powerbank + kable",
      "eSIM aktywne po lądowaniu"
    ],
    daily: [
      "Woda min. 1 L / os.",
      "Ochrona przeciwsłoneczna (SPF50+)",
      "Czołówka (sunrise Areeiro / Ponta do Rosto)",
      "Mapa offline pobrana",
      "Kody QR SIMplifica zapisane",
      "Apteczka w aucie, numer 112"
    ]
  },

  // Linki oficjalne
  links: [
    { k: "IFCN",        label: "Status szlaków PR",        url: "https://ifcn.madeira.gov.pt/pt/atividades-de-natureza/percursos-pedestres-recomendados.html" },
    { k: "SIMplifica",  label: "Rezerwacje PR + Cabo Girão", url: "https://simplifica.madeira.gov.pt/services/78-82-259" },
    { k: "IPMA",        label: "Pogoda (chmury orograficzne)", url: "https://www.ipma.pt/pt/otempo/prev.localidade/index.jsp?lid=2310300" },
    { k: "Visit Madeira", label: "Atrakcje oficjalne",     url: "https://visitmadeira.com/" },
    { k: "Carreiros",   label: "Monte / toboggans",       url: "https://www.carreirosdomonte.com/v3/en/index.php" },
    { k: "Funchal CC",  label: "Funchal Cable Car",       url: "https://madeiracablecar.com/en/price-and-schedule/" },
    { k: "Porto Moniz", label: "Cable car / pools",       url: "https://www.portomoniz.pt/en/visit/points-interest/cable-car" },
    { k: "Monte Palace", label: "Monte Palace garden",    url: "https://montepalacemadeira.com/visita/" },
    { k: "Airport FNC", label: "Rental / parking",        url: "https://www.madeiraairport.pt/en/fnc/access-parking/for-your-full-comfort/car-rental" },
    { k: "Sun times",   label: "Sunrise/sunset Funchal",  url: "https://www.timeanddate.com/sun/portugal/funchal?month=5" }
  ],

  // Potwierdzone koszty
  costs: [
    { k: "PR (poza PR1)", v: "4,50 € / os.", note: "SIMplifica" },
    { k: "PR1 do Pedra Rija", v: "4,50 € / os.", note: "status warunkowy, reopening fazowany" },
    { k: "Cabo Girão", v: "5,00 € / os.", note: ">12 lat; 08:00–20:00 codz." },
    { k: "Funchal Cable Car", v: "22 € R/T • 16 € one-way", note: "08:45–17:45" },
    { k: "Carreiros do Monte", v: "35,00 € / 2 os.", note: "09:00–18:00 • gotówka na miejscu" },
    { k: "Achadas da Cruz CC", v: "3 € / 5 € R/T", note: "operacyjnie warunkowe przy wietrze" },
    { k: "Porto Moniz pools", v: "3,00 € / os.", note: "09:00–19:00 lato" },
    { k: "Monte Palace", v: "18,00 € / dorosły", note: "09:00–19:00 IV–IX; zamknięte 25.12" },
    { k: "Rocha do Navio CC", v: "— (sprawdź)", note: "09:00–13:00 / 14:00–17:00 (wkd do 18:00)" }
  ],

  // Wschody/zachody słońca dla Funchal (maj 2026) — sztywne dane (jeden timer to liczy)
  // Format: YYYY-MM-DD: [sunrise, sunset] w lokalnym czasie wyspy (WEST = UTC+1 w maju)
  sun: {
    "2026-05-07": ["07:15", "20:53"],
    "2026-05-08": ["07:14", "20:53"],
    "2026-05-09": ["07:13", "20:54"],
    "2026-05-10": ["07:12", "20:55"],
    "2026-05-11": ["07:11", "20:56"],
    "2026-05-12": ["07:10", "20:56"],
    "2026-05-13": ["07:09", "20:57"],
    "2026-05-14": ["07:08", "20:58"]
  },

  // Dni
  days: [
    {
      n: 1, date: "2026-05-07", weekday: "czwartek",
      title: "Przylot i miękkie wejście",
      module: "OPERACYJNY",
      region: "Santa Cruz → Baza",
      priority: "operacyjny",
      effort: "very low",
      drive: "0:35–1:10",
      walk: "0:15–0:45",
      duration: "4–6 h",
      startTime: "17:15–17:45 (po odbiorze auta)",
      goal: "Odebrać auto, dojechać do bazy, drobne zakupy, nie przepalić energii.",
      reasoning: "Lądowanie 16:05 — po bagażu, aucie i dojeździe nie ma sensownego buforu.",
      sequence: "Lotnisko → auto → sklep → check-in → kolacja → opcjonalny spacer blisko bazy.",
      lightWindow: "sunset ≈ 20:53",
      foodNote: "Kolacja przy bazie; nie buduj dnia pod konkretną restaurację.",
      bestBet: ["Bardzo lekki zachód w promieniu kilku minut od noclegu — tylko jeśli wszystko poszło sprawnie."],
      skipIfTired: ["Ambitny objazd wyspy", "Monte / Funchal", "Jakikolwiek punkt ze sztywną godziną"],
      risks: ["Kolejka po auto", "Opóźniony bagaż", "Zmęczenie po podróży", "Ruch przy wyjeździe z FNC"],
      reserve: ["Auto", "Nocleg", "Parking noclegu"],
      verify: ["Zasady odbioru auta", "Godziny check-in", "Paliwo", "Prognoza i status na 08.05"],
      verdict: "ZOSTAWIĆ jako pełnoprawny dzień operacyjny.",
      plans: {
        A: { label: "Dobra pogoda", badge: "REKOMENDOWANY", narrative:
          "Odbierz auto bez nerwów. Wyjedź z FNC ok. 17:15, zatrzymaj się po drodze w Pingo Doce / Continente — tylko to, co potrzebne na 48 h. Check-in w bazie. Kolacja lokalnie. Jeśli wszystko grało i zostało światło — krótki zachód w promieniu 5 minut od noclegu (promenada Ponta do Sol, seafront Ribeira Brava). Nic więcej — jutro 05:50 start na Areeiro.",
          effort: "very low", status: "confirmed" },
        B: { label: "Słaba pogoda", badge: "BEZPIECZNY", narrative:
          "Bez zachodu. Zakupy, kolacja, rozpakowanie. Zarezerwuj 20 min na rytuał 20:00 dla jutrzejszego Areeiro — to najbardziej wrażliwy operacyjnie dzień całego wyjazdu.",
          effort: "very low", status: "confirmed" },
        C: { label: "Low energy", badge: "MINIMUM", narrative:
          "Lotnisko → baza, bez przystanków. 15–20 min spacer po okolicy, jeśli masz siłę. Pełna regeneracja pod sunrise Areeiro.",
          effort: "very low", status: "confirmed" }
      },
      spots: [
        { name: "Lotnisko FNC", type: "logistics", status: "confirmed" },
        { name: "Baza: Ribeira Brava / Ponta do Sol", type: "base", status: "confirmed" }
      ]
    },
    {
      n: 2, date: "2026-05-08", weekday: "piątek",
      title: "Areeiro + Ninho da Manta + Eira do Serrado",
      module: "PRIORYTET",
      region: "Centralne góry",
      priority: "priorytet",
      effort: "medium",
      drive: "2:15–3:00",
      walk: "1:45–2:45",
      duration: "7–9 h",
      startTime: "05:50 z Ribeira Brava / 06:10 z Ponta do Sol",
      goal: "Zagrać najmocniejszy i najbardziej wrażliwy operacyjnie moduł na początku pobytu.",
      reasoning: "Po reotwarciu fazowanym PR1, piątek–niedziela to najbardziej racjonalne okno na próbę Areeiro. Nie warto odkładać na środek wyjazdu — jeśli pogoda lub status zgniotą ten dzień, masz 5 kolejnych dni na reset.",
      sequence: "Areeiro parking → sunrise → Ninho da Manta → odcinek do Pedra Rija (jeśli dostępny) → śniadanie niżej → Eira do Serrado → regeneracja.",
      lightWindow: "sunrise ≈ 07:14 • najlepsze 06:50–07:40 bez chmur",
      foodNote: "Kawa i śniadanie po zejściu, nie przed sunrise.",
      bestBet: ["Sunrise na tarasie Areeiro", "Ninho da Manta", "Pierwszy fragment grani", "Eira do Serrado jako kontrast krajobrazowy"],
      skipIfTired: ["Forsowanie dłuższego odcinka PR1 przy mgle / silnym wietrze / słabej widoczności"],
      risks: ["Zamknięcie lub ograniczenie odcinka PR1", "Tłum po 08:00", "Wiatr / brak miejsc parkingowych", "Mgła zabierająca widoczność"],
      reserve: ["PR1 przez SIMplifica"],
      verify: ["IFCN status PR1", "Slot w SIMplifica", "Wiatr / zachmurzenie / widoczność", "Realny zakres dostępnego odcinka"],
      verdict: "ZOSTAWIĆ i traktować jako pierwszy pełny dzień.",
      gearWarning: null,
      plans: {
        A: { label: "Dobra pogoda", badge: "REKOMENDOWANY", narrative:
          "Start 05:50 z bazy. Na parking Areeiro być 06:40 — przed tłumem i przed światłem. Sunrise z tarasu głównego (07:14). Potem Ninho da Manta — to jest THE viewpoint dnia, pionowa ściana w dół na Faial. Jeśli PR1 oficjalnie otwarty do Pedra Rija: idź kawałek grani, wróć tą samą trasą (nie forsuj pętli Ruivo — to osobna logistyka z transportem). Zejdź do kawiarni w Poiso / Monte na kawę i tost. Po południu Eira do Serrado — 5 min od parkingu do widoku na Curral das Freiras, zupełnie inna skala. Powrót, drzemka, kolacja.",
          effort: "medium", status: "conditional", cost: "PR1 — 4,50 € / os." },
        B: { label: "Słaba pogoda", badge: "PRZEŁÓŻ", narrative:
          "Góry w chmurze = zmarnowany poranek. Przerzuć Areeiro na dzień 3, 5 lub 7 (ten z najlepszą prognozą). Dziś: południe low-drive — Cabo Girão + Câmara de Lobos + Madalena do Mar.",
          effort: "low", status: "conditional" },
        C: { label: "Low energy", badge: "SKRÓCONY", narrative:
          "Sam punkt widokowy Areeiro + Ninho da Manta (15 min od parkingu), bez grani. Eira do Serrado po południu. Bez ciśnienia na Pedra Rija.",
          effort: "low", status: "confirmed" }
      },
      spots: [
        { name: "Pico do Areeiro", type: "viewpoint", status: "confirmed", parking: "5–20 min dojścia" },
        { name: "Ninho da Manta", type: "viewpoint", status: "confirmed" },
        { name: "PR1 → Pedra Rija", type: "trail", status: "conditional", cost: "4,50 €" },
        { name: "Eira do Serrado", type: "viewpoint", status: "confirmed", parking: "5–10 min" }
      ]
    },
    {
      n: 3, date: "2026-05-09", weekday: "sobota",
      title: "Wschód / Ponta do Rosto / PR8",
      module: "PRIORYTET",
      region: "Wschodni kraniec",
      priority: "priorytet",
      effort: "medium",
      drive: "2:30–3:15",
      walk: "2:30–4:00",
      duration: "7–8,5 h",
      startTime: "05:20 z Ribeira Brava / 05:40 z Ponta do Sol",
      goal: "Zebrać klifowy, surowy krajobraz wschodu bez zmuszania się do pełnego przejścia za wszelką cenę.",
      reasoning: "Wschód daje ogromny efekt wizualny, ale klasyczny błąd to robienie \"całości za wszelką cenę\" pod słońcem i wietrze. Boat-return NIE jest powrotem do zaparkowanego auta — to osobna usługa wodna z osobną logistyką.",
      sequence: "Ponta do Rosto sunrise → Baía d'Abra trailhead → PR8 do Casa do Sardinha → ewentualnie dalej tylko przy dobrej energii → Machico późny lunch → powrót.",
      lightWindow: "sunrise ≈ 07:13 • najlepsze 06:50–08:15",
      foodNote: "Machico po zejściu. Pamiętaj twarde okno 13:00–14:30.",
      bestBet: ["Ponta do Rosto o świcie", "Pierwsza połowa PR8 (czerwona ziemia + klify)", "Casa do Sardinha"],
      skipIfTired: ["Pełna wersja PR8", "Boat-return tylko dlatego, że \"już tu jesteśmy\""],
      risks: ["Silny wiatr", "Pełne słońce", "Odwodnienie", "Tłum po 09:00", "Błędne założenie, że łódź rozwiąże logistykę"],
      reserve: ["PR8 przez SIMplifica"],
      verify: ["Wiatr", "Ekspozycja słoneczna", "Status szlaku", "Jeśli boat-return: operator i transfer do auta"],
      verdict: "ZOSTAWIĆ, ale domyślnie SKRÓCIĆ.",
      gearWarning: "Motorówka na otwartym Atlantyku = gęsty salt-spray. Sprzęt foto tylko w zamykanym dry-bagu. Sól trwale niszczy elektronikę i optykę.",
      plans: {
        A: { label: "Dobra pogoda", badge: "REKOMENDOWANY", narrative:
          "Start 05:20. Ponta do Rosto na sunrise — krótkie zejście od parkingu (2–5 min), światło trafia w klify Roca → Desertas na horyzoncie. Około 08:00 przeniesienie się do Baía d'Abra. PR8 w skróconej wersji: do Casa do Sardinha i z powrotem. To jest właściwy PR8 — dalsze odcinki (wzniesienie 150 m, pełne słońce, tłum) dają diminishing returns. Po 11:00 zrobi się upalnie. Machico na lunch do 14:30. Popołudnie: promenada w Machico lub powrót i odpoczynek. Boat-return pomijamy — osobna usługa wodna, osobny transfer do auta, osobny budżet.",
          effort: "medium", status: "confirmed", cost: "PR8 — 4,50 € / os." },
        B: { label: "Słaba pogoda / wiatr", badge: "VIEWPOINTY", narrative:
          "Bez PR8. Sama Ponta do Rosto + Miradouro do Guindaste + promenada Machico + Canical. Nadal świetne widoki, znacznie mniej ryzyka.",
          effort: "low", status: "confirmed" },
        C: { label: "Low energy", badge: "VIEWPOINT-HOPPING", narrative:
          "Ponta do Rosto + Guindaste + promenada Machico. Zero szlaku. Wróć wcześnie, wieczór wolny.",
          effort: "very low", status: "confirmed" }
      },
      spots: [
        { name: "Miradouro Ponta do Rosto", type: "viewpoint", status: "confirmed" },
        { name: "PR8 Baía d'Abra → Casa do Sardinha", type: "trail", status: "confirmed", cost: "4,50 €" },
        { name: "Miradouro do Guindaste", type: "viewpoint", status: "confirmed" },
        { name: "Machico", type: "town", status: "confirmed" }
      ]
    },
    {
      n: 4, date: "2026-05-10", weekday: "niedziela",
      title: "Południe / recovery day",
      module: "RECOVERY",
      region: "Południe",
      priority: "recovery",
      effort: "low",
      drive: "1:00–1:45",
      walk: "0:45–1:30",
      duration: "5–7 h",
      startTime: "09:00–09:30",
      goal: "Wstawić lekki, niskokosztowy dzień po dwóch mocniejszych porankach.",
      reasoning: "To ma być dzień lekki, a nie kolejny moduł do odhaczania. Cabo Girão jest mocnym stopem, ale nie niesie pół dnia.",
      sequence: "Cabo Girão → Câmara de Lobos (kawa/lunch) → Madalena do Mar / Rota do Banana → zachód przy bazie.",
      lightWindow: "sunset ≈ 20:55",
      foodNote: "Câmara de Lobos lub Madalena do Mar. Najłatwiejsza infrastruktura gastronomiczna dnia.",
      bestBet: ["Cabo Girão jako 15–25 min stop", "Port w Câmara de Lobos", "Płaski spacer wśród bananowców", "Zachód przy bazie"],
      skipIfTired: ["Robienie z Cabo Girão dnia premium", "Dokładanie losowych małych stopów"],
      risks: ["Tłok na Cabo Girão", "Płaska jakość światła przy pełnym overcaście"],
      reserve: ["Płatność za Cabo Girão — sprawdź najwygodniejszy tryb przed podjazdem"],
      verify: ["Pogoda na zachód", "Czy nie chcesz zamienić na moduł miejski"],
      verdict: "ZOSTAWIĆ, ale trzymać krótko.",
      plans: {
        A: { label: "Dobra pogoda", badge: "REKOMENDOWANY", narrative:
          "Późny start — 09:00. Cabo Girão (5 € / os.): szklana platforma 580 m nad oceanem, 15–25 min wystarczy. Zejście do Câmara de Lobos na kawę przy porcie (tu Churchill malował). Madalena do Mar lub Rota do Banana — płaski spacer wzdłuż plantacji, zero cardio, rekompensata za poranek Areeiro i wschód. Zachód z balkonu bazy albo z Ponta do Sol.",
          effort: "low", status: "confirmed", cost: "Cabo Girão — 5 € / os." },
        B: { label: "Słaba pogoda", badge: "MIEJSKI BACKUP", narrative:
          "Old Town Funchal (Zona Velha) jako miejski backup. Rua de Santa Maria, Mercado dos Lavradores, Fortaleza do Pico. Słabszy fit do briefu widokowego, ale pełna infrastruktura.",
          effort: "low", status: "confirmed" },
        C: { label: "Low energy", badge: "MINIMUM", narrative:
          "Sama Câmara de Lobos + zachód przy bazie. Resztę dnia leżeć.",
          effort: "very low", status: "confirmed" }
      },
      spots: [
        { name: "Cabo Girão Skywalk", type: "viewpoint", status: "confirmed", cost: "5 €" },
        { name: "Câmara de Lobos", type: "town", status: "confirmed" },
        { name: "Madalena do Mar", type: "town", status: "confirmed" }
      ]
    },
    {
      n: 5, date: "2026-05-11", weekday: "poniedziałek",
      title: "Ribeiro Frio / Balcões / Santana",
      module: "STABILNY",
      region: "Północny interior",
      priority: "stabilny",
      effort: "low",
      drive: "2:15–3:00",
      walk: "1:15–2:00",
      duration: "6–8 h",
      startTime: "08:00–08:30",
      goal: "Zielony i spokojniejszy kontrast dla dni klifowych i górskich.",
      reasoning: "Balcões ma świetny stosunek efekt/wysiłek. Santana i Rocha do Navio są logicznymi dopięciami, ale nie muszą dominować dnia.",
      sequence: "Ribeiro Frio → PR11 Balcões → Santana krótko → Rocha do Navio viewpoint / cable car (jeśli działa) → powrót.",
      lightWindow: "Poranek i późne przedpołudnie lepsze niż środek dnia.",
      foodNote: "Ribeiro Frio lub Santana. Licz na miasteczka i kawiarnie, nie na viewpointy.",
      bestBet: ["Balcões przy dobrej widzialności", "Klify Rocha do Navio", "Krótki kontrast architektoniczny Santany"],
      skipIfTired: ["Długie siedzenie w Santanie", "Dopychanie Rocha do Navio, gdy kolejka nie działa"],
      risks: ["Niska chmura", "Słaba widzialność", "Nieczynna kolejka", "Zbyt optymistyczny plan z PR9 bez jasnego statusu"],
      reserve: ["PR11 przez SIMplifica; jeśli finalnie PR9.1 — rezerwujesz PR9.1"],
      verify: ["Widoczność w Balcões", "Działanie kolejki Rocha do Navio", "Status PR9 / PR9.1 przy podmianie"],
      verdict: "ZOSTAWIĆ, z Rocha do Navio jako WARUNKOWYM dodatkiem.",
      plans: {
        A: { label: "Dobra pogoda", badge: "REKOMENDOWANY", narrative:
          "Start 08:00. Ribeiro Frio — krótki spacer przy rezerwacie, kawa. PR11 Balcões: 1,5 km w jedną stronę po płaskim levada, czas przejścia 30–40 min. Widok na Penha d'Águia i grań Pico Ruivo — jeśli widoczność czysta, to jeden z najlepszych stosunków efekt/wysiłek całego wyjazdu. Santana: 30 min, casas de colmo (chatki z trzciną), kawa. Rocha do Navio: kolejka jeśli działa (09:00–13:00 / 14:00–17:00, wkd do 18:00). Alternatywa: sam viewpoint bez zjazdu.",
          effort: "low", status: "confirmed", cost: "PR11 — 4,50 € / os." },
        B: { label: "Słaba pogoda", badge: "PR9.1 ZAMIANA", narrative:
          "Balcões w chmurze = bez sensu. Zamień na PR9.1 — levada do Caldeirão Verde w wariancie dostępnym dla wszystkich (status: potwierdzone). Bardziej osłonięty, leśny. UWAGA: pełne PR9 — obecnie zamknięte wg IFCN.",
          effort: "low", status: "confirmed", cost: "PR9.1 — 4,50 € / os." },
        C: { label: "Low energy", badge: "SAME VIEWPOINTY", narrative:
          "Santana + Rocha do Navio viewpoint bez Balcões. Pełne miasteczkowe tempo. Kolejka zjazdowa tylko jeśli bez kolejki i wiatru.",
          effort: "very low", status: "check" }
      },
      spots: [
        { name: "Ribeiro Frio", type: "nature", status: "confirmed" },
        { name: "PR11 Balcões", type: "trail", status: "confirmed", cost: "4,50 €" },
        { name: "Santana", type: "town", status: "confirmed" },
        { name: "Rocha do Navio Cable Car", type: "cablecar", status: "check", note: "cena: sprawdź na miejscu" },
        { name: "PR9.1 (backup)", type: "trail", status: "confirmed" }
      ]
    },
    {
      n: 6, date: "2026-05-12", weekday: "wtorek",
      title: "Seixal / Véu da Noiva / Porto Moniz",
      module: "STABILNY",
      region: "Północny zachód",
      priority: "stabilny",
      effort: "low",
      drive: "2:15–3:15",
      walk: "0:30–1:30",
      duration: "6–8 h",
      startTime: "08:00–08:30",
      goal: "Zagrać jeden z najlepszych dni \"widoki bez cardio\".",
      reasoning: "Północny zachód najlepiej działa samochodem i krótkimi stopami. Wejście do oceanu ma sens tylko przy spokojnym morzu.",
      sequence: "Seixal rano → Véu da Noiva → Porto Moniz na dłuższy stop i lunch → powrót.",
      lightWindow: "Seixal najlepiej wcześnie rano.",
      foodNote: "Porto Moniz. Najlepsza infrastruktura dnia: przebieralnie, bar, first aid, parking.",
      bestBet: ["Seixal nawet bez kąpieli", "Véu da Noiva (wodospad przy drodze)", "Porto Moniz jako relaks i spacer"],
      skipIfTired: ["Wymuszoną kąpiel przy złych warunkach", "Dokładanie kolejnych wodnych punktów na siłę"],
      risks: ["Swell", "Śliskie skały", "Tłum w Porto Moniz", "Gorsza pogoda na północy niż na południu"],
      reserve: ["Brak krytycznej rezerwacji"],
      verify: ["Fale / wiatr / deszcz na północy", "Możliwość kąpieli", "Własna gotowość do wejścia do wody"],
      verdict: "ZOSTAWIĆ.",
      gearWarning: "W Seixal i Porto Moniz nieprzewidziane wyższe fale regularnie zalewają turystów. Sprzęt foto tylko w zamykanym plecaku z pokrowcem przeciwdeszczowym. Nic na skałach przy surge.",
      plans: {
        A: { label: "Dobra pogoda", badge: "REKOMENDOWANY", narrative:
          "Start 08:00 — północ ma gorszą pogodę popołudniami, wyprzedź to. Seixal — czarna piaszczysta plaża + naturalne baseny wulkaniczne. Wejdź tylko jeśli morze faktycznie spokojne (brak surge, brak wysokich fal). Véu da Noiva — wodospad spadający z klifu wprost przy VR-101, parking przy drodze, 2 min spaceru do tarasu. Porto Moniz — baseny wulkaniczne (3 € / os., 09:00–19:00 lato), lunch do 14:30. Powrót przez tunele.",
          effort: "low", status: "confirmed", cost: "Pools 3 € / os." },
        B: { label: "Słaba pogoda", badge: "BEZ WODY", narrative:
          "Véu da Noiva + Porto Moniz jako spacer i lunch. Zero wody, zero ryzyka. Seixal tylko z tarasu, bez schodzenia do basenów.",
          effort: "very low", status: "confirmed" },
        C: { label: "Low energy", badge: "TYLKO PORTO MONIZ", narrative:
          "Tylko Porto Moniz + 1–2 stop pointy po drodze. Wróć wcześnie.",
          effort: "very low", status: "confirmed" }
      },
      spots: [
        { name: "Seixal (plaża + pools)", type: "beach", status: "conditional" },
        { name: "Véu da Noiva", type: "viewpoint", status: "confirmed" },
        { name: "Porto Moniz Natural Pools", type: "pools", status: "confirmed", cost: "3 €" }
      ]
    },
    {
      n: 7, date: "2026-05-13", weekday: "środa",
      title: "Achadas / Garganta Funda / Ponta do Pargo",
      module: "STABILNY",
      region: "Zachodni kraniec",
      priority: "stabilny",
      effort: "low",
      drive: "2:30–3:30",
      walk: "0:45–2:00",
      duration: "7–9 h",
      startTime: "10:00–10:30",
      goal: "Maksymalny zachodni payoff widokowy przy minimalnym wysiłku.",
      reasoning: "Tu payoff robią pionowe klify, nie dystans. Najlepiej ustawić dzień pod popołudniowe światło w Garganta Funda i zachód w Ponta do Pargo.",
      sequence: "Achadas da Cruz → zjazd (jeśli działa i nie wieje) → krótki spacer na fajã → lunch → Garganta Funda po południu → Ponta do Pargo sunset.",
      lightWindow: "Garganta Funda ≈ 16:00–18:00 • sunset ≈ 20:57",
      foodNote: "Porto Moniz po drodze albo Ponta do Pargo village.",
      bestBet: ["Sam zachodni kraniec wyspy", "Garganta Funda w dobrym świetle", "Achadas — tylko gdy kolejka działa"],
      skipIfTired: ["Dodatkowe objazdy w środku dnia", "Losowe przystanki kosztem zachodu"],
      risks: ["Wiatr wyłączający kolejkę Achadas", "Niski przepływ wodospadu", "Mgła zabierająca zachód"],
      reserve: ["Brak krytycznej rezerwacji"],
      verify: ["Działanie kolejki Achadas", "Wiatr / ewentualny edital serwisowy", "Stan wodospadu", "Zachmurzenie na zachodzie"],
      verdict: "ZOSTAWIĆ.",
      plans: {
        A: { label: "Dobra pogoda", badge: "REKOMENDOWANY", narrative:
          "Późny start 10:00 — dzień układa się pod popołudniowe światło. Achadas da Cruz: kolejka (3 € / 5 € R/T) zjeżdża 450 m w dół na fajã — jeśli wieje mocno albo dzień serwisowy, zostajesz na górnym viewpointcie. Lunch w Porto Moniz lub Ponta do Pargo village (nie po 14:30). Garganta Funda po południu — wodospad o popołudniowym świetle, parking przy drodze, 5–10 min spaceru. Ponta do Pargo na sunset (20:57): latarnia morska na najzachodniejszym cyplu wyspy, otwarte niebo nad Atlantykiem.",
          effort: "low", status: "conditional", cost: "Achadas — 3 € / 5 €" },
        B: { label: "Słaba pogoda / wiatr", badge: "BEZ ZJAZDU", narrative:
          "Achadas tylko z górnego viewpointu. Ponta da Ladeira + Garganta Funda + Ponta do Pargo. Jeśli mgła w Fanal — detour się opłaca (TYLKO za mgłą, inaczej słaby ROI).",
          effort: "very low", status: "confirmed" },
        C: { label: "Low energy", badge: "SAME VIEWPOINTY", narrative:
          "Ponta da Ladeira + Garganta Funda + Ponta do Pargo. Wszystko od parkingu w 2–10 min. Zero zjazdów.",
          effort: "very low", status: "confirmed" }
      },
      spots: [
        { name: "Achadas da Cruz Cable Car", type: "cablecar", status: "conditional", cost: "3 € / 5 € R/T" },
        { name: "Garganta Funda", type: "waterfall", status: "confirmed" },
        { name: "Ponta do Pargo (latarnia)", type: "viewpoint", status: "confirmed" },
        { name: "Fanal (detour mgły)", type: "forest", status: "conditional" }
      ]
    },
    {
      n: 8, date: "2026-05-14", weekday: "czwartek",
      title: "Wylot",
      module: "OPERACYJNY",
      region: "Baza → FNC",
      priority: "operacyjny",
      effort: "very low",
      drive: "0:45–1:30",
      walk: "0:15–0:45",
      duration: "4–5 h",
      startTime: "10:30–11:00 z bazy",
      goal: "Zamknąć wyjazd bez ryzyka spóźnienia i bez udawania, że to normalny dzień zwiedzania.",
      reasoning: "Wylot 16:45 oznacza, że każdy \"jeszcze tylko szybki Monte/Funchal\" bardzo łatwo robi się złą decyzją.",
      sequence: "Śniadanie → checkout → ewentualnie jeden łatwy stop po drodze na wschód → lekki lunch → zwrot auta → lotnisko 13:45–14:15.",
      lightWindow: "Nieistotne — dziś logistyka, nie światło.",
      foodNote: "Machico lub Santa Cruz. Najwygodniejsze logistycznie.",
      bestBet: ["Mały, niskotarciowy punkt po drodze jeśli wszystko pod kontrolą"],
      skipIfTired: ["Monte", "Areeiro", "Pełen Funchal", "Ambitne objazdy \"na koniec\""],
      risks: ["Spóźniony zwrot auta", "Zbyt późny wyjazd", "Ekspozycja bagaży", "Zakorkowany dojazd"],
      reserve: ["Nic nowego poza logistyką auta i lotu"],
      verify: ["Polityka paliwowa", "Dokumenty", "Czas dojazdu do lotniska", "Warunki zdania auta"],
      verdict: "ZOSTAWIĆ jako dzień operacyjny.",
      plans: {
        A: { label: "Dobra pogoda", badge: "KRÓTKI STOP", narrative:
          "Checkout 10:30–11:00. W drodze na wschód: krótki spacer w Machico albo Santa Cruz (promenada, kawa). Lunch lekki, do 13:30. Zwrot auta z buforem 30 min. Na lotnisku 13:45–14:15 — wylot 16:45.",
          effort: "very low", status: "confirmed" },
        B: { label: "Słaba pogoda / spóźnienie", badge: "PROSTO NA FNC", narrative:
          "Bez zwiedzania: śniadanie, checkout, lotnisko. Najbezpieczniejsza opcja.",
          effort: "very low", status: "confirmed" },
        C: { label: "Low energy", badge: "TYLKO KAWA", narrative:
          "Kawa po drodze i prosto na FNC.",
          effort: "very low", status: "confirmed" }
      },
      spots: [
        { name: "Machico / Santa Cruz", type: "town", status: "confirmed" },
        { name: "Lotnisko FNC", type: "logistics", status: "confirmed" }
      ]
    }
  ],

  // Scenariusze pogodowe (bottom sheet)
  weatherScenarios: [
    { k: "Góry w chmurach",   v: "Nie marnuj Areeiro. Zamień z dniem południowym albo wschodnim." },
    { k: "Wschód wietrzny",    v: "Skróć PR8 do viewpointów lub przerzuć na Machico / południe." },
    { k: "Morze wzburzone",    v: "Seixal i wejścia do wody skreśl bez dyskusji. Zostaw viewpointy + Porto Moniz." },
    { k: "Cable car off",      v: "Górne miradouros i zachód. Nie ratuj identycznego programu." },
    { k: "Fanal",              v: "Tylko za mgłą. Bez mgły — słaby ROI." },
    { k: "Areeiro zamknięte cały tydzień", v: "Priorytet: PR8 sunrise deck → Eira do Serrado + południe → zachód (Ponta do Pargo, Garganta Funda)." },
    { k: "Chory / zero energii", v: "Promień 45 min: Madalena do Mar, Ponta do Sol seafront, kawa w Ribeira Brava. Zero sztywnych godzin." },
    { k: "Zachód mglisty 12–13.05", v: "D6 → same viewpointy + lunch, zero wody. D7 → Ponta da Ladeira + Garganta + Pargo bez zjazdu. Fallback: południe." }
  ],

  // Okno lunchowe — twarda reguła
  lunchRule: {
    window: "13:00 – 14:30",
    note: "Kuchnie poza Funchal zamykają się 15:00–18:30. Po 15:00: Funchal lub baza. Plan B: Pingo Doce / Continente — zimne jedzenie."
  },

  // Auto
  carRules: [
    "Wykup CDW bez wkładu własnego (standard na Maderze)",
    "ZERO dróg szutrowych / nieutwardzonych (większość wypożyczalni = złamanie umowy)",
    "Polityka paliwowa zwykle full-to-full",
    "Zdjęcia stanu auta przy odbiorze i zdaniu (cały obwód + wnętrze)",
    "Mapy offline pobrane przed wyjazdem",
    "eSIM aktywowany po lądowaniu",
    "112 — numer alarmowy UE"
  ]
};
