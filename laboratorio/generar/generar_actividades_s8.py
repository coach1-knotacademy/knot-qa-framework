"""Genera laboratorio/actividades_S8.html (las actividades de la clase S8) y docs/datos-y-reportes.md.

La página va en el orden de la clase (ver HORARIO en fichas_s8.py): el rescate, lo preciso (las correcciones de la S7),
la ficha del Esquema del escenario, «¿cuántas pruebas salen?», el revisor con Ejemplos (un CP por sala), tu proyecto,
el reporte que lee negocio, la Rosetta, el boleto y el cierre.
El contenido sale de fichas_s8.py, la misma fuente del deck y del kit de proyecto. El revisor se lee del repo
(laboratorio/revisor-escenarios.js) y se incrusta, así la página abre con doble clic y nunca queda desactualizada.
Los estilos son los de la S7 (se leen de generar_actividades_s7.py): el mismo visual Knot.
Todos los enlaces van completos a Pages, así la copia de ../para_enviar/ es el mismo archivo y funciona con doble clic.
No carga nada de internet (solo las fuentes de Google, y si no cargan se usan las del sistema).

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_actividades_s8.py
"""
import ast, html, json, re, shutil, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
sys.path.insert(0, str(D))
from fichas_s7 import FILAS, VIAS, FRASE_PROYECTO, PROYECTO, GUIA, ACTIVIDADES as ACTIVIDADES_S7  # noqa: E402
from fichas_s8 import (PAGES, REPO, CPS_PAGINA, TEMA, OBJETIVO, IDEA_FUERZA, FRASE_GANCHO, FRASE_CIERRE, REGLA_EJEMPLOS, FRASE_CHAT,  # noqa: E402
                       RESCATE_MENSAJE, RESCATE_EJEMPLO, RESCATE_NOTA, CORRECCIONES, CORRECCIONES_CIERRE, FOTO_VIDEO,
                       PREGUNTA_FOTO_VIDEO, PRECISION_CLAVE, PRECISION_BANCO, FICHA, CUANTAS, SALAS, CRITERIO_SALA,
                       ANUNCIO_10, ANUNCIO_15, CP_106_NOTA, PROYECTO_S8, PROYECTO_ESPECIFICADOR, VIA_ESPECIFICADOR,
                       REPORTE_PASOS, ERROR_PROVOCADO, ALLURE_NOTA, ROSETTA_DDT, ROSETTA_FRASE, BOLETO, HORARIO, FUENTES, a_html)

leer = lambda r: (RAIZ / r).read_text(encoding='utf-8')
LOGO = re.search(r'<img src="(data:image/png;base64,[^"]+)"', (D / 'plantilla.html').read_text(encoding='utf-8')).group(1)
PARA_ENVIAR = RAIZ.parent / 'para_enviar'
HORA = {texto: h for h, texto, _, _ in HORARIO}


def hora(empieza):
    """La hora del bloque del HORARIO cuyo texto empieza así (una sola fuente para las horas)."""
    for texto, h in HORA.items():
        if re.sub(r'\*\*', '', texto).startswith(empieza):
            return h
    raise SystemExit(f'No encontré «{empieza}» en HORARIO de fichas_s8.py')


def css_de_la_s7():
    """El CSS de las actividades de la S7, leído de su generador (sin ejecutarlo): el mismo visual Knot."""
    arbol = ast.parse((D / 'generar_actividades_s7.py').read_text(encoding='utf-8'))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and any(getattr(t, 'id', '') == 'CSS' for t in nodo.targets):
            return ast.literal_eval(nodo.value)
    raise SystemExit('No encontré CSS en generar_actividades_s7.py')


# ---------- El revisor del repo (el mismo de la S7 y de npm run revisar-escenarios) ----------
REVISOR_JS = leer('laboratorio/revisor-escenarios.js')
assert '</script' not in REVISOR_JS.lower(), 'revisor-escenarios.js no puede contener </script>'
assert 'RevisorDeEscenarios' in REVISOR_JS and 'paraElChat' in REVISOR_JS, 'revisor-escenarios.js ya no expone revisar() y paraElChat()'

# ---------- Lo que ya existe en el repo (si otro agente todavía no lo creó, la página no lo muestra) ----------
SPEC_LIMITES = RAIZ / 'tests/recargas/CP-104-limites.spec.ts'


def extracto_limites():
    """El `for` de CP-104-limites.spec.ts (una prueba por fila, con título único), si el archivo ya está en el repo."""
    if not SPEC_LIMITES.exists():
        return ''
    texto = SPEC_LIMITES.read_text(encoding='utf-8')
    m = re.search(r'^[ \t]*for \(const ', texto, re.M)
    if not m:
        return ''
    # Desde el `for` hasta la llave que lo cierra (las de ${…} se cuentan igual y quedan balanceadas).
    abre, nivel, fin = texto.index('{', m.end()), 0, None
    for k in range(abre, len(texto)):
        nivel += {'{': 1, '}': -1}.get(texto[k], 0)
        if nivel == 0:
            fin = k + 1
            break
    if fin is None:
        return ''
    bloque = texto[m.start():fin]
    sangria = min((len(l) - len(l.lstrip()) for l in bloque.split('\n') if l.strip()), default=0)
    return '\n'.join(l[sangria:] for l in bloque.split('\n'))


# ---------- Piezas de la página (las mismas de la S7) ----------
def codigo(texto):
    return '<pre class="code">' + html.escape(texto.rstrip('\n')) + '</pre>'


def clasificador(cid, filas, opciones):
    """filas: (texto_html, clave_correcta, explicacion_html). opciones: [(clave, etiqueta)]."""
    trs = ''.join(
        f'<tr data-ok="{ok}"><td class="n">{n + 1}</td><td>{txt}<div class="exp" hidden>{exp}</div></td>'
        f'<td class="opc">' + ''.join(f'<button type="button" data-v="{k}">{et}</button>' for k, et in opciones) + '</td></tr>'
        for n, (txt, ok, exp) in enumerate(filas))
    return (f'<table class="clasif" id="t-{cid}"><tbody>{trs}</tbody></table>'
            f'<p><button type="button" class="grande" data-revisar="{cid}">Revisar</button>'
            f'<button type="button" data-reiniciar="{cid}">Reiniciar</button><span class="puntaje" id="p-{cid}" aria-live="polite"></span></p>')


