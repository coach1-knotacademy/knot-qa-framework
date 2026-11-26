"""Genera laboratorio/actividades_S7.html (las actividades de la clase S7) y docs/gherkin-y-bdd.md.

La página va en el orden de la clase (ver HORARIO en fichas_s7.py): el boleto de la S6, el CP-101 en tres
idiomas, la ficha de Gherkin y BDD, «¿cuál es declarativo?», tu CP en el revisor de escenarios, del escenario a
las capas, tu mapeo, «¿qué capa ejecuta este paso?», la Rosetta, tu proyecto, el boleto y el cierre.
El contenido sale de fichas_s7.py, la misma fuente del deck y del kit de proyecto. El código, los escenarios y el
revisor se leen del repo, así la página no queda desactualizada.
No carga nada de internet (solo las fuentes de Google, y si no cargan se usan las del sistema). Abre con doble clic.

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_actividades_s7.py
"""
import html, json, re, shutil, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
sys.path.insert(0, str(D))
from fichas_s7 import (PAGES, TEMA, IDEA_FUERZA, FRASE_GANCHO, FRASE_CIERRE, OBJETIVO, FICHA, FILAS, TRES_COSAS, FRASE_BANCO,  # noqa: E402
                       TRES_IDIOMAS, DECLARATIVO, MAPEO, REGLA_MAPEO, QUE_CAPA, PRECISIONES, ROSETTA, ROSETTA_FRASE,
                       BOLETO, BOLETO_S6, HORARIO, PREGUNTA_GUIA, FRASE_PROYECTO, VIAS, PLAN_PROYECTO, PLANTILLA_FEATURE,
                       CPS, PROYECTO, GUIA, PLANTILLA, LABORATORIO_S6, CRITERIO_REVISOR, CAPAS, TU_MAPEO, CRITERIO_MAPEO,
                       FUENTES, a_html)

leer = lambda r: (RAIZ / r).read_text(encoding='utf-8')
LOGO = re.search(r'<img src="(data:image/png;base64,[^"]+)"', (D / 'plantilla.html').read_text(encoding='utf-8')).group(1)
PARA_ENVIAR = RAIZ.parent / 'para_enviar'
HORA = {texto: hora for hora, texto, _, _ in HORARIO}

def hora(empieza):
    """La hora del bloque del HORARIO cuyo texto empieza así (una sola fuente para las horas)."""
    for texto, h in HORA.items():
        if re.sub(r'\*\*', '', texto).startswith(empieza):
            return h
    raise SystemExit(f'No encontré «{empieza}» en HORARIO de fichas_s7.py')

# ---------- Código real del repo ----------
REVISOR_JS = leer('laboratorio/revisor-escenarios.js')
assert '</script' not in REVISOR_JS.lower(), 'revisor-escenarios.js no puede contener </script>'
assert 'RevisorDeEscenarios' in REVISOR_JS, 'revisor-escenarios.js ya no expone window.RevisorDeEscenarios'

SPEC = leer('tests/recargas/CP-101-gherkin.spec.ts')
PRUEBA_CP101 = SPEC[SPEC.index("test('CP-101"):].strip()
CORRER_CP101 = re.search(r'Correr solo este caso:\s*(.+)', SPEC).group(1).strip()

def escenarios(texto):
    """{'CP-101': bloque} con cada escenario (desde su etiqueta @CP-xxx), tal cual está en el .feature."""
    bloques, actual, cp = {}, [], None
    for l in texto.split('\n'):
        m = re.match(r'\s*@(CP-\d+)', l)
        if m or re.match(r'\s*# ──', l):
            if cp:
                bloques[cp] = '\n'.join(actual).rstrip()
            cp, actual = (m.group(1), [l]) if m else (None, [])
            continue
        if cp:
            actual.append(l)
    if cp:
        bloques[cp] = '\n'.join(actual).rstrip()
    return bloques

def dedent2(bloque):
    return '\n'.join(l[2:] if l.startswith('  ') else l for l in bloque.split('\n'))

FEATURE = leer('especificaciones/recargas.feature')
SOLUCION = leer('laboratorio/generar/s07_solucion/especificaciones/recargas.feature')
PRACTICA = escenarios(FEATURE)
RESUELTOS = escenarios(SOLUCION)
CARACTERISTICA = FEATURE[FEATURE.index('Característica:'):FEATURE.index('  @CP-101')].rstrip()
CP101_RESUELTO = '# language: es\n' + CARACTERISTICA + '\n\n' + PRACTICA['CP-101'] + '\n'
SALA_DE = {cp: re.search(r'# (Sala \d+)', b).group(1) for cp, b in PRACTICA.items() if re.search(r'# Sala \d+', b)}
TITULO_DE = {cp: re.search(r'Escenario:\s*(.+)', b).group(1).strip() for cp, b in PRACTICA.items()}
for cp in [c['id'] for c in CPS]:
    assert cp in RESUELTOS, f'Falta el {cp} en s07_solucion/especificaciones/recargas.feature'

# ---------- Piezas de la página (las mismas de la S5 y la S6) ----------
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

def revelar(rid, boton, contenido):
    return f'<p><button type="button" class="grande" data-revelar="{rid}">{boton}</button></p><div id="{rid}" hidden>{contenido}</div>'

ABC = [(k, k) for k in 'abc']

def preguntas(cid, lista, etiqueta='Ver las respuestas'):
    """Preguntas a/b/c (pregunta, opciones, letra, por qué): clasificador para marcar y las letras detrás de revelar()."""
    filas = [(f'<b>{a_html(p)}</b><p class="opciones">' + '<br>'.join(f'<b>{"abc"[k]})</b> {a_html(o)}' for k, o in enumerate(ops)) + '</p>',
              ok, f'<b>{ok})</b> {a_html(por)}') for p, ops, ok, por in lista]
    letras = ' '.join(ok for _, _, ok, _ in lista)
    resp = f'<p class="letras">{letras}</p><ol class="boleto">' + ''.join(f'<li><b>{ok}</b> · {a_html(por)}</li>' for _, _, ok, por in lista) + '</ol>'
    return clasificador(cid, filas, ABC) + revelar(f'{cid}-resp', etiqueta, resp)

A_LA_VEZ = '<span class="chip">respondan a la vez: escriban sin enviar · «3, 2, 1, envíen»</span>'

# ---------- Encabezado ----------
ENLACES = [('Laboratorio S6', LABORATORIO_S6, ''), ('La plantilla', PLANTILLA, ' blanco'),
           ('Kit de proyecto', PROYECTO, ' blanco'), ('Guía de estudio', GUIA, ' blanco')]
enlaces_html = ''.join(f'<a class="boton{c}" href="{u}">{t}</a>' for t, u, c in ENLACES)

