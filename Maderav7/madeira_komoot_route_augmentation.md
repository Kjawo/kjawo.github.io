# Madera 2026 — dopasowanie tras Komoot i fallbacki GPX

Źródłowy plan podróży: fileciteturn0file0

Tutaj jest ścisły pass routingowy. Czyste, dokładne dopasowania Komoot istnieją dla **PR8**, **PR11** i opcjonalnego mikro-spaceru **Rota de Banana**. Dzień 2 **nie ma** bezpiecznego exact matcha w formie, której naprawdę chce ten plan, bo oficjalny bieżący dostęp do **PR1** jest ograniczony do **Pico do Areeiro ↔ Pedra Rija**, podczas gdy oficjalny smarttour Komoot dla PR1 nadal modeluje pełny trawers **Areeiro–Pico Ruivo**. Dni krajobrazowo-regeneracyjne lepiej reprezentować jako **driving GPX z punktami stop**, a nie fałszywe pętle hikingowe. Nie dodaję obiektów tras dla **D1**, **D8** ani miejskiego backupu **Monte/Funchal**, bo ta wersja planu trzyma je jako operacyjne/warunkowe, a nie jako kanoniczne moduły tras.

---

## Section 1 — Route extraction from plan

Wyciągnięte z załadowanego planu; ujęte są tylko elementy faktycznie niosące routing. fileciteturn0file0

| Day | Activity block | Route intent | Route category | Priority level | Conditionality | Matching keywords |
| --- | --- | --- | --- | --- | --- | --- |
| D2 | Areeiro -> Ninho da Manta -> Pedra Rija -> return | Restricted PR1 access logic from parking, with sunrise/viewpoint emphasis | Short mountain out-and-back / restricted trail segment | Core | Conditional on official PR1 access | Pico do Areeiro, Ninho da Manta, Pedra Rija, PR1 restricted |
| D2 | Eira do Serrado | Short hotel-side path to viewpoint | Viewpoint approach | Secondary add-on | Flexible add-on | Eira do Serrado, Estalagem, viewpoint path |
| D3 | Ponta do Rosto sunrise | Parking-to-viewpoint sunrise access | Short viewpoint walk | Optional high-value add-on | Only if sleep/sunrise gate is passed | Ponta do Rosto, sunrise, São Lourenço viewpoint |
| D3 | PR8 Baía d'Abra -> Casa do Sardinha -> return | Official PR8 baseline; no boat-return logic | Full hike / official out-and-back | Core | Weather/wind conditional; boat-return excluded | PR8, Vereda da Ponta de São Lourenço, Baía d'Abra, Casa do Sardinha |
| D4 | Cabo Girão -> Câmara de Lobos -> Madalena do Mar | Low-cardio stop sequence | Scenic drive with short stops | Recovery-day core | Flexible / low-energy default | Cabo Girão, Câmara de Lobos, Madalena do Mar |
| D4 | Madalena do Mar banana stroll | Flat banana-grove loop if energy is still good | Short easy walk | Optional | Energy-dependent | Rota de Banana, Madalena do Mar |
| D5 | Ribeiro Frio -> Balcões -> return | Official PR11 out-and-back | Short official out-and-back | Core | Visibility/weather conditional | PR11, Vereda dos Balcões, Ribeiro Frio |
| D5 | Rocha do Navio | Upper viewpoint; optional cable-car lower add-on | Viewpoint/cable-car access | Conditional add-on | Only if cable car works and day is flowing | Rocha do Navio, cable car, Santana |
| D5 | PR9.1 Queimadas -> Pico das Pedras | Sheltered forest backup only | Accessible forest route / backup | Backup only | Official-status conditional | PR9.1, PR JOEL, Um caminho para todos, Queimadas, Pico das Pedras |
| D6 | Seixal -> Véu da Noiva -> Porto Moniz | Low-cardio north-west stop sequence | Scenic drive with short stops | Core | Sea-state conditional for water only | Seixal, Véu da Noiva, Porto Moniz pools |
| D7 | Achadas da Cruz -> Garganta Funda -> Ponta do Pargo | West-end stop sequence with one short trail and one cable-car decision point | Scenic drive + cable car + short access trail | Core | Cable car/wind/waterfall conditional | Achadas da Cruz, Garganta Funda, Ponta do Pargo lighthouse |

