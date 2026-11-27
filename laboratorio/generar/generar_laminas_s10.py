"""Genera laboratorio/laminas_s10.html (en Pages: laminas-s10.html): la plantilla de las 6 láminas de la S10.

Se edita en el navegador (cada campo es editable), se guarda solo en este navegador (localStorage, con try/catch) y se
imprime una lámina por página a 16:9, para guardarla como PDF desde Edge. Trae el ejemplo del instructor (el MODELO de
la S9, sobre el CP-106) para verlo al lado, sin pisar lo de cada quien.
El contenido sale de fichas_s9.py (LAMINAS_S10, MODELO, CREDITOS_NOTA, FORMATO_S10); el mapa de capas es el de
docs/arquitectura.md (las capas de la S3). El visual es el de las actividades (el mismo visual Knot).
Todos los enlaces van completos a Pages, así la copia de ../para_enviar/ es el mismo archivo y funciona con doble clic.

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_laminas_s10.py
"""
import html, json, re, shutil, sys
from pathlib import Path

D = Path(__file__).parent
sys.path.insert(0, str(D))
from generar_actividades_s9 import LOGO, RAIZ, PARA_ENVIAR, css_de_la_s7, data_uri, RELATIVO  # noqa: E402
from fichas_s6 import CPS  # noqa: E402
from fichas_s7 import PROYECTO, GUIA  # noqa: E402
from fichas_s9 import (LAMINAS_S10, MODELO, MODELO_FRASE, CREDITOS_NOTA, FORMATO_S10, ROJOS, ACTIVIDADES, a_html)  # noqa: E402

e = lambda t: html.escape(t, quote=True)
sin_marcas = lambda t: re.sub(r'\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`', lambda m: next(g for g in m.groups() if g), t)
COLORES = ['c-lav', 'c-yel', 'c-cyan', 'c-peach', 'c-lime', 'c-lav']
assert len(LAMINAS_S10) == 6, 'La plantilla espera 6 láminas'

# El mapa de capas (docs/arquitectura.md): filas de arriba hacia abajo; dos piezas en la misma fila van lado a lado.
CAPAS = [
  [('especificaciones', 'especificaciones/', 'el escenario (Gherkin)')],
  [('tests', 'tests/', 'QUÉ se prueba')],
  [('soporte', 'src/soporte/', 'fixtures y registro de la corrida')],
  [('flujos', 'src/flujos/', 'pasos de negocio')],
  [('paginas', 'src/paginas/', 'la pantalla'), ('api', 'src/api/', 'los servicios')],
  [('config', 'src/config/', 'dónde y con qué clave'), ('datos', 'src/datos/', 'con qué datos')],
]
arq = (RAIZ / 'docs' / 'arquitectura.md').read_text(encoding='utf-8')
for fila in CAPAS:
    for _, carpeta, _ in fila:
        assert carpeta.rstrip('/') in arq or carpeta == 'especificaciones/', f'{carpeta} no está en docs/arquitectura.md'


def mapa(prefijo, activas=(), editable=True):
    filas = ''
    for fila in CAPAS:
        piezas = ''
        for cid, carpeta, que in fila:
            on = cid in activas
            if editable:
                piezas += (f'<button type="button" class="capa" data-capa="{cid}" aria-pressed="{"true" if on else "false"}">'
                           f'<code>{e(carpeta)}</code><span>{e(que)}</span><em class="mia">mi pieza</em></button>')
            else:
                piezas += (f'<div class="capa{" on" if on else ""}"><code>{e(carpeta)}</code><span>{e(que)}</span>'
                           f'{"<em class=mia>mi pieza</em>" if on else ""}</div>')
        filas += f'<div class="capa-fila">{piezas}</div>'
    return f'<div class="mapa" role="group" aria-label="Las capas del framework{": marca tu pieza" if editable else ""}">{filas}</div>'