# ---------- El CP-101 en tres idiomas ----------
manual_html = (f'<p><b>{a_html(TRES_IDIOMAS["manual"][0]).replace("<b>", "").replace("</b>", "")}</b></p>'
               + ''.join(f'<p class="linea-cp">{a_html(l)}</p>' for l in TRES_IDIOMAS['manual'][1:]))

def prueba_marcada(texto):
    """La prueba real, con las líneas de test.step resaltadas: cada una es un paso del escenario."""
    out = []
    for l in texto.split('\n'):
        e = html.escape(l) or ' '
        out.append(f'<span class="ln m-verde">{e}</span>' if 'test.step(' in l else f'<span class="ln">{e}</span>')
    return '<pre class="code num comparar">' + ''.join(out) + '</pre>'

# ---------- Ficha ----------
ficha_html = ''.join(f'<div class="fk">{et}</div><div class="fv">{a_html(FICHA[k])}</div>' for k, et in FILAS)
tres_cosas_html = ''.join(
    f'<div class="card {c}"><p class="paso">{n + 1} · {html.escape(nombre)}</p><p>{a_html(que)}</p><p class="nota"><b>{a_html(hoy)}</b></p></div>'
    for n, ((nombre, que, hoy), c) in enumerate(zip(TRES_COSAS, ['c-lav', 'c-lime', 'c-cyan'])))

# ---------- Tu CP en Gherkin ----------
def cp_panel(cp):
    pasos = ''.join(f'<li>{html.escape(p)}</li>' for p in cp['pasos'])
    nota = f'<p class="nota">{a_html(cp["nota"])}</p>' if cp.get('nota') else ''
    sala = f'<span class="chip">{SALA_DE[cp["id"]]}</span>' if cp['id'] in SALA_DE else '<span class="chip">el modelo</span>'
    titulo = (f'<p class="nota">El título del escenario ya está en <code>especificaciones/recargas.feature</code>: '
              f'«{html.escape(TITULO_DE[cp["id"]])}».</p>') if cp['id'] in TITULO_DE else ''
    if cp['id'] == 'CP-101':
        extra = '<p class="nota">Es el modelo: cárguenlo en el revisor con el botón «Cargar el CP-101 resuelto».</p>'
    else:
        extra = revelar(f'sol-{cp["id"]}', f'Ver una solución del {cp["id"]}',
                        codigo(dedent2(RESUELTOS[cp['id']])) + '<p class="nota">Es una solución posible, no la única. Pásenla por el revisor y compárenla con la suya.</p>')
    return (f'<div class="cp-panel" data-cp="{cp["id"]}" hidden><div class="meta"><span class="chip">{cp["id"]}</span>{sala}</div>'
            f'<h3 style="margin-top:0">{html.escape(cp["titulo"])}</h3>'
            f'<p><b>Precondición:</b> {html.escape(cp["pre"])}</p><ol class="pasos">{pasos}</ol>'
            f'<p><b>Resultado esperado:</b> {html.escape(cp["esperado"])}</p>{nota}{titulo}{extra}</div>')

opciones_cp = ''.join(f'<option value="{cp["id"]}"{" selected" if cp["id"] == "CP-102" else ""}>{cp["id"]} · {html.escape(cp["titulo"])}'
                      f'{" (" + SALA_DE[cp["id"]] + ")" if cp["id"] in SALA_DE else " (modelo)"}</option>' for cp in CPS)
paneles_cp = ''.join(cp_panel(cp) for cp in CPS)
opciones_sala = ''.join(f'<option value="{n}">Sala {n}</option>' for n in range(1, 6))

# ---------- Del escenario a las capas ----------
mapeo_html = ''.join(f'<tr><td>{a_html(a)}</td><td>{a_html(b)}</td><td>{a_html(c)}</td><td class="cod">{a_html(d)}</td></tr>' for a, b, c, d in MAPEO)
precisiones_html = ''.join(
    f'<div class="card {c}"><p class="paso">precisión {n + 1}</p><h3 style="margin-top:0">{a_html(t)}</h3><p>{a_html(x)}</p></div>'
    for n, ((_, t, x), c) in enumerate(zip(PRECISIONES, ['c-cyan', 'c-lime', 'c-peach'])))

# ---------- Tu mapeo ----------
opciones_capa = '<option value="">capa…</option>' + ''.join(f'<option value="{html.escape(c)}">{html.escape(c)}</option>' for c in CAPAS)
mapeo_filas = ''.join(
    f'<tr><td class="n">{n}</td>'
    f'<td><input type="text" class="m-paso" aria-label="Fila {n}: el paso de Gherkin" placeholder="el paso (Dado, Cuando, Entonces…), el dato o el ambiente"></td>'
    f'<td><select class="m-capa" aria-label="Fila {n}: la capa">{opciones_capa}</select></td>'
    f'<td><input type="text" class="m-pieza" aria-label="Fila {n}: la pieza" placeholder="la tarea, la página, la fábrica, el expect…"></td></tr>'
    for n in range(1, 7))

# ---------- Rosetta ----------
rosetta_html = ''.join(f'<tr><td><b>{a_html(a)}</b></td><td>{a_html(b)}</td><td>{a_html(c)}</td></tr>' for a, b, c in ROSETTA)

# ---------- Tu proyecto ----------
vias_html = ' · '.join(f'<b>{v["id"]}</b> {html.escape(v["nombre"])}' for v in VIAS)
partes_frase = FRASE_PROYECTO.split('___')
frase_inputs = ''.join(
    html.escape(parte) + (f'<input id="fp-{n}" aria-label="Espacio {n + 1} de la frase" placeholder="___">' if n < len(partes_frase) - 1 else '')
    for n, parte in enumerate(partes_frase))
PLAN_HOY = next(t for s, _, _, t in PLAN_PROYECTO if s == 'S7')

# ---------- Datos para el JavaScript ----------
DATOS = json.dumps({'plantilla': PLANTILLA_FEATURE + '\n', 'cp101': CP101_RESUELTO}, ensure_ascii=False).replace('</', '<\\/')

