"""Compare the two local publication layouts and ZIP; never contacts hosting."""
import hashlib
import json
from pathlib import Path
import zipfile
from build_pages import PUBLIC_FILES, PUBLIC_DIRS

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/'dist'
sha=lambda b:hashlib.sha256(b).hexdigest()
expected=[ROOT/name for name in PUBLIC_FILES]
for directory in PUBLIC_DIRS:
    expected.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
for source in expected:
    rel=source.relative_to(ROOT)
    assert sha(source.read_bytes())==sha((DIST/rel).read_bytes()),str(rel)
headers=(DIST/'_headers').read_text(encoding='utf-8')
assert '/gpx/aphrodite-akamas.gpx\n  Content-Type: application/gpx+xml' in headers
assert '/gpx/*\n  Content-Type:' not in headers
assert not (DIST/'_src').exists()
files={p.relative_to(DIST).as_posix():p for p in DIST.rglob('*') if p.is_file()}
with zipfile.ZipFile(ROOT/'cypr2026-pages.zip') as z:
    assert set(z.namelist())==set(files)
    for name,file in files.items():assert sha(z.read(name))==sha(file.read_bytes()),name
plan=json.loads((DIST/'data/Cypr_2026_zrodlo_prawdy.json').read_text(encoding='utf-8'))
assert len(list((DIST/'gpx').glob('*.gpx')))==sum(bool(r['gpx']['path']) for r in plan['routes'])==7
print(f'PASS: {len(files)} plików dist i ZIP, identyczne publiczne pliki GitHub/Cloudflare, 7 GPX, ODbL, PDF, ICS, SW i źródłowy JSON. To weryfikacja lokalna; mirror wymaga publikacji.')