Celowo pakuję D6 i D7 jako driving GPX zamiast produkować stado pseudo-tras po 200 m. To jest zgodne z własną logiką planu: nie prze-routowywać recovery days. Pełne **PR9** zostaje poza głównym patchem: oficjalna strona obecnie oznacza odcinek między **Caldeirão Verde** a **Caldeirão do Inferno** jako **CLOSED**, a plan traktuje **PR9 / PR9.1** jako obszar do sprawdzenia dzień wcześniej, nie jako twarde zobowiązanie. 

---

## Section 2 — Route augmentation

### [Day 2] Areeiro restricted access (Ninho da Manta + Pedra Rija)
- **Plan intent:** Sunrise at Pico do Areeiro, quick Ninho da Manta stop, continue only to Pedra Rija if the currently allowed PR1 section is open, then backtrack to the car. fileciteturn0file0
- **Komoot exact match found:** Partial
- **Komoot route name:** Candidate only: `Pico do Areeiro - Pedra Rija`; nearby exact sub-location card: `Ninho da Manta Viewpoint – Pico do Arieiro loop from Areeiro`
- **Komoot URL:** `https://www.komoot.com/de-de/tour/1843581600` ; nearby-route card page `https://www.komoot.com/highlight/221057`
- **Why it matches:** The official current PR1 access is restricted to **Pico do Areeiro ↔ Pedra Rija Belvedere (km 1.2)**, and **Ninho da Manta** sits only a few metres from the PR1 start, so the place identity is correct.
- **Warnings / mismatches:** The clean official Komoot PR1 smarttour still models the full **Areeiro–Pico Ruivo** traverse at about **11 km / 5:31**, so it contradicts the current restriction and the day logic. The user-recorded Pedra Rija candidate does not expose enough metadata in search to prove the same out-and-back logic, so it should not be treated as confirmed exact. Rejected alternate: `https://www.komoot.com/smarttour/e1375536065/pico-do-areeiro-and-pico-ruivo-pr1-vereda-do-areeiro-route-on-the-island-of-madeira`
- **Add to plan as:** Main D2 route via GPX fallback, not as a confirmed Komoot exact link
- **Confidence:** Medium
- **GPX fallback required:** Yes
- **GPX route spec:**
  - **Name:** `D2 Areeiro sunrise - Ninho da Manta - Pedra Rija (restricted out-and-back)`
  - **Type:** Mountain trail out-and-back
  - **Start:** Pico do Areeiro parking / PR1 trailhead
  - **End:** Pico do Areeiro parking / PR1 trailhead
  - **Via points:** Pico do Areeiro viewpoint -> Ninho da Manta -> PR1 stair/ridge section -> Pedra Rija Belvedere -> same way back
  - **Estimated distance:** `2.4–2.6 km`
  - **Estimated elevation:** `+150 to +190 m / -150 to -190 m`
  - **Estimated duration:** `1:10–1:40`
  - **Surface/terrain:** Stone steps, built mountain path, exposed ridge sections
  - **Notes:** Distance/elevation are inferred from the official restriction to km 1.2 and nearby Komoot route cards around Ninho/Pedra Rija. Do **not** continue beyond Pedra Rija unless the official status changes.
  - **Confidence:** Medium

