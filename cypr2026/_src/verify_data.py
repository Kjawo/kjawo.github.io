"""Check generated data/HTML/ICS consistency without additional packages."""
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import copy
from urllib.parse import urlsplit, unquote
from gpx import validate_routes

ROOT = Path(__file__).resolve().parent.parent
p = json.loads((ROOT/'data/Cypr_2026_zrodlo_prawdy.json').read_text(encoding='utf-8'))
html = (ROOT/'index.html').read_text(encoding='utf-8')
embedded = re.search(r'<script type="application/json" id="cypr-data">(.*?)</script>', html, re.S).group(1)
assert json.loads(embedded.replace('<\\/', '</')) == p
assert p['trip']['car']['pickup_agreed_at'] == '2026-11-07T10:30:00+02:00'
assert p['trip']['car']['return_agreed_at'] == '2026-11-13T03:30:00+02:00'
assert p['trip']['car']['total_price_eur'] == 325.5
assert next(e for e in p['days'][6]['timeline'] if e['id']=='D7-03')['start_local'] == '02:40'
assert p['trip']['return_deadlines']['baggage_closes'] == '05:20'
assert p['trip']['return_deadlines']['gate_closes'] == '05:50'

def dt(value):
    key, value = value.split(':', 1)
    if 'VALUE=DATE' in key:
        return datetime.strptime(value, '%Y%m%d').replace(tzinfo=ZoneInfo('Asia/Nicosia'))
    if value.endswith('Z'):
        return datetime.strptime(value, '%Y%m%dT%H%M%SZ').replace(tzinfo=ZoneInfo('UTC'))
    zone = key.split('TZID=')[-1]
    return datetime.strptime(value, '%Y%m%dT%H%M%S').replace(tzinfo=ZoneInfo(zone))

all_events = {}
major,minor,patch = map(int, p['meta']['version'].split('.'))
sequence = major*1000000 + minor*1000 + patch
for file in sorted((ROOT/'cal').glob('*.ics')):
    raw = file.read_bytes()
    assert b'\r\n' in raw, file
    assert all(len(line)<=75 for line in raw.split(b'\r\n')), file
    text = raw.decode('utf-8').replace('\r\n ', '').replace('\r\n\t','')
    assert 'Brak potwierdzonej rezerwacji' not in text, file
    events = re.findall(r'BEGIN:VEVENT\r\n(.*?)END:VEVENT', text, re.S)
    ids = []
    for event in events:
        lines=event.split('\r\n')
        uid=next(x[4:] for x in lines if x.startswith('UID:'));ids.append(uid)
        start=next(x for x in lines if x.startswith('DTSTART'))
        end=next(x for x in lines if x.startswith('DTEND'))
        assert f'SEQUENCE:{sequence}' in lines, (file,uid)
        assert dt(start)<dt(end), (file,uid)
        if uid in all_events: assert all_events[uid]==event, (file,uid)
        all_events[uid]=event
    assert len(ids)==len(set(ids)),file
assert 'DTSTART:20261107T083000Z' in all_events['cypr2026-car-pickup@kjawo.github.io']
assert 'DTSTART:20261113T013000Z' in all_events['cypr2026-car-return@kjawo.github.io']
assert 'DTSTART:20261107T044000Z' in all_events['cypr2026-FL-OUT@kjawo.github.io']
assert 'DTSTART:20261113T042000Z' in all_events['cypr2026-FL-IN@kjawo.github.io']
assert 'DTEND:20261113T074500Z' in all_events['cypr2026-FL-IN@kjawo.github.io']
places={x['id']:x for x in p['places']}
for day in p['days'][:6]:
    for event in day['timeline']:
        assert all(places[id]['coordinates'] for id in event['place_ids']), event['id']
for id in ['POI-HOTEL','POI-PARK','POI-ARTEMIS','POI-HARBOUR','POI-SOLOMONI','POI-POLIS','POI-HONDROS','POI-MOUSTAKALLIS','POI-KATOI']:
    place=places[id];assert place.get('coordinate_source_url'), id
    assert str(place['coordinates']['lat']) in place['map_url'],id