CSS = """:root { --bg:#f7f6f2; --surface:#fff; --ink:#1d2130; --muted:#454a58; --morado:#8b55f6; --morado-osc:#5b34c9; --neon:#8be000;
  --lav:#e7defe; --lime:#e2f7c9; --peach:#ffdccf; --cyan:#d3f4f7; --yellow:#fffccb; --ok:#2f7d32; --bad:#c62828;
  --f-display:"Archivo Black","Arial Black",Impact,sans-serif; --f-body:"Nunito","Segoe UI",system-ui,sans-serif; --f-mono:"JetBrains Mono",Consolas,"Cascadia Mono",Menlo,monospace; color-scheme: light; }
* { box-sizing: border-box; }
body { margin:0; background-color:var(--bg); background-image:radial-gradient(#d9d6cc 1.2px, transparent 1.2px); background-size:22px 22px; color:var(--ink); font:16px/1.5 var(--f-body); }
.wrap { max-width:1100px; margin:0 auto; padding:0 16px 48px; }
.knot-bar { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:14px 0 0; font:800 14px var(--f-body); flex-wrap:wrap; }
.knot-bar span { display:flex; align-items:center; gap:8px; } .knot-bar img { height:26px; } .knot-bar small { font-weight:600; color:var(--muted); }
h1, h2, h3 { font-family:var(--f-display); font-weight:400; letter-spacing:-.01em; line-height:1.15; text-wrap:balance; }
h1 { font-size:clamp(28px,5vw,44px); margin:22px 0 6px; } h1 .acc, h2 .acc { color:var(--morado-osc); }
h2 { font-size:clamp(22px,3.4vw,30px); margin:0 0 6px; } h3 { font-size:19px; margin:14px 0 6px; }
.lead { font-size:18px; max-width:760px; }
nav.top { position:sticky; top:0; z-index:5; background:var(--bg); padding:10px 0; display:flex; gap:8px; flex-wrap:wrap; border-bottom:2px solid var(--ink); margin-bottom:18px; }
nav.top a { color:var(--ink); text-decoration:none; border:2px solid var(--ink); border-radius:999px; padding:4px 12px; font-weight:800; font-size:14px; background:var(--surface); }
nav.top a:hover { background:var(--lav); }
@media (max-width:820px) { nav.top { position:static; } }
section { margin:30px 0; scroll-margin-top:110px; }
.card { background:var(--surface); border:2px solid var(--ink); border-radius:14px; box-shadow:5px 5px 0 var(--ink); padding:18px 20px; margin:14px 0; min-width:0; overflow-wrap:anywhere; }
@media (max-width:480px) { .card { padding:14px 14px; } }
.c-lav { background:var(--lav); } .c-lime { background:var(--lime); } .c-peach { background:var(--peach); } .c-cyan { background:var(--cyan); } .c-yel { background:var(--yellow); }
.meta { display:flex; gap:8px; flex-wrap:wrap; margin:6px 0 10px; }
.chip code { background:none; padding:0; }
.chip { border:2px solid var(--ink); border-radius:999px; padding:3px 10px; font-weight:800; font-size:13px; background:var(--surface); }
.grid2, .grid3 { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:16px; } .grid3 { grid-template-columns:repeat(3,minmax(0,1fr)); }
.grid2 > *, .grid3 > * { min-width:0; } .grid3 > .card { margin:0; }
@media (max-width:820px) { .grid2, .grid3 { grid-template-columns:minmax(0,1fr); } }
code { font-family:var(--f-mono); font-size:.88em; background:#efece3; border-radius:5px; padding:1px 5px; overflow-wrap:anywhere; }
pre.code { max-width:100%; overflow-wrap:normal; font:13px/1.55 var(--f-mono); background:#1f2331; color:#e8ebf2; border:2px solid var(--ink); border-radius:12px; padding:14px; overflow:auto; margin:10px 0; }
pre.comparar { white-space:pre-wrap; overflow-wrap:anywhere; font-size:12.5px; }
pre.comparar .ln { padding:0 4px; border-radius:4px; } pre.comparar .ln::before { content:none; }
pre.comparar .m-rojo { background:#5a1f2a; } pre.comparar .m-ambar { background:#4d3d12; } pre.comparar .m-verde { background:#173f2a; }
.insignia { display:inline-grid; place-items:center; min-width:1.5em; height:1.5em; padding:0 4px; border-radius:999px; font:800 12px/1 var(--f-body); text-indent:0; vertical-align:middle; }
.i-rojo { background:#ff8a8a; color:#2a0b10; } .i-ambar { background:#ffd36b; color:#2b2000; } .i-verde { background:#8be3a8; color:#06240f; }
ol.leyenda { list-style:none; padding:0; margin:8px 0; } ol.leyenda li { margin:6px 0; } ol.leyenda .insignia { margin-right:6px; }
pre.num { counter-reset:l; } pre.num .ln { display:block; } pre.num .ln::before { counter-increment:l; content:counter(l); display:inline-block; width:2.4em; color:#8c93a8; }
table { width:100%; border-collapse:collapse; } td, th { border-top:2px solid var(--ink); padding:10px 8px; vertical-align:top; text-align:left; }
th { font-weight:800; font-size:14px; color:var(--muted); }
td.n { font-family:var(--f-display); width:2em; } td.opc { width:1%; white-space:nowrap; } td.cod { width:44%; } td.cod code { white-space:pre-wrap; }
@media (max-width:820px) { td.opc { white-space:normal; } table.clasif, table.clasif tbody, table.clasif tr, table.clasif td, table.trad, table.trad tbody, table.trad tr, table.trad td, table.apilar, table.apilar tbody, table.apilar tr, table.apilar td { display:block; }
  table.trad thead, table.apilar thead { display:none; } td.n { width:auto; border-top:2px solid var(--ink); padding-bottom:0; } table.clasif td:not(.n) { border-top:0; }
  table.trad td, table.apilar td { border-top:0; padding:4px 8px; } table.trad tr, table.apilar tr { border-top:2px solid var(--ink); padding:6px 0; } td.cod { width:auto; } }
button { font:800 14px var(--f-body); border:2px solid var(--ink); border-radius:10px; background:var(--surface); color:var(--ink); padding:6px 10px; margin:2px; cursor:pointer; }
button:hover { background:var(--lav); } button.sel { background:var(--morado-osc); color:#fff; }
button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible, summary:focus-visible { outline:3px solid var(--morado-osc); outline-offset:2px; }
button.grande { background:var(--neon); box-shadow:3px 3px 0 var(--ink); padding:9px 16px; font-size:15px; }
tr.bien td { background:#eefbe3; } tr.mal td { background:#ffe9e3; } .exp { margin-top:6px; font-size:14px; }
.puntaje { font-weight:800; margin-left:10px; }
ol.pasos li, ul.lista li, ol.lista li, ol.boleto li { margin:6px 0; } .fix { color:var(--morado-osc); font-weight:700; }
.nota { color:var(--muted); font-size:14px; }
a.boton { display:inline-block; text-decoration:none; color:var(--ink); background:var(--neon); border:2px solid var(--ink); border-radius:10px; box-shadow:3px 3px 0 var(--ink); padding:9px 16px; font-weight:800; margin:4px 6px 4px 0; }
a.boton.blanco { background:var(--surface); }
.frase { display:flex; flex-wrap:wrap; gap:8px; align-items:center; font-size:17px; }
.frase input, .frase select, select.cp-sel { font:16px var(--f-body); border:2px solid var(--ink); border-radius:8px; padding:6px 8px; min-width:0; max-width:100%; background:var(--surface); color:var(--ink); }
.frase input { flex:1 1 200px; }
textarea { width:100%; min-height:110px; font:15px/1.5 var(--f-body); border:2px solid var(--ink); border-radius:10px; padding:10px; }
.cp-prac table.trad td:nth-child(3) { width:48%; } @media (max-width:820px) { .cp-prac table.trad td:nth-child(3) { width:auto; } }
table.trad input { width:100%; font:14px var(--f-mono); border:2px solid var(--ink); border-radius:8px; padding:6px 8px; }
.ok { color:var(--ok); font-weight:800; margin-left:6px; }
.ficha-card h2 { color:var(--morado-osc); }
.ficha { display:grid; grid-template-columns:minmax(0,15em) minmax(0,1fr); border-top:2px solid var(--ink); }
.ficha .fk, .ficha .fv { padding:9px 8px; border-bottom:1px solid #c9c5ba; } .ficha .fk { font-weight:800; color:var(--morado-osc); }
@media (max-width:820px) { .ficha { grid-template-columns:minmax(0,1fr); } .ficha .fk { border-bottom:0; padding-bottom:0; } }
.desde { font-weight:700; } .paso { font:400 15px var(--f-display); color:var(--morado-osc); margin:0 0 4px; }
.opciones { margin:2px 0 8px; }
details { margin:8px 0; } summary { cursor:pointer; font-weight:800; }
.check { display:flex; gap:10px; align-items:flex-start; cursor:pointer; } .check input { width:20px; height:20px; margin-top:3px; flex:none; accent-color:var(--morado-osc); }
ul.checks { list-style:none; padding-left:0; } ul.checks li { margin:8px 0; }
.ves { margin:2px 0 10px; font-size:15px; background:var(--surface); border:2px dashed #9a968b; border-radius:10px; padding:6px 10px; }
ol.escalera { list-style:none; padding:0; margin:12px 0; }
.peldano { display:flex; gap:12px; align-items:flex-start; border:2px solid var(--ink); border-radius:12px; background:var(--surface); padding:10px 12px; margin:8px 0; box-shadow:3px 3px 0 var(--ink); }
.peldano .num { font:400 22px var(--f-display); width:1.6em; flex:none; color:var(--morado-osc); }
.peldano > div { min-width:0; }
.p1 { margin-right:16%; } .p2 { margin-left:4%; margin-right:12%; } .p3 { margin-left:8%; margin-right:8%; } .p4 { margin-left:12%; margin-right:4%; } .p5 { margin-left:16%; background:var(--peach); }
@media (max-width:600px) { .p1, .p2, .p3, .p4, .p5 { margin-left:0; margin-right:0; } }
.tipo { display:inline-block; border:2px solid var(--ink); border-radius:999px; padding:1px 9px; font-weight:800; font-size:12.5px; white-space:nowrap; }
.t-ambiente { background:var(--cyan); } .t-pre { background:var(--lav); } .t-paso { background:var(--lime); } .t-dato { background:var(--yellow); } .t-esperado { background:var(--peach); }
.contador { font:400 18px var(--f-display); color:var(--morado-osc); }
.cp h3 { font-size:18px; }
.cps { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; } .cps > .card { margin:0; }
@media (max-width:980px) { .cps { grid-template-columns:minmax(0,1fr) minmax(0,1fr); } } @media (max-width:640px) { .cps { grid-template-columns:minmax(0,1fr); } }
/* S7: el revisor y el mapeo */
[hidden] { display:none !important; }
@media (max-width:820px) { td.opc { width:auto; } }
pre.code, code, textarea.gherkin { font-variant-ligatures:none; }
.grid2 pre.code { white-space:pre-wrap; overflow-wrap:anywhere; }
.idea { font:400 clamp(18px,2.6vw,22px)/1.35 var(--f-display); margin:6px 0 12px; max-width:860px; }
.objetivo { display:flex; gap:10px; align-items:baseline; flex-wrap:wrap; }
.objetivo b.k { font:400 14px var(--f-display); color:var(--morado-osc); text-transform:uppercase; letter-spacing:.04em; }
.linea-cp { margin:4px 0; }
.frase-grande { font:400 clamp(17px,2.4vw,21px)/1.4 var(--f-display); margin:8px 0; }
.letras { font:400 22px var(--f-display); color:var(--morado-osc); letter-spacing:.2em; margin:6px 0; }
@media (min-width:821px) { .grid2.revisor { grid-template-columns:minmax(0,2fr) minmax(0,3fr); } }
textarea.gherkin { min-height:320px; font:13px/1.55 var(--f-mono); background:#fbfaf6; color:var(--ink); white-space:pre; overflow:auto; tab-size:2; }
.barra { display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:8px 0; }
.criterio { border:2px dashed var(--ink); border-radius:10px; padding:8px 12px; background:var(--surface); }
.resumen { font:400 18px var(--f-display); padding:8px 12px; border:2px solid var(--ink); border-radius:10px; margin:10px 0; display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
.resumen.r-ok { background:#eefbe3; } .resumen.r-aviso { background:#fff3c4; } .resumen.r-error { background:#ffe9e3; }
.escenario { border:2px solid var(--ink); border-radius:12px; background:var(--surface); padding:10px 12px; margin:10px 0; }
.escenario h4 { margin:0 0 6px; font-size:16px; }
ul.hallazgos { list-style:none; padding:0; margin:0; } ul.hallazgos li { display:flex; gap:8px; align-items:flex-start; padding:6px 8px; border-radius:8px; margin:4px 0; }
.nivel { flex:none; font:800 12px/1 var(--f-body); border:2px solid currentColor; border-radius:999px; padding:3px 8px; margin-top:2px; text-transform:uppercase; }
.h-ok { background:#eefbe3; color:#1e5a22; } .h-aviso { background:#fff3c4; color:#5e4500; } .h-error { background:#ffe9e3; color:#9c1616; }
ul.hallazgos li span.t { color:var(--ink); }
.cp-panel { border-top:2px solid var(--ink); padding-top:10px; margin-top:10px; }
table.mapeo input, table.mapeo select { width:100%; font:14px var(--f-body); border:2px solid var(--ink); border-radius:8px; padding:6px 8px; background:var(--surface); color:var(--ink); min-width:0; }
table.mapeo td:nth-child(2) { width:38%; } table.mapeo td:nth-child(3) { width:20%; }
@media (max-width:820px) { table.mapeo, table.mapeo tbody, table.mapeo tr, table.mapeo td { display:block; } table.mapeo thead { display:none; }
  table.mapeo tr { border-top:2px solid var(--ink); padding:6px 0; } table.mapeo td { border-top:0; padding:4px 8px; width:auto !important; } }
.frase input { flex:1 1 160px; }
a.boton.enorme { font-size:19px; padding:14px 22px; }
"""

