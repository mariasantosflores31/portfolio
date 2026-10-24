"""Constrói a secção de stills de 'Se eu quiser, Choro' (por cenário) e as 5 molduras da página inicial.

Uso (a partir da raiz do repositório): python3 tools/choro_build.py
Lê import/choro/epN/*.webp (descarregados do Drive pelo fluxo 'Importar stills').
"""
import re, shutil, colorsys
from pathlib import Path
from PIL import Image
import sys
sys.path.insert(0, 'tools')
import gallery

ROOT = Path('.')
IMP = ROOT / 'import' / 'choro'
OUT = ROOT / 'assets' / 'choro'
OUT.mkdir(parents=True, exist_ok=True)

# cenário -> [(nome, descrição)]
CENAS = {
    'QUARTO': [
        ('ep1-00001', 'Duas raparigas sentadas no chão do quarto, em volta do caldeirão, com velas e livros à volta'),
        ('ep1-00009', 'Rapariga ajoelhada junto da cama de colcha de margaridas, a mexer o caldeirão entre as velas'),
        ('ep1-00011', 'Plano próximo de uma rapariga a levar uma colher de pau à boca, com velas e a colcha de margaridas atrás'),
        ('ep1-00053', 'Rapariga deitada na cama, de olhos abertos, com o candeeiro de franjas atrás'),
        ('ep2-00005', 'Rapariga a segurar o sapo diante do candelabro, numa luz roxa'),
        ('ep2-00006', 'Vela acesa sobre cartas de tarot, numa luz rosada'),
        ('ep2-00009', 'Velas desfocadas em cor-de-rosa, com uma figura em segundo plano'),
        ('ep2-00014', 'Rapariga sentada na cama, a agarrar a colcha aos quadrados, junto ao dossel de renda'),
        ('ep2-00094', 'Rapariga a ler deitada na cama, com o candeeiro verde aceso'),
        ('ep3-00040', 'Rapariga à secretária, entre livros, velas e um candeeiro de sal'),
    ],
    'COZINHA': [
        ('ep1-00019', 'A mesa posta: três pessoas a jantar sob os azulejos azuis'),
        ('ep1-00027', 'Rapariga a comer, a olhar para a câmara por cima da panela'),
        ('ep1-00029', 'A mulher mais velha à mesa, com a mão junto à boca'),
        ('ep1-00052', 'A mulher mais velha à mesa, à luz de uma vela, com a rapariga encostada ao seu ombro'),
        ('ep2-00089', 'Rapariga sentada à mesa com um lenço vermelho ao pescoço, em frente a um relógio grande'),
        ('ep2-00092', 'Rapariga de pé com a mão no rosto e a mulher mais velha sentada à mesa'),
        ('ep3-00065', 'A mulher mais velha de camisola branca, junto ao frigorífico'),
        ('ep3-00067', 'Rapariga de braços cruzados, junto ao aparador, com uma vela acesa'),
        ('ep4-00052', 'A mulher mais velha de pé, em camisola de lã branca, diante dos azulejos'),
        ('ep4-00057', 'Rapariga e mulher mais velha debruçadas sobre a mesa, entre velas'),
        ('ep4-00059', 'Mão sobre um caderno antigo com desenhos de flores'),
        ('ep4-00062', 'A mulher mais velha a acender velas numa mesa cheia delas, com a rapariga ao lado'),
        ('ep4-00063', 'A mulher mais velha e a rapariga de olhos fechados, à luz das velas'),
        ('ep5-00025', 'A mulher mais velha com a mão na cara, de olhar perdido'),
        ('ep5-00026', 'Rapariga de olhos fechados, a esfregar a testa, junto à janela azul'),
    ],
    'MINI CASA DE LUCY': [
        ('ep2-00015', 'O sapo entre musgo, junto a um baú'),
        ('ep2-00016', 'Rapariga a olhar, sorridente, para o terrário do sapo'),
        ('ep3-00074', 'Rapaz a olhar para o terrário, numa luz vermelha'),
    ],
    'SALA': [
        ('ep3-00049', 'Quatro pessoas à volta da mesa, à luz de velas, diante da lareira'),
        ('ep3-00051', 'Rapariga de franja, de perfil, numa sala com candeeiros acesos'),
        ('ep3-00060', 'Três personagens num corredor: um rapaz, a mulher mais velha e uma rapariga'),
        ('ep4-00014', 'Duas mulheres junto a velas e garrafas, uma delas com a mão no peito'),
        ('ep4-00019', 'Rapariga a deitar um líquido num frasco, ao lado de uma vela'),
        ('ep4-00021', 'Rapariga a olhar para um frasco de vidro com líquido azul brilhante'),
    ],
    'ESTUFA': [
        ('ep3-00003', 'Rapariga de braços cruzados na estufa, com uma pá amarela ao lado'),
        ('ep3-00009', 'Mulher de chapéu axadrezado entre vasos de flores na estufa'),
        ('ep3-00011', 'Rapariga a sorrir de lado, de lenço aos quadrados, na estufa'),
    ],
    'CARRO E EXTERIOR': [
        ('ep1-00038', 'Rapariga com sangue no rosto, dentro do carro, de olhos arregalados'),
        ('ep1-00039', 'Plano escuro de uma figura ensanguentada, vista de lado'),
        ('ep1-00056', 'Figura à porta da casa, ao fundo das escadas, numa noite azul'),
        ('ep1-00072', 'Rapariga e rapaz frente a frente, dentro do carro'),
        ('ep2-00063', 'Rapariga de gorro vermelho a espreitar por uma janela'),
        ('ep2-00084', 'Rapariga de gorro vermelho dentro do carro, a olhar para trás'),
        ('ep5-00062', 'Rapaz de cabelo encaracolado à janela, com a casa ao fundo'),
    ],
    'CASA DE BANHO': [
        ('ep5-00039', 'Mulher sorridente numa banheira, rodeada de velas e frascos'),
    ],
}