def revelar(rid, boton, contenido, clase='grande'):
    return f'<p><button type="button" class="{clase}" data-revelar="{rid}">{boton}</button></p><div id="{rid}" hidden>{contenido}</div>'


ABC = [(k, k) for k in 'abc']


def preguntas(cid, lista, etiqueta='Ver las respuestas', previo=''):
    """Preguntas a/b/c (pregunta, opciones, letra, por qué): clasificador para marcar y las letras detrás de revelar()."""
    filas = [(f'<b>{previo}{a_html(p)}</b><p class="opciones">' + '<br>'.join(f'<b>{"abc"[k]})</b> {a_html(o)}' for k, o in enumerate(ops)) + '</p>',
              ok, f'<b>{ok})</b> {a_html(por)}') for p, ops, ok, por in lista]
    letras = ' '.join(ok for _, _, ok, _ in lista)
    resp = f'<p class="letras">{letras}</p><ol class="boleto">' + ''.join(f'<li><b>{ok}</b> · {a_html(por)}</li>' for _, _, ok, por in lista) + '</ol>'
    return clasificador(cid, filas, ABC) + revelar(f'{cid}-resp', etiqueta, resp)


A_LA_VEZ = '<span class="chip">respondan a la vez: escriban sin enviar · «3, 2, 1, envíen»</span>'

# ---------- Encabezado ----------
ENLACES = [('Los CP del curso', CPS_PAGINA, ''), ('Kit de proyecto', PROYECTO, ' blanco'),
           ('Actividades S7', ACTIVIDADES_S7, ' blanco'), ('Guía de estudio', GUIA, ' blanco')]
enlaces_html = ''.join(f'<a class="boton{c}" href="{u}">{t}</a>' for t, u, c in ENLACES)

# ---------- El rescate ----------
TODAS_LAS_VIAS = VIAS + [VIA_ESPECIFICADOR]
opciones_via = '<option value="">vía…</option>' + ''.join(
    f'<option value="{v["id"]} · {html.escape(v["nombre"].lower())}">{v["id"]} · {html.escape(v["nombre"])}</option>' for v in TODAS_LAS_VIAS)


# ---------- Lo preciso: las correcciones, sin decir quién lo dijo ----------
def sin_autor(texto):
    """«Dije que el expect…» → «El expect…»; «Me equivoqué: el Y…» → «El Y…». En la página no se dice quién lo dijo."""
    t = re.sub(r'^(Dije que|Me equivoqué:)\s*', '', texto.strip())
    t = re.sub(r'^(\*\*)?(Me equivoqué:)\s*', r'\1', t)
    i = next((k for k, ch in enumerate(t) if ch.isalpha()), 0)
    return t[:i] + t[i].upper() + t[i + 1:] if t else t


def fuente(url):
    return f' <a href="https://{url}" class="nota">({html.escape(url)})</a>' if url else ''


preciso_html = ''.join(
    f'<tr><td class="oye" data-k="Se oyó"><b>{html.escape(t)}</b><br><span>«{a_html(sin_autor(dijo))}»</span></td>'
    f'<td data-k="Lo preciso"><span class="flecha">→</span> {a_html(sin_autor(bien))}{fuente(url)}</td></tr>'
    for t, dijo, bien, url in CORRECCIONES)
for _, dijo, bien, _ in CORRECCIONES:
    assert not re.search(r'\b(dije|me equivoqué|mías?)\b', sin_autor(dijo) + sin_autor(bien), re.I), 'Lo preciso no dice quién lo dijo'

# ---------- Ficha ----------
ficha_html = ''.join(f'<div class="fk">{et}</div><div class="fv">{a_html(FICHA[k])}</div>' for k, et in FILAS)

# ---------- Las salas ----------
POR_CP = {s['id']: s for s in SALAS}
assert len(POR_CP) == len(SALAS), 'Dos salas con el mismo CP'


def arranque(s):
    """Lo que la sala encuentra en el revisor: el ID, el Dado y el Cuando con su <marcador>, y los nombres de las columnas."""
    cab = '| ' + ' | '.join(s['columnas']) + ' |'
    return (f'# {s["sala"]} · {s["id"]} · {s["titulo"]}\n'
            f'@{s["id"]}\n'
            f'Esquema del escenario: ___\n'
            + ''.join(f'  {l.strip()}\n' for l in s['arranque'].split('\n'))
            + '  Entonces ___\n\n'
            f'  Ejemplos:\n'
            f'    {cab}\n')


ARRANQUE_PROYECTO = """# Mi proyecto · mi CP como Esquema del escenario, con 3 filas
@CP-___
Esquema del escenario: ___
  Dado que ___
  Cuando ___
  Entonces ___

  Ejemplos:
    | ___ |
"""


def tabla_ejemplos(columnas, filas):
    return ('<table class="ejemplos"><thead><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in columnas) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{html.escape(v)}</td>' for v in f) + '</tr>' for f in filas) + '</tbody></table>')


def panel_sala(s):
    cid = s['id']
    return (f'<div class="cp-panel" data-cp="{cid}" hidden><div class="meta"><span class="chip">{s["sala"]}</span><span class="chip">{cid}</span>'
            f'<a class="chip" href="{CPS_PAGINA}#{cid}">el caso manual ↗</a></div>'
            f'<h3 style="margin-top:0">{html.escape(s["titulo"])}</h3>'
            f'<p class="paso">los datos de su tabla</p>{tabla_ejemplos(s["columnas"], s["filas"])}'
            f'<p class="nota">La primera fila del revisor ya tiene los nombres de las columnas. Cada fila de datos es una prueba.</p>'
            f'<p class="paso">lo que se discute</p><p class="frase-grande" style="font-size:18px">{a_html(s["pregunta"])}</p>'
            + revelar(f'resp-{cid}', 'Ver la respuesta', f'<p class="criterio">{a_html(s["respuesta"])}</p>', clase='')
            + revelar(f'sol-{cid}', 'Terminamos: ver la solución',
                      codigo(s['solucion'])
                      + f'<p><button type="button" data-cargar="{cid}">Cargar la solución de la {s["sala"]} en el revisor</button></p>'
                      '<p class="nota">Es una solución posible, no la única. Si la cargan, su borrador se guarda: «Deshacer» lo trae de vuelta.</p>', clase='')
            + '</div>')


