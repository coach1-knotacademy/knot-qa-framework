"""Genera laboratorio/proyecto.html (el kit del proyecto final) y laboratorio/guia_estudio.html (la guía de estudio, repaso opcional).

Todo el contenido sale de fichas_s7.py (y de fichas_s6 / fichas_s5 para los CP, la escalera, la lista de cotejo y los boletos),
la misma fuente que usan las actividades y el deck de la S7: si cambia una frase, se cambia allí.
Decisiones en ../../../sesion_07/council_S7.md (veredicto del presidente).

En Pages se publican como proyecto.html y guia-estudio.html (scripts/construir-sitio.js). Los enlaces del sitio van relativos
(plantilla.html, actividades-s7.html, presentaciones/presentacion_S5.pdf…). En la copia de ../para_enviar/ esos mismos enlaces
apuntan a la dirección completa de Pages, para que funcionen con doble clic. Los de GitHub siempre van completos.
No carga nada de internet (solo las fuentes de Google, y si no cargan se usan las del sistema).

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_proyecto.py
"""
import html, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
sys.path.insert(0, str(D))
from fichas_s7 import (PAGES, CPS, COTEJO, ESCALERA, BOLETO_S6, BOLETO, a_html,  # noqa: E402
                       PREGUNTA_GUIA, FRASE_PROYECTO, VIAS, KITS, KITS_INTRO, KITS_FRASE, FICHA_PROYECTO, MATRIZ, CRITERIO_LISTO, CHARLA, CHARLA_NOTA,
                       PLAN_PROYECTO, REGLAS_PROYECTO, PLANTILLA_FEATURE, GUIA_SESIONES, LO_PRECISO)
from fichas_s5 import BOLETO as BOLETO_S5  # noqa: E402
# S8 (council_S8): la vía D de especificador, el plan del proyecto de la S8 y la guía de la S7 (con el índice del video) y la S8.
from fichas_s8 import (VIA_ESPECIFICADOR, PROYECTO_S8, PROYECTO_ESPECIFICADOR, GUIA_S7, GUIA_S8,  # noqa: E402
                       BOLETO as BOLETO_S8)
# S9 (council_S9): el plan del proyecto de la S9 (la falla provocada y clasificada), la guía de la S9 y su boleto.
from fichas_s9 import (GUIA_S9, PROYECTO_S9, PROYECTO_ESPECIFICADOR as PROYECTO_ESPECIFICADOR_S9,  # noqa: E402
                       BOLETO as BOLETO_S9)

VIAS_TODAS = VIAS + [VIA_ESPECIFICADOR]
# El plan de la S8 sale de PROYECTO_S8 (20 min fijos, en la sala principal), no del plan que se escribió en la S7.
# El de la S9 sale de PROYECTO_S9 (20 min fijos en la sala principal, y después el ensayo de 90 s en las salas).
PLAN_PROYECTO = [(ses, f, '20 min fijos', PROYECTO_S8 + ' ' + PROYECTO_ESPECIFICADOR) if ses == 'S8'
                 else (ses, f, '20 min fijos + el ensayo', PROYECTO_S9 + ' ' + PROYECTO_ESPECIFICADOR_S9) if ses == 'S9'
                 else (ses, f, t, q)
                 for ses, f, t, q in PLAN_PROYECTO]
assert any(ses == 'S8' for ses, _, _, _ in PLAN_PROYECTO), 'El plan del proyecto no tiene la S8'
assert any(ses == 'S9' for ses, _, _, _ in PLAN_PROYECTO), 'El plan del proyecto no tiene la S9'
GUIA_TODAS = GUIA_SESIONES + [g for g in (GUIA_S7, GUIA_S8, GUIA_S9) if g['s'] not in {x['s'] for x in GUIA_SESIONES}]

LOGO = re.search(r'<img src="(data:image/png;base64,[^"]+)"', (D / 'plantilla.html').read_text(encoding='utf-8')).group(1)
PARA_ENVIAR = RAIZ.parent / 'para_enviar'
e = lambda t: html.escape(t, quote=True)

# Rutas del sitio de Pages (relativas a la raíz del sitio).
SITIO = {
  'plantilla': 'plantilla.html',
  'actividades_s7': 'actividades-s7.html',
  'actividades_s8': 'actividades-s8.html',
  'actividades_s9': 'actividades-s9.html',
  'laminas': 'laminas-s10.html',
  'guia': 'guia-estudio.html',
  'proyecto': 'proyecto.html',
  'lab_s4': 'laboratorio-s4.html',
  'lab_s5': 'laboratorio-s5.html',
  'lab_s6': 'laboratorio-s6.html',
  'banco': 'banco/recargas.html',
  'voz': 'voz.html', 'movil': 'movil.html', 'web': 'web-real.html', 'integraciones': 'integraciones.html',
}