HERO = [
    ('ep1-00001', 'Duas raparigas no chão do quarto, em volta do caldeirão, com velas'),
    ('ep1-00019', 'A mesa posta na cozinha, sob os azulejos azuis'),
    ('ep2-00005', 'Rapariga a segurar o sapo diante do candelabro, numa luz roxa'),
    ('ep1-00056', 'Figura à porta da casa, ao fundo das escadas, numa noite azul'),
]

# molduras da página inicial: espaço -> nome do still
CAPAS = {'01': 'ep2-00009', '04': 'ep1-00001', '08': 'ep4-00062', '14': 'ep3-00049', '23': 'ep1-00056'}

# --- revisão pedida pela Maria (24 out) ---
ALT = {n: a for lst in list(CENAS.values()) + [HERO] for n, a in lst}


def _tirar(cena, *nomes):
    CENAS[cena] = [x for x in CENAS[cena] if x[0] not in nomes]


def _item(nome):
    return (nome, ALT[nome])


# topo: a 4.ª foto (escadas à noite) dá lugar ao still da cozinha com as velas (12.ª da cozinha)
HERO[3] = _item('ep4-00062')
_tirar('COZINHA', 'ep4-00062')
# quarto: sai o do colar com a vela (7.º) e o do sapo (5.º); entra o das duas mulheres com velas, que estava na sala
_tirar('QUARTO', 'ep2-00009', 'ep2-00005')
_tirar('SALA', 'ep4-00014')
CENAS['QUARTO'].append(_item('ep4-00014'))
# estufa: sai a 1.ª
_tirar('ESTUFA', 'ep3-00003')
# stills dentro do carro (vão para a Mini casa de Lucy, a cara com sangue e a cabeça primeiro)
CARRO_DENTRO = [_item(n) for n in ('ep1-00038', 'ep1-00039', 'ep1-00072', 'ep2-00084')]
# cenários que só aparecem uma vez
CENAS['OUTROS CENÁRIOS'] = [_item('ep5-00039'), _item('ep5-00062'), _item('ep1-00056')]
_tirar('CARRO E EXTERIOR', 'ep1-00056', 'ep5-00062')
del CENAS['CASA DE BANHO']


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def hexc(c):
    return '#%02X%02X%02X' % tuple(int(v) for v in c)


def paleta(paths, n):
    """n cores dominantes (claras e escuras) ordenadas por luminosidade."""
    tiles = []
    for p in paths:
        im = Image.open(p).convert('RGB').resize((96, 54))
        tiles.append(im)
    w = 96
    sheet = Image.new('RGB', (w * len(tiles), 54))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * w, 0))
    q = sheet.quantize(colors=n, method=Image.MEDIANCUT)
    pal = q.getpalette()[:n * 3]
    cols = [tuple(pal[i * 3:i * 3 + 3]) for i in range(n)]
    return sorted(cols, key=lum)


def cor_principal(cols):
    """a cor mais saturada de luminosidade média (como nas outras molduras)."""
    best = max(cols, key=lambda c: colorsys.rgb_to_hsv(*[v / 255 for v in c])[1] * (1 - abs(lum(c) / 255 - 0.5)))
    h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in best])
    r, g, b = colorsys.hsv_to_rgb(h, min(1, max(s, 0.45)), min(0.9, max(v, 0.6)))
    return (r * 255, g * 255, b * 255)


def src(name):
    return IMP / name[:3] / (name + '.webp')


# 1) copiar os stills para assets/choro (já vêm em WebP leve); só os que a página usa
for f in OUT.glob('*.webp'):
    f.unlink()
for nome in {n for lst in list(CENAS.values()) + [HERO, CARRO_DENTRO] for n, _ in lst}:
    shutil.copyfile(src(nome), OUT / (nome + '.webp'))


def pill(txt):
    return ('<div style="margin-bottom: 12px;"><span style="display: inline-block; border: 1px solid var(--ink); '
            'border-radius: 999px; padding: 4px 12px; font-size: 12px; line-height: 1.2;">%s</span></div>' % txt)


def bloco(lista, etiqueta='Stills', per=2):
    paths = ['assets/choro/%s.webp' % n for n, _ in lista]
    alts = [a for _, a in lista]
    return '<div>%s%s</div>' % (pill(etiqueta), gallery.rows(paths, alts, per=per))