def lamina(i, titulo, guia, editable=True, ejemplo=None):
    """Una lámina 16:9. En la plantilla los campos son editables; en el ejemplo, texto fijo."""
    ejemplo = ejemplo or {}
    nombre = titulo.split('·', 1)[1].strip()
    cab = (f'<div class="l-cab"><span class="l-num">{i}</span><span class="l-marca"><span class="l-logo" aria-hidden="true"></span>'
           f'Bootcamp QA · S10{" · ejemplo del instructor" if not editable else ""}</span></div>')
    if editable:
        t = f'<h2 class="l-titulo" contenteditable="plaintext-only" data-campo="titulo" data-ph="{e(nombre)}" aria-label="Título de la lámina {i}" spellcheck="true">{e(nombre)}</h2>'
        x = f'<div class="l-texto" contenteditable="plaintext-only" data-campo="texto" data-ph="{e(sin_marcas(guia))}" aria-label="Texto de la lámina {i}: {e(sin_marcas(guia))}" spellcheck="true"></div>'
        img = '<figure class="l-img" hidden><img alt="" data-impeccable-ignore="broken-image"></figure>'
        cred = (f'<p class="l-cred" contenteditable="plaintext-only" data-campo="creditos" data-ph="Solo vía de especificador: Escenarios, datos y aceptación: ___ · Código: instructor, con ayuda de IA" aria-label="Línea de créditos (solo vía de especificador)"></p>'
                if i == 1 else '')
        extra = (mapa('m') + '<p class="l-pie" contenteditable="plaintext-only" data-campo="pie" data-ph="Mi pieza: ___ (haz clic en tu capa)" aria-label="Qué es tu pieza"></p>') if i == 2 else ''
    else:
        t = f'<h2 class="l-titulo">{e(ejemplo.get("titulo", nombre))}</h2>'
        x = f'<div class="l-texto">{ejemplo.get("texto", "")}</div>'
        img = f'<figure class="l-img"><img src="{data_uri(ejemplo["img"])}" alt="{e(ejemplo["alt"])}"></figure>' if ejemplo.get('img') else ''
        cred = ''
        extra = (mapa('e', ejemplo.get('capas', ()), editable=False) + f'<p class="l-pie">{ejemplo.get("pie", "")}</p>') if i == 2 else ''
    cuerpo = f'<div class="l-cuerpo{" con-mapa" if i == 2 else ""}">' + (f'<div class="l-izq">{extra}</div>' if i == 2 else '') + f'<div class="l-der">{x}{img}</div></div>'
    return (f'<section class="lamina {COLORES[i - 1]}" data-i="{i}" aria-label="Lámina {i} · {e(nombre)}{" (ejemplo)" if not editable else ""}">'
            f'{cab}{t}{cuerpo}{cred}</section>')


def bloque(i, titulo, guia):
    controles = (f'<div class="controles no-print"><label class="boton-archivo">Agregar una imagen<input type="file" accept="image/*" data-imagen="{i}"></label>'
                 f'<button type="button" data-quitar-imagen="{i}" hidden>Quitar la imagen</button>'
                 f'<span class="nota">o pega una captura con Ctrl + V sobre la lámina</span>'
                 f'<span class="largo" data-largo="{i}" aria-live="polite"></span></div>')
    return (f'<div class="bloque" id="lamina-{i}"><p class="guia no-print"><b>{e(titulo)}</b> · {a_html(guia)}</p>'
            + lamina(i, titulo, guia) + controles + '</div>')