def enlace(ruta, base):
    """Las rutas del sitio llevan la base ('' en Pages, la dirección de Pages en la copia local). GitHub va tal cual."""
    return ruta if ruta.startswith(('http://', 'https://', '#')) else base + ruta


# ─────────────────────────── Piezas comunes (las mismas de actividades_S6) ───────────────────────────
CSS = """
:root { --bg:#f7f6f2; --surface:#fff; --ink:#1d2130; --muted:#454a58; --morado:#8b55f6; --morado-osc:#5b34c9; --neon:#8be000;
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
a { color:var(--morado-osc); }
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
.grid2 > *, .grid3 > * { min-width:0; } .grid2 > .card, .grid3 > .card { margin:0; }
@media (max-width:820px) { .grid2, .grid3 { grid-template-columns:minmax(0,1fr); } }
code, pre { font-variant-ligatures:none; }
code { font-family:var(--f-mono); font-size:.88em; background:#efece3; border-radius:5px; padding:1px 5px; overflow-wrap:anywhere; }
pre.code { max-width:100%; overflow-wrap:normal; font:13px/1.55 var(--f-mono); background:#1f2331; color:#e8ebf2; border:2px solid var(--ink); border-radius:12px; padding:14px; overflow:auto; margin:10px 0; }
pre.code.prosa { white-space:pre-wrap; overflow-wrap:anywhere; }
table { width:100%; border-collapse:collapse; } td, th { border-top:2px solid var(--ink); padding:10px 8px; vertical-align:top; text-align:left; }
th { font-weight:800; font-size:14px; color:var(--muted); } th:first-child { white-space:nowrap; }
td.n { font-family:var(--f-display); width:2em; }
@media (max-width:820px) { table.apilar, table.apilar tbody, table.apilar tr, table.apilar td { display:block; }
  table.apilar thead { display:none; } table.apilar td { border-top:0; padding:4px 8px; } table.apilar tr { border-top:2px solid var(--ink); padding:6px 0; }
  table.apilar td[data-k]::before { content:attr(data-k); display:block; font-weight:800; font-size:13px; color:var(--morado-osc); } td.n { width:auto; } }
button { font:800 14px var(--f-body); border:2px solid var(--ink); border-radius:10px; background:var(--surface); color:var(--ink); padding:6px 10px; margin:2px; cursor:pointer; }
button:hover { background:var(--lav); }
button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible, summary:focus-visible { outline:3px solid var(--morado-osc); outline-offset:2px; }
button.grande { background:var(--neon); box-shadow:3px 3px 0 var(--ink); padding:9px 16px; font-size:15px; }
ol.pasos li, ul.lista li, ol.lista li, ol.boleto li { margin:6px 0; }
ul.lista, ol.lista, ol.pasos { padding-left:22px; }
.nota { color:var(--muted); font-size:14px; }
a.boton { display:inline-block; text-decoration:none; color:var(--ink); background:var(--neon); border:2px solid var(--ink); border-radius:10px; box-shadow:3px 3px 0 var(--ink); padding:9px 16px; font-weight:800; margin:4px 6px 4px 0; }
a.boton.blanco { background:var(--surface); } a.boton:hover { background:var(--lav); }
a.boton.chico { padding:5px 11px; font-size:14px; box-shadow:2px 2px 0 var(--ink); }
.frase { display:flex; flex-wrap:wrap; gap:8px; align-items:center; font-size:17px; }
.frase input { font:16px var(--f-body); border:2px solid var(--ink); border-radius:8px; padding:6px 8px; min-width:0; max-width:100%; background:var(--surface); color:var(--ink); flex:1 1 200px; }
.ok { color:var(--ok); font-weight:800; margin-left:6px; }
.paso { font:400 15px var(--f-display); color:var(--morado-osc); margin:0 0 4px; }
.opciones { margin:2px 0 8px; }
.check { display:flex; gap:10px; align-items:flex-start; cursor:pointer; } .check input { width:20px; height:20px; margin-top:3px; flex:none; accent-color:var(--morado-osc); }
ul.checks { list-style:none; padding-left:0; } ul.checks li { margin:10px 0; }
.contador { font:400 18px var(--f-display); color:var(--morado-osc); }
.rotulo { display:inline-block; background:var(--yellow); border:2px solid var(--ink); border-radius:999px; padding:6px 14px; font-weight:800; box-shadow:3px 3px 0 var(--ink); margin:6px 0 4px; }
.pregunta { font:400 clamp(22px,3.6vw,32px)/1.2 var(--f-display); margin:4px 0 0; text-wrap:balance; }
.cab { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap; }
.cab > div { min-width:0; flex:1 1 240px; }
.via .letra { display:inline-grid; place-items:center; width:2em; height:2em; border:2px solid var(--ink); border-radius:999px; background:var(--surface); font:400 18px var(--f-display); margin-right:8px; vertical-align:middle; }
.via h3 { margin-top:6px; }
a.kit { display:block; color:var(--ink); text-decoration:none; } a.kit:hover { transform:translate(-1px,-1px); box-shadow:6px 6px 0 var(--ink); } a.kit b { color:var(--morado-osc); }
.via dt { font-weight:800; color:var(--morado-osc); margin-top:10px; } .via dd { margin:2px 0 0; }
.ficha { display:grid; grid-template-columns:minmax(0,13em) minmax(0,1fr); border-top:2px solid var(--ink); }
.ficha .fk, .ficha .fv { padding:9px 8px; border-bottom:1px solid #c9c5ba; } .ficha .fk { font-weight:800; color:var(--morado-osc); }
@media (max-width:980px) { .ficha { grid-template-columns:minmax(0,1fr); } .ficha .fk { border-bottom:0; padding-bottom:0; } }
.estado-verde { font-weight:800; color:var(--ok); } .estado-rojo { font-weight:800; color:var(--bad); }
.min { font:400 20px var(--f-display); color:var(--morado-osc); white-space:nowrap; }
ol.escalera { list-style:none; padding:0; margin:12px 0; }
.peldano { display:flex; gap:12px; align-items:flex-start; border:2px solid var(--ink); border-radius:12px; background:var(--surface); padding:10px 12px; margin:8px 0; box-shadow:3px 3px 0 var(--ink); }
.peldano .num { font:400 22px var(--f-display); width:1.6em; flex:none; color:var(--morado-osc); }
.peldano > div { min-width:0; }
.p1 { margin-right:16%; } .p2 { margin-left:4%; margin-right:12%; } .p3 { margin-left:8%; margin-right:8%; } .p4 { margin-left:12%; margin-right:4%; } .p5 { margin-left:16%; background:var(--peach); }
@media (max-width:600px) { .p1, .p2, .p3, .p4, .p5 { margin-left:0; margin-right:0; } }
.sesion .meta { margin-top:0; } .sesion h3 { margin-top:4px; } .sesion .idea { font-weight:700; }
.sesion ul.lista { margin:6px 0 10px; }
table.video td.m { font-family:var(--f-mono); font-weight:600; width:5.5em; white-space:nowrap; }
.preciso td.oye { width:42%; } .preciso td.oye span { color:var(--muted); }
@media (max-width:820px) { .preciso td.oye { width:auto; } }
.flecha { font-weight:800; color:var(--morado-osc); }
ol.pasos-cp { margin:0; padding-left:20px; } ol.pasos-cp li { margin:2px 0; }
td.id { font-family:var(--f-display); white-space:nowrap; }
.creditos { font:700 15px/1.4 var(--f-mono); background:var(--surface); border:2px solid var(--ink); border-radius:10px; padding:8px 12px; margin:4px 0; overflow-wrap:anywhere; }
table.ejemplos { width:auto; min-width:60%; max-width:100%; margin:6px 0; font:13px/1.4 var(--f-mono); background:var(--surface); border:2px solid var(--ink); border-radius:10px; border-collapse:separate; border-spacing:0; overflow:hidden; }
table.ejemplos th, table.ejemplos td { border-top:1px solid #c9c5ba; padding:5px 10px; } table.ejemplos td:not(:last-child) { white-space:nowrap; } table.ejemplos thead th { border-top:0; background:var(--yellow); color:var(--ink); font:800 13px var(--f-mono); white-space:normal; }
.via .aviso { background:var(--surface); border:2px dashed var(--ink); border-radius:10px; padding:6px 10px; font-weight:700; }
.respuestas { background:var(--yellow); border:2px dashed var(--ink); border-radius:12px; padding:4px 14px; margin-top:8px; }
.respuestas ol.boleto { padding-left:22px; }
"""