panel_proyecto = ('<div class="cp-panel" data-cp="proyecto" hidden><div class="meta"><span class="chip">mi proyecto</span></div>'
                  '<h3 style="margin-top:0">Mi CP como Esquema del escenario</h3>'
                  f'<p>{a_html(PROYECTO_S8)}</p><p class="nota">{a_html(PROYECTO_ESPECIFICADOR)}</p>'
                  f'<p class="nota">El borrador de su proyecto se guarda aparte del de las salas.</p></div>')

opciones_sala = ''.join(f'<option value="{s["id"]}">{s["sala"]} · {s["id"]} · {html.escape(s["titulo"])}</option>' for s in SALAS) + \
                '<option value="proyecto">Mi proyecto · mi CP</option>'
paneles = ''.join(panel_sala(s) for s in SALAS) + panel_proyecto

# ---------- Tu proyecto: la vía de especificador ----------
V = VIA_ESPECIFICADOR
limites_html = ''.join(f'<li>{a_html(x)}</li>' for x in V['limites'])
ejemplos_via = ''.join(f'<li>{a_html(x)}</li>' for x in V['ejemplos'])

# ---------- El reporte ----------
reporte_html = ''.join(f'<tr><td class="n">{n}</td><td data-k="Paso"><b>{a_html(p)}</b></td><td data-k="Qué se hace">{a_html(q)}</td><td data-k="Qué se ve">{a_html(v)}</td></tr>'
                       for n, (p, q, v) in enumerate(REPORTE_PASOS, 1))
EXTRACTO = extracto_limites()
extracto_html = (f'<div class="card"><p class="paso">el <code>for</code> de <code>tests/recargas/CP-104-limites.spec.ts</code></p>{codigo(EXTRACTO)}'
                 '<p class="nota">Un <code>test()</code> por fila de la fábrica, con el dato en el título y la etiqueta <code>@CP-104</code>: cada fila tiene su línea en el reporte.</p></div>') if EXTRACTO else ''

# ---------- Rosetta ----------
rosetta_html = ''.join(f'<tr><td data-k="La pieza"><b>{a_html(a)}</b></td><td data-k="Gherkin (hoy)">{a_html(b)}</td><td data-k="En el banco (Java)">{a_html(c)}</td><td data-k="Playwright">{a_html(d)}</td></tr>'
                       for a, b, c, d in ROSETTA_DDT)

# ---------- Datos para el JavaScript ----------
DATOS = json.dumps({
    'arranques': dict({s['id']: arranque(s) for s in SALAS}, proyecto=ARRANQUE_PROYECTO),
    'soluciones': {s['id']: s['solucion'] + '\n' for s in SALAS},
    'salas': dict({s['id']: s['sala'] for s in SALAS}, proyecto='Mi CP'),
    'frase': FRASE_PROYECTO,
}, ensure_ascii=False).replace('</', '<\\/')

CSS = css_de_la_s7() + """
/* S8: el rescate, el revisor con Ejemplos y el reporte */
.linea-chat { font:600 15px/1.5 var(--f-mono); background:var(--surface); border:2px dashed var(--ink); border-radius:10px; padding:8px 12px; margin:10px 0; overflow-wrap:anywhere; }
.rescate { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:10px 14px; }
.rescate label { display:flex; flex-direction:column; gap:4px; font-weight:800; font-size:14px; min-width:0; }
.rescate .ancho { grid-column:1 / -1; }
.rescate input, .rescate select { font:16px var(--f-body); border:2px solid var(--ink); border-radius:8px; padding:6px 8px; background:var(--surface); color:var(--ink); min-width:0; width:100%; }
@media (max-width:640px) { .rescate { grid-template-columns:minmax(0,1fr); } }
.preciso td.oye { width:40%; } .preciso td.oye span { color:var(--muted); } .flecha { font-weight:800; color:var(--morado-osc); }
@media (max-width:820px) { .preciso td.oye { width:auto; } table.apilar td[data-k]::before { content:attr(data-k); display:block; font-weight:800; font-size:13px; color:var(--morado-osc); } }
table.ejemplos { width:auto; min-width:60%; max-width:100%; margin:6px 0; font:13px/1.4 var(--f-mono); background:var(--surface); border:2px solid var(--ink); border-radius:10px; border-collapse:separate; border-spacing:0; overflow:hidden; }
table.ejemplos th, table.ejemplos td { border-top:1px solid #c9c5ba; padding:5px 10px; } table.ejemplos thead th { border-top:0; background:var(--yellow); color:var(--ink); font:800 13px var(--f-mono); }
.cp-panel pre.code { white-space:pre; overflow-wrap:normal; overflow-x:auto; font-size:12.5px; }
table.ejemplos td:not(:last-child), table.ejemplos th { white-space:nowrap; }
.salen { font:400 clamp(22px,3vw,28px)/1.1 var(--f-display); color:var(--morado-osc); }
.resumen .cabeza { font:700 14px/1.4 var(--f-mono); flex:1 1 260px; min-width:0; overflow-wrap:anywhere; }
.escenario .chips { display:flex; flex-wrap:wrap; gap:6px; margin:0 0 8px; }
ol.titulos { margin:4px 0 10px; padding-left:22px; font:13px/1.5 var(--f-mono); } ol.titulos li { margin:2px 0; overflow-wrap:anywhere; }
ol.titulos li.repite { color:var(--bad); font-weight:700; }
a.chip { color:var(--ink); text-decoration:none; } a.chip:hover { background:var(--lav); }
.via-d dt { font-weight:800; color:var(--morado-osc); margin-top:10px; } .via-d dd { margin:2px 0 0; }
.creditos { font:700 15px/1.4 var(--f-mono); background:var(--surface); border:2px solid var(--ink); border-radius:10px; padding:8px 12px; overflow-wrap:anywhere; }
@media (max-width:820px) { table.reporte td:first-child { display:none; } }
"""