photos=json.loads((ROOT/'data/photos.json').read_text(encoding='utf-8'))['photos']
by={x['slot']:x for x in photos}
assert by['place-faros-c']['target']['id']=='POI-ALYKES'
assert all(by[id]['target']['id']=='POI-CHOIROKOITIA-VILLAGE' for id in ['place-choirokoitia-b','place-choirokoitia-c'])
assert 'PTFS' not in by['day-07-b']['source_url']
assert 'ulica' in by['place-pissouri-b']['caption']
worker=(ROOT/'sw.js').read_text(encoding='utf-8')
for photo in photos:
    small=next(v for v in photo['files'] if v['width']==480)
    assert small['jpeg'] in worker, photo['slot']
    for v in photo['files']:
        for fmt in ['avif','webp','jpeg']:
            if v.get(fmt): assert (ROOT/v[fmt]).is_file(),v[fmt]
assert './cypr2026-handbook.pdf' in worker
assert './cypr2026-print.pdf' not in re.search(r'const PRECACHE_URLS = (\[.*?\]);',worker,re.S).group(1)
gpx_results = validate_routes(p,ROOT)
for r in p['routes']:
    if r['gpx']['path']: assert './'+r['gpx']['path'] in worker
assert 'assets/vendor/leaflet/leaflet.js' in worker
assert 'assets/vendor/leaflet/leaflet.css' in worker
precache = json.loads(re.search(r'const PRECACHE_URLS = (\[.*?\]);',worker,re.S).group(1).replace(',\n]', '\n]'))
precache_bytes = sum((ROOT/(unquote(urlsplit(url).path).removeprefix('./') or 'index.html')).stat().st_size for url in precache)
assert precache_bytes < 25_000_000, precache_bytes
exports = json.loads((ROOT/'data/exports.json').read_text(encoding='utf-8'))
assert exports['version'] == p['meta']['version']
asset_hash = re.search(r'<meta name="cypr-asset-version" content="([^"]+)"',html).group(1)
assert exports['build_hash'] == asset_hash
assert f'<strong data-build-hash>{asset_hash}</strong>' in html
for name,digest in exports['sha256'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
for issue in p['open_issues']:
    assert 'resolved_on' in issue and 'resolution' in issue
assert p['meta']['version'] == '1.4.0'
assert p['days'][3]['timeline'][1]['start_local'] == '07:00'
assert p['days'][3]['timeline'][3]['start_local'] == '09:30'
for name in ['index.html','cypr2026-handbook.html']:
    rendered = (ROOT/name).read_text(encoding='utf-8')
    for text in ['1.4.0','Paphos General Hospital','Polis Chrysochous Hospital','Kyperounta Hospital','WPISZ: sektor, klucze','WPISZ','EKUZ','NRC','typ G']:
        assert text in rendered,(name,text)
print(f'PASS: GPX validation ({len(gpx_results)} routes), export SHA-256 / build hash, precache {precache_bytes:,} B / {len(precache)} URLs (< 25 MB).')
from build import Plan, render_todo, nearest_issue
resolved_data = copy.deepcopy(p)
for issue in resolved_data['open_issues']:
    issue['resolved_on'] = '2026-11-06'
    issue['resolution'] = 'Synthetic renderer test only'
resolved_plan = Plan(resolved_data)
assert not resolved_plan.blocking_issues
assert nearest_issue(resolved_plan) is None
assert render_todo(resolved_plan).count('issue-card--resolved') == len(p['open_issues'])
assert 'Synthetic renderer test only' in render_todo(resolved_plan)
assert 'status--otwarte' not in render_todo(resolved_plan)
print(f'PASS: embedded JSON, {len(all_events)} calendar events / 8 ICS, booking times, base map coverage, {len(photos)} photos and precache.')