### [Day 2] Eira do Serrado viewpoint access
- **Plan intent:** Short add-on after Areeiro; this is a viewpoint approach, not a second hike. fileciteturn0file0
- **Komoot exact match found:** No
- **Komoot route name:** None clean. Komoot surfaces a general highlight and broader cycling/hiking routes around Eira do Serrado, not the short hotel-side access path.
- **Komoot URL:** —
- **Why it matches:** Officially, access is via a short footpath that begins next to **Estalagem da Eira do Serrado**. That is exactly the day logic in the plan.
- **Warnings / mismatches:** Any Komoot loop that turns this into a real hike is the wrong object.
- **Add to plan as:** Short GPX viewpoint approach
- **Confidence:** High on intent, Medium on the exact walk geometry
- **GPX fallback required:** Yes
- **GPX route spec:**
  - **Name:** `D2 Eira do Serrado viewpoint access`
  - **Type:** Viewpoint approach
  - **Start:** Estalagem da Eira do Serrado parking
  - **End:** Eira do Serrado viewpoint / return
  - **Via points:** Parking -> signed footpath -> viewpoint platform -> same way back
  - **Estimated distance:** `0.4–0.8 km round trip`
  - **Estimated elevation:** `+40 to +70 m / -40 to -70 m`
  - **Estimated duration:** `10–20 min`
  - **Surface/terrain:** Short paved/stone footpath, uphill but non-technical
  - **Notes:** Keep this as an add-on only; skip it if visibility is flat after Areeiro.
  - **Confidence:** Medium

### [Day 3] Ponta do Rosto sunrise access
- **Plan intent:** Ultra-short sunrise stop before PR8, only if the sleep gate is met. fileciteturn0file0
- **Komoot exact match found:** No
- **Komoot route name:** None clean. The surfaced Komoot result is a much longer peninsula hike, not a parking-based sunrise micro-stop.
- **Komoot URL:** —
- **Why it matches:** Official viewpoint identity is clear: **Ponta do Rosto** on the São Lourenço peninsula, with north- and south-coast views from the eastern tip.
- **Warnings / mismatches:** Do not let Komoot turn this into an 8.88 km outing.
- **Add to plan as:** Optional micro-GPX only
- **Confidence:** High on intent, Medium on geometry
- **GPX fallback required:** Yes
- **GPX route spec:**
  - **Name:** `D3 Ponta do Rosto sunrise access`
  - **Type:** Short viewpoint walk
  - **Start:** Ponta do Rosto parking
  - **End:** Ponta do Rosto viewpoint / return
  - **Via points:** Parking -> viewpoint edge / rail -> same way back
  - **Estimated distance:** `0.1–0.4 km round trip`
  - **Estimated elevation:** `Minimal`
  - **Estimated duration:** `5–15 min`
  - **Surface/terrain:** Short paved/gravel viewpoint access
  - **Notes:** Operationally useful only for the sunrise version of D3; otherwise skip.
  - **Confidence:** Medium

### [Day 3] PR8 — Baía d'Abra to Casa do Sardinha
- **Plan intent:** PR8 in shortened/smart form, keeping the standard trail logic and explicitly excluding boat-return as the default execution mode. fileciteturn0file0
- **Komoot exact match found:** Yes
- **Komoot route name:** `Vereda da Ponta de São Lourenço — PR8 on the Island of Madeira`
- **Komoot URL:** `https://www.komoot.com/smarttour/e1375832832/vereda-da-ponta-de-sao-lourenco-pr8-on-the-island-of-madeira`
- **Why it matches:** Official PR8 is **OPEN**, officially runs **Baía d'Abra / Casa do Sardinha**, and is listed as **3 km + 3 km return**. Komoot’s official smarttour uses the same trail identity and very close route stats at **6.75 km / 2:04 / 230 m**, which fits the intended baseline.
- **Warnings / mismatches:** Official duration is **2:30** while Komoot shows **2:04**; that is a presentation difference, not a route mismatch. Boat-return remains excluded because it changes the route type and the car logistics.
- **Add to plan as:** Main D3 trail
- **Confidence:** High

