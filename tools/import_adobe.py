"""Descarrega textos e imagens do portfolio antigo (Adobe) para import/<slug>/.
Corre no GitHub Actions (tem acesso à internet)."""
import os, re, json, urllib.request, html
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
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36'}
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
def best(tag):
    for attr in ('data-srcset', 'srcset'):
        m = re.search(attr + r'="([^"]+)"', tag)
        if m:
            cands = []
            for part in html.unescape(m.group(1)).split(','):
                bits = part.strip().split()
                if bits:
                    w = int(bits[1][:-1]) if len(bits) > 1 and bits[1].endswith('w') else 0
                    cands.append((w, bits[0]))
            if cands:
                return max(cands)[1]
    for attr in ('data-src', 'src'):
        m = re.search(attr + r'="([^"]+)"', tag)
        if m and 'cdn.myportfolio.com' in m.group(1):
            return html.unescape(m.group(1))
    return None
for slug, path in PAGES.items():
    out = os.path.join('import', slug)
    os.makedirs(out, exist_ok=True)
    page = get(BASE + path).decode('utf-8', 'replace')
    open(os.path.join(out, 'page.html'), 'w').write(page)
    # conteúdo do projeto termina antes de "You may also like"
    cut = page.find('other-projects')
    body = page[:cut] if cut > 0 else page
    seen, n, log = set(), 0, []
    for m in re.finditer(r'<img\b[^>]*>', body):
        url = best(m.group(0))
        if not url or url in seen or 'cdn.myportfolio.com' not in url:
            continue
        seen.add(url); n += 1
        ext = re.search(r'\.(jpe?g|png|gif|webp)', url.lower())
        ext = ext.group(1) if ext else 'jpg'
        fn = '%02d.%s' % (n, ext)
        try:
            open(os.path.join(out, fn), 'wb').write(get(url))
            log.append({'file': fn, 'url': url})
        except Exception as e:
            log.append({'file': None, 'url': url, 'error': str(e)})
    json.dump(log, open(os.path.join(out, 'images.json'), 'w'), indent=1)
    print(slug, n, 'imagens')