JS = """
(function () {
  function copiar(texto, aviso) {
    var listo = function () { if (aviso) { aviso.textContent = 'Copiado'; setTimeout(function () { aviso.textContent = ''; }, 2000); } };
    var aMano = function () {
      var t = document.createElement('textarea'); t.value = texto; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.left = '-9999px';
      document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); listo(); } catch (e) { if (aviso) aviso.textContent = 'Selecciónalo y usa Ctrl + C'; }
      document.body.removeChild(t);
    };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(texto).then(listo, aMano); else aMano();
  }
  function aviso(id) { return document.querySelector('[data-copiado="' + id + '"]'); }
  document.querySelectorAll('[data-copiar]').forEach(function (b) {
    b.addEventListener('click', function () {
      var id = b.getAttribute('data-copiar'), el = document.getElementById(id);
      copiar(el.value !== undefined ? el.value : el.textContent, aviso(id));
    });
  });
  document.querySelectorAll('[data-revelar]').forEach(function (boton) {
    boton.addEventListener('click', function () { document.getElementById(boton.getAttribute('data-revelar')).hidden = false; boton.hidden = true; });
  });
  var frase = document.getElementById('copiar-frase');
  if (frase) frase.addEventListener('click', function () {
    var partes = document.querySelectorAll('.frase input'), molde = frase.getAttribute('data-molde').split('___'), texto = molde[0];
    partes.forEach(function (inp, i) { texto += (inp.value.trim() || '___') + (molde[i + 1] || ''); });
    copiar(texto, aviso('frase'));
  });
  // El criterio de listo: las casillas se guardan solo en este navegador (si el navegador lo permite).
  var CLAVE = 'knot-proyecto-criterio-listo';
  var casillas = document.querySelectorAll('input.listo'), cuenta = document.getElementById('listo-cuenta');
  function leer() { try { return JSON.parse(localStorage.getItem(CLAVE) || '{}') || {}; } catch (e) { return {}; } }
  function guardar(estado) { try { localStorage.setItem(CLAVE, JSON.stringify(estado)); } catch (e) { /* sin almacenamiento: se marca igual */ } }
  function contar() { var n = 0; casillas.forEach(function (c) { if (c.checked) n++; }); if (cuenta) cuenta.textContent = n + ' de ' + casillas.length + ' listos'; }
  var estado = leer();
  casillas.forEach(function (c) {
    c.checked = !!estado[c.getAttribute('data-id')];
    c.addEventListener('change', function () { var s = leer(); s[c.getAttribute('data-id')] = c.checked; guardar(s); contar(); });
  });
  var borrar = document.getElementById('listo-borrar');
  if (borrar) borrar.addEventListener('click', function () { casillas.forEach(function (c) { c.checked = false; }); guardar({}); contar(); });
  contar();
  var cot = document.querySelectorAll('input.cot'), cuentaCot = document.getElementById('cotejo-cuenta');
  function contarCot() { var n = 0; cot.forEach(function (c) { if (c.checked) n++; }); cuentaCot.textContent = n + ' de ' + cot.length + ' se cumplen'; }
  if (cuentaCot) { cot.forEach(function (c) { c.addEventListener('change', contarCot); }); contarCot(); }
})();
"""