JS = """
(function () {
  function guardar(clave, valor) { try { localStorage.setItem(clave, valor); } catch (e) {} }
  function recuperar(clave) { try { return localStorage.getItem(clave); } catch (e) { return null; } }
  var DATOS = JSON.parse(document.getElementById('datos-s8').textContent);
  var R = window.RevisorDeEscenarios;

  // Clasificadores (los mismos de la S5 a la S7), con Reiniciar
  document.querySelectorAll('table.clasif').forEach(function (tabla) {
    tabla.querySelectorAll('tr').forEach(function (tr) {
      tr.querySelectorAll('button').forEach(function (b) {
        b.setAttribute('aria-pressed', 'false');
        b.addEventListener('click', function () {
          tr.querySelectorAll('button').forEach(function (x) { x.classList.remove('sel'); x.setAttribute('aria-pressed', 'false'); });
          b.classList.add('sel'); b.setAttribute('aria-pressed', 'true'); tr.classList.remove('bien', 'mal');
        });
      });
    });
  });
  document.querySelectorAll('[data-revisar]').forEach(function (boton) {
    boton.addEventListener('click', function () {
      var id = boton.getAttribute('data-revisar');
      var filas = document.querySelectorAll('#t-' + id + ' tr');
      var bien = 0, marcadas = 0;
      filas.forEach(function (tr) {
        var sel = tr.querySelector('button.sel');
        tr.classList.remove('bien', 'mal');
        tr.querySelector('.exp').hidden = false;
        if (!sel) return;
        marcadas++;
        if (sel.getAttribute('data-v') === tr.getAttribute('data-ok')) { bien++; tr.classList.add('bien'); } else tr.classList.add('mal');
      });
      document.getElementById('p-' + id).textContent = bien + ' de ' + filas.length + ' bien' + (marcadas < filas.length ? ' (faltan ' + (filas.length - marcadas) + ' por marcar)' : '');
    });
  });
  document.querySelectorAll('[data-reiniciar]').forEach(function (boton) {
    boton.addEventListener('click', function () {
      var id = boton.getAttribute('data-reiniciar');
      document.querySelectorAll('#t-' + id + ' tr').forEach(function (tr) {
        tr.classList.remove('bien', 'mal'); tr.querySelector('.exp').hidden = true;
        tr.querySelectorAll('button').forEach(function (x) { x.classList.remove('sel'); x.setAttribute('aria-pressed', 'false'); });
      });
      document.getElementById('p-' + id).textContent = '';
      var resp = document.getElementById(id + '-resp'), b = document.querySelector('[data-revelar="' + id + '-resp"]');
      if (resp && b) { resp.hidden = true; b.hidden = false; }
    });
  });
  document.querySelectorAll('[data-revelar]').forEach(function (boton) {
    boton.addEventListener('click', function () { document.getElementById(boton.getAttribute('data-revelar')).hidden = false; boton.hidden = true; });
  });

  function copiar(texto, aviso) {
    var listo = function () { if (aviso) { aviso.textContent = 'Copiado'; setTimeout(function () { aviso.textContent = ''; }, 2500); } };
    var aMano = function () {
      var t = document.createElement('textarea'); t.value = texto; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.left = '-9999px';
      document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); listo(); } catch (e) { if (aviso) aviso.textContent = 'Selecciónalo y usa Ctrl + C'; }
      document.body.removeChild(t);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(texto).then(listo, aMano); else aMano();
  }

  // ---------- El rescate: una línea por persona ----------
  var campos = ['r-via', 'r-cp', 'r-modo', 'r-con', 'r-frase'].map(function (id) { return document.getElementById(id); });
  var lineaRescate = document.getElementById('rescate-linea'), conQuien = document.getElementById('r-con-caja');
  function armarLinea() {
    var v = function (i) { return campos[i].value.trim() || '___'; };
    var modo = campos[2].value === 'equipo' ? 'en equipo con ' + v(3) : campos[2].value === 'solo' ? 'solo' : '___';
    conQuien.hidden = campos[2].value !== 'equipo';
    return [v(0), v(1).toUpperCase(), modo, v(4)].join(' · ');
  }
  function pintarLinea() { lineaRescate.textContent = armarLinea(); guardar('s8-rescate', JSON.stringify(campos.map(function (c) { return c.value; }))); }
  try { var r = JSON.parse(recuperar('s8-rescate') || 'null'); if (r) campos.forEach(function (c, i) { if (r[i] !== undefined) c.value = r[i]; }); } catch (e) {}
  campos.forEach(function (c) { c.addEventListener('input', pintarLinea); c.addEventListener('change', pintarLinea); });
  lineaRescate.textContent = armarLinea();
  document.getElementById('copiar-linea').addEventListener('click', function () { copiar(armarLinea(), document.getElementById('linea-ok')); });

  // ---------- El revisor con Ejemplos: un borrador por CP (s8-CP-104) ----------
  var area = document.getElementById('gherkin'), salida = document.getElementById('hallazgos'), resumen = document.getElementById('resumen');
  var selector = document.getElementById('sala-cp'), estado = document.getElementById('estado-revisor'), deshacer = document.getElementById('deshacer');
  var actual = null, respaldo = null;
  function clave(cp) { return 's8-' + cp; }
  function limpiarHallazgos() { salida.textContent = ''; resumen.hidden = true; }
  function mostrarPanel() {
    document.querySelectorAll('.cp-panel').forEach(function (d) { d.hidden = d.getAttribute('data-cp') !== actual; });
    document.querySelectorAll('.etiqueta-sala').forEach(function (s) { s.textContent = DATOS.salas[actual]; });
  }
  function abrir(cp) {
    actual = cp; respaldo = null; deshacer.hidden = true;
    var b = recuperar(clave(cp));
    area.value = b !== null && b.trim() ? b : DATOS.arranques[cp];
    guardar('s8-sala', cp); limpiarHallazgos(); mostrarPanel();
    estado.textContent = (b !== null && b.trim() ? 'Su borrador de ' : 'El arranque de ') + DATOS.salas[cp] + (cp === 'proyecto' ? '' : ' · ' + cp) + '.';
  }
  var guardada = recuperar('s8-sala');
  if (guardada && DATOS.arranques[guardada]) selector.value = guardada;
  selector.addEventListener('change', function () { abrir(selector.value); });
  area.addEventListener('input', function () { guardar(clave(actual), area.value); });

  var NOMBRE = { ok: 'ok', aviso: 'aviso', error: 'error' };
  function plural(n, uno, varios) { return n + ' ' + (n === 1 ? uno : varios); }
  function tituloDeFila(titulo, columnas, fila) {
    return titulo.replace(/<([^<>]+)>/g, function (todo, m) { var i = columnas.indexOf(m.trim()); return i > -1 && fila[i] !== undefined ? fila[i] : todo; });
  }
  function revisarTexto() {
    var resultado = R.revisar(area.value), errores = 0, avisos = 0, pruebas = 0;
    salida.textContent = '';
    if (!resultado.length) {
      var p = document.createElement('p'); p.className = 'escenario h-error';
      p.textContent = 'No encontré ningún «Esquema del escenario:». Escriban uno, con su etiqueta @CP-xxx encima y su tabla «Ejemplos».';
      salida.appendChild(p); errores = 1;
    }
    resultado.forEach(function (e) {
      pruebas += e.pruebas;
      var caja = document.createElement('div'); caja.className = 'escenario';
      var h = document.createElement('h4'); h.textContent = (e.esquema ? 'Esquema' : 'Escenario') + ' (línea ' + e.linea + '): ' + e.titulo; caja.appendChild(h);
      var chips = document.createElement('div'); chips.className = 'chips';
      [e.id || 'sin ID', e.columnas.length ? 'columnas: ' + e.columnas.join(' · ') : 'sin tabla', e.esquema ? plural(e.pruebas, 'prueba', 'pruebas') : '1 prueba (no es Esquema)']
        .forEach(function (t) { var c = document.createElement('span'); c.className = 'chip'; c.textContent = t; chips.appendChild(c); });
      caja.appendChild(chips);
      if (e.esquema && e.filas.length) {
        var lbl = document.createElement('p'); lbl.className = 'paso'; lbl.textContent = 'así se llaman en el reporte (una línea por fila)'; caja.appendChild(lbl);
        var ol = document.createElement('ol'); ol.className = 'titulos'; var vistos = {};
        e.filas.forEach(function (f) {
          var t = tituloDeFila(e.titulo, e.columnas, f), li = document.createElement('li');
          li.textContent = t; if (vistos[t]) { li.className = 'repite'; li.textContent = t + '  ← se llama igual que otra: en el reporte no se distinguen'; }
          vistos[t] = true; ol.appendChild(li);
        });
        caja.appendChild(ol);
      }
      var ul = document.createElement('ul'); ul.className = 'hallazgos';
      e.hallazgos.forEach(function (x) {
        if (x.nivel === 'error') errores++; if (x.nivel === 'aviso') avisos++;
        var li = document.createElement('li'); li.className = 'h-' + x.nivel;
        var n = document.createElement('span'); n.className = 'nivel'; n.textContent = (x.nivel === 'ok' ? '✓ ' : x.nivel === 'aviso' ? '! ' : '✗ ') + NOMBRE[x.nivel];
        var t = document.createElement('span'); t.className = 't'; t.textContent = x.texto;
        li.appendChild(n); li.appendChild(t); ul.appendChild(li);
      });
      caja.appendChild(ul); salida.appendChild(caja);
    });
    resumen.hidden = false;
    resumen.className = 'resumen ' + (errores ? 'r-error' : avisos ? 'r-aviso' : 'r-ok');
    resumen.querySelector('.salen').textContent = (errores ? '✗ ' : '✓ ') + (pruebas === 1 ? 'Sale 1 prueba' : 'Salen ' + pruebas + ' pruebas');
    resumen.querySelector('.cabeza').textContent = R.paraElChat(area.value, DATOS.salas[actual]).split('\\n')[0] + (avisos ? ' (' + plural(avisos, 'aviso', 'avisos') + ')' : '');
    estado.textContent = 'Revisado: ' + plural(errores, 'error', 'errores') + ', ' + plural(avisos, 'aviso', 'avisos') + ' y ' + (pruebas === 1 ? 'sale 1 prueba.' : 'salen ' + pruebas + ' pruebas.');
  }
  function reemplazar(texto, mensaje) {
    respaldo = area.value; area.value = texto; guardar(clave(actual), texto);
    deshacer.hidden = respaldo === texto; limpiarHallazgos(); estado.textContent = mensaje;
  }
  document.getElementById('revisar-gherkin').addEventListener('click', revisarTexto);
  document.getElementById('reiniciar-gherkin').addEventListener('click', function () {
    reemplazar(DATOS.arranques[actual], 'Volvió el arranque. Si fue sin querer: «Deshacer».');
  });
  deshacer.addEventListener('click', function () {
    if (respaldo === null) return;
    area.value = respaldo; guardar(clave(actual), respaldo); respaldo = null; deshacer.hidden = true; limpiarHallazgos();
    estado.textContent = 'Volvió su borrador.';
  });
  document.querySelectorAll('[data-cargar]').forEach(function (b) {
    b.addEventListener('click', function () {
      var cp = b.getAttribute('data-cargar');
      if (cp !== actual) { selector.value = cp; abrir(cp); }
      reemplazar(DATOS.soluciones[cp], 'Cargada la solución de la ' + DATOS.salas[cp] + '. Para volver a lo suyo: «Deshacer».');
      revisarTexto(); area.scrollIntoView({ block: 'nearest' });
    });
  });
  document.getElementById('copiar-chat').addEventListener('click', function () {
    copiar(R.paraElChat(area.value, DATOS.salas[actual]), document.getElementById('chat-ok'));
  });
  document.querySelectorAll('[data-ir-proyecto]').forEach(function (b) {
    b.addEventListener('click', function () { selector.value = 'proyecto'; abrir('proyecto'); document.getElementById('revisor').scrollIntoView(); area.focus(); });
  });
  abrir(selector.value);

  // ---------- Los créditos de la vía de especificador ----------
  var cred = document.getElementById('copiar-creditos');
  if (cred) cred.addEventListener('click', function () { copiar(document.getElementById('creditos').textContent, document.getElementById('creditos-ok')); });
})();
"""