### [Day 4] South recovery scenic drive
- **Plan intent:** Cabo Girão short stop, Câmara de Lobos coffee/lunch, Madalena do Mar, with recovery-day effort discipline. fileciteturn0file0
- **Komoot exact match found:** No
- **Komoot route name:** None clean. The surfaced Komoot objects around Cabo Girão are true hikes from Câmara de Lobos, not a low-cardio scenic stop sequence.
- **Komoot URL:** —
- **Why it matches:** Officially, **Cabo Girão** is a viewpoint/skywalk stop; the day logic is a scenic south-coast sequence, not a hiking module.
- **Warnings / mismatches:** Using a Komoot hike loop here would vandalize the point of D4.
- **Add to plan as:** Main D4 driving GPX scaffold
- **Confidence:** High for stop order, Medium for distance
- **GPX fallback required:** Yes
- **GPX route spec:**
  - **Name:** `D4 South recovery scenic drive - Cabo Girão / Câmara de Lobos / Madalena do Mar`
  - **Type:** Driving GPX with short stop points
  - **Start:** Rose Sun House / Canhas
  - **End:** Rose Sun House / Canhas
  - **Via points:** Cabo Girão parking/skywalk -> Câmara de Lobos harbour parking -> Madalena do Mar seafront parking -> optional Rota de Banana start -> Ponta do Sol / base sunset
  - **Estimated distance:** `60–80 km driving`
  - **Estimated elevation:** `Road profile only; hiking gain negligible`
  - **Estimated duration:** `5–7 h elapsed`
  - **Surface/terrain:** Paved roads; harbour promenade; flat seafront walking if desired
  - **Notes:** This GPX is intentionally a **stop sequence**, not a hike. If energy is low, cut the banana stroll first.
  - **Confidence:** Medium

### [Day 4] Rota de Banana, Madalena do Mar
- **Plan intent:** Flat banana-grove stroll only if energy is still good after the south-coast stops. fileciteturn0file0
- **Komoot exact match found:** Yes
- **Komoot route name:** `Rota de Banana – church loop from Madalena do Mar`
- **Komoot URL:** `https://www.komoot.com/de-de/tour/1801865266`
- **Why it matches:** Same named route/place, same start area, same easy loop logic, same recovery-day effort profile.
- **Warnings / mismatches:** This is a user-planned Komoot tour, not an official trail object. Keep it optional.
- **Add to plan as:** Optional micro-walk inside D4
- **Confidence:** Medium
- **Alternates:** `https://www.komoot.com/de-de/tour/2054582834` ; `https://www.komoot.com/de-de/tour/662118621`

### [Day 5] PR11 — Ribeiro Frio to Balcões
- **Plan intent:** Ribeiro Frio -> Balcões -> return as the main low-cardio forest/viewpoint route. fileciteturn0file0
- **Komoot exact match found:** Yes
- **Komoot route name:** `PR11 Vereda dos Balcões Trail`
- **Komoot URL:** `https://www.komoot.com/smarttour/e1375848179/pr11-vereda-dos-balcoes-trail`
- **Why it matches:** Official PR11 is **OPEN**, runs from **E.R. 103 (Ribeiro Frio)** to **Balcões**, and is **1.5 km + 1.5 km return**. Komoot’s official smarttour is the same trail at **2.89 km / 00:52 / 90 m**.
- **Warnings / mismatches:** None meaningful. The only real variable is visibility.
- **Add to plan as:** Main D5 trail
- **Confidence:** High