html = Path('se-eu-quiser-choro.html').read_text(encoding='utf8')

# 2) hero: grelha 2x2 em vez da colagem
hero_old = re.search(r'<div style="position: relative; z-index: 6;"><img src="assets/1da2fec7e9a95880c4d91a3dda9ff35f\.webp"[^>]*></div>', html)
assert hero_old, 'hero'
hero_new = gallery.rows(['assets/choro/%s.webp' % n for n, _ in HERO], [a for _, a in HERO], per=2)
for n, _ in HERO:
    assert (OUT / (n + '.webp')).exists(), n
html = html.replace(hero_old.group(0), hero_new.replace('margin-top: -16px;', 'margin-top: 0;'))

# 3) quarto: stills logo a seguir ao cabeçalho
m = re.search(r'QUARTO</h3></div>\n', html)
html = html[:m.end()] + bloco(CENAS['QUARTO'], per=3) + '\n<div style="margin-top: 56px;"></div>' + html[m.end():]

# 4) cozinha: substituir a colagem de 4 stills
coz_old = re.search(r'<div style="position: relative; z-index: 6;"><img src="assets/8c56efcee6fd69b61fcec12c9b57b398\.webp"[^>]*></div>', html)
assert coz_old, 'cozinha'
html = html.replace(coz_old.group(0), bloco(CENAS['COZINHA'], per=3))

# 5) mini casa de Lucy: stills + stills do carro; a imagem de bastidores fica sem título
anchor = '<div style="margin-top: 56px;"><div style="margin-bottom: 12px;"><span style="display: inline-block; border: 1px solid var(--ink); border-radius: 999px; padding: 4px 12px; font-size: 12px; line-height: 1.2;">Stills e bastidores</span></div>'
assert anchor in html, 'bastidores'
carro = gallery.rows(['assets/choro/%s.webp' % n for n, _ in CARRO_DENTRO], [a for _, a in CARRO_DENTRO], per=2)
html = html.replace(anchor, '<div style="margin-top: 56px;">%s</div>\n<div style="padding-top: 16px;">%s</div>\n<div style="margin-top: 16px;">' % (bloco(CENAS['MINI CASA DE LUCY'], per=3), carro))

# 6) novos cenários
novas = ''
num = 4
for titulo in ['SALA', 'ESTUFA', 'CARRO E EXTERIOR', 'OUTROS CENÁRIOS']:
    lista = CENAS[titulo]
    pal = ','.join(hexc(c) for c in paleta([OUT / (n + '.webp') for n, _ in lista], 6))
    novas += gallery.head('%02d' % num, titulo, pal) + bloco(lista, per=3 if titulo == 'OUTROS CENÁRIOS' else 2) + '\n</section>\n'
    num += 1
fim = '<section style="padding: 112px 48px 0;">\n<a class="nl" href="auto-de-fe.html"'
assert fim in html, 'fim'
html = html.replace(fim, novas + fim)

# paletas das barras laterais nas secções que já existiam não mudam.
Path('se-eu-quiser-choro.html').write_text(html, encoding='utf8')

# 7) molduras da página inicial
idx = Path('index.html').read_text(encoding='utf8')
for slot, nome in CAPAS.items():
    im = Image.open(src(nome)).convert('RGB')
    w, h = im.size
    th = round(w * 3 / 4)
    box = ((w - th) // 2, 0, (w - th) // 2 + th, h) if th <= w else (0, 0, w, h)
    # recorte 4:3 centrado
    tw = round(h * 4 / 3)
    box = ((w - tw) // 2, 0, (w - tw) // 2 + tw, h)
    im.crop(box).resize((900, 675), Image.LANCZOS).save('assets/capa/%s.webp' % slot, quality=84, method=6)
    cols = paleta([src(nome)], 5)
    main = hexc(cor_principal(cols))
    pat = re.compile(r'(<a class="chip" href=")[^"]*(" data-slot="%s"[^>]*>)<span class="ph"><img src="assets/capa/%s\.webp" alt="[^"]*"></span><span class="cd"><b>#[0-9A-Fa-f]{6}</b><i>[^<]*</i></span><span class="pal" aria-hidden="true">.*?</span></span></a>' % (slot, slot), re.S)
    mm = pat.search(idx)
    assert mm, slot
    sw = ''.join('<span class="sw" style="--s:%s"><i>%s</i></span>' % (hexc(c), hexc(c)) for c in cols)
    novo = (mm.group(1) + 'se-eu-quiser-choro.html' + mm.group(2) +
            '<span class="ph"><img src="assets/capa/%s.webp" alt="Still de Se eu quiser, Choro"></span>' % slot +
            '<span class="cd"><b>%s</b><i>Se eu quiser, Choro</i></span><span class="pal" aria-hidden="true">%s</span></a>' % (main, sw))
    idx = idx[:mm.start()] + novo + idx[mm.end():]
Path('index.html').write_text(idx, encoding='utf8')
print('feito')