JS = """
(function () {
  function guardar(clave, valor) { try { localStorage.setItem(clave, valor); } catch (e) {} }
  function recuperar(clave) { try { return localStorage.getItem(clave); } catch (e) { return null; } }
  function borrar(clave) { try { localStorage.removeItem(clave); } catch (e) {} }
  var DATOS = JSON.parse(document.getElementById('datos-s7').textContent);

  // Clasificadores (los mismos de la S5 y la S6), ahora con Reiniciar
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
      var t = document.createElement('textarea'); t.value = texto; document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); } catch (e) {} document.body.removeChild(t); listo();
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(texto).then(listo, aMano); else aMano();
  }

  // ---------- El revisor de escenarios ----------
  var area = document.getElementById('gherkin'), salida = document.getElementById('hallazgos');
  var resumen = document.getElementById('resumen'), sala = document.getElementById('sala'), estado = document.getElementById('estado-revisor');
  var deshacer = document.getElementById('deshacer'), respaldo = null, ultimo = '';
  var borrador = recuperar('s7-borrador');
  area.value = borrador !== null && borrador.trim() ? borrador : DATOS.plantilla;
  var guardado = recuperar('s7-sala'); if (guardado) sala.value = guardado;
  area.addEventListener('input', function () { guardar('s7-borrador', area.value); });
  sala.addEventListener('change', function () { guardar('s7-sala', sala.value); pintarResumen(); });

  var NOMBRE = { ok: 'ok', aviso: 'aviso', error: 'error' };
  var cuenta = null;
  function pintarResumen() {
    if (!cuenta) return;
    var texto = 'Sala ' + sala.value + ': ' + cuenta.errores + (cuenta.errores === 1 ? ' error' : ' errores');
    ultimo = texto + (cuenta.avisos ? ' (' + cuenta.avisos + (cuenta.avisos === 1 ? ' aviso' : ' avisos') + ')' : '');
    resumen.hidden = false;
    resumen.className = 'resumen ' + (cuenta.errores ? 'r-error' : cuenta.avisos ? 'r-aviso' : 'r-ok');
    resumen.querySelector('.r-texto').textContent = (cuenta.errores ? '✗ ' : '✓ ') + ultimo;
  }
  function revisarTexto() {
    var resultado = window.RevisorDeEscenarios.revisar(area.value);
    salida.textContent = '';
    cuenta = { errores: 0, avisos: 0 };
    if (!resultado.length) {
      var p = document.createElement('p'); p.className = 'escenario h-error';
      p.textContent = 'No encontré ningún «Escenario:». Escriban al menos uno, con su etiqueta @CP-xxx encima.';
      salida.appendChild(p); cuenta.errores = 1;
    }
    resultado.forEach(function (e) {
      var caja = document.createElement('div'); caja.className = 'escenario';
      var h = document.createElement('h4'); h.textContent = 'Escenario (línea ' + e.linea + '): ' + e.titulo; caja.appendChild(h);
      var ul = document.createElement('ul'); ul.className = 'hallazgos';
      e.hallazgos.forEach(function (x) {
        if (x.nivel === 'error') cuenta.errores++; if (x.nivel === 'aviso') cuenta.avisos++;
        var li = document.createElement('li'); li.className = 'h-' + x.nivel;
        var n = document.createElement('span'); n.className = 'nivel'; n.textContent = (x.nivel === 'ok' ? '✓ ' : x.nivel === 'aviso' ? '! ' : '✗ ') + NOMBRE[x.nivel];
        var t = document.createElement('span'); t.className = 't'; t.textContent = x.texto;
        li.appendChild(n); li.appendChild(t); ul.appendChild(li);
      });
      caja.appendChild(ul); salida.appendChild(caja);
    });
    pintarResumen();
    estado.textContent = 'Revisado: ' + resultado.length + (resultado.length === 1 ? ' escenario' : ' escenarios') + ', ' + cuenta.errores + ' errores y ' + cuenta.avisos + ' avisos.';
  }
  function limpiarHallazgos() { salida.textContent = ''; resumen.hidden = true; cuenta = null; estado.textContent = ''; }
  function reemplazar(texto, mensaje) {
    respaldo = area.value; area.value = texto; guardar('s7-borrador', texto);
    deshacer.hidden = respaldo === texto; limpiarHallazgos(); estado.textContent = mensaje;
  }
  document.getElementById('revisar-gherkin').addEventListener('click', revisarTexto);
  document.getElementById('reiniciar-gherkin').addEventListener('click', function () {
    reemplazar(DATOS.plantilla, 'Volvió la plantilla. Si fue sin querer: «Deshacer».');
  });
  document.getElementById('cargar-cp101').addEventListener('click', function () {
    reemplazar(DATOS.cp101, 'Cargado el CP-101 resuelto. Pulsen «Revisar». Para volver a lo suyo: «Deshacer».');
  });
  deshacer.addEventListener('click', function () {
    if (respaldo === null) return;
    area.value = respaldo; guardar('s7-borrador', respaldo); respaldo = null; deshacer.hidden = true; limpiarHallazgos();
    estado.textContent = 'Volvió su borrador.';
  });
  document.getElementById('copiar-gherkin').addEventListener('click', function () { copiar(area.value, document.getElementById('gherkin-ok')); });
  document.getElementById('copiar-resumen').addEventListener('click', function () { copiar(ultimo, document.getElementById('resumen-ok')); });

  // El CP manual de la sala
  var cpSel = document.getElementById('cp-elegido');
  function mostrarCp() { document.querySelectorAll('.cp-panel').forEach(function (d) { d.hidden = d.getAttribute('data-cp') !== cpSel.value; }); guardar('s7-cp', cpSel.value); }
  var cpGuardado = recuperar('s7-cp'); if (cpGuardado && cpSel.querySelector('option[value="' + cpGuardado + '"]')) cpSel.value = cpGuardado;
  cpSel.addEventListener('change', mostrarCp); mostrarCp();

  // ---------- Tu mapeo ----------
  var filas = Array.prototype.slice.call(document.querySelectorAll('#tabla-mapeo tbody tr'));
  var cuentaMapeo = document.getElementById('mapeo-cuenta'), salaMapeo = document.getElementById('sala-mapeo');
  function leerMapeo() { return filas.map(function (tr) { return [tr.querySelector('.m-paso').value, tr.querySelector('.m-capa').value, tr.querySelector('.m-pieza').value]; }); }
  function contarMapeo() {
    var n = leerMapeo().filter(function (f) { return f[0].trim() && f[1] && f[2].trim(); }).length;
    cuentaMapeo.textContent = 'Sala ' + salaMapeo.value + ': ' + n + ' de ' + filas.length;
    return n;
  }
  function guardarMapeo() { guardar('s7-mapeo', JSON.stringify(leerMapeo())); contarMapeo(); }
  try {
    var m = JSON.parse(recuperar('s7-mapeo') || 'null');
    if (m) filas.forEach(function (tr, i) { if (!m[i]) return; tr.querySelector('.m-paso').value = m[i][0] || ''; tr.querySelector('.m-capa').value = m[i][1] || ''; tr.querySelector('.m-pieza').value = m[i][2] || ''; });
  } catch (e) {}
  if (guardado) salaMapeo.value = guardado;
  filas.forEach(function (tr) { tr.querySelectorAll('input, select').forEach(function (c) { c.addEventListener('input', guardarMapeo); c.addEventListener('change', guardarMapeo); }); });
  salaMapeo.addEventListener('change', function () { guardar('s7-sala', salaMapeo.value); contarMapeo(); });
  document.getElementById('traer-pasos').addEventListener('click', function () {
    var pasos = area.value.split(/\\r?\\n/).map(function (l) { return l.trim(); })
      .filter(function (l) { return /^(Dado|Dada|Dados|Dadas|Cuando|Entonces|Y|E|Pero)\\b/.test(l); });
    var aviso = document.getElementById('traer-ok');
    if (!pasos.length) { aviso.textContent = 'No hay pasos en el revisor todavía'; return; }
    filas.forEach(function (tr, i) { if (pasos[i]) tr.querySelector('.m-paso').value = pasos[i]; });
    aviso.textContent = pasos.length > filas.length ? 'Traje los primeros ' + filas.length + ' pasos' : 'Traje ' + pasos.length + ' pasos';
    guardarMapeo();
  });
  document.getElementById('reiniciar-mapeo').addEventListener('click', function () {
    filas.forEach(function (tr) { tr.querySelector('.m-paso').value = ''; tr.querySelector('.m-capa').value = ''; tr.querySelector('.m-pieza').value = ''; });
    borrar('s7-mapeo'); contarMapeo(); document.getElementById('traer-ok').textContent = '';
  });
  document.getElementById('copiar-mapeo').addEventListener('click', function () {
    var lineas = [cuentaMapeo.textContent].concat(leerMapeo().map(function (f, i) { return (i + 1) + '. ' + (f[0].trim() || '___') + ' → ' + (f[1] || '___') + ' → ' + (f[2].trim() || '___'); }));
    copiar(lineas.join('\\n'), document.getElementById('mapeo-ok'));
  });
  contarMapeo();

  // ---------- La frase del proyecto ----------
  var fp = document.querySelectorAll('[id^="fp-"]'), plantillaFrase = document.getElementById('copiar-frase').getAttribute('data-frase');
  document.getElementById('copiar-frase').addEventListener('click', function () {
    var i = 0, texto = plantillaFrase.replace(/___/g, function () { var v = fp[i++]; return (v && v.value.trim()) || '___'; });
    copiar(texto, document.getElementById('frase-ok'));
  });
})();
"""