# ─────────────────────────── El ejemplo del instructor (MODELO, sobre el CP-106) ───────────────────────────
M = dict(MODELO)
CP106 = next(c for c in CPS if c['id'] == 'CP-106')
R1 = next(r for r in ROJOS if r['n'] == 1)
assert R1['caja'] == 'sistema'
EJEMPLO = {
  1: {'texto': f'<p>{a_html(M["El problema"])}</p>'},
  2: {'capas': ('tests', 'api'), 'pie': 'Mi pieza: la prueba del CP-106 en <code>tests/</code>, y el saldo se verifica en <code>src/api/</code> (el servicio), no en la pantalla.',
      'texto': f'<p>{a_html(M["La evidencia"].split(",")[0])}.</p>'},
  3: {'titulo': f'Tu CP · {CP106["id"]} · {CP106["titulo"]}',
      'texto': (f'<p><b>Precondición.</b> {a_html(CP106["pre"])}</p><p><b>Pasos.</b> ' + ' '.join(e(p) for p in CP106['pasos']) + '</p>'
                f'<p><b>Esperado.</b> {a_html(CP106["esperado"])}</p>'),
      'img': 'rojo1-1-accion.png', 'alt': 'El trace del CP-106: la pantalla de Recargas con el aviso «El operador no responde» y el saldo en $1.480.000.'},
  4: {'texto': (f'<p><b>La falla.</b> {a_html(R1["titulo"])}.</p><p><b>La caja.</b> <span class="caja-ej">{e(R1["caja"])}</span></p>'
                f'<p><b>La línea que lo prueba.</b> <code>Expected: 1500000 · Received: 1480000</code></p><p>{a_html(R1["evidencia"])}</p>'),
      'img': 'rojo1-2-error.png', 'alt': 'El error del CP-106 en el trace: Expected 1500000, Received 1480000.'},
  5: {'texto': f'<p>{a_html(M["La decisión"])}</p>'},
  6: {'texto': f'<p>{a_html(M["El lunes"])}</p>'},
}

