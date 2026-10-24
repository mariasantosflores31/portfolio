"""Converte os stills (PNG 4K) descarregados do Drive em WebP leve para o site."""
import sys, re
from pathlib import Path
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
for p in sorted(src.rglob('*')):
    if p.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        continue
    m = re.search(r'(EP\d)_SEQC_(\d+)', p.name, re.I)
    name = ('%s-%s' % (m.group(1).lower(), m.group(2))) if m else re.sub(r'\W+', '-', p.stem.lower())
    im = Image.open(p).convert('RGB')
    if im.width > 2200:
        im = im.resize((2200, round(im.height * 2200 / im.width)), Image.LANCZOS)
    im.save(dst / (name + '.webp'), quality=84, method=6)
    print(p.name, '->', name + '.webp', im.size)