### [Day 5] Rocha do Navio conditional access
- **Plan intent:** Upper viewpoint first; cable car and a lower add-on only if the operation is running sensibly. fileciteturn0file0
- **Komoot exact match found:** Partial
- **Komoot route name:** `Weg zum Aussichtspunkt und Strand Rocha do Navio`; alternate lower add-on: `Madeira: Faja da Rocha do Navio - Rückweg mit der Seilbahn`
- **Komoot URL:** `https://www.komoot.com/de-de/highlight/6591641`
- **Why it matches:** Komoot does have the short upper approach to the viewpoint/beach access at roughly **210 m**, and separately a short lower route with **cable car return** at **1.28 km / 00:31**.
- **Warnings / mismatches:** Komoot does not surface one clean route object that exactly bundles **upper viewpoint + optional cable car + optional lower stroll** in the same conditional shape as the plan.
- **Add to plan as:** Conditional add-on, not a base route
- **Confidence:** Medium-Low
- **GPX fallback required:** Yes
- **GPX route spec:**
  - **Name:** `D5 Rocha do Navio upper viewpoint access`
  - **Type:** Viewpoint access / cable-car decision point
  - **Start:** Rocha do Navio upper parking / cable car station
  - **End:** Rocha do Navio upper parking / cable car station
  - **Via points:** Upper station -> upper viewpoint path -> decision point: cable car if running -> optional lower station short promenade -> return by cable car
  - **Estimated distance:** `0.2–0.4 km walking on top; optional lower stroll 0.8–1.3 km`
  - **Estimated elevation:** `Top spur about -90 m / +10 m; lower stroll negligible`
  - **Estimated duration:** `10–20 min top only; 30–50 min with cable car + lower stroll`
  - **Surface/terrain:** Short paved/stepped upper path; cable car transfer; flat/littoral lower promenade if added
  - **Notes:** GPX covers only the safe/explicit top access. Keep the lower branch conditional.
  - **Confidence:** Medium

### [Day 5] PR9.1 backup — Queimadas to Pico das Pedras
- **Plan intent:** Backup-only sheltered forest option; not a silent swap for full PR9. fileciteturn0file0
- **Komoot exact match found:** Partial
- **Komoot route name:** `Madeira PR Joel (Un caminho para todos)`
- **Komoot URL:** `https://www.komoot.com/de-de/tour/1073689799`
- **Why it matches:** Official PR9.1 is **OPEN**, runs between **Queimadas Park / Pico das Pedras**, and is **1.9 km / 45 min** one way. Komoot’s user-recorded PR JOEL listing clearly references the same route identity and shows **3.72 km / 01:06 / 70 m**, which is very close to a practical out-and-back execution.
- **Warnings / mismatches:** The Komoot listing is user-recorded, not the official PR9.1 smarttour, and search results do not expose clean start/end metadata. Also, full PR9 is **not** inserted.
- **Add to plan as:** Backup only
- **Confidence:** Medium-Low
- **GPX fallback required:** Yes
- **GPX route spec:**
  - **Name:** `D5 Backup - PR9.1 Queimadas to Pico das Pedras`
  - **Type:** Easy forest point-to-point, normally walked out-and-back
  - **Start:** Queimadas Park
  - **End:** Pico das Pedras
  - **Via points:** Queimadas houses / trailhead -> accessible forest path -> Pico das Pedras park -> optional return same way
  - **Estimated distance:** `1.9 km one way / 3.8 km return`
  - **Estimated elevation:** `+20 to +70 m / similar descent`
  - **Estimated duration:** `45 min one way / 1:10–1:30 return`
  - **Surface/terrain:** Wide accessible forest path / levada esplanade
  - **Notes:** Backup only. Do not silently morph this into full PR9.
  - **Confidence:** Medium