def pagina(titulo, subtitulo, cuerpo, generador='generar_proyecto.py'):
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titulo}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&amp;family=Nunito:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;600&amp;display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · {subtitulo}</small></div>
{cuerpo}
<p class="nota">Página del Bootcamp QA · Knot Academy, generada con <code>laboratorio/generar/{generador}</code>. No carga nada de internet salvo las fuentes. Los datos son de práctica: nunca escribas aquí datos reales.</p>
</div>
<script>{JS}</script>
</body>
</html>
'''


def boton_copiar(id_, texto='Copiar'):
    return f'<button type="button" class="grande" data-copiar="{id_}">{texto}</button><span class="ok" data-copiado="{id_}" aria-live="polite"></span>'


def revelar(rid, boton, contenido):
    return f'<p><button type="button" class="grande" data-revelar="{rid}">{boton}</button></p><div id="{rid}" hidden>{contenido}</div>'


def boleto(bid, titulo, preguntas):
    items = ''.join(
        f'<li><p><b>{a_html(p)}</b></p><p class="opciones">' + ' · '.join(f'<b>{"abc"[k]})</b> {a_html(o)}' for k, o in enumerate(ops)) + '</p></li>'
        for p, ops, ok, por in preguntas)
    resp = ''.join(f'<li><b>{ok}</b> · {a_html(por)}</li>' for p, ops, ok, por in preguntas)
    return (f'<div class="card"><p class="paso">{titulo}</p><ol class="boleto">{items}</ol>'
            + revelar(f'resp-{bid}', 'Ver las respuestas', f'<div class="respuestas"><p class="paso" style="margin-top:10px">respuestas</p><ol class="boleto">{resp}</ol></div>') + '</div>')


# ─────────────────────────── proyecto.html ───────────────────────────
def proyecto(base):
    s = lambda clave: enlace(SITIO[clave], base)
    def extra_via(v):
        """La vía D (S8) trae sus límites, cuándo se entrega, la defensa en la S10 y la línea de créditos."""
        if 'limites' not in v:
            return ''
        cid = f'creditos-{v["id"].lower()}'
        return (f'<dt>Los límites</dt><dd><ul class="lista">' + ''.join(f'<li>{a_html(x)}</li>' for x in v['limites']) + '</ul></dd>'
                f'<dt>La defensa en la S10</dt><dd>{a_html(v["defensa"])}</dd>'
                f'<dt>Los créditos (en la primera lámina)</dt><dd><p class="creditos" id="{cid}">{e(v["creditos"])}</p>{boton_copiar(cid, "Copiar los créditos")}</dd>')

    vias = ''.join(
        f'<div class="card via c-{v["color"]}" id="via-{v["id"].lower()}"><p class="paso"><span class="letra">{v["id"]}</span>{e(v["verbo"])}</p>'
        f'<h3>{e(v["nombre"])}</h3>'
        + (f'<p class="aviso">{a_html(PROYECTO_ESPECIFICADOR)}</p>' if v is VIA_ESPECIFICADOR else '')
        + f'<dl><dt>Para quién</dt><dd>{a_html(v["para"])}</dd><dt>Qué</dt><dd>{a_html(v["que"])}</dd>'
        + extra_via(v)
        + f'<dt>Ejemplos</dt><dd><ul class="lista">' + ''.join(f'<li>{a_html(x)}</li>' for x in v['ejemplos']) + '</ul></dd></dl></div>'
        for v in VIAS_TODAS)

    kits = ''.join(
        f'<a class="card via kit c-{k["color"]}" href="{s(k["id"])}"><p class="paso">vía {e(k["via"])}</p><h3>{e(k["titulo"])}</h3>'
        f'<p>{a_html(k["caso"])}</p><p><b>Sin instalar:</b> {a_html(k["sin_instalar"])}</p><p class="nota">{a_html(k["para"])}</p><p><b>Abrir el kit →</b></p></a>'
        for k in KITS)

    partes_frase = FRASE_PROYECTO.split('___')
    placeholders = ['qué pruebas', 'qué puede salir mal', 'qué CP y qué evidencia']
    frase_inputs = e(partes_frase[0])
    for i, resto in enumerate(partes_frase[1:]):
        frase_inputs += f'<input type="text" aria-label="{e(placeholders[i])}" placeholder="{e(placeholders[i])}">{e(resto)}'

    ficha_vacia = 'FICHA DE MI PROYECTO (una hoja)\n\n' + '\n\n'.join(f'{k}:\n___' for k, _ in FICHA_PROYECTO)
    ficha_llena = ''.join(f'<div class="fk">{a_html(k)}</div><div class="fv">{a_html(v)}</div>' for k, v in FICHA_PROYECTO)

    cols = MATRIZ['columnas']
    def celda_estado(t):
        cls = 'estado-verde' if t.lower().startswith('verde') else 'estado-rojo' if t.lower().startswith('rojo') else ''
        return f'<span class="{cls}">{a_html(t)}</span>' if cls else a_html(t)
    matriz_filas = ''.join('<tr>' + ''.join(
        f'<td data-k="{e(cols[i])}">{celda_estado(c) if i == len(cols) - 1 else a_html(c)}</td>' for i, c in enumerate(fila)) + '</tr>'
        for fila in MATRIZ['ejemplo'])
    matriz_vacia = '\t'.join(cols) + '\n' + '\n'.join('\t'.join(['CP-___'] + [''] * (len(cols) - 1)) for _ in range(3))

    listo = ''.join(
        f'<li><label class="check"><input type="checkbox" class="listo" data-id="c{n}"> <span><b>{a_html(t)}.</b> {a_html(d)}</span></label></li>'
        for n, (t, d) in enumerate(CRITERIO_LISTO, 1))

    charla = ''.join(f'<tr><td data-k="Tiempo"><span class="min">{e(m)}</span></td><td data-k="Parte"><b>{a_html(p)}</b></td><td data-k="Qué va">{a_html(q)}</td></tr>'
                     for m, p, q in CHARLA)
    # S9: la fila lleva el enlace a la plantilla de láminas y a las actividades (la línea «Mi CP · falla · caja · evidencia»).
    extra_plan = {'S9': f'<p><a class="boton chico" href="{s("laminas")}">La plantilla de láminas</a>'
                        f'<a class="boton blanco chico" href="{s("actividades_s9")}#proyecto">Actividades S9 · tu falla</a></p>'}
    plan = ''.join(f'<tr><td class="id" data-k="Sesión">{e(ses)}</td><td data-k="Fecha">{e(f)}</td><td data-k="En clase">{e(t)}</td><td data-k="Qué se hace">{a_html(q)}{extra_plan.get(ses, "")}</td></tr>'
                   for ses, f, t, q in PLAN_PROYECTO)
    reglas = ''.join(f'<li>{a_html(r)}</li>' for r in REGLAS_PROYECTO)

    cps = ''.join(
        f'<tr><td class="id" data-k="CP">{cp["id"]}</td><td data-k="Caso"><b>{e(cp["titulo"])}</b></td><td data-k="Precondición">{e(cp["pre"])}</td>'
        f'<td data-k="Pasos"><ol class="pasos-cp">' + ''.join(f'<li>{e(p)}</li>' for p in cp['pasos']) + '</ol></td>'
        f'<td data-k="Resultado esperado">{e(cp["esperado"])}' + (f'<p class="nota">{a_html(cp["nota"])}</p>' if cp.get('nota') else '') + '</td></tr>'
        for cp in CPS)

    cuerpo = f'''<h1>El kit de <span class="acc">tu proyecto final</span></h1>
