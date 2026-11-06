"""Recreate local photo variants: python _src/photo_variants.py SLOT ORIGINAL.

Requires Pillow with AVIF/WebP support. Source attribution stays in photos.json.
"""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent


def make_variants(photo, original):
    image = ImageOps.exif_transpose(Image.open(original)).convert('RGB')
    photo['source_width'], photo['source_height'] = image.size
    ratio = {'3:2': 3/2, '4:3': 4/3, '16:9': 16/9, '4:5': 4/5}[photo['aspect']]
    max_width = min(image.width, int(image.height * ratio), 1920)
    if max_width < 800:
        raise ValueError('Source is too small for the required 800px variant')
    folder = ROOT / 'assets' / 'photos' / photo['slot']
    folder.mkdir(parents=True, exist_ok=True)
    variants = []
    for width in [w for w in (480, 800, 1280, 1920) if w <= max_width]:
        height = round(width / ratio)
        resized = ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS,
                               centering=(photo['focal_point']['x'], photo['focal_point']['y']))
        row = {'width': width, 'height': height}
        for fmt, extension, quality in [('avif', 'avif', 55), ('webp', 'webp', 72), ('jpeg', 'jpg', 78)]:
            target = folder / f'{photo["slot"]}-{width}.{extension}'
            budget = 45*1024 if width == 480 else (70*1024 if fmt == 'avif' and width == 800 else (120*1024 if width <= 1280 else 180*1024))
            while True:
                resized.save(target, format=fmt.upper(), quality=quality)
                if target.stat().st_size <= budget or quality <= 24:
                    break
                quality -= 4
            row.update({fmt: target.relative_to(ROOT).as_posix(), fmt+'_bytes': target.stat().st_size, fmt+'_quality': quality})
        variants.append(row)
    photo['files'] = variants
    photo['width'], photo['height'] = variants[-1]['width'], variants[-1]['height']
    photo['offline'] = variants[0]['jpeg']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slot')
    parser.add_argument('original', type=Path)
    args = parser.parse_args()
    manifest = ROOT/'data/photos.json'
    data = json.loads(manifest.read_text(encoding='utf-8'))
    photo = next(p for p in data['photos'] if p['slot'] == args.slot)
    make_variants(photo, args.original)
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