N = lambda s: f'<a href="#{s[0]}">{s[1]}</a>'
NAV = ''.join(N(s) for s in [('rescate', 'Rescate'), ('preciso', 'Lo preciso'), ('ficha', 'Ficha'), ('cuantas', '¿Cuántas pruebas?'),
                             ('revisor', 'Tus Ejemplos'), ('proyecto', 'Tu proyecto'), ('reporte', 'El reporte'),
                             ('rosetta', 'Rosetta'), ('boleto', 'Boleto'), ('cierre', 'Cierre')]) + \
      f'<a href="{CPS_PAGINA}" style="background:var(--neon)">📋 Los CP</a>'

HTML = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Actividades S8 Datos</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&amp;family=Nunito:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;600&amp;display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · S8 · {html.escape(TEMA)}</small></div>
<h1>Una prueba, <span class="acc">muchos datos</span>, y el reporte que lee negocio</h1>
<p class="idea">{a_html(IDEA_FUERZA)}</p>
<div class="card c-lime objetivo"><b class="k">Objetivo de hoy</b> <span class="frase-grande" style="margin:0">{a_html(OBJETIVO)}</span></div>
<div class="card c-cyan">
<p style="margin-top:0"><b>Abran estos enlaces y respondan en el chat ✅ si cargan o ❌ si alguno no carga (digan cuál):</b></p>
{enlaces_html}
<p class="nota">Todo funciona sin instalar nada. Si GitHub no abre en su red, el instructor sube los archivos al chat: se abren con doble clic en Edge.</p>
</div>
<nav class="top" aria-label="Actividades">{NAV}</nav>