<p class="lead">Todo lo que necesitas para armar tu proyecto: la pregunta que responde, las cuatro vías, la ficha de una hoja, el escenario, la matriz de trazabilidad, el criterio de listo y la charla del último día.</p>
<p class="rotulo">Todo se trabaja en clase; avanzar por tu cuenta es opcional.</p>
<nav class="top" aria-label="Secciones">
<a href="#pregunta">La pregunta</a><a href="#vias">Las vías</a><a href="#kits">Los kits</a><a href="#frase">La frase</a><a href="#ficha">La ficha</a><a href="#escenario">El escenario</a><a href="#matriz">La matriz</a><a href="#listo">Criterio de listo</a><a href="#charla">La charla</a><a href="#plan">Plan por sesión</a><a href="#reglas">Reglas</a><a href="#enlaces">Enlaces y CP</a>
</nav>

<section id="pregunta">
<div class="card c-lav">
<p class="paso">la pregunta guía</p>
<p class="pregunta">{e(PREGUNTA_GUIA)}</p>
</div>
</section>

<section id="vias">
<h2>Cuatro vías, <span class="acc">el mismo valor</span></h2>
<p>Elige la que te sirve según lo que puedes hacer en tu equipo y lo que pruebas en tu trabajo.</p>
<div class="grid2">{vias}</div>
</section>

