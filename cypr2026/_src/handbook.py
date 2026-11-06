"""Generate a compact, printable handbook from the same canonical plan."""
from html import escape as esc
from pathlib import Path


def render_handbook(plan, canonical):
    p = plan.raw
    pages = []

    def page(title, body):
        pages.append(f'<section class="sheet"><header>CYPR 2026 · {esc(plan.meta["version"])} · {esc(plan.meta["updated_on"])}</header><h1>{esc(title)}</h1>{body}</section>')

    def para(label, text):
        return f'<p><b>{esc(label)}:</b> {esc(text)}</p>'

    def listing(items):
        return '<ul>' + ''.join('<li>' + esc(str(s)) + '</li>' for s in items) + '</ul>'

    car = p['trip']['car']
    hotel = plan.places[p['trip']['hotel']['place_id']]
    flights = [f"{f['flight_no']} · {int(f['departure_at'][8:10])} XI · {f['departure_airport']} {f['departure_at'][11:16]} → {f['arrival_airport']} {f['arrival_at'][11:16]} (czasy lokalne lotnisk)" for f in p['trip']['flights']]
    amount = f"{car['total_price_eur']:.2f}".replace('.', ',') + ' EUR'
    car_details = f"{car['provider']} · {car['vehicle_class']} {car['transmission']} · {amount}" + (' prepaid' if car.get('prepaid') else '')
    return_events = {e['id']:e for e in plan.day_list[-1]['timeline']}
    limits = p['trip']['return_deadlines']
    return_times = (f"{return_events['D7-01']['start_local']} pobudka → {return_events['D7-02']['start_local']} wyjście z pokoju → "
                    f"{return_events['D7-03']['start_local']} wyjazd → {car['return_agreed_at'][11:16]} zwrot umówiony → "
                    f"{limits['baggage_target_start']}–{limits['baggage_target_end']} cel nadania → {limits['gate_target']} cel bramki.")
    page('7–13 listopada · Pafos', '<p class="lead">Dwa trekkingi, spokojny początek, lekki czwartek. Godziny na Cyprze: Asia/Nicosia (UTC+2); Polska: Europe/Warsaw (UTC+1).</p>'
         + '<h2>Rezerwacje</h2>' + listing(flights + [
             f"{hotel['name']} · {p['trip']['hotel']['check_in_date']} – {p['trip']['hotel']['check_out_date']} · {p['trip']['nights']} nocy",
             car_details + '; model niegwarantowany',
             f"Odbiór umówiony {int(car['pickup_agreed_at'][8:10])} XI {car['pickup_agreed_at'][11:16]}. {car['pickup_plan_window']['note']}",
             f"Zwrot umówiony {int(car['return_agreed_at'][8:10])} XI {car['return_agreed_at'][11:16]}. {car['return_plan_window']['note']}"])
         + '<h2>Nocny powrót</h2><p class="important">' + esc(return_times) + f'</p><p><b>Granice:</b> bag drop {esc(limits["baggage_closes"])}, zamknięcie bramki {esc(limits["gate_closes"])}. To granice, nie cele przyjścia. Opóźnienie lotu samo ich nie przesuwa.</p>'
         + '<h2>Kontakty</h2>' + para('Alarm', '112') + para('Hotel', hotel['address'] + ' · ' + hotel['phone'])
         + para('Petsas PFO', '+357 26 423046') + para('Petsas — publiczny numer awaryjny', '+357 24 643350 (24 h; warunki assistance do potwierdzenia)')
         + '<p>Dokumenty i numery rezerwacji trzymaj osobno. Statusy „do potwierdzenia” wymagają rzeczywistej odpowiedzi; odhaczenie checklisty nie potwierdza faktu.</p>'
         + f'<p>Pełny plan i źródła: <a href="{esc(canonical)}">{esc(canonical)}</a></p>')

    for d in plan.day_list:
        brief = d['morning_brief']
        place = plan.places[brief['next_place_id']]
        coords = place.get('coordinates')
        gps = f" · GPS {coords['lat']}, {coords['lon']}" if coords else ''
        body = para('Program', brief['program']) + para('Rano', brief['weather_decision'])
        body += f'<p><b>Nawigacja:</b> <a href="{esc(place["map_url"])}">{esc(place["name"])}</a>{esc(gps)}<br><small>{esc(place.get("map_kind", ""))}</small></p>'
        body += '<table><thead><tr><th>Godzina CY*</th><th>Plan</th></tr></thead><tbody>'
        for e in d['timeline']:
            times = e['start_local'] + ('–' + e['end_local'] if e.get('end_local') else '')
            if e.get('timezone') == 'Europe/Warsaw': times += ' PL'
            body += f'<tr><td>{esc(times)}</td><td><b>{esc(e["title"])}</b>{" · opcja" if e.get("optional") else ""}<br>{esc(e["description"])}</td></tr>'
        body += '</tbody></table>' + para('Rezygnujemy kolejno', ' → '.join(d['cut_order']))
        body += '<p><small>*Czas Cypru, oprócz jawnie oznaczonych godzin PL. Przejazdy i okna są szacunkami; loty i umówione terminy z materiału użytkownika. Pełne scenariusze i źródła w planie.</small></p>'
        page(d['date'][8:] + ' XI · ' + d['title'], body)

    for id in ['TR-APHRODITE', 'TR-ARTEMIS']:
        r = plan.routes[id]
        start = plan.places[r['start_place_id']]
        body = para('Pętla', (str(r['distance_km'][0]) if r['distance_km'][0] == r['distance_km'][1] else '–'.join(map(str, r['distance_km']))) + ' km · oficjalna trudność ' + str(r['official_difficulty']) + '/3')
        body += para('Opis', r['description']) + f'<p><b>Start:</b> <a href="{esc(start["map_url"])}">{esc(start["name"])}</a></p>' + para('Dojazd i punkt', start['notes'])
        body += '<h2>Przed wyjściem</h2>' + listing(r['activation']) + '<h2>Rezygnacja</h2>' + listing(r['cancel'])
        body += '<h2>Na trasie</h2>' + listing(r['risks'] + r['notes'])
        body += '<p><b>Prowiant, własna woda, warstwa od wiatru i czołówka.</b> Brak załączonego GPX i zweryfikowanej sumy podejść. Sprawdzić konkretny przebieg, otwarcie, pogodę i mapy polowań. 8 i 11 XI bez trekkingu.</p>'
        page('Trasa · ' + r['name'], body)

    # Two short option sheets keep alternatives separate from the base week.
    options = [a for a in plan.alternative_list if a['id'] not in {'ALT-EAST-COMBO','ALT-SUNDAY'}]
    for index, group in enumerate([options[:8], options[8:]]):
        body = '<p>Wybierz zamiennik kosztem wskazanego punktu; czwartek domyślnie na odpoczynek. Czasy są szacunkami.</p>'
        for a in group:
            body += f'<h2>{esc(a["name"])}</h2>' + para('Zamiast / dodatek', '; '.join(a['replaces'])) + '<p>' + esc(a['schedule']) + '</p>'
            if a['id']=='ALT-NORTH-VAROSHA': body += '<p><b>Północ:</b> pisemna zgoda Petsas i zakres ochrony auta/OC/assistance do potwierdzenia. Polisa na przejściu nie rozstrzyga ochrony auta.</p>'
        page('Dodatki i zamienniki · ' + str(index+1), body)

    page('Pytania i przygotowanie', '<h2>Do Petsas — do potwierdzenia</h2>' + listing([i['action'] for i in p['open_issues'] if i['id'] in {'TODO-PETSAS-PICKUP','TODO-CAR','TODO-RETURN','TODO-NORTH-CAR'}])
         + '<h2>Do hotelu / kontrola vouchera</h2>' + listing([i['action'] for i in p['open_issues'] if i['id'] in {'TODO-PARKING','TODO-HOTEL-MEALS'}])
         + '<h2>Decyzje i pakowanie</h2>' + listing(['☐ Ustalić dojazd do WMI i powrót z WAW, w tym odzyskanie auta pozostawionego przy innym lotnisku.','☐ Dokumenty, prawo jazdy, karta pokładowa offline, warunki najmu i pisemne instrukcje.','☐ Paliwo po ostatniej dalszej jeździe, paragon, jedzenie na drogę, bagaż gotowy przed wieczorem 12 XI.','☐ Osobno pobrać mapy Cypru i Troodos; mapa strony nie działa jako nawigacja offline.']))

    ids=['SRC-AUDIT-20261106','SRC-HOTEL-MAP','SRC-ARTEMIS','SRC-ARTEMIS-FLYER','SRC-PARK','SRC-RYANAIR-60','SRC-RYANAIR-GATE','SRC-PET','SRC-PETSAS-LOCATIONS','SRC-OSM-POINTS']
    body = '<p>Rezerwacje pochodzą z materiałów użytkownika; procedury usługodawców i gotowość terenowa pozostają do potwierdzenia. Korekty harmonogramu i opcje pochodzą z zaakceptowanego audytu 6 XI 2026. Świeżo odczytane lokalizacje mają źródła przy miejscach w pełnym planie.</p>'
    for id in ids:
        s=plan.sources.get(id)
        if s:
            body+=f'<h2>{esc(s["title"])}</h2><p>{esc(s.get("scope", ""))}</p>'
            if s.get('url'): body+=f'<p class="url"><a href="{esc(s["url"])}">{esc(s["url"])}</a></p>'
    body+=f'<p>Pełna tabela źródeł, zdjęcia i licencje: <a href="{esc(canonical)}#zrodla">{esc(canonical)}#zrodla</a>. Pełny PDF: cypr2026-print.pdf. Niniejszy skrót: cypr2026-handbook.pdf.</p>'
    page('Źródła i zakres skrótu', body)
    css = '''@page{size:A4;margin:12mm 13mm 15mm}*{box-sizing:border-box}body{margin:0;color:#173b3f;font:10pt/1.28 Arial,sans-serif}h1{font:22pt Georgia,serif;margin:4mm 0}h2{font-size:11pt;margin:3mm 0 1mm}p{margin:1.5mm 0}a{color:#174c58;overflow-wrap:anywhere}header{font-size:8pt;color:#555;border-bottom:1px solid #aaa;padding-bottom:2mm}.sheet{break-before:page}.sheet:first-child{break-before:auto}ul{margin:1mm 0;padding-left:5mm}li{margin:1mm 0}table{border-collapse:collapse;width:100%;font-size:9pt}td,th{border-bottom:1px solid #ddd;padding:1.5mm;vertical-align:top;text-align:left}td:first-child{width:24mm;font-weight:bold}tr{break-inside:avoid}.important{padding:3mm;border:1px solid #888}.url{font-size:7.5pt;overflow-wrap:anywhere}.sheet:last-child{font-size:9pt;line-height:1.2}.sheet:last-child h2{font-size:10pt;margin-top:2mm}small{font-size:8pt}.lead{font-size:12pt}'''
    return '<!doctype html><html lang="pl"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Cypr 2026 — podręczny plan</title><style>' + css + '</style><body>' + ''.join(pages) + '</body></html>'