<section id="rescate">
<div class="card c-yel">
<h2>El rescate · <span class="acc">una línea cada uno</span></h2>
<div class="meta"><span class="chip">{hora('Rescate')} · antes de saludar</span><span class="chip">en el chat principal</span></div>
<p class="frase-grande">{a_html(RESCATE_MENSAJE)}</p>
<p class="nota">Por ejemplo: <code>{html.escape(RESCATE_EJEMPLO)}</code></p>
<div class="rescate">
<label>Mi vía <select id="r-via">{opciones_via}</select></label>
<label>Mi CP <input id="r-cp" type="text" placeholder="CP-104" autocomplete="off"></label>
<label>Solo o en equipo <select id="r-modo"><option value="">elige…</option><option value="solo">solo</option><option value="equipo">en equipo</option></select></label>
<label id="r-con-caja" hidden>Con quién <input id="r-con" type="text" placeholder="los nombres de tu equipo" autocomplete="off"></label>
<label class="ancho">Mi frase <input id="r-frase" type="text" placeholder="{html.escape(FRASE_PROYECTO)}" autocomplete="off"></label>
</div>
<p class="paso" style="margin-top:12px">así queda en el chat</p>
<p class="linea-chat" id="rescate-linea"></p>
<p><button type="button" class="grande" id="copiar-linea">Copiar mi línea</button><span class="ok" id="linea-ok" aria-live="polite"></span></p>
<p class="nota">{a_html(RESCATE_NOTA)}</p>
<p class="criterio"><b>{a_html(FRASE_CHAT)}</b></p>
</div>
</section>

<section id="preciso">
<div class="card c-lav">
<h2>Lo preciso · <span class="acc">tres correcciones de la S7</span></h2>
<div class="meta"><span class="chip">{hora('Las tres correcciones')}</span></div>
<table class="apilar preciso"><thead><tr><th>Se oyó</th><th>Lo preciso</th></tr></thead><tbody>{preciso_html}</tbody></table>
<p class="frase-grande">{a_html(CORRECCIONES_CIERRE)}</p>
</div>
<div class="grid2">
<div class="card"><p class="paso">foto o video</p><p style="margin-top:0">{a_html(FOTO_VIDEO)}</p></div>
<div class="card c-cyan"><p class="paso">comprobación · una letra</p><div class="meta">{A_LA_VEZ}</div>{preguntas('fv', [PREGUNTA_FOTO_VIDEO], 'Ver la respuesta')}</div>
</div>
<div class="grid2">
<div class="card c-peach"><p class="paso">la clave</p><p class="frase-grande" style="margin:0">{a_html(PRECISION_CLAVE)}</p></div>
<div class="card c-peach"><p class="paso">en los escenarios</p><p class="frase-grande" style="margin:0">{a_html(PRECISION_BANCO)}</p></div>
</div>
</section>

<section id="ficha">
<div class="card c-peach">
<p class="paso">gancho · {hora('Gancho')}</p>
<p class="frase-grande" style="margin:0">«{a_html(FRASE_GANCHO)}»</p>
</div>
<div class="card ficha-card"><div class="meta"><span class="chip">ficha · {hora('Gancho')} · 3 min</span></div>
<h2>{html.escape(FICHA["titulo"])}</h2>
<div class="ficha">{ficha_html}</div></div>
<div class="card c-yel"><p class="paso">la regla de los Ejemplos</p><p class="frase-grande" style="margin:0">{a_html(REGLA_EJEMPLOS)}</p></div>
</section>

<section id="cuantas">
<div class="card c-lav">
<p class="paso">comprobación · {hora('Gancho')}</p>
<h2>¿Cuántas pruebas <span class="acc">salen de esta tabla</span>?</h2>
<div class="meta">{A_LA_VEZ}</div>
<p>Tres letras en el chat, en orden, al mismo tiempo. Las respuestas, cuando el instructor lo diga.</p>
{preguntas('cuantas', CUANTAS, previo='¿Cuántas pruebas salen? ')}
</div>
</section>