<section id="kits">
<h2>Kits para empezar <span class="acc">con algo real</span></h2>
<p>{a_html(KITS_INTRO)}</p>
<div class="grid2">{kits}</div>
<p class="nota">{a_html(KITS_FRASE)}</p>
</section>

<section id="frase">
<div class="card c-lime">
<h2>La frase de <span class="acc">tu proyecto</span></h2>
<p>Complétala y pégala en el chat.</p>
<div class="frase">{frase_inputs}</div>
<p><button type="button" class="grande" id="copiar-frase" data-molde="{e(FRASE_PROYECTO)}">Copiar mi frase</button><span class="ok" data-copiado="frase" aria-live="polite"></span></p>
</div>
</section>

<section id="ficha">
<h2>La ficha de <span class="acc">una hoja</span></h2>
<div class="grid2">
<div class="card">
<div class="cab"><div><p class="paso">plantilla · cópiala y llénala</p></div><div style="flex:none">{boton_copiar("ficha-vacia", "Copiar la ficha")}</div></div>
<pre class="code prosa" id="ficha-vacia">{e(ficha_vacia)}</pre>
</div>
<div class="card c-yel">
<p class="paso">ejemplo lleno</p>
<div class="ficha">{ficha_llena}</div>
</div>
</div>
</section>

<section id="escenario">
<div class="card">
<div class="cab"><div><h2>Tu escenario en <span class="acc">Gherkin</span></h2><p>Reemplaza lo que está entre <code>&lt;…&gt;</code>. Después pásalo por el revisor de escenarios: desde la S8, como Esquema del escenario con su tabla de Ejemplos (en el revisor, «Mi proyecto»).</p></div>
<div style="flex:none">{boton_copiar("plantilla-feature", "Copiar el .feature")}</div></div>
<pre class="code" id="plantilla-feature">{e(PLANTILLA_FEATURE)}</pre>
<a class="boton" href="{s("actividades_s8")}#revisor">Abrir el revisor con Ejemplos (actividades S8)</a><a class="boton blanco" href="{s("actividades_s7")}">El revisor de la S7</a>
</div>
</section>

<section id="matriz">
<div class="card">
<div class="cab"><div><h2>La matriz de <span class="acc">trazabilidad</span></h2><p>Una fila por CP: del ID del caso a la evidencia.</p></div>
<div style="flex:none">{boton_copiar("matriz-vacia", "Copiar la matriz vacía")}</div></div>
<table class="apilar"><thead><tr>{"".join(f"<th>{e(c)}</th>" for c in cols)}</tr></thead><tbody>{matriz_filas}</tbody></table>
<textarea hidden id="matriz-vacia">{e(matriz_vacia)}</textarea>
<p class="nota">La matriz vacía se copia separada por tabulaciones: se pega directo en Excel.</p>
</div>
</section>

