"""Ajudas para gerar galerias de imagens nas páginas (linhas com a mesma altura)."""
from PIL import Image
import numpy as np

def ratio(p):
    w, h = Image.open(p).size
    return w / h

def rows(paths, alts, per=3, gap=16):
    out = ''
    for k in range(0, len(paths), per):
        chunk = list(zip(paths[k:k + per], alts[k:k + per]))
        rs = [ratio(p) for p, _ in chunk]
        avg = sum(rs) / len(rs)
        cells = ''.join('<div style="flex: %.4f 1 0; min-width: 0;"><img src="%s" alt="%s" loading="lazy" style="display: block; width: 100%%; height: auto;"></div>' % (r, p, a) for (p, a), r in zip(chunk, rs))
        cells += ''.join('<div style="flex: %.4f 1 0;"></div>' % avg for _ in range(per - len(chunk)))
        out += '<div style="display: flex; gap: %dpx; margin-top: %dpx;">%s</div>\n' % (gap, gap, cells)
    return '<div style="position: relative; z-index: 6; margin-top: -%dpx;">\n%s</div>' % (gap, out)

def head(n, t, pal=None):
    dp = ' data-pal="%s"' % pal if pal else ''
    return ('<section%s style="padding: 96px 48px 0;">\n<div style="display: flex; align-items: baseline; gap: 20px; border-top: 1px solid var(--line); padding-top: 28px; margin-bottom: 32px;">'
            '<span style="font-size: 14px; color: var(--muted); letter-spacing: 0.08em;">%s</span><h3 style="margin: 0; font-family: \'Special Elite\', cursive; font-weight: 400; font-size: 28px; line-height: 1.1;">%s</h3></div>\n') % (dp, n, t)

def image(p, alt):
    return '<div style="position: relative; z-index: 6;"><img src="%s" alt="%s" loading="lazy" style="display: block; width: 100%%; height: auto;"></div>' % (p, alt)

def bbox_crop(im, thr=14):
    a = np.asarray(im.convert('L')).astype(float)
    cols = np.where((a > thr).mean(0) > 0.02)[0]
    rws = np.where((a > thr).mean(1) > 0.02)[0]
    return im.crop((cols[0] + 2, rws[0] + 2, cols[-1] - 1, rws[-1] - 1))

def save(im, path, w=1600, q=84):
    im = im.convert('RGB')
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(path, quality=q, method=6)
    return im.size