<section id="revisor">
<div class="card c-cyan">
<h2>Tus Ejemplos · <span class="acc">el revisor de escenarios</span></h2>
<div class="meta"><span class="chip">salas {hora('Salas, un tramo')} · un tramo de 18 min</span><span class="chip">un CP por sala</span></div>
<p>Elijan su sala: el revisor carga el arranque de su CP (el Dado, el Cuando con su <code>&lt;marcador&gt;</code> y los nombres de las columnas). Completen el título con el dato, el «Entonces» y las filas de «Ejemplos», y pulsen <b>Revisar</b>. El revisor dice cuántas pruebas salen y cómo se llamaría cada una en el reporte.</p>
<p class="criterio">{a_html(CRITERIO_SALA)}</p>
<ul class="lista nota"><li>{a_html(ANUNCIO_10)}</li><li>{a_html(ANUNCIO_15)}</li></ul>
</div>
<div class="grid2 revisor">
<div class="card">
<p class="paso">su sala y su caso</p>
<p><label for="sala-cp"><b>Mi sala:</b></label> <select id="sala-cp" class="cp-sel">{opciones_sala}</select></p>
{paneles}
<p class="nota">{a_html(CP_106_NOTA)}</p>
</div>
<div class="card">
<p class="paso">su escenario · <span class="etiqueta-sala"></span></p>
<label for="gherkin" class="nota">Escriban sobre el arranque. Se guarda solo en este navegador, un borrador por CP: cambiar de sala no borra el de otra.</label>
<textarea id="gherkin" class="gherkin" spellcheck="false"></textarea>
<div class="barra">
<button type="button" class="grande" id="revisar-gherkin">Revisar</button>
<button type="button" id="reiniciar-gherkin">Volver al arranque</button>
<button type="button" id="deshacer" hidden>Deshacer</button>
<button type="button" class="grande" id="copiar-chat">Copiar para el chat</button><span class="ok" id="chat-ok" aria-live="polite"></span>
</div>
<p class="nota" id="estado-revisor" aria-live="polite"></p>
<div class="resumen" id="resumen" hidden><span class="salen"></span><span class="cabeza"></span></div>
<div id="hallazgos"></div>
</div>
</div>
</section>

<section id="proyecto">
<div class="card c-peach">
<h2>Tu proyecto · <span class="acc">tu CP con 3 filas</span></h2>
<div class="meta"><span class="chip">{hora('Tu proyecto')} · 20 min fijos · en la sala principal</span></div>
<p class="frase-grande">{a_html(PROYECTO_S8)}</p>
<p><button type="button" class="grande" data-ir-proyecto>Abrir mi proyecto en el revisor</button></p>
<p class="nota">En el revisor, «Mi proyecto» tiene su propio borrador y el botón copia «Mi CP · CP-xxx · 0 errores · salen 3 pruebas».</p>
</div>
<div class="card c-{V["color"]} via-d" id="via-d">
<p class="paso">vía {V["id"]} · {html.escape(V["verbo"].lower())}</p>
<h3 style="margin-top:0">{html.escape(V["nombre"])}</h3>
<p class="criterio"><b>{a_html(PROYECTO_ESPECIFICADOR)}</b></p>
<dl><dt>Para quién</dt><dd>{a_html(V["para"])}</dd><dt>Qué</dt><dd>{a_html(V["que"])}</dd>
<dt>Los límites</dt><dd><ul class="lista">{limites_html}</ul></dd>
<dt>Cómo lo defiendes en la S10</dt><dd>{a_html(V["defensa"])}</dd>
<dt>Ejemplos</dt><dd><ul class="lista">{ejemplos_via}</ul></dd>
<dt>La primera lámina lleva los créditos</dt><dd><p class="creditos" id="creditos">{html.escape(V["creditos"])}</p>
<button type="button" id="copiar-creditos">Copiar los créditos</button><span class="ok" id="creditos-ok" aria-live="polite"></span></dd></dl>
<p><a class="boton blanco" href="{PROYECTO}#vias">Las cuatro vías en el kit de proyecto</a></p>
</div>
</section>

<section id="reporte">
<div class="card">
<h2>El reporte <span class="acc">que lee negocio</span></h2>
<div class="meta"><span class="chip">mírame · {hora('El reporte que lee negocio')}</span><span class="chip">con las manos: leer una fila</span></div>
<p class="frase-grande">{a_html(IDEA_FUERZA.split(". ")[-1])}</p>
<table class="apilar reporte"><thead><tr><th></th><th>Paso</th><th>Qué se hace</th><th>Qué se ve</th></tr></thead><tbody>{reporte_html}</tbody></table>
<p class="nota">Lo corre el instructor en su pantalla. Con el repo instalado en Windows, el mismo comando va con <code>npx.cmd</code> y <code>npm.cmd</code>.</p>
</div>
{extracto_html}
<div class="grid2">
<div class="card c-peach"><p class="paso">el error provocado</p><p style="margin-top:0">{a_html(ERROR_PROVOCADO)}</p></div>
<div class="card c-yel"><p class="paso">¿y Allure?</p><p style="margin-top:0">{a_html(ALLURE_NOTA)}</p></div>
</div>
</section>

<section id="rosetta">
<div class="card">
<p class="paso">solo lectura · 1 min</p>
<h2>Rosetta · <span class="acc">una prueba por fila, en el framework del banco</span></h2>
<table class="apilar"><thead><tr><th>La pieza</th><th>Gherkin (hoy)</th><th>En el banco (Java · Cucumber · Serenity)</th><th>Playwright</th></tr></thead><tbody>{rosetta_html}</tbody></table>
<p class="frase-grande">{a_html(ROSETTA_FRASE)}</p>
</div>
</section>

<section id="boleto">
<div class="card c-lime">
<h2>Boleto de salida</h2>
<div class="meta"><span class="chip">{hora('Boleto de la S8')}</span>{A_LA_VEZ}</div>
<p>Las cuatro letras en orden, en el chat, todos al mismo tiempo.</p>
{preguntas('b8', BOLETO)}
</div>
</section>