N = lambda s: f'<a href="#{s[0]}">{s[1]}</a>'
NAV = ''.join(N(s) for s in [('boleto-s6', 'Boleto S6'), ('tres-idiomas', 'Tres idiomas'), ('ficha', 'Ficha'), ('declarativo', '¿Declarativo?'),
                             ('revisor', 'Tu CP en Gherkin'), ('capas', 'A las capas'), ('mapeo', 'Tu mapeo'), ('que-capa', '¿Qué capa?'),
                             ('rosetta', 'Rosetta'), ('proyecto', 'Tu proyecto'), ('boleto', 'Boleto'), ('cierre', 'Cierre')]) + \
      f'<a href="{PAGES}cps.html" style="background:var(--neon)">📋 Los CP</a>'

HTML = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Actividades S7 Gherkin</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&amp;family=Nunito:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;600&amp;display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · S7 · {html.escape(TEMA)}</small></div>
<h1>Tu CP en <span class="acc">Gherkin</span>, mapeado a las capas</h1>
<p class="idea">{a_html(IDEA_FUERZA)}</p>
<div class="card c-lime objetivo"><b class="k">Objetivo de hoy</b> <span class="frase-grande" style="margin:0">{a_html(OBJETIVO)}</span></div>
<div class="card c-cyan">
<p style="margin-top:0"><b>Abran estos enlaces y respondan en el chat ✅ si cargan o ❌ si alguno no carga (digan cuál):</b></p>
{enlaces_html}
<p class="nota">Todo funciona sin instalar nada. Si GitHub no abre en su red, el instructor sube los archivos al chat: se abren con doble clic en Edge.</p>
</div>
<nav class="top" aria-label="Actividades">{NAV}</nav>