### [Day 6] North-west scenic drive — Seixal / Véu da Noiva / Porto Moniz
- **Plan intent:** A strong low-cardio scenic day; ocean entry only if conditions are perfect. fileciteturn0file0
- **Komoot exact match found:** No
- **Komoot route name:** None selected.
- **Komoot URL:** —
- **Why it matches:** The real objects are **Seixal Beach**, **Véu da Noiva Viewpoint**, and **Porto Moniz Natural Swimming Pools**. What does not exist is one exact Komoot route object that matches the intended scenic-drive execution.
- **Warnings / mismatches:** Adding Komoot promenade loops here would over-route the day.
- **Add to plan as:** Main D6 driving GPX scaffold
- **Confidence:** High for stop order, Medium for distance
- **GPX fallback required:** Yes
- **GPX route spec:**
  - **Name:** `D6 North-west scenic drive - Seixal / Véu da Noiva / Porto Moniz`
  - **Type:** Driving GPX with short stop points
  - **Start:** Rose Sun House / Canhas
  - **End:** Rose Sun House / Canhas
  - **Via points:** Seixal beach/pools parking -> Véu da Noiva viewpoint -> Porto Moniz natural pools parking -> short promenade / lunch zone -> return
  - **Estimated distance:** `95–110 km driving`
  - **Estimated elevation:** `Road profile only; walking gain negligible`
  - **Estimated duration:** `6–8 h elapsed`
  - **Surface/terrain:** Paved roads; beach access; viewpoint platform; promenade around pools
  - **Notes:** Water entry stays outside the GPX logic and remains a pure day-of-conditions decision.
  - **Confidence:** Medium

### [Day 7] West-end scenic drive — Achadas / Garganta Funda / Ponta do Pargo
- **Plan intent:** Achadas da Cruz with cable car only if running, then Garganta Funda in better light, then Ponta do Pargo at sunset. fileciteturn0file0
- **Komoot exact match found:** No
- **Komoot route name:** None selected.
- **Komoot URL:** —
- **Why it matches:** The day’s real objects are the **Achadas da Cruz cable car**, the **Garganta Funda** short path from Pedregal, and the **Ponta do Pargo Lighthouse Viewpoint**. Garganta Funda itself is effectively a short access walk, so a composite driving GPX is the right tool.
- **Warnings / mismatches:** Turning this into a west-coast hike day would break the “max payoff, minimal cardio” rule.
- **Add to plan as:** Main D7 driving GPX scaffold
- **Confidence:** High for stop order, Medium for distance
- **GPX fallback required:** Yes
- **GPX route spec:**
  - **Name:** `D7 West-end scenic drive - Achadas / Garganta Funda / Ponta do Pargo`
  - **Type:** Driving GPX with cable-car decision point and short access trail
  - **Start:** Rose Sun House / Canhas
  - **End:** Rose Sun House / Canhas
  - **Via points:** Achadas da Cruz upper station -> optional lower station via cable car -> short lower promenade turnpoint -> Pedregal parking -> Garganta Funda viewpoint -> Ponta do Pargo lighthouse viewpoint -> return
  - **Estimated distance:** `105–125 km driving + up to 2 km walking`
  - **Estimated elevation:** `Road profile only; Garganta path low gain; cable car handles the major vertical change`
  - **Estimated duration:** `10–12 h elapsed`
  - **Surface/terrain:** Paved roads; cable-car stations; short dirt/paved access path at Garganta Funda; lighthouse viewpoint access
  - **Notes:** If Achadas is off, delete that waypoint and keep the western spine of the day intact. Do not “replace” it with a hike.
  - **Confidence:** Medium

---

## Section 3 — Updated plan patch

Poniżej przepisałem tylko fragmenty planu, które faktycznie wymagają bloków tras. fileciteturn0file0

### Dzień 2 — 08.05, piątek — Areeiro + Eira do Serrado

**Route**
- Type: Restricted mountain out-and-back
- Exact Komoot match: Partial
- Link: `https://www.komoot.com/de-de/tour/1843581600` (candidate only; do not default to the full PR1 smarttour)
- Backup: viewpoint-only Areeiro + Ninho da Manta
- GPX needed: Yes
- Notes: Official current limit is **Pedra Rija Belvedere** only; **Ninho da Manta** lies a few metres from the start.