CSS = css_de_la_s7() + """
a.boton.chico { padding:5px 11px; font-size:14px; box-shadow:2px 2px 0 var(--ink); }
.barra-l { position:sticky; top:0; z-index:5; background:var(--bg); padding:10px 0; display:flex; gap:6px; flex-wrap:wrap; align-items:center; border-bottom:2px solid var(--ink); margin-bottom:12px; }
.barra-l button[aria-pressed="true"] { background:var(--morado-osc); color:#fff; }
@media (max-width:820px) { .barra-l { position:static; } }
#estado { font-weight:800; color:var(--ok); }
#estado.error { color:var(--bad); }
.bloque { margin:22px 0 30px; scroll-margin-top:80px; }
.guia { margin:0 0 6px; }
.controles { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:8px; }
.boton-archivo { display:inline-block; font:800 14px var(--f-body); border:2px solid var(--ink); border-radius:10px; background:var(--surface); padding:6px 10px; cursor:pointer; }
.boton-archivo:hover, .boton-archivo:focus-within { background:var(--lav); outline:3px solid transparent; }
.boton-archivo:focus-within { outline:3px solid var(--morado-osc); outline-offset:2px; }
.boton-archivo input { position:absolute; width:1px; height:1px; opacity:0; }
.largo { color:var(--bad); font-weight:800; }

/* La lámina: 16:9, todo en unidades del ancho de la lámina (cqw), así se ve igual en pantalla, en el celular y en el PDF. */
.lamina { position:relative; margin:0; aspect-ratio:16 / 9; container-type:inline-size; border:2px solid var(--ink); border-radius:14px; box-shadow:5px 5px 0 var(--ink);
  background-image:radial-gradient(#d9d6cc 1.2px, transparent 1.2px); background-size:22px 22px; overflow:hidden; display:flex; flex-direction:column;
  padding:3.2cqw 4cqw 3cqw; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.lamina.c-lav { background-color:var(--lav); } .lamina.c-yel { background-color:var(--yellow); } .lamina.c-cyan { background-color:var(--cyan); }
.lamina.c-peach { background-color:var(--peach); } .lamina.c-lime { background-color:var(--lime); }
.l-cab { display:flex; justify-content:space-between; align-items:center; font:800 1.5cqw var(--f-body); color:var(--muted); }
.l-num { font:400 3.4cqw/1 var(--f-display); color:var(--morado-osc); }
.l-marca { display:flex; align-items:center; gap:.6cqw; } .l-logo { width:2.4cqw; height:2.4cqw; background:var(--logo) center / contain no-repeat; }
.l-titulo { font:400 4.4cqw/1.1 var(--f-display); margin:1.2cqw 0 1.6cqw; color:var(--ink); }
.l-cuerpo { flex:1; min-height:0; display:flex; gap:2.4cqw; }
.l-der { flex:1; min-width:0; display:flex; gap:2.4cqw; }
.l-texto { flex:1; min-width:0; font:600 2.3cqw/1.42 var(--f-body); white-space:pre-wrap; overflow-wrap:anywhere; }
.l-texto p { margin:0 0 1cqw; } .l-texto code, .l-pie code { font-size:.85em; }
.l-img { flex:1.1; min-width:0; margin:0; display:flex; align-items:flex-start; }
.l-img img { width:100%; max-height:100%; object-fit:contain; border:2px solid var(--ink); border-radius:1cqw; background:#fff; }
.l-cred { font:700 1.6cqw/1.3 var(--f-mono); margin:1cqw 0 0; border-top:2px solid var(--ink); padding-top:.8cqw; }
.l-izq { flex:1.15; min-width:0; }
.mapa { display:flex; flex-direction:column; gap:.7cqw; }
.capa-fila { display:flex; gap:.7cqw; }
.capa { flex:1; display:flex; align-items:baseline; gap:1cqw; flex-wrap:wrap; text-align:left; margin:0; padding:.55cqw 1cqw; border:2px solid var(--ink); border-radius:.9cqw;
  background:var(--surface); font:600 1.55cqw/1.25 var(--f-body); color:var(--ink); box-shadow:none; position:relative; }
.capa code { font:700 1.5cqw var(--f-mono); background:none; padding:0; }
.capa .mia { display:none; font:400 1.3cqw var(--f-display); font-style:normal; margin-left:auto; }
.capa[aria-pressed="true"], .capa.on { background:var(--neon); box-shadow:.4cqw .4cqw 0 var(--ink); }
.capa[aria-pressed="true"] .mia, .capa.on .mia { display:inline; }
.l-pie { font:600 1.8cqw/1.35 var(--f-body); margin:1.2cqw 0 0; }
.caja-ej { display:inline-block; border:2px solid var(--ink); border-radius:999px; padding:0 1cqw; background:var(--peach); font:400 1em var(--f-display); text-transform:uppercase; }
.ejemplo-marca { position:absolute; right:3cqw; bottom:2.2cqw; font:800 1.3cqw var(--f-body); background:var(--surface); border:2px solid var(--ink); border-radius:999px; padding:.2cqw 1cqw; }
@media screen {
  [data-ph]:empty::before { content:attr(data-ph); color:#6d7180; font-weight:600; }
  [contenteditable]:hover { outline:2px dashed #9a968b; outline-offset:4px; border-radius:4px; }
  [contenteditable]:focus { outline:3px solid var(--morado-osc); outline-offset:4px; border-radius:4px; }
}
@media (max-width:640px) { .lamina { border-radius:10px; box-shadow:3px 3px 0 var(--ink); } }

@page { size:13.333in 7.5in; margin:0; }
@media print {
  body { background:none !important; }
  .wrap { max-width:none; padding:0; margin:0; }
  .no-print, .knot-bar, h1, .lead, .barra-l, .card, .controles, .guia, .pie-pagina { display:none !important; }
  .bloque { margin:0; }
  .lamina { width:13.333in; height:7.5in; aspect-ratio:auto; border:0; border-radius:0; box-shadow:none; break-after:page; page-break-after:always; break-inside:avoid; }
  .deck > .bloque:last-child .lamina, .deck > .lamina:last-child { break-after:auto; page-break-after:auto; }
  .deck[hidden] { display:none !important; }
  .l-cred:empty, .l-pie:empty { display:none; }
}
"""