<section id="boleto-s6">
<div class="card c-lime">
<h2>Repaso · <span class="acc">el boleto de la S6</span></h2>
<div class="meta"><span class="chip">{hora('Portada')} · para quien ya llegó</span>{A_LA_VEZ}</div>
<p>Las cuatro letras en orden, en el chat, todos al mismo tiempo. Por ejemplo: <b>«a c b a»</b>. Marquen aquí y pulsen «Revisar» cuando el instructor lo diga.</p>
{preguntas('b6', BOLETO_S6)}
</div>
</section>

<section id="tres-idiomas">
<div class="card c-peach">
<p class="paso">gancho · {hora('Gancho')}</p>
<h2>El CP-101 en <span class="acc">tres idiomas</span></h2>
<p class="frase-grande">«{a_html(FRASE_GANCHO)}»</p>
</div>
<div class="grid2">
<div class="card"><p class="paso">1 · el caso manual (el Excel o el ALM)</p>{manual_html}</div>
<div class="card"><p class="paso">2 · Gherkin · <code>especificaciones/recargas.feature</code></p>{codigo(TRES_IDIOMAS["gherkin"])}
<p class="nota">El mismo caso, en el idioma del negocio: sin clics ni localizadores, con el ID en la etiqueta y el dato en el «Entonces».</p></div>
</div>
<div class="card"><p class="paso">3 · la prueba · <code>tests/recargas/CP-101-gherkin.spec.ts</code></p>
{prueba_marcada(PRUEBA_CP101)}
<p class="nota">Cada <code>test.step</code> (resaltado) lleva el mismo texto del paso de Gherkin, y el reporte HTML muestra la prueba con esos pasos. Se corre con <code>{html.escape(CORRER_CP101)}</code>.</p>
</div>
</section>

<section id="ficha">
<div class="card ficha-card"><div class="meta"><span class="chip">ficha · {hora('Ficha')}</span></div>
<h2>{html.escape(FICHA["titulo"])}</h2>
<div class="ficha">{ficha_html}</div></div>
<h3>BDD, Gherkin y la herramienta <span class="acc">no son lo mismo</span></h3>
<div class="grid3">{tres_cosas_html}</div>
<div class="card c-yel"><p class="paso">en el banco</p><p style="margin:0">{a_html(FRASE_BANCO)}</p></div>
</section>

