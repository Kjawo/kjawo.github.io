"""Validate local hiking tracks using only XML and geodesic distances."""
import math
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET


def haversine(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 6371000 * 2 * math.asin(min(1, math.sqrt(h)))


def read_track(path):
    xml = Path(path).read_text(encoding='utf-8-sig')
    if '<!DOCTYPE' in xml.upper():
        raise ValueError('GPX nie może zawierać DOCTYPE')
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise ValueError('Nieprawidłowy XML GPX') from exc
    segments = root.findall('.//{*}trkseg') or root.findall('.//{*}rte')
    if len(segments) != 1:
        raise ValueError('GPX musi zawierać jedną ciągłą linię (jeden segment)')
    points, elevations = [], []
    for node in segments[0]:
        if node.tag.split('}')[-1] not in {'trkpt', 'rtept'}:
            continue
        lat, lon = float(node.attrib['lat']), float(node.attrib['lon'])
        if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError('Nieprawidłowe współrzędne GPX')
        points.append((lat, lon))
        ele = node.find('{*}ele')
        value = float(ele.text) if ele is not None else None
        if value is not None and not math.isfinite(value):
            raise ValueError('Nieprawidłowa wysokość GPX')
        elevations.append(value)
    if len(points) < 2:
        raise ValueError('GPX wymaga przynajmniej dwóch punktów')
    return points, elevations


def validate_track(path, distance_km, start, loop=True, *, max_gap_m=100, allowed_retrace_m=200, trusted_elevation=False):
    points, elevations = read_track(path)
    steps = [haversine(a, b) for a, b in zip(points, points[1:])]
    length = sum(steps)
    low, high = distance_km if isinstance(distance_km, list) else (distance_km, distance_km)
    seen, run, longest = set(), 0, 0
    for a, b, step in zip(points, points[1:], steps):
        edge = tuple(sorted((tuple(round(x, 7) for x in a), tuple(round(x, 7) for x in b))))
        run = run + step if edge in seen else 0
        longest = max(longest, run)
        seen.add(edge)
    checks = {
        'length': low*850 <= length <= high*1150,
        'start': haversine(points[0], start) <= 300,
        'loop': not loop or haversine(points[0], points[-1]) <= 300,
        'gaps': max(steps) <= max_gap_m,
        'repeated_section': not loop or longest <= allowed_retrace_m,
    }
    ascent = None
    if trusted_elevation and all(e is not None for e in elevations):
        ascent, anchor = 0, elevations[0]
        for elevation in elevations[1:]:
            if abs(elevation-anchor) >= 5:
                ascent += max(0, elevation-anchor)
                anchor = elevation
    return {
        'passed': all(checks.values()), 'checks': checks,
        'length_km': round(length/1000, 3),
        'start_distance_m': round(haversine(points[0], start), 1),
        'closure_m': round(haversine(points[0], points[-1]), 1),
        'max_gap_m': round(max(steps), 1),
        'repeated_section_m': round(longest, 1), 'ascent_m': ascent,
    }


def validate_routes(data, root):
    places = {p['id']: p for p in data['places']}
    results = []
    for route in data['routes']:
        gpx = route.get('gpx', {})
        if 'path' not in gpx or not gpx.get('note'):
            raise ValueError(f"{route['id']}: wymagane gpx.path (lub null) i gpx.note")
        if gpx['path'] is None:
            results.append({'route': route['id'], 'path': None, 'note': gpx['note']})
            continue
        path = (root/gpx['path']).resolve()
        if root.resolve()/'gpx' not in path.parents or path.suffix.lower() != '.gpx':
            raise ValueError(f"{route['id']}: GPX musi być lokalnym plikiem w gpx/")
        if gpx.get('status') not in {'sprawdzony_automatycznie', 'zweryfikowany'}:
            raise ValueError(f"{route['id']}: brak automatycznej walidacji GPX")
        if not all(gpx.get(k) for k in ['source', 'license', 'checked_on']):
            raise ValueError(f"{route['id']}: brak źródła, licencji lub daty GPX")
        if gpx.get('sha256') and hashlib.sha256(path.read_bytes()).hexdigest() != gpx['sha256']:
            raise ValueError(f"{route['id']}: plik GPX różni się od sprawdzonej wersji SHA-256")
        coord = places[route['start_place_id']].get('coordinates')
        if not coord:
            raise ValueError(f"{route['id']}: brak współrzędnych startu")
        options = {}
        if gpx.get('provenance'):
            from route_sources import reviewed_points
            expected, review = reviewed_points(route['id'], root)
            points, _ = read_track(path)
            if points != expected:
                raise ValueError(f"{route['id']}: GPX różni się od sprawdzonych węzłów OSM")
            if not review.get('review'):
                raise ValueError(f"{route['id']}: brak oceny wariantu i ciągłości")
            options = {'max_gap_m': review.get('max_gap_m', 100), 'allowed_retrace_m': review.get('allowed_retrace_m', 200)}
        if gpx.get('elevation_source'):
            options['trusted_elevation'] = True
        result = validate_track(path, route['distance_km'], (coord['lat'], coord['lon']), route.get('shape', 'loop') == 'loop', **options)
        if not result['passed']:
            raise ValueError(f"{route['id']}: GPX odrzucony: {result}")
        if gpx.get('length_km') is None or abs(gpx['length_km']-result['length_km']) > .02:
            raise ValueError(f"{route['id']}: gpx.length_km nie odpowiada pomiarowi")
        if result['ascent_m'] is None and gpx.get('ascent_m') is not None:
            raise ValueError(f"{route['id']}: przewyższenie bez wysokości w GPX")
        results.append({'route': route['id'], 'path': gpx['path'], **result})
    return results