<section id="listo">
<div class="card c-lime">
<h2>El criterio <span class="acc">de listo</span></h2>
<p>Lo que tiene tu proyecto el día de la presentación. Marca lo que ya tienes.</p>
<ul class="checks">{listo}</ul>
<p class="contador" id="listo-cuenta" aria-live="polite"></p>
<p><button type="button" id="listo-borrar">Desmarcar todo</button></p>
<p class="nota">Las marcas se guardan solo en este navegador. Si el navegador no lo permite, se pueden marcar igual, pero no quedan guardadas.</p>
</div>
</section>

<section id="charla">
<div class="card">
<h2>La charla <span class="acc">del último día</span></h2>
<table class="apilar"><thead><tr><th>Tiempo</th><th>Parte</th><th>Qué va</th></tr></thead><tbody>{charla}</tbody></table>
<p class="nota" style="font-size:15px">{a_html(CHARLA_NOTA)}</p>
<p><a class="boton" href="{s("laminas")}">Arma tus láminas con la plantilla (una por página, a 16:9)</a></p>
</div>
</section>

<section id="plan">
<div class="card c-cyan">
<h2>El plan, <span class="acc">sesión por sesión</span></h2>
<p><b>Todo se trabaja en clase; avanzar por tu cuenta es opcional.</b></p>
<table class="apilar"><thead><tr><th>Sesión</th><th>Fecha</th><th>En clase</th><th>Qué se hace</th></tr></thead><tbody>{plan}</tbody></table>
</div>
</section>

<section id="reglas">
<div class="card c-peach">
<h2>Las <span class="acc">reglas</span></h2>
<ul class="lista">{reglas}</ul>
</div>
</section>

<section id="enlaces">
<h2>Lo que <span class="acc">vas a usar</span></h2>
<div class="card">
<a class="boton" href="{s("plantilla")}">La plantilla del framework</a><a class="boton blanco" href="{s("laminas")}">La plantilla de láminas (S10)</a><a class="boton blanco" href="{s("actividades_s9")}">Actividades S9 · triage</a><a class="boton blanco" href="{s("actividades_s8")}">Actividades S8 · revisor con Ejemplos</a><a class="boton blanco" href="{s("actividades_s7")}">Actividades S7 · revisor de escenarios</a><a class="boton blanco" href="{s("lab_s6")}">Laboratorio S6</a><a class="boton blanco" href="{s("lab_s5")}">Laboratorio S5</a><a class="boton blanco" href="{s("lab_s4")}">Laboratorio S4</a><a class="boton blanco" href="{s("banco")}">Banco Demo · Recargas</a><a class="boton blanco" href="{s("guia")}">Guía de estudio</a>
<p class="nota">Banco Demo: usuario <code>ana</code>, clave <code>Clave123</code> (es de práctica) y el código que llega al buzón de SMS.</p>
</div>
<div class="card">
<h3 style="margin-top:0">Los casos del Banco Demo (CP-101 a CP-106)</h3>
<p>Para tu proyecto, si no traes un caso propio. Son casos del Banco Demo: nunca casos del ALM del banco.</p>
<table class="apilar"><thead><tr><th>CP</th><th>Caso</th><th>Precondición</th><th>Pasos</th><th>Resultado esperado</th></tr></thead><tbody>{cps}</tbody></table>
</div>
</section>'''
    return pagina('Kit de proyecto', 'proyecto final', cuerpo)


# ─────────────────────────── guia_estudio.html ───────────────────────────
NOTA_VIDEO = 'El video está en el Drive del curso; usa estos minutos para ir al tema.'


def guia(base):
    tarjetas = []
    for g in GUIA_TODAS:
        enl = ''.join(f'<a class="boton blanco chico" href="{enlace(u, base)}">{e(t)}</a>' for t, u in g['enlaces'])
        tarjetas.append(
            f'<div class="card sesion"><div class="meta"><span class="chip">{e(g["s"])}</span><span class="chip">{e(g["fecha"])}</span></div>'
            f'<h3>{a_html(g["tema"])}</h3><p class="idea">{a_html(g["idea"])}</p>'
            f'<p class="paso">tres conceptos</p><ul class="lista">' + ''.join(f'<li>{a_html(c)}</li>' for c in g['conceptos']) + '</ul>'
            f'<div>{enl}</div>' + (f'<p class="nota"><a href="#video-{g["s"].lower()}">El video, por minuto ↓</a></p>' if g.get('video') else '') + '</div>')
    # El índice de cada video va en su propia tarjeta, a lo ancho, después de las sesiones.
    videos = ''.join(
        f'<div class="card c-cyan" id="video-{g["s"].lower()}"><h3 style="margin-top:0">El video de la {e(g["s"])}, por minuto</h3>'
        f'<p class="nota">{NOTA_VIDEO}</p><table class="video"><tbody>'
        + ''.join(f'<tr><td class="m">{e(m)}</td><td>{a_html(t)}</td></tr>' for m, t in g['video']) + '</tbody></table></div>'
        for g in GUIA_TODAS if g.get('video'))

    preciso = ''.join(f'<tr><td class="oye" data-k="Se oye a veces"><span>«{a_html(o)}»</span></td><td data-k="Lo preciso"><span class="flecha">→</span> {a_html(p)}</td></tr>'
                      for o, p in LO_PRECISO)
    escalera = ''.join(
        f'<li class="peldano p{n + 1}"><span class="num">{n + 1}</span><div><b>{e(p)}</b><br><code>{e(ej)}</code><div class="nota">{a_html(c)}</div></div></li>'
        for n, (p, ej, c) in enumerate(ESCALERA))
    cotejo = ''.join(f'<li><label class="check"><input type="checkbox" class="cot"> <span>{a_html(t)}</span></label></li>' for t in COTEJO)

    cuerpo = f'''<h1>Guía de estudio · <span class="acc">repaso opcional</span></h1>