**Route**
- Type: Short viewpoint approach
- Exact Komoot match: No
- Link: —
- Backup: skip if visibility is flat or energy is low
- GPX needed: Yes
- Notes: Access is the short footpath starting beside **Estalagem da Eira do Serrado**.

### Dzień 3 — 09.05, sobota — Wschód / Ponta do Rosto / PR8

**Route**
- Type: Short sunrise viewpoint access
- Exact Komoot match: No
- Link: —
- Backup: skip if sunrise gate fails
- GPX needed: Yes
- Notes: Keep this as a micro-stop only, not a hike. The longer Komoot Ponta do Rosto routes are the wrong object.

**Route**
- Type: Official hike, out-and-back
- Exact Komoot match: Yes
- Link: `https://www.komoot.com/smarttour/e1375832832/vereda-da-ponta-de-sao-lourenco-pr8-on-the-island-of-madeira`
- Backup: east viewpoint-hopping + Machico
- GPX needed: No
- Notes: This matches the official **Baía d'Abra -> Casa do Sardinha -> return** logic. Boat-return remains a separate conditional service and is **not** part of this route.

### Dzień 4 — 10.05, niedziela — Południe / recovery day

**Route**
- Type: Scenic drive with short stops
- Exact Komoot match: No
- Link: —
- Backup: cut Cabo Girão or the banana stroll, but keep the day low-cardio
- GPX needed: Yes
- Notes: This day should stay a stop-sequence day: **Cabo Girão -> Câmara de Lobos -> Madalena do Mar**. Do not replace it with Cabo Girão Komoot hike loops.

**Route**
- Type: Optional flat micro-walk
- Exact Komoot match: Yes
- Link: `https://www.komoot.com/de-de/tour/1801865266`
- Backup: `https://www.komoot.com/de-de/tour/2054582834`
- GPX needed: No
- Notes: `Rota de Banana` fits only as an optional add-on.

### Dzień 5 — 11.05, poniedziałek — Ribeiro Frio / Balcões / Santana

**Route**
- Type: Official short hike, out-and-back
- Exact Komoot match: Yes
- Link: `https://www.komoot.com/smarttour/e1375848179/pr11-vereda-dos-balcoes-trail`
- Backup: PR9.1 only if Balcões loses the visibility battle
- GPX needed: No
- Notes: This is the clean exact match for **Ribeiro Frio -> Balcões -> return**.

**Route**
- Type: Conditional viewpoint/cable-car add-on
- Exact Komoot match: Partial
- Link: `https://www.komoot.com/de-de/highlight/6591641`
- Backup: upper viewpoint only
- GPX needed: Yes
- Notes: Treat **Rocha do Navio** as a top-access decision point first; the lower cable-car branch stays day-of conditional.

**Route**
- Type: Conditional forest backup
- Exact Komoot match: Partial
- Link: `https://www.komoot.com/de-de/tour/1073689799`
- Backup: same route as out-and-back GPX
- GPX needed: Yes
- Notes: **PR9.1** only. Full **PR9** is not inserted.

### Dzień 6 — 12.05, wtorek — Seixal / Véu da Noiva / Porto Moniz

**Route**
- Type: Scenic drive with short stops
- Exact Komoot match: No
- Link: —
- Backup: same stop sequence without water entry
- GPX needed: Yes
- Notes: Keep this as **Seixal -> Véu da Noiva -> Porto Moniz**. Do not inflate it into separate Komoot hikes.

### Dzień 7 — 13.05, środa — Zachód / Achadas / Garganta / Ponta do Pargo

**Route**
- Type: Scenic drive + cable-car decision point + short access trail
- Exact Komoot match: No
- Link: —
- Backup: skip Achadas if cable car/wind fail; keep **Garganta Funda + Ponta do Pargo**
- GPX needed: Yes
- Notes: **Garganta Funda** is the only real short trail here; **Ponta do Pargo** remains a sunset stop, not a hike.