<section id="cierre">
<div class="card">
<h2>Cierre</h2>
<div class="meta"><span class="chip">{hora('Cierre')}</span></div>
<p class="frase-grande">{a_html(FRASE_CIERRE)}</p>
{enlaces_html}
<p class="nota">En el repo: la ficha de hoy en <code>docs/datos-y-reportes.md</code>, los Esquemas en <code>especificaciones/recargas-datos.feature</code> y la prueba en <code>tests/recargas/CP-104-limites.spec.ts</code>.</p>
</div>
</section>
<p class="nota">Página de práctica del Bootcamp QA · Knot Academy, generada con <code>laboratorio/generar/generar_actividades_s8.py</code>. No carga nada de internet salvo las fuentes. Los datos son de práctica: nunca escriban aquí datos, pantallas ni casos del banco. Lo que escriban queda solo en este navegador.</p>
</div>
<script type="application/json" id="datos-s8">{DATOS}</script>
<script>
{REVISOR_JS}
</script>
<script>{JS}</script>
</body>
</html>
'''

# ---------- Comprobaciones antes de escribir ----------
RELATIVO = re.compile(r'href="(?!https?://|#|data:)([^"]+)"')
assert not RELATIVO.findall(HTML), f'Enlaces relativos (no funcionan con doble clic): {RELATIVO.findall(HTML)}'
assert 'claude.ai' not in HTML, 'Enlace de claude.ai'
for s in SALAS:
    r = s['solucion']
    assert f'@{s["id"]}' in r and 'Esquema del escenario' in r, f'La solución de la {s["sala"]} no es un Esquema con su ID'

salida = RAIZ / 'laboratorio' / 'actividades_S8.html'
salida.write_text(HTML, encoding='utf-8')
if PARA_ENVIAR.is_dir():
    shutil.copyfile(salida, PARA_ENVIAR / 'actividades_S8.html')

# ---------- docs/datos-y-reportes.md: la misma ficha, para leer en el repo ----------
md = ['# Datos y reportes: Data Driven Testing sobre el framework (S8)', '',
      'Construye sobre las capas de la S3 (ver [arquitectura.md](arquitectura.md)), la fábrica de la S5 (ver [patrones.md](patrones.md)) '
      'y los escenarios de la S7 (ver [gherkin-y-bdd.md](gherkin-y-bdd.md)). Este archivo lo genera '
      '`laboratorio/generar/generar_actividades_s8.py` desde `fichas_s8.py`, la misma fuente de las actividades y del deck: si cambias algo, cámbialo allí.', '',
      f'**{IDEA_FUERZA}**', '', f'Objetivo de la sesión: {OBJETIVO}', '',
      '| Pieza | Dónde verla |', '|---|---|',
      '| Los Esquemas del escenario con sus Ejemplos | `especificaciones/recargas-datos.feature` |',
      '| Las filas con nombre (los datos de la tabla) | `src/datos/fabricaDeRecargas.ts` (`rechazosPorMonto`, `paraCadaOperador`) |',
      '| Un `test()` por fila, con título único y `@CP-104` | `tests/recargas/CP-104-limites.spec.ts` |',
      '| El revisor de escenarios (dice cuántas pruebas salen) | `laboratorio/revisor-escenarios.js` · `npm.cmd run revisar-escenarios` |', '',
      f'## {FICHA["titulo"]}', '', '| | |', '|---|---|']
md += [f'| **{et}** | {FICHA[k]} |' for k, et in FILAS]
md += ['', '## La regla de los Ejemplos', '', REGLA_EJEMPLOS, '',
       '| Sala | CP | Columnas | Filas | Lo que se discute |', '|---|---|---|---|---|']
md += [f'| {s["sala"]} | {s["id"]} · {s["titulo"]} | {" · ".join("`" + c + "`" for c in s["columnas"])} | '
       f'{"; ".join(" · ".join(f) for f in s["filas"])} | {s["pregunta"]} {s["respuesta"]} |' for s in SALAS]
md += ['', CP_106_NOTA, '', '## El reporte que lee negocio', '', '| Paso | Qué se hace | Qué se ve |', '|---|---|---|']
md += [f'| {p} | {q} | {v} |' for p, q, v in REPORTE_PASOS]
md += ['', f'**El error provocado.** {ERROR_PROVOCADO}', '', ALLURE_NOTA, '',
       '## Lo preciso (las esperas, el «Y» y el «Entonces»)', '']
md += [f'- **{t}.** {sin_autor(bien)}' + (f' ({url})' if url else '') for t, _, bien, url in CORRECCIONES]
md += [f'- **Foto o video.** {FOTO_VIDEO}', f'- **La clave.** {PRECISION_CLAVE}', f'- **En los escenarios.** {PRECISION_BANCO}', '',
       '## Rosetta: una prueba por fila en Java + Cucumber o Serenity', '',
       '| La pieza | Gherkin (hoy) | En el banco (Java · Cucumber · Serenity) | Playwright |', '|---|---|---|---|']
md += [f'| {a} | {b} | {c} | {d} |' for a, b, c, d in ROSETTA_DDT]
md += ['', ROSETTA_FRASE, '', '## Fuentes', '']
md += [f'- {f}' for f in FUENTES]
md.append('')


def sin_html(linea):
    """En GitHub, un <marcador> suelto se lee como etiqueta de HTML y desaparece: fuera de `código` va como &lt;marcador&gt;."""
    return '`'.join(p if k % 2 else p.replace('<', '&lt;').replace('>', '&gt;') for k, p in enumerate(linea.split('`')))


(RAIZ / 'docs' / 'datos-y-reportes.md').write_text('\n'.join(sin_html(l) if not l.startswith(('```',)) else l for l in md), encoding='utf-8')
print(f'actividades_S8.html y docs/datos-y-reportes.md listos ({len(SALAS)} salas; extracto de CP-104-limites: {"sí" if EXTRACTO else "todavía no existe"}; '
      f'copia en para_enviar: {PARA_ENVIAR.is_dir()})')