<section id="declarativo">
<div class="card c-lav">
<p class="paso">comprobación · {hora('Ficha')}</p>
<h2>¿Cuál es <span class="acc">declarativo</span>?</h2>
<div class="meta">{A_LA_VEZ}</div>
<p>Declarativo = dice <b>qué</b> pasa en el negocio, no <b>cómo</b> se hace en la pantalla. Tres letras en el chat, en orden, al mismo tiempo.</p>
{preguntas('decl', DECLARATIVO)}
</div>
</section>

<section id="revisor">
<div class="card c-cyan">
<h2>Tu CP en Gherkin · <span class="acc">el revisor de escenarios</span></h2>
<div class="meta"><span class="chip">mírame {hora('Mírame')} · salas {hora('Salas, tramo 1')} · tramo 1 · 8 min</span><span class="chip">un CP por sala: CP-102 a CP-106</span></div>
<p>Escriban el escenario de su CP en el cuadro y pulsen <b>Revisar</b>. El revisor señala lo típico: clics, localizadores, más de 5 pasos, falta de ID o un «Entonces» sin dato. Es una ayuda, no un juez: si el esperado es el correcto lo deciden ustedes.</p>
<p class="criterio">{a_html(CRITERIO_REVISOR)}</p>
</div>
<div class="grid2 revisor">
<div class="card">
<p class="paso">su caso manual</p>
<p><label for="cp-elegido"><b>Mi caso:</b></label> <select id="cp-elegido" class="cp-sel">{opciones_cp}</select></p>
{paneles_cp}
</div>
<div class="card">
<p class="paso">su escenario</p>
<label for="gherkin" class="nota">Escriban sobre la plantilla. Se guarda solo en este navegador.</label>
<textarea id="gherkin" class="gherkin" spellcheck="false">{html.escape(PLANTILLA_FEATURE)}
</textarea>
<div class="barra">
<button type="button" class="grande" id="revisar-gherkin">Revisar</button>
<button type="button" id="reiniciar-gherkin">Reiniciar</button>
<button type="button" id="copiar-gherkin">Copiar</button><span class="ok" id="gherkin-ok" aria-live="polite"></span>
<button type="button" id="cargar-cp101">Cargar el CP-101 resuelto</button>
<button type="button" id="deshacer" hidden>Deshacer</button>
</div>
<p class="nota" id="estado-revisor" aria-live="polite"></p>
<div class="barra"><label for="sala"><b>Mi sala:</b></label> <select id="sala" class="cp-sel">{opciones_sala}</select></div>
<div class="resumen" id="resumen" hidden><span class="r-texto"></span><button type="button" id="copiar-resumen">Copiar para el chat</button><span class="ok" id="resumen-ok" aria-live="polite"></span></div>
<div id="hallazgos"></div>
</div>
</div>
<div class="card c-yel">
<p class="paso">mírame · {hora('Mírame')}</p>
<p style="margin-top:0">El instructor carga el CP-101 resuelto en el revisor (0 errores) y lo corre con <code>{html.escape(CORRER_CP101)}</code>: el reporte HTML muestra los cuatro pasos con el texto del escenario.</p>
<p class="nota">Con el repo instalado, los <code>.feature</code> de <code>especificaciones/</code> se revisan con <code>npm.cmd run revisar-escenarios</code>: son las mismas reglas de esta página.</p>
</div>
</section>

<section id="capas">
<div class="card">
<h2>Del escenario <span class="acc">a las capas</span></h2>
<div class="meta"><span class="chip">{hora('Del escenario')}</span><span class="chip">el CP-101, paso a paso</span></div>
<table class="apilar"><thead><tr><th>En el escenario</th><th>Capa</th><th>Pieza</th><th>En el código</th></tr></thead><tbody>{mapeo_html}</tbody></table>
<p class="frase-grande">{a_html(REGLA_MAPEO)}</p>
</div>
<h3>Tres precisiones que afectan lo que construyen hoy</h3>
<div class="grid3">{precisiones_html}</div>
</section>

<section id="mapeo">
<div class="card c-lime">
<h2>Tu mapeo · <span class="acc">cada paso a su capa</span></h2>
<div class="meta"><span class="chip">salas {hora('Salas, tramo 2')} · tramo 2 · 8 min</span></div>
<p>{a_html(TU_MAPEO)}</p>
<p class="criterio">{a_html(CRITERIO_MAPEO)}</p>
<div class="barra"><button type="button" id="traer-pasos">Traer los pasos de mi escenario</button><span class="ok" id="traer-ok" aria-live="polite"></span>
<label for="sala-mapeo"><b>Mi sala:</b></label> <select id="sala-mapeo" class="cp-sel">{opciones_sala}</select></div>
<table class="mapeo" id="tabla-mapeo"><thead><tr><th></th><th>Paso de Gherkin</th><th>Capa</th><th>Pieza</th></tr></thead><tbody>{mapeo_filas}</tbody></table>
<p class="contador" id="mapeo-cuenta" aria-live="polite"></p>
<div class="barra"><button type="button" class="grande" id="copiar-mapeo">Copiar mi mapeo</button><span class="ok" id="mapeo-ok" aria-live="polite"></span>
<button type="button" id="reiniciar-mapeo">Reiniciar</button></div>
</div>
</section>

<section id="que-capa">
<div class="card c-lav">
<p class="paso">comprobación · {hora('«¿Qué capa')}</p>
<h2>¿Qué capa <span class="acc">ejecuta este paso</span>?</h2>
<div class="meta">{A_LA_VEZ}</div>
{preguntas('capa', QUE_CAPA)}
</div>
</section>

<section id="rosetta">
<div class="card">
<p class="paso">solo lectura · 2 min</p>
<h2>Rosetta · <span class="acc">lo de hoy en el framework del banco</span></h2>
<p>Playwright + TypeScript a la izquierda; lo que van a heredar (Java + Selenium + Cucumber o Serenity) a la derecha.</p>
<table class="apilar"><thead><tr><th>La pieza</th><th>Hoy (Playwright)</th><th>En el banco (Selenium · Cucumber · Serenity)</th></tr></thead><tbody>{rosetta_html}</tbody></table>
<p class="frase-grande">{a_html(ROSETTA_FRASE)}</p>
</div>
</section>

