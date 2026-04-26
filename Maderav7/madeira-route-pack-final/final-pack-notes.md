# Madeira 2026 final merged route pack

Base archive: `madeira-route-pack-pro.zip`.
Merged features: stronger GPX import labels and conditional cable-car handling from `madeira-route-pack-thinking.zip`.

## Route IDs covered

- D2-AREEIRO: restricted Areeiro fallback GPX/GeoJSON only; not full PR1.
- D2-EIRA: Eira do Serrado viewpoint access GPX/GeoJSON.
- D3-ROSTO: optional sunrise micro-access GPX/GeoJSON.
- D3-PR8: exact Komoot primary GPX/GeoJSON from downloaded export.
- D4-DRIVE: south recovery stop-sequence GPX/GeoJSON.
- D4-BANANA: optional exact Komoot link.
- D5-PR11: exact Komoot primary GPX/GeoJSON from downloaded export.
- D5-ROCHA: conditional module.
- D5-ROCHA-UPPER: upper access GPX/GeoJSON.
- D5-ROCHA-LOWER-OPTIONAL: manifest-only, no GPX.
- D5-PR91: PR9.1 backup-only GPX/GeoJSON.
- D6-DRIVE: north-west scenic stop-sequence GPX/GeoJSON.
- D7-DRIVE: west-end scenic stop-sequence GPX/GeoJSON.

## Merge rules preserved

- D2 is Pico do Areeiro -> Ninho da Manta -> Pedra Rija -> return only.
- PR8 and PR11 remain exact Komoot route objects and now include local GPX/GeoJSON geometry.
- PR9.1 is backup-only and never replaces PR9 silently.
- D4, D6, and D7 are scenic drive stop-sequences, not pseudo-hikes.
- Rocha do Navio keeps upper-sure / lower-conditional semantics.
- Public-facing drive files use a Canhas / Ponta do Sol public base anchor, not a private accommodation pin.
