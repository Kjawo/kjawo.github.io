"""Reproduce GPX from the reviewed OSM snapshot, without routing or interpolation.

The snapshot is a separate ODbL database in gpx/sources/osm-network.json.
Each output vertex must be an original OSM node; each consecutive edge must
belong to a documented source way for that route. No nearest-point joining.
"""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'gpx' / 'sources' / 'osm-network.json'
NS = 'http://www.topografix.com/GPX/1/1'


def reviewed_points(route_id, root=ROOT):
    data = json.loads((root/'gpx/sources/osm-network.json').read_text(encoding='utf-8'))
    route = data['routes'][route_id]
    edges = {tuple(sorted((a, b))) for wid in route['way_ids']
             for a, b in zip(data['ways'][str(wid)], data['ways'][str(wid)][1:])}
    ids = route['nodes']
    if ids[0] != ids[-1] or not all(tuple(sorted((a, b))) in edges for a, b in zip(ids, ids[1:])):
        raise ValueError(route_id + ': nieciągłe lub pozbawione źródła połączenie')
    return [tuple(data['nodes'][str(node)]) for node in ids], route


def write_gpx(route):
    points, review = reviewed_points(route['id'])
    ET.register_namespace('', NS)
    doc = ET.Element('gpx', {'xmlns': NS, 'version': '1.1', 'creator': 'Cypr2026 / reviewed OpenStreetMap ways'})
    meta = ET.SubElement(doc, 'metadata')
    ET.SubElement(meta, 'name').text = route['name']
    ET.SubElement(meta, 'desc').text = route['gpx']['note']
    credit = ET.SubElement(meta, 'copyright', {'author': 'OpenStreetMap contributors'})
    ET.SubElement(credit, 'license').text = 'https://opendatacommons.org/licenses/odbl/1-0/'
    ET.SubElement(meta, 'link', {'href': route['gpx']['source_url']})
    track = ET.SubElement(doc, 'trk')
    ET.SubElement(track, 'name').text = route['name']
    segment = ET.SubElement(track, 'trkseg')
    for lat, lon in points:
        ET.SubElement(segment, 'trkpt', {'lat': str(lat), 'lon': str(lon)})
    ET.indent(doc)
    (ROOT/route['gpx']['path']).write_bytes(ET.tostring(doc, encoding='utf-8', xml_declaration=True) + b'\n')


if __name__ == '__main__':
    data = json.loads((ROOT/'data/Cypr_2026_zrodlo_prawdy.json').read_text(encoding='utf-8'))
    for route in data['routes']:
        if route.get('gpx', {}).get('provenance') == 'gpx/sources/osm-network.json':
            write_gpx(route)
            print('GPX:', route['name'], route['gpx']['path'])
