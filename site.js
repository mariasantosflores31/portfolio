// Maria Flores — comportamento partilhado por todas as páginas.
(function () {
  var root = document.querySelector('.mf');
  if (!root) return;

  // ---- Modo claro / escuro ----
  var btn = document.querySelector('[data-theme-toggle]');
  function setTheme(t) {
    root.classList.toggle('mf-dark', t === 'dark');
    root.classList.toggle('mf-light', t !== 'dark');
    if (btn) btn.textContent = t === 'dark' ? 'Modo claro' : 'Modo escuro';
  }
  var saved = null;
  try { saved = window.localStorage.getItem('mf-theme'); } catch (e) {}
  setTheme(saved === 'dark' ? 'dark' : 'light');
  if (btn) btn.addEventListener('click', function () {
    var n = root.classList.contains('mf-dark') ? 'light' : 'dark';
    try { window.localStorage.setItem('mf-theme', n); } catch (e) {}
    setTheme(n);
  });

  // ---- Barras laterais: códigos RGB ----
  function rgbText(c) {
    c = String(c || '').trim();
    var r = 85, g = 85, b = 85, m;
    if (c.charAt(0) === '#' && c.length >= 7) {
      r = parseInt(c.slice(1, 3), 16); g = parseInt(c.slice(3, 5), 16); b = parseInt(c.slice(5, 7), 16);
    } else if ((m = c.match(/[\d.]+/g)) && m.length >= 3) {
      r = Math.round(m[0]); g = Math.round(m[1]); b = Math.round(m[2]);
    }
    return r + ',' + g + ',' + b;
  }
  function setLabels(pal) {
    document.querySelectorAll('[data-lab]').forEach(function (el) {
      var c = pal[+el.getAttribute('data-lab')];
      el.textContent = c ? rgbText(c) : '';
    });
  }
  function setBars(pal) {
    document.querySelectorAll('.bar').forEach(function (el) {
      pal.forEach(function (c, i) { el.style.setProperty('--b' + i, c); });
    });
    setLabels(pal);
  }
  var bl = document.querySelector('.bar-l');
  if (bl) {
    var cs = getComputedStyle(bl);
    setLabels([0, 1, 2, 3, 4, 5].map(function (k) { return cs.getPropertyValue('--b' + k).trim(); }));
  }

  // ---- Cores das barras mudam com a secção (data-pal) ----
  var sections = document.querySelectorAll('[data-pal]');
  if (sections.length) {
    var current = '';
    var onScroll = function () {
      var mid = window.innerHeight * 0.5, best = sections[0];
      sections.forEach(function (e) { if (e.getBoundingClientRect().top <= mid) best = e; });
      var k = best.getAttribute('data-pal');
      if (k === current) return;
      current = k;
      setBars(k.split(','));
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ---- Página inicial: reel de projetos ----
  if (window.REEL_BASE) {
    var base = window.REEL_BASE, PAL = window.REEL_PAL || [], i = 0, timer;
    var show = function (n) {
      i = (n + base.length) % base.length;
      var c = base[i];
      var set = function (key, val) {
        document.querySelectorAll('[data-cur="' + key + '"]').forEach(function (el) { el.textContent = val; });
      };
      set('titulo', c.titulo); set('papel', c.papel); set('formato', c.formato); set('ano', c.ano);
      set('n', String(i + 1).padStart(2, '0'));
      set('label', '[corte do reel · ' + c.titulo + ']');
      document.querySelectorAll('[data-cur-bg]').forEach(function (el) { el.style.background = c[el.getAttribute('data-cur-bg')]; });
      document.querySelectorAll('[data-cur-img]').forEach(function (el) { el.src = 'assets/covers/' + c.href.replace('.html', '') + '.webp'; el.alt = 'Fotograma de ' + c.titulo; });
      document.querySelectorAll('[data-cur-href]').forEach(function (el) { el.setAttribute('href', c.href); });
      if (PAL[i]) {
        PAL[i].forEach(function (col, k) { document.documentElement.style.setProperty('--b' + k, col); });
        setLabels(PAL[i]);
      }
    };
    var restart = function () { clearInterval(timer); timer = setInterval(function () { show(i + 1); }, 4500); };
    document.querySelectorAll('[data-reel]').forEach(function (b) {
      b.addEventListener('click', function () { show(i + (b.getAttribute('data-reel') === 'next' ? 1 : -1)); restart(); });
    });
    show(0);
    restart();
  }

  // ---- Sobre: fotos a passar ----
  document.querySelectorAll('[data-slideshow]').forEach(function (box) {
    var imgs = box.querySelectorAll('img'), k = 0, stamp = box.querySelector('.stamp');
    var label = function () { if (stamp) stamp.textContent = (imgs[k].getAttribute('data-proj') || '').toUpperCase(); };
    label();
    if (imgs.length < 2) return;
    setInterval(function () {
      imgs[k].classList.remove('on');
      k = (k + 1) % imgs.length;
      imgs[k].classList.add('on');
      label();
    }, 3500);
  });
})();