JS = """
(function () {
  var CLAVE = 'knot-laminas-s10';
  var estado = document.getElementById('estado');
  function leer() { try { return JSON.parse(localStorage.getItem(CLAVE) || 'null') || {}; } catch (e) { return {}; } }
  function avisar(texto, error) { estado.textContent = texto; estado.classList.toggle('error', !!error); }
  var mio = document.getElementById('deck-mio'), ej = document.getElementById('deck-ejemplo');
  var DEF = {}; mio.querySelectorAll('[data-campo="titulo"]').forEach(function (t) { DEF[t.closest('.lamina').getAttribute('data-i')] = t.textContent; });

  function recoger() {
    var datos = { v: 1, laminas: {}, capas: [] };
    mio.querySelectorAll('.lamina').forEach(function (l) {
      var i = l.getAttribute('data-i'), d = {};
      l.querySelectorAll('[data-campo]').forEach(function (c) { d[c.getAttribute('data-campo')] = c.innerText.replace(/\\n$/, ''); });
      var img = l.querySelector('.l-img img'); if (img && img.getAttribute('src')) d.img = img.getAttribute('src');
      datos.laminas[i] = d;
    });
    mio.querySelectorAll('.capa[aria-pressed="true"]').forEach(function (b) { datos.capas.push(b.getAttribute('data-capa')); });
    return datos;
  }
  var espera = null;
  function guardar() {
    clearTimeout(espera);
    espera = setTimeout(function () {
      try {
        localStorage.setItem(CLAVE, JSON.stringify(recoger()));
        var h = new Date(); avisar('Guardado en este navegador · ' + h.getHours() + ':' + ('0' + h.getMinutes()).slice(-2));
      } catch (e) {
        avisar('No se pudo guardar en este navegador (¿una imagen muy pesada, o el navegador no lo permite?). Lo escrito sigue en pantalla: imprime o copia el texto antes de cerrar.', true);
      }
      medir();
    }, 300);
  }
  function ponerImagen(l, src) {
    var fig = l.querySelector('.l-img'), img = fig.querySelector('img'), i = l.getAttribute('data-i');
    var quitar = document.querySelector('[data-quitar-imagen="' + i + '"]');
    if (src) { img.src = src; img.alt = 'Imagen de la lámina ' + i; fig.hidden = false; quitar.hidden = false; }
    else { img.removeAttribute('src'); fig.hidden = true; quitar.hidden = true; }
  }
  function pintar(datos) {
    mio.querySelectorAll('.lamina').forEach(function (l) {
      var i = l.getAttribute('data-i'), d = (datos.laminas || {})[i] || {};
      l.querySelectorAll('[data-campo]').forEach(function (c) {
        var k = c.getAttribute('data-campo');
        c.textContent = d[k] !== undefined ? d[k] : (k === 'titulo' ? DEF[i] : '');
      });
      ponerImagen(l, d.img || null);
    });
    mio.querySelectorAll('.capa').forEach(function (b) { b.setAttribute('aria-pressed', (datos.capas || []).indexOf(b.getAttribute('data-capa')) > -1 ? 'true' : 'false'); });
    medir();
  }
  // Aviso de lámina con demasiado texto (en el PDF se cortaría).
  function medir() {
    mio.querySelectorAll('.lamina').forEach(function (l) {
      var aviso = document.querySelector('[data-largo="' + l.getAttribute('data-i') + '"]');
      var cuerpo = l.querySelector('.l-cuerpo'), sobra = false;
      cuerpo.querySelectorAll('.l-texto, .l-izq').forEach(function (x) { if (x.scrollHeight > cuerpo.clientHeight + 2) sobra = true; });
      if (l.scrollHeight > l.clientHeight + 2) sobra = true;
      var texto = sobra ? 'Esta lámina tiene demasiado: córtala (en el PDF no cabe).' : '';
      if (aviso.textContent !== texto) aviso.textContent = texto;
    });
  }

  mio.querySelectorAll('[data-campo]').forEach(function (c) {
    c.addEventListener('input', guardar);
    c.addEventListener('blur', function () { if (!c.innerText.trim()) c.textContent = ''; guardar(); });
  });
  mio.querySelectorAll('.capa').forEach(function (b) {
    b.addEventListener('click', function () { b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); guardar(); });
  });

  // Imágenes: se achican a 1600 px de ancho (JPEG) para que quepan en el navegador.
  function cargarImagen(l, archivo) {
    if (!archivo || !/^image\\//.test(archivo.type)) return;
    var lector = new FileReader();
    lector.onload = function () {
      var img = new Image();
      img.onload = function () {
        var esc = Math.min(1, 1600 / img.naturalWidth), cv = document.createElement('canvas');
        cv.width = Math.round(img.naturalWidth * esc); cv.height = Math.round(img.naturalHeight * esc);
        var cx = cv.getContext('2d'); cx.fillStyle = '#fff'; cx.fillRect(0, 0, cv.width, cv.height); cx.drawImage(img, 0, 0, cv.width, cv.height);
        var src; try { src = cv.toDataURL('image/jpeg', 0.86); } catch (e) { src = lector.result; }
        ponerImagen(l, src); guardar();
      };
      img.src = lector.result;
    };
    lector.readAsDataURL(archivo);
  }
  document.querySelectorAll('[data-imagen]').forEach(function (inp) {
    inp.addEventListener('change', function () {
      var l = mio.querySelector('.lamina[data-i="' + inp.getAttribute('data-imagen') + '"]');
      cargarImagen(l, inp.files && inp.files[0]); inp.value = '';
    });
  });
  document.querySelectorAll('[data-quitar-imagen]').forEach(function (b) {
    b.addEventListener('click', function () { ponerImagen(mio.querySelector('.lamina[data-i="' + b.getAttribute('data-quitar-imagen') + '"]'), null); guardar(); });
  });
  mio.querySelectorAll('.lamina').forEach(function (l) {
    l.addEventListener('paste', function (ev) {
      var items = (ev.clipboardData && ev.clipboardData.items) || [];
      for (var k = 0; k < items.length; k++) {
        if (items[k].type && items[k].type.indexOf('image/') === 0) { ev.preventDefault(); cargarImagen(l, items[k].getAsFile()); return; }
      }
    });
  });

  // El ejemplo del instructor: se ve en lugar de las suyas, sin pisarlas.
  var bEj = document.getElementById('ver-ejemplo');
  bEj.addEventListener('click', function () {
    var ver = bEj.getAttribute('aria-pressed') !== 'true';
    bEj.setAttribute('aria-pressed', ver ? 'true' : 'false'); bEj.textContent = ver ? 'Volver a mis láminas' : 'Ver el ejemplo del instructor';
    ej.hidden = !ver; mio.hidden = ver;
    avisar(ver ? 'Viendo el ejemplo del instructor: sus láminas siguen guardadas.' : 'Sus láminas.');
    if (!ver) medir();
  });
  document.getElementById('imprimir').addEventListener('click', function () { window.print(); });

  // Borrar todo: dos pasos, sin ventanas emergentes.
  var bBorrar = document.getElementById('borrar'), armado = null;
  bBorrar.addEventListener('click', function () {
    if (!armado) {
      bBorrar.textContent = '¿Seguro? Pulsa otra vez para borrar'; bBorrar.classList.add('peligro');
      armado = setTimeout(function () { armado = null; bBorrar.textContent = 'Borrar todo'; bBorrar.classList.remove('peligro'); }, 4000);
      return;
    }
    clearTimeout(armado); armado = null; bBorrar.textContent = 'Borrar todo'; bBorrar.classList.remove('peligro');
    try { localStorage.removeItem(CLAVE); } catch (e) {}
    pintar({}); avisar('Se borró todo. La plantilla quedó vacía.');
  });

  // Copiar el texto (para pasarlo a PowerPoint o a otro formato).
  document.getElementById('copiar-texto').addEventListener('click', function () {
    var d = recoger(), lineas = [];
    Object.keys(d.laminas).forEach(function (i) {
      var x = d.laminas[i];
      lineas.push('Lámina ' + i + ' · ' + (x.titulo || ''));
      if (i === '2' && d.capas.length) lineas.push('Mi pieza en el mapa: ' + d.capas.join(', '));
      ['pie', 'texto', 'creditos'].forEach(function (k) { if (x[k]) lineas.push(x[k]); });
      lineas.push('');
    });
    var texto = lineas.join('\\n'), aviso = document.getElementById('copiar-texto-ok');
    var listo = function () { aviso.textContent = 'Copiado'; setTimeout(function () { aviso.textContent = ''; }, 2500); };
    var aMano = function () {
      var t = document.createElement('textarea'); t.value = texto; t.style.position = 'fixed'; t.style.left = '-9999px';
      document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); listo(); } catch (e) { aviso.textContent = 'No se pudo copiar'; }
      document.body.removeChild(t);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(texto).then(listo, aMano); else aMano();
  });

  pintar(leer());
  window.addEventListener('resize', medir);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(medir);
})();
"""


