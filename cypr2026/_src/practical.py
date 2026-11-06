"""Shared HTML fragments for the page and the compact handbook."""
from html import escape


def hospitals_html(emergency):
    cards = []
    for hospital in emergency.get('hospitals', []):
        phone = hospital.get('phone')
        contact = f'<a href="tel:{escape(phone)}">{escape(phone)}</a>' if phone else 'telefon: do_potwierdzenia'
        coord = hospital.get('coordinates')
        gps = f"{coord['lat']}, {coord['lon']}" if coord else 'współrzędne: do_potwierdzenia'
        source = hospital.get('source_url')
        source_link = f' · <a href="{escape(source)}">Źródło kontaktu</a>' if source else ''
        cards.append(f'<article class="hospital"><h4>{escape(hospital["name"])}</h4>'
                     f'<p>{escape(hospital.get("address") or "Adres: do_potwierdzenia")} · {contact}<br>{escape(gps)}</p>'
                     f'<p>{escape(hospital.get("note", ""))}</p>'
                     f'<p class="fine-print">{escape(hospital["status"])} · {escape(hospital.get("checked_on", ""))}{source_link}</p></article>')
    return '<div class="hospitals">' + ''.join(cards) + '</div>'


def assistance_html(emergency):
    return '<p><b>Assistance polisy:</b> ' + escape(emergency.get('insurance_assistance_phone') or 'WPISZ') + '<br><b>Assistance auta:</b> ' + escape(emergency.get('car_assistance_phone') or 'WPISZ') + '</p>'


def extensions_html(plan, day):
    cards = []
    for extension in day.get('extensions', []):
        item = plan.routes.get(extension.get('route_id')) or plan.alternatives.get(extension.get('alternative_id'))
        if not item:
            continue
        conditions = ''.join('<li>' + escape(s) + '</li>' for s in extension['conditions'])
        warning = '' if item.get('gpx', {}).get('path') else '<p class="extension-warning">' + escape(plan.raw['route_ui']['unavailable_extension']) + '</p>'
        cards.append('<section class="day-extension"><h4>Wydłużenie — decyzja na parkingu</h4><p><b>' + escape(item['name']) + '</b></p><ul>' + conditions + '</ul>' + warning + '</section>')
    return ''.join(cards)