<p class="lead">Lo esencial de cada sesión en una tarjeta: la idea, tres conceptos y dónde está el material. Úsala para repasar lo que quieras, cuando quieras.</p>
<nav class="top" aria-label="Secciones">
<a href="#sesiones">Sesión por sesión</a><a href="#preciso">Lo preciso</a><a href="#escalera">La escalera</a><a href="#cotejo">Lista de cotejo</a><a href="#autoevaluacion">Autoevaluación</a>
</nav>

<section id="sesiones">
<h2>Sesión <span class="acc">por sesión</span></h2>
<div class="grid2">{"".join(tarjetas)}</div>
{videos}
</section>

<section id="preciso">
<div class="card c-lav">
<h2>Lo <span class="acc">preciso</span></h2>
<p>Frases que se oyen a veces y lo que es exacto.</p>
<table class="apilar preciso"><thead><tr><th>Se oye a veces</th><th>Lo preciso</th></tr></thead><tbody>{preciso}</tbody></table>
</div>
</section>

<section id="escalera">
<div class="card">
<h2>La escalera de <span class="acc">localizadores</span></h2>
<p>Del más robusto al que nunca se usa.</p>
<ol class="escalera">{escalera}</ol>
</div>
</section>

<section id="cotejo">
<div class="card c-lime">
<h2>Lista de cotejo <span class="acc">de una prueba</span></h2>
<p>La lee una persona, no una herramienta. Sirve para tu prueba, la de un compañero o la que escribió una IA.</p>
<ul class="checks">{cotejo}</ul>
<p class="contador" id="cotejo-cuenta" aria-live="polite"></p>
</div>
</section>

<section id="autoevaluacion">
<h2>Autoevaluación <span class="acc">corta</span></h2>
<p>Los boletos de salida. Responde primero y después mira las respuestas.</p>
{boleto("s5", "S5 · patrones", BOLETO_S5)}
{boleto("s6", "S6 · configuración, localizadores y esperas", BOLETO_S6)}
{boleto("s7", "S7 · Gherkin sobre el framework", BOLETO)}
{boleto("s8", "S8 · Data Driven Testing y el reporte", BOLETO_S8)}
{boleto("s9", "S9 · ¿sistema, script o ambiente?", BOLETO_S9)}
</section>'''
    return pagina('Guía de estudio', 'guía de estudio · repaso opcional', cuerpo)


# ─────────────────────────── Salida ───────────────────────────
RELATIVO = re.compile(r'href="(?!https?://|#|data:)([^"]+)"')

if __name__ == '__main__':
    for nombre, fn in [('proyecto.html', proyecto), ('guia_estudio.html', guia)]:
        (RAIZ / 'laboratorio' / nombre).write_text(fn(''), encoding='utf-8')
        local = fn(PAGES)
        sueltos = RELATIVO.findall(local)
        assert not sueltos, f'{nombre}: enlaces relativos en la copia local: {sueltos}'
        assert 'claude.ai' not in local, f'{nombre}: enlace de claude.ai'
        if PARA_ENVIAR.is_dir():
            (PARA_ENVIAR / nombre).write_text(local, encoding='utf-8')

    print('proyecto.html y guia_estudio.html listos (y sus copias en para_enviar/ con enlaces completos de Pages)')