def construir():
    mias = ''.join(bloque(i, t, g) for i, (t, g) in enumerate(LAMINAS_S10, 1))
    ejemplo = ''.join(lamina(i, t, g, editable=False, ejemplo=EJEMPLO[i]).replace('</section>', '<span class="ejemplo-marca">ejemplo</span></section>', 1)
                      .join(['<div class="bloque">', '</div>'])
                      for i, (t, g) in enumerate(LAMINAS_S10, 1))
    indice = ''.join(f'<a href="#lamina-{i}">{e(t)}</a>' for i, (t, _) in enumerate(LAMINAS_S10, 1))
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Láminas S10</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&amp;family=Nunito:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;600&amp;display=swap" rel="stylesheet">
<style>:root {{ --logo:url("{LOGO}"); }}{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · S10 · la plantilla de tus láminas</small></div>
<h1>Tus seis láminas <span class="acc">para la S10</span></h1>
<p class="lead">Escribe sobre cada lámina: el título y el texto se editan con un clic. Se guarda solo en este navegador. Cuando esté lista, «Imprimir o guardar como PDF»: sale una lámina por página, a 16:9.</p>
<div class="card c-yel">
<p style="margin-top:0"><b>El formato.</b> {a_html(FORMATO_S10)}</p>
<p><b>Los créditos.</b> {a_html(CREDITOS_NOTA)}</p>
<p class="nota" style="margin-bottom:0">{a_html(MODELO_FRASE)} Nunca datos, pantallas, nombres ni casos del banco: el caso real se cuenta, el código va sobre el Banco Demo.</p>
</div>
<details class="card no-print"><summary>Cómo guardarla como PDF en Edge</summary>
<ol class="lista"><li>Pulsa <b>Imprimir o guardar como PDF</b> (o Ctrl + P).</li><li>En <b>Impresora</b>, elige <b>Guardar como PDF</b>.</li>
<li>En <b>Más configuraciones</b>: márgenes <b>Ninguno</b> y <b>Gráficos de fondo</b> activado (para los colores).</li><li><b>Guardar</b>. Salen 6 páginas, una por lámina.</li></ol>
<p class="nota">Si el navegador no guarda (modo privado o bloqueado), lo escrito sigue en pantalla mientras no cierres: imprímelo o usa «Copiar el texto».</p></details>
<div class="barra-l no-print" role="toolbar" aria-label="La plantilla">
<button type="button" class="grande" id="imprimir">Imprimir o guardar como PDF</button>
<button type="button" id="ver-ejemplo" aria-pressed="false">Ver el ejemplo del instructor</button>
<button type="button" id="copiar-texto">Copiar el texto</button><span class="ok" id="copiar-texto-ok" aria-live="polite"></span>
<button type="button" id="borrar">Borrar todo</button>
<span id="estado" role="status" aria-live="polite"></span>
</div>
<nav class="top no-print" aria-label="Láminas" style="position:static">{indice}<a href="{ACTIVIDADES}">Actividades S9</a><a href="{PROYECTO}#charla">La charla</a></nav>
<div class="deck" id="deck-mio">{mias}</div>
<div class="deck" id="deck-ejemplo" hidden>{ejemplo}</div>
<p class="nota pie-pagina">Página del Bootcamp QA · Knot Academy, generada con <code>laboratorio/generar/generar_laminas_s10.py</code>. No carga nada de internet salvo las fuentes. Lo que escribas queda solo en este navegador. <a href="{GUIA}">Guía de estudio</a></p>
</div>
<script>{JS}</script>
</body>
</html>
'''


if __name__ == '__main__':
    HTML = construir()
    assert not RELATIVO.findall(HTML), f'Enlaces relativos (no funcionan con doble clic): {RELATIVO.findall(HTML)}'
    assert 'claude.ai' not in HTML, 'Enlace de claude.ai'
    salida = RAIZ / 'laboratorio' / 'laminas_s10.html'
    salida.write_text(HTML, encoding='utf-8')
    if PARA_ENVIAR.is_dir():
        shutil.copyfile(salida, PARA_ENVIAR / 'laminas_S10.html')
    print(f'laminas_s10.html listo ({len(HTML) // 1024} KB); copia en para_enviar: {PARA_ENVIAR.is_dir()}')
