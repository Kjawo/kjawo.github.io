"""Explicit task completeness, independent of the validator accepting null GPX.

The snapshot intentionally permits only the individually documented unresolved
Vouni and Timi 12 km. --require-all fails while any requested GPX is missing.
"""
import hashlib
import json
from pathlib import Path
import sys
from gpx import validate_routes

ROOT=Path(__file__).resolve().parent.parent
d=json.loads((ROOT/'data/Cypr_2026_zrodlo_prawdy.json').read_text(encoding='utf-8'))
assert len(d['places'])==50 and len(d['routes'])==8
for p in d['places']:
    assert p['coordinates'] and p['coordinates']['status']=='zweryfikowane',p['id']
    v=p['coordinate_verification']
    assert v['checked_on']=='2026-11-06' and v['point_kind'] in ['obiekt','wejscie','parking','poczatek_szlaku'],p['id']
    assert v['source_url']==p['coordinate_source_url'] and v['meaning']==p['map_kind'],p['id']
    assert str(p['coordinates']['lat']) in p['map_url'] and str(p['coordinates']['lon']) in p['map_url'],p['id']
results=validate_routes(d,ROOT)
ready=[r for r in d['routes'] if r['gpx']['path']]
missing=[r['id'] for r in d['routes'] if not r['gpx']['path']]
assert missing==['TR-VOUNI'],missing
assert len(ready)==7
for r in ready:
    g=r['gpx']
    assert hashlib.sha256((ROOT/g['path']).read_bytes()).hexdigest()==g['sha256'],r['id']
    assert g['provenance']=='gpx/sources/osm-network.json' and g['license'].startswith('ODbL-1.0')
    assert g['ascent_m'] is None and g['elevation_source'] is None
places={p['id']:p for p in d['places']}
day_counts=[]
for day in d['days']:
    base={pid for e in day['timeline'] for pid in e['place_ids']}
    primary=next((r for r in d['routes'] if r['id']==day['primary_route_id']),None)
    if primary:base.add(primary['start_place_id'])
    ids=base|{s['place_id'] for s in day['optional_stops']}
    assert all(places[pid]['coordinates'] for pid in ids)
    day_counts.append(len(ids))
assert day_counts==[4,8,5,4,5,5,3],day_counts
for b in d['cycling_options']['options']:
    assert b['gpx_local']['path'] is None and not b['gpx_local']['redistribution_confirmed']
    if b['id']=='CYCLE-TIMI-12':assert b['map']['status']=='unavailable' and b['gpx_url'] is None
    else:assert b['geometry_verification']['preview_points_ordered'] and b['map']['status']=='preview'
    assert not b['logistics_status']['rental_confirmed'] and not b['logistics_status']['return_with_bike_confirmed']
print('KOMPLETNOŚĆ: punkty 50/50; lokalne GPX piesze 7/8; podglądy rowerowe 2/3; pełne lokalne GPX rowerowe 0/3.')
print('NIEZREALIZOWANE: Vouni 9,8 km; Timi terenowe 12 km; zgoda na redystrybucję obu oficjalnych GPX rowerowych; logistyka rowerów. Publikacja GitHub/Cloudflare osobno.')
if '--require-all' in sys.argv:
    raise SystemExit(2 if missing or any(not b['gpx_local']['path'] for b in d['cycling_options']['options']) else 0)
print('PASS: zgodność z jawną listą braków; ten wynik nie oznacza pełnego ukończenia zadania.')
