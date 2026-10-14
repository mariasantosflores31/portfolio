"""Descarrega textos e imagens do portfolio antigo (Adobe) para import/<slug>/,
usando um browser real (Playwright). Corre no GitHub Actions."""
import os, re, json, traceback
from playwright.sync_api import sync_playwright
PAGES = {
  'ultimo-canto': 'copia-de-auto-de-fe-2',
  'se-eu-quiser-choro': 'copia-de-ultimo-canto',
  'auto-de-fe': 'auto-de-fe',
  'severa': 'copia-de-auto-de-fe',
  'os-terriveis': 'copia-de-so',
  'falta-sempre-qualquer-coisa': 'copia-de-os-terriveis',
  'so': 'copia-de-severa',
}
BASE = 'https://mariasantosflores.myportfolio.com/'
JS = r"""() => {
  const out = [];
  const stop = document.querySelector('.other-projects, .project-covers, footer');
  for (const im of document.querySelectorAll('img')) {
    if (stop && (stop.compareDocumentPosition(im) & Node.DOCUMENT_POSITION_FOLLOWING)) continue;
    if (stop && stop.contains(im)) continue;
    let best = null, bw = 0;
    const ss = im.getAttribute('data-srcset') || im.getAttribute('srcset') || '';
    for (const part of ss.split(',')) {
      const b = part.trim().split(/\s+/); if (!b[0]) continue;
      const w = parseInt((b[1] || '0').replace('w', '')) || 0;
      if (w >= bw) { bw = w; best = b[0]; }
    }
    best = best || im.getAttribute('data-src') || im.currentSrc || im.src;
    if (best && best.includes('cdn.myportfolio.com')) out.push(best);
  }
  return { imgs: out, text: document.body.innerText };
}"""
os.makedirs('import', exist_ok=True)
LOG = open('import/log.txt', 'w')
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36', viewport={'width': 1440, 'height': 900})
    pg = ctx.new_page()
    for slug, path in PAGES.items():
        try:
            out = os.path.join('import', slug); os.makedirs(out, exist_ok=True)
            r = pg.goto(BASE + path, wait_until='networkidle', timeout=90000)
            LOG.write('%s status %s\n' % (slug, r.status if r else '?'))
            for y in range(0, 40000, 700):
                pg.evaluate('y => window.scrollTo(0, y)', y); pg.wait_for_timeout(120)
            pg.wait_for_timeout(1500)
            data = pg.evaluate(JS)
            open(os.path.join(out, 'text.txt'), 'w').write(data['text'])
            seen, log = [], []
            for u in data['imgs']:
                if u in seen: continue
                seen.append(u)
            for n, u in enumerate(seen, 1):
                ext = re.search(r'\.(jpe?g|png|gif|webp)', u.lower()); ext = ext.group(1) if ext else 'jpg'
                fn = '%02d.%s' % (n, ext)
                try:
                    resp = ctx.request.get(u, timeout=60000)
                    open(os.path.join(out, fn), 'wb').write(resp.body()); log.append({'file': fn, 'url': u, 'status': resp.status})
                except Exception as e:
                    log.append({'file': None, 'url': u, 'error': str(e)})
            json.dump(log, open(os.path.join(out, 'images.json'), 'w'), indent=1)
            LOG.write('%s %d imagens\n' % (slug, len(seen)))
        except Exception:
            LOG.write(slug + '\n' + traceback.format_exc() + '\n')
        LOG.flush()
    b.close()