<section id="proyecto">
<div class="card c-peach">
<h2>Tu proyecto · <span class="acc">empieza hoy</span></h2>
<div class="meta"><span class="chip">{hora('Tu proyecto')} · 20 min, fijo</span></div>
<p class="frase-grande">{a_html(PREGUNTA_GUIA)}</p>
<p><b>Hoy:</b> {a_html(PLAN_HOY)}</p>
<p>Las vías: {vias_html}.</p>
<p><b>Escríbanla en el chat:</b></p>
<div class="frase">{frase_inputs}</div>
<p><button type="button" class="grande" id="copiar-frase" data-frase="{html.escape(FRASE_PROYECTO)}">Copiar mi frase</button><span class="ok" id="frase-ok" aria-live="polite"></span></p>
<p><a class="boton enorme" href="{PROYECTO}">Abrir el kit de proyecto</a></p>
<p class="nota">Las vías, la ficha, la matriz de trazabilidad, el criterio de listo y el plan por sesión están en el kit. Su escenario, en el <a href="#revisor">revisor</a> de arriba.</p>
</div>
</section>

<section id="boleto">
<div class="card c-lime">
<h2>Boleto de salida</h2>
<div class="meta"><span class="chip">{hora('Boleto de la S7')}</span>{A_LA_VEZ}</div>
<p>Las cuatro letras en orden, en el chat, todos al mismo tiempo.</p>
{preguntas('b7', BOLETO)}
</div>
</section>

<section id="cierre">
<div class="card">
<h2>Cierre</h2>
<div class="meta"><span class="chip">{hora('Cierre')}</span></div>
<p class="frase-grande">{a_html(FRASE_CIERRE)}</p>
{enlaces_html}
<p class="nota">En el repo: la ficha de hoy en <code>docs/gherkin-y-bdd.md</code>, los escenarios en <code>especificaciones/recargas.feature</code> y la prueba en <code>tests/recargas/CP-101-gherkin.spec.ts</code>.</p>
</div>
</section>
<p class="nota">Página de práctica del Bootcamp QA · Knot Academy. No carga nada de internet salvo las fuentes. Los datos son de práctica: nunca escriban aquí datos, pantallas ni casos del banco. Lo que escriban queda solo en este navegador.</p>
</div>
<script type="application/json" id="datos-s7">{DATOS}</script>
<script>
{REVISOR_JS}
</script>
<script>{JS}</script>
</body>
</html>
'''
salida = RAIZ / 'laboratorio' / 'actividades_S7.html'
salida.write_text(HTML, encoding='utf-8')
if PARA_ENVIAR.is_dir():
    shutil.copyfile(salida, PARA_ENVIAR / 'actividades_S7.html')

# ---------- docs/gherkin-y-bdd.md: la misma ficha, para leer en el repo ----------
md = ['# Gherkin y BDD sobre el framework (S7)', '',
      'Construye sobre las capas de la S3 (ver [arquitectura.md](arquitectura.md)), los patrones de la S5 (ver [patrones.md](patrones.md)) '
      'y la configuración de la S6 (ver [configuracion-y-localizadores.md](configuracion-y-localizadores.md)). Este archivo lo genera '
      '`laboratorio/generar/generar_actividades_s7.py` desde `fichas_s7.py`, la misma fuente de las actividades y del deck: si cambias algo, cámbialo allí.', '',
      f'**{IDEA_FUERZA}**', '', f'Objetivo de la sesión: {OBJETIVO}', '',
      '| Pieza | Dónde verla |', '|---|---|',
      '| Los escenarios (CP-101 resuelto; CP-102 a CP-106 para practicar) | `especificaciones/recargas.feature` |',
      '| La prueba con un `test.step` por paso | `tests/recargas/CP-101-gherkin.spec.ts` |',
      '| La tarea del «Cuando», que usa el Page Object por dentro | `src/screenplay/recargas/RecargarDesdeLaPantalla.ts` |',
      '| El revisor de escenarios | `laboratorio/revisor-escenarios.js` · `npm.cmd run revisar-escenarios` |', '',
      f'## {FICHA["titulo"]}', '', '| | |', '|---|---|']
md += [f'| **{et}** | {FICHA[k]} |' for k, et in FILAS]
md += ['', '## BDD, Gherkin y la herramienta no son lo mismo', '', '| | Qué es | Hoy |', '|---|---|---|']
md += [f'| **{a}** | {b} | {c} |' for a, b, c in TRES_COSAS]
md += ['', FRASE_BANCO, '', '## El CP-101 en tres idiomas', '', '**1 · El caso manual**', '']
md += [f'- {l}' for l in TRES_IDIOMAS['manual']]
md += ['', '**2 · Gherkin** (`especificaciones/recargas.feature`)', '', '```gherkin', TRES_IDIOMAS['gherkin'], '```', '',
       '**3 · La prueba** (`tests/recargas/CP-101-gherkin.spec.ts`)', '', '```ts', PRUEBA_CP101, '```', '',
       f'Se corre con `{CORRER_CP101}`. El reporte HTML muestra los pasos con el texto del escenario.', '',
       '## Del escenario a las capas', '', '| En el escenario | Capa | Pieza | En el código (CP-101) |', '|---|---|---|---|']
md += [f'| {a} | {b} | {c} | {d} |' for a, b, c, d in MAPEO]
md += ['', f'**{REGLA_MAPEO}**', '', '### Tres precisiones', '']
md += [f'- **{t}.** {x}' for _, t, x in PRECISIONES]
md += ['', '## Rosetta: lo de hoy en Java + Selenium + Cucumber o Serenity', '', '| La pieza | Hoy (Playwright) | En el banco |', '|---|---|---|']
md += [f'| {a} | {b} | {c} |' for a, b, c in ROSETTA]
md += ['', ROSETTA_FRASE, '', '## El revisor de escenarios', '',
       'Señala lo típico: clics y pantalla (aviso), localizadores o código (error), esperas fijas y claves escritas (error), '
       'falta de ID `@CP-xxx` (error), falta de Dado, Cuando o Entonces (error), más de 5 pasos (aviso) y un «Entonces» sin dato (aviso). '
       'Es una ayuda, no un juez: si el esperado es el correcto lo decide la persona.', '',
       '- En el navegador: actividades de la S7, sección «Tu CP en Gherkin».',
       '- Con el repo: `npm.cmd run revisar-escenarios` (o `-- archivo.feature`).',
       '- La solución de la práctica (CP-102 a CP-106) está en `laboratorio/generar/s07_solucion/especificaciones/recargas.feature`.', '',
       '## La plantilla de un escenario', '', '```gherkin', PLANTILLA_FEATURE, '```', '',
       '## Fuentes', '']
md += [f'- {f}' for f in FUENTES]
md.append('')
(RAIZ / 'docs' / 'gherkin-y-bdd.md').write_text('\n'.join(md), encoding='utf-8')
print(f'actividades_S7.html y docs/gherkin-y-bdd.md listos ({len(RESUELTOS)} escenarios en la solución; copia en para_enviar: {PARA_ENVIAR.is_dir()})')
