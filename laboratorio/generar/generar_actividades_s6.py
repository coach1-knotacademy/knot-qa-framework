"""Genera laboratorio/actividades_S6.html (las actividades de la clase S6) y docs/configuracion-y-localizadores.md.

La página va en el orden de la clase (ver sesion_06/plan_S6.md, «Clase minuto a minuto»): la IA de la S5
(5:50, voluntario), el repaso, configuración y Postman, el reto 1, localizadores, el reto 2, esperas, tu CP,
la lista de cotejo, el boleto y el cierre. Las fichas salen de fichas_s6.py, la misma fuente que usa el deck
del instructor. El código que se muestra se lee del repo, así la página no queda desactualizada.
No carga nada de internet (solo las fuentes de Google, y si no cargan se usan las del sistema).

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_actividades_s6.py
"""
import html, re, shutil, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
sys.path.insert(0, str(D))
from fichas_s6 import (FICHAS, FILAS as FILAS_FICHA, ESCALERA, ORDENAR, ROBUSTA, ROBUSTA_ANTES, SIN_AWAIT, COTEJO, PRUEBA_A_REVISAR,  # noqa: E402
                       DEFECTOS_REVISAR, BOLETO, CPS, TIPOS, PAGES, AMBIENTES, POSTMAN, LABORATORIO, PLANTILLA, BANCO,
                       a_html, linea_escapada)
from fichas_s5 import BOLETO as BOLETO_S5  # noqa: E402

leer = lambda r: (RAIZ / r).read_text(encoding='utf-8')
LOGO = re.search(r'<img src="(data:image/png;base64,[^"]+)"', (D / 'plantilla.html').read_text(encoding='utf-8')).group(1)
PARA_ENVIAR = RAIZ.parent / 'para_enviar'

def codigo(texto, numerado=False):
    lineas = texto.rstrip('\n').split('\n')
    if numerado:
        return '<pre class="code num">' + ''.join(f'<span class="ln">{html.escape(l) or " "}</span>' for l in lineas) + '</pre>'
    return '<pre class="code">' + html.escape('\n'.join(lineas)) + '</pre>'

def sin_comentarios_de_cabecera(texto):
    """Quita las líneas de comentario del encabezado y la nota final de los archivos de docs/ia-s5/."""
    lineas = texto.split('\n')
    while lineas and lineas[0].startswith('//'):
        lineas.pop(0)
    s = '\n'.join(lineas)
    s = re.split(r'\n// Nota de la IA|\n/\* Lo que explicó la IA', s)[0]
    return s.strip()

# ---------- Código real del repo ----------
IA = [sin_comentarios_de_cabecera(leer(f'docs/ia-s5/{f}')) for f in
      ('1_sin_contexto.spec.ts', '2_con_contexto.spec.ts', '3_regresion_bug_4x1000.spec.ts')]
s = leer('src/config/entorno.ts')
ENTORNO_HOY = s[s.index('export const entorno'):].strip()
N_ESCAPADA, LINEA_ESCAPADA = linea_escapada(RAIZ)
assert "readonly saldoDisponible" in leer('src/paginas/PaginaRecargas.ts') and "page.locator('#saldo')" in leer('src/paginas/PaginaRecargas.ts'), \
    'PaginaRecargas ya no usa #saldo: revisa la demo del rediseño'

# ---------- Piezas de la página (las mismas de la S5) ----------
def clasificador(cid, filas, opciones):
    """filas: (texto_html, clave_correcta, explicacion_html). opciones: [(clave, etiqueta)]."""
    trs = ''.join(
        f'<tr data-ok="{ok}"><td class="n">{n + 1}</td><td>{txt}<div class="exp" hidden>{exp}</div></td>'
        f'<td class="opc">' + ''.join(f'<button type="button" data-v="{k}">{et}</button>' for k, et in opciones) + '</td></tr>'
        for n, (txt, ok, exp) in enumerate(filas))
    return (f'<table class="clasif" id="t-{cid}"><tbody>{trs}</tbody></table>'
            f'<p><button type="button" class="grande" data-revisar="{cid}">Revisar</button><span class="puntaje" id="p-{cid}"></span></p>')

def ficha(f, minutos='3 min'):
    filas = ''.join(f'<div class="fk">{et}</div><div class="fv">{a_html(f[k])}</div>' for k, et in FILAS_FICHA)
    return (f'<div class="card ficha-card"><div class="meta"><span class="chip">ficha · {minutos}</span><span class="chip">capa: <code>{f["capa"]}</code></span></div>'
            f'<h2>{f["nombre"]}</h2><p class="desde">{a_html(f["desde"])}</p><div class="ficha">{filas}</div></div>')

def revelar(rid, boton, contenido):
    return f'<p><button type="button" class="grande" data-revelar="{rid}">{boton}</button></p><div id="{rid}" hidden>{contenido}</div>'

def boleto(preguntas):
    items = ''.join(
        f'<li><p><b>{a_html(p)}</b></p><p class="opciones">' + ' · '.join(f'<b>{"abc"[k]})</b> {a_html(o)}' for k, o in enumerate(ops)) + '</p></li>'
        for p, ops, ok, por in preguntas)
    resp = ''.join(f'<li><b>{ok}</b> · {a_html(por)}</li>' for p, ops, ok, por in preguntas)
    return items, resp

A_LA_VEZ = '<span class="chip">respondan a la vez: escriban sin enviar · «3, 2, 1, envíen»</span>'
F = {f['id']: f for f in FICHAS}

# ---------- 5:50 · La IA de la S5 ----------
IA_INFO = [
  ('1 · sin ver el repo', 'c-peach', 'Solo el pedido del tester.',
   '<b>Rojo al primer paso.</b> Inventó la ruta <code>/login</code>, que no existe, y se quedó esperando el campo Usuario. URL, clave y datos a mano, localizadores dentro de la prueba, y no sabía que $60.000 pide código.'),
  ('2 · dentro del repo', 'c-lime', 'El mismo pedido, pero leyó <code>.github/copilot-instructions.md</code> y los Page Objects.',
   '<b>Verde.</b> Usó el flujo de ingreso, la fábrica y el Page Object. Agregó sola el paso del código: lo encontró en la regla de negocio.'),
  ('3 · «déjamela en verde»', 'c-yel', 'Exploró la app (sin ver el código) con el pedido «déjame la prueba en verde».',
   '<b>Rojo a propósito.</b> Vio que la app respondía «total $100.400» pero el saldo bajaba solo $100.000, y no quiso fijar el defecto como correcto (BUG-02 del 4x1000).'),
]
ia_cols = ''.join(
    f'<div class="card {cls}"><p class="paso">{tag}</p><p>{recibio}</p>'
    f'<details><summary>Ver el código, tal cual</summary>{codigo(cod)}</details></div>'
    for (tag, cls, recibio, _), cod in zip(IA_INFO, IA))
ia_res = '<ol class="lista">' + ''.join(f'<li><b>{tag}:</b> {res}</li>' for tag, _, _, res in IA_INFO) + '</ol>'
INVENTO = [
  'La dirección del sitio: ¿la escribió a mano o la sacó de la configuración?',
  'Las rutas y las pantallas: ¿existen de verdad (por ejemplo, <code>/login</code>)?',
  'Los localizadores: ¿son de la pantalla real o supuestos (<code>getByTestId(\'saldo\')</code>)?',
  'Los datos y la clave: ¿a mano o de la fábrica y del entorno?',
  'El resultado esperado: ¿sale de la regla (más de $50.000 pide código) o de lo que imaginó?',
]
invento_html = ''.join(f'<li><label class="check"><input type="checkbox"> <span>{t}</span></label></li>' for t in INVENTO)
PEDIDO = ('Escribe una prueba de Playwright con TypeScript para el Banco Demo: Ana entra con su usuario, '
          'recarga $10.000 a Claro al celular 3001234567 y el saldo de Ahorros baja $10.000.')

# ---------- 6:02 · Repaso de la S5 ----------
b5_items, b5_resp = boleto(BOLETO_S5)
b5_resp = b5_resp.replace('Factory: un objeto nuevo y único en cada prueba.',
                          'Factory: cada llamada entrega un objeto <b>nuevo</b>, y <code>...cambios</code> solo pisa lo que la prueba pidió («el combo 2, sin cebolla»). Si los cambios se quedaran, la prueba siguiente recibiría datos de la anterior.')

# ---------- 6:08 · Configuración ----------
ENTORNO_DESPUES = """// src/config/entorno.ts, después del reto 1
import { configurarAmbiente } from './ambientes';

export const entorno = Object.freeze(
  configurarAmbiente(process.env.AMBIENTE ?? 'local', process.env),
);
// La forma no cambia: entorno.urlBase, entorno.usuario, entorno.clave"""
DEMO_LUIS = """test('A · cambia el usuario «de afán»', () => {
  entorno.usuario = 'luis';
});

test('B · espera el de siempre', () => {
  expect(entorno.usuario).toBe('ana');
});"""
SALIDA_LUIS = """✘ B · espera el de siempre

  Expected: "ana"
  Received: "luis\""""
CAMBIA = [
  ('La dirección del banco', 'C', 'Cambia: <code>entorno.urlBase</code>. En Postman, <code>{{urlBase}}</code>.'),
  ('La clave del usuario de pruebas', 'C', 'Cambia, y además es <b>secreta</b>: llega por una variable de la terminal, nunca escrita en el código.'),
  ('Los pasos de la prueba (abrir Recargas, recargar, revisar)', 'P', 'No cambian: es la misma prueba en todos los ambientes.'),
  ('La regla «más de $50.000 pide código»', 'P', 'No cambia: es negocio. Si fuera distinta en UAT, sería un hallazgo, no una configuración.'),
  ('Los datos que tiene cada ambiente (cuentas y saldos)', 'C', 'Cambian: <b>un ambiente también se distingue por sus datos</b>. Lo van a ver en Postman.'),
  ("El localizador del botón «Recargar»", 'P', 'No cambia: vive en el Page Object y es el mismo en QA y en UAT.'),
]

# ---------- 6:15 · Postman ----------
PASOS_POSTMAN = [
  ('Un workspace aparte, nunca el del equipo',
   'Arriba a la izquierda: <b>Workspaces → Create Workspace</b>. Nombre: «Bootcamp S6 · práctica». Si su Postman es de la empresa, el workspace del equipo es donde viven las colecciones reales: ahí no se practica.',
   'En la barra de arriba aparece el nombre «Bootcamp S6 · práctica».'),
  ('Importar la colección y los dos ambientes',
   f'Botón <b>Import</b> → peguen el enlace de la colección y den Enter. Repitan con QA y con UAT:<br><code>{POSTMAN["coleccion"]}</code><br><code>{POSTMAN["QA"]}</code><br><code>{POSTMAN["UAT"]}</code>',
   'A la izquierda, en <b>Collections</b>, aparece «Bootcamp-S6» con 2 pedidos. En <b>Environments</b> aparecen QA y UAT.'),
  ('Elegir el ambiente QA y enviar',
   'Arriba a la derecha hay un menú que dice <b>No environment</b>: elijan <b>QA</b>. Abran el primer pedido y pulsen <b>Send</b>.',
   'Abajo: <b>200 OK</b>, un JSON con <code>"ambiente": "QA"</code> y, en la pestaña <b>Test Results</b>, las revisiones en verde (PASS).'),
  ('Cambiar a UAT y enviar el mismo pedido',
   'En el mismo menú, elijan <b>UAT</b>. No toquen el pedido: pulsen <b>Send</b> otra vez. Luego prueben el pedido de cuentas en los dos.',
   'El mismo pedido, ahora con <code>"ambiente": "UAT"</code>. Las cuentas traen <b>datos distintos</b> en cada ambiente.'),
  ('La clave, solo local (sin compartir)',
   'Abran el ambiente UAT. La variable <code>clave</code> es de tipo <i>secret</i> y está vacía. Escriban una clave inventada como valor <b>local</b>. <b>Postman nuevo</b> (una sola columna <b>Value</b>): escríbanla ahí y <b>no</b> la compartan; a su lado no debe aparecer la nube ☁. <b>Postman anterior</b> (dos columnas): en <b>Current value</b>, con <b>Initial value</b> vacío.',
   'Lo compartido (la nube ☁ en Postman nuevo, el <i>initial value</i> en el anterior) se sincroniza y lo ve quien comparta el workspace. Lo local se queda en su equipo. Para comprobar en Postman nuevo: <b>⋯ → Shared value</b>; el de <code>clave</code> debe estar vacío.'),
]
pasos_postman = ''.join(f'<li><p><b>{t}.</b> {q}</p><p class="ves"><b>Lo que ven:</b> {v}</p></li>' for t, q, v in PASOS_POSTMAN)
PLAN_B_POSTMAN = (f'<p><b>¿No deja importar por enlace?</b> Creen todo a mano, en 2 minutos: <b>Environments → +</b>, nombre <code>QA</code>, '
                  f'variables <code>urlBase</code> = <code>{AMBIENTES["QA"]}</code> y <code>nombreAmbiente</code> = <code>QA</code>. Lo mismo para '
                  f'<code>UAT</code> con <code>{AMBIENTES["UAT"]}</code>. Después, un pedido nuevo: <b>GET</b> <code>{{{{urlBase}}}}/salud.json</code>.</p>'
                  '<p><b>¿No tienen Postman?</b> Trabajen en pareja con quien sí lo tenga. Quien ya sabe Postman guía; esta vez los capitanes aprenden de ustedes. Si usan Insomnia, es lo mismo con <i>Environments</i>.</p>')

# ---------- 6:25 · Reto 1 ----------
PASOS_RETO1 = [
  ('Paso 1', '<code>qa</code> y <code>uat</code> devuelven su dirección del catálogo, y <code>URL_BANCO</code> la puede reemplazar.'),
  ('Paso 2', 'Fuera de <code>local</code>, si falta <code>CLAVE_BANCO</code>, falla <b>de inmediato</b> con un mensaje claro: <code>Falta CLAVE_BANCO para el ambiente qa. Defínela en la terminal: $env:CLAVE_BANCO = \'...\'</code>. En <code>local</code> se usa la clave de práctica del Banco Demo.'),
  ('Paso 3', '<code>produccion</code>, o cualquier nombre que no esté en el catálogo, queda <b>bloqueado</b>: <code>Este framework no corre contra producción</code>.'),
  ('Paso 4', 'La configuración queda <b>congelada</b> con <code>Object.freeze</code>: si una prueba intenta cambiarla, lanza un error.'),
]
pasos_reto1 = ''.join(f'<li><b>{p}.</b> {t}</li>' for p, t in PASOS_RETO1)

# ---------- 6:39 · Localizadores ----------
escalera_html = ''.join(
    f'<li class="peldano p{n + 1}"><span class="num">{n + 1}</span><div><b>{html.escape(p)}</b><br><code>{html.escape(e)}</code><div class="nota">{a_html(c)}</div></div></li>'
    for n, (p, e, c) in enumerate(ESCALERA))
ordenar = [(f'<code>{html.escape(c)}</code>', ok, exp) for c, ok, exp in ORDENAR]
OPC_ORDEN = [(str(i), str(i)) for i in range(1, 6)]
REDISENO = [
  ('Cambia', 'los ids, las clases, el orden de los campos y los contenedores. El id <code>#saldo</code> <b>desaparece</b>.'),
  ('Se mantiene', 'las etiquetas (<code>&lt;label&gt;</code>), los roles, los textos de los botones y el <code>data-testid="saldo-disponible"</code> pactado.'),
]
rediseno_html = ''.join(f'<li><b>{a}:</b> {b}</li>' for a, b in REDISENO)
PATIO_DEMO = [
  ("page.locator('#saldo')", '1', '0', 'se cae'),
  ("page.getByTestId('saldo-disponible')", '1', '1', 'sobrevive'),
  ("page.getByRole('button', { name: 'Recargar' })", '1', '1', 'sobrevive'),
]
patio_html = ''.join(f'<tr><td class="cod"><code>{html.escape(l)}</code></td><td>{h}</td><td>{r}</td><td><b>{v}</b></td></tr>' for l, h, r, v in PATIO_DEMO)

# ---------- 6:55 · Reto 2 ----------
FRAGILES = [
  ('Clase CSS', 'se cae cuando cambian el diseño', "<code>getByRole('button', { name: '…' })</code>"),
  ('<code>nth-child</code>', 'se cae cuando cambian el orden de los campos', "<code>getByLabel('…')</code>"),
  ('XPath absoluto', 'se cae cuando agregan un contenedor', "<code>getByLabel('…')</code> o <code>getByRole(…)</code>"),
  ('El id <code>#saldo</code>', 'desaparece en el rediseño', "<code>getByTestId('saldo-disponible')</code>"),
  ('Texto parcial con CSS', 'depende de la estructura y de un pedazo de texto', "<code>getByRole(…, { name })</code> o <code>getByText(…)</code>"),
]
fragiles_html = ''.join(f'<tr><td class="n">{n + 1}</td><td><b>{a}</b> · {b}</td><td>→ {c}</td></tr>' for n, (a, b, c) in enumerate(FRAGILES))

# ---------- 7:09 · Esperas ----------
sin_await_ops = ' · '.join(f'<b>{"abc"[k]})</b> {html.escape(o)}' for k, o in enumerate(SIN_AWAIT['opciones']))
robusta = [(codigo(c), ok, exp) for c, ok, exp in ROBUSTA]

# ---------- 7:17 · Tu CP ----------
def tipo_chip(t):
    return f'<span class="tipo t-{t}">{TIPOS[t]}</span>'

def cp_tarjeta(cp):
    pasos = ''.join(f'<li>{html.escape(p)}</li>' for p in cp['pasos'])
    nota = f'<p class="nota">{a_html(cp["nota"])}</p>' if cp.get('nota') else ''
    texto = (f'{cp["id"]} · {cp["titulo"]}\nPrecondición: {cp["pre"]}\nPasos:\n' + '\n'.join(f'{n + 1}. {p}' for n, p in enumerate(cp['pasos']))
             + f'\nResultado esperado: {cp["esperado"]}')
    return (f'<div class="card cp"><p class="paso">{cp["id"]}</p><h3 style="margin-top:0">{html.escape(cp["titulo"])}</h3>'
            f'<p><b>Precondición:</b> {html.escape(cp["pre"])}</p><ol class="pasos">{pasos}</ol>'
            f'<p><b>Resultado esperado:</b> {html.escape(cp["esperado"])}</p>{nota}'
            f'<textarea hidden id="txt-{cp["id"]}">{html.escape(texto)}</textarea>'
            f'<p><button type="button" data-copiar="txt-{cp["id"]}">Copiar el caso</button><span class="ok" data-copiado="txt-{cp["id"]}"></span></p></div>')

cps_html = ''.join(cp_tarjeta(cp) for cp in CPS)
MODELO = CPS[0]
modelo_filas = ''.join(f'<tr><td>{tipo_chip(t)}</td><td>{html.escape(c)}</td><td>{a_html(p)}</td></tr>' for t, c, p in MODELO['filas'])
MODELO_CODIGO = """test('CP-101 · una recarga normal da comprobante y deja Ahorros en $1.490.000', async ({ page, cliente, paginaRecargas }) => {
  await abrirConSesion(page, cliente, usuarios.ana);          // precondición → tarea
  await paginaRecargas.abrir();                               // paso → Page Object

  await paginaRecargas.recargar(fabricaDeRecargas.valida());  // dato → fábrica · pasos → localizadores

  expect(await paginaRecargas.esperarResultado()).toContain('Recarga exitosa');   // esperado → expect
  await expect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000');          // esperado → expect
});
// El ambiente no aparece: llega solo, desde entorno (baseURL)."""

def cp_practica(cp):
    filas = ''.join(
        f'<tr><td>{tipo_chip(t)}</td><td>{html.escape(c)}</td><td><input type="text" aria-label="{html.escape(c)}: cómo queda en la prueba" placeholder="cómo queda en la prueba"></td></tr>'
        for t, c, p in cp['filas'])
    sol = ''.join(f'<tr><td>{tipo_chip(t)}</td><td>{html.escape(c)}</td><td>{a_html(p)}</td></tr>' for t, c, p in cp['filas'])
    nota = f'<p class="nota">{a_html(cp["nota"])}</p>' if cp.get('nota') else ''
    return (f'<div class="cp-prac" data-cp="{cp["id"]}" hidden><table class="trad" id="tabla-{cp["id"]}"><thead><tr><th>Tipo</th><th>Lo que dice el caso</th><th>Cómo queda en la prueba</th></tr></thead><tbody>{filas}</tbody></table>'
            f'<p><button type="button" data-copiar-tabla="tabla-{cp["id"]}" data-titulo="{cp["id"]} · {html.escape(cp["titulo"])}">Copiar mi tabla</button><span class="ok" data-copiado="tabla-{cp["id"]}"></span></p>'
            + revelar(f'sol-{cp["id"]}', 'Ver una traducción posible', f'<table class="trad"><tbody>{sol}</tbody></table>{nota}') + '</div>')

practica_html = ''.join(cp_practica(cp) for cp in CPS[1:])
opciones_cp = ''.join(f'<option value="{cp["id"]}">{cp["id"]} · {html.escape(cp["titulo"])}</option>' for cp in CPS[1:])
opciones_cp_todas = ''.join(f'<option value="{cp["id"]}">{cp["id"]} · {html.escape(cp["titulo"])}</option>' for cp in CPS)

# ---------- 7:35 · Lista de cotejo ----------
cotejo_html = ''.join(f'<li><label class="check"><input type="checkbox" class="cot"> <span>{a_html(t)}</span></label></li>' for t in COTEJO)
defectos_html = ''.join(f'<li><b>{l}</b> · {a_html(d)} <span class="fix">→ ítem {i} de la lista</span></li>' for l, d, i in DEFECTOS_REVISAR)

# ---------- 7:45 · Boleto ----------
b6_items, b6_resp = boleto(BOLETO)

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
"""

JS = """
(function () {
  document.querySelectorAll('table.clasif').forEach(function (tabla) {
    tabla.querySelectorAll('tr').forEach(function (tr) {
      tr.querySelectorAll('button').forEach(function (b) {
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
  document.querySelectorAll('[data-revelar]').forEach(function (boton) {
    boton.addEventListener('click', function () { document.getElementById(boton.getAttribute('data-revelar')).hidden = false; boton.hidden = true; });
  });
  function copiar(texto, aviso) {
    var listo = function () { if (aviso) aviso.textContent = 'Copiado'; };
    var aMano = function () {
      var t = document.createElement('textarea'); t.value = texto; document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); } catch (e) {} document.body.removeChild(t); listo();
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(texto).then(listo, aMano); else aMano();
  }
  function aviso(id) { return document.querySelector('[data-copiado="' + id + '"]'); }
  document.querySelectorAll('[data-copiar]').forEach(function (b) {
    b.addEventListener('click', function () {
      var id = b.getAttribute('data-copiar'), el = document.getElementById(id);
      copiar(el.value !== undefined ? el.value : el.textContent, aviso(id));
    });
  });
  document.querySelectorAll('[data-copiar-tabla]').forEach(function (b) {
    b.addEventListener('click', function () {
      var id = b.getAttribute('data-copiar-tabla'), lineas = [b.getAttribute('data-titulo')];
      document.querySelectorAll('#' + id + ' tbody tr').forEach(function (tr) {
        var c = tr.querySelectorAll('td');
        lineas.push(c[0].textContent.trim() + ' | ' + c[1].textContent.trim() + ' | ' + (c[2].querySelector('input').value.trim() || '___'));
      });
      copiar(lineas.join('\\n'), aviso(id));
    });
  });
  var sel = document.getElementById('cp-elegido');
  function mostrarCp() {
    document.querySelectorAll('.cp-prac').forEach(function (d) { d.hidden = d.getAttribute('data-cp') !== sel.value; });
  }
  if (sel) { sel.addEventListener('change', mostrarCp); mostrarCp(); }
  var cot = document.querySelectorAll('input.cot'), cuenta = document.getElementById('cotejo-cuenta');
  function contar() { var n = 0; cot.forEach(function (c) { if (c.checked) n++; }); cuenta.textContent = n + ' de ' + cot.length + ' se cumplen'; }
  cot.forEach(function (c) { c.addEventListener('change', contar); }); if (cuenta) contar();
  var frase = document.getElementById('copiar-frase');
  if (frase) frase.addEventListener('click', function () {
    var v = function (id) { return document.getElementById(id).value.trim() || '___'; };
    var texto = 'Mi CP es ' + v('f-cp') + ': su paso clave se vuelve ' + v('f-paso') + ' y su esperado se vuelve ' + v('f-esp') + '.';
    copiar(texto, document.getElementById('frase-ok'));
  });
})();
"""

HTML = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Actividades S6 Ambientes</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&amp;family=Nunito:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;600&amp;display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · S6 · configuración, ambientes y localizadores</small></div>
<h1>Una prueba que <span class="acc">sobrevive al cambio</span> de ambiente y de diseño</h1>
<p class="lead">Las actividades de hoy, en el orden de la clase. La misma prueba debe correr en QA y en UAT sin tocarla, y seguir en verde cuando cambien el diseño de la pantalla. Todo funciona sin instalar nada.</p>
<div class="card c-cyan">
<p style="margin-top:0"><b>Abran estos enlaces y respondan en el chat ✅ si cargan o ❌ si alguno no carga (digan cuál):</b></p>
<a class="boton" href="{LABORATORIO}">Laboratorio de la S6</a><a class="boton blanco" href="{BANCO}recargas.html">Banco Demo · Recargas</a><a class="boton blanco" href="{AMBIENTES["QA"]}/salud.json">Ambiente QA</a><a class="boton blanco" href="{PLANTILLA}">La plantilla</a>
<p class="nota">Banco Demo: usuario <code>ana</code>, clave <code>Clave123</code> (es de práctica) y el código que llega al buzón de SMS. Las recargas de más de $50.000 piden un segundo código. Si GitHub no abre en su red, el instructor sube los archivos al chat: se abren con doble clic en Edge.</p>
</div>
<nav class="top" aria-label="Actividades">
<a href="#ia">La IA de la S5</a><a href="#repaso">Repaso</a><a href="#config">Configuración</a><a href="#postman">Postman</a><a href="#reto1">Reto 1</a><a href="#localizadores">Localizadores</a><a href="#reto2">Reto 2</a><a href="#esperas">Esperas</a><a href="#cp">Tu CP</a><a href="#cotejo">Lista de cotejo</a><a href="#boleto">Boleto</a><a href="#cierre">Cierre</a>
</nav>

<section id="ia">
<div class="card c-lav">
<h2>Antes de empezar · <span class="acc">la IA de la S5</span></h2>
<div class="meta"><span class="chip">5:50 · voluntario · 10 min</span>{A_LA_VEZ}</div>
<p>El jueves no alcanzamos a verlo. Le pedimos tres pruebas a una IA y las corrimos contra el Banco Demo, sin corregirlas. <b>Antes de ver los resultados: ¿cuál de las 3 pasa?</b> En el chat, un número.</p>
</div>
<div class="grid3">{ia_cols}</div>
{revelar('ia-res', 'Ver qué pasó al correrlas', ia_res + '<p><b>Solo pasó la 2.</b> La diferencia no fue la IA, fue el contexto: con un framework ordenado y alguien que decide el resultado esperado, la IA copia el molde; darle solo el sitio no basta para que salgan los casos.</p><p class="nota">Ojo: que la IA se negara <b>una vez</b> a dejar verde un bug no garantiza que lo haga siempre. El esperado lo decide la regla de negocio, y la persona que la conoce.</p>')}
<div class="card">
<p class="paso">en vivo · el mismo pedido, sin y con contexto</p>
<p>El instructor le pide esto a un asistente, primero solo y después con el prompt de la plantilla. Hoy no se corre: lo leemos como revisores.</p>
<p style="background:var(--yellow);border:2px solid var(--ink);border-radius:10px;padding:10px 12px"><i>«{html.escape(PEDIDO)}»</i></p>
<h3>Mientras responde: ¿qué inventó?</h3>
<ul class="checks">{invento_html}</ul>
<p class="nota"><b>Regla de uso:</b> solo el asistente que su empresa aprobó. A la IA solo va código de práctica o de un sitio público: nunca pantallas, datos, logs ni casos del banco. Todo lo de esta página está en <code>docs/ia-s5/</code> del repo.</p>
</div>
</section>

<section id="repaso">
<div class="card c-lime">
<h2>Repaso · <span class="acc">el boleto que quedó pendiente</span></h2>
<div class="meta"><span class="chip">6:02 · 6 min · primera victoria</span>{A_LA_VEZ}</div>
<p>El boleto de salida de la S5. En el chat, las cuatro letras en orden, todos al mismo tiempo. Por ejemplo: <b>«a c b a»</b>.</p>
<ol class="boleto">{b5_items}</ol>
<p><b>Y una más, en una palabra:</b> Factory, ¿es un patrón <b>de pruebas</b> o <b>creacional</b>?</p>
{revelar('b5-resp', 'Ver las respuestas', '<ol class="boleto">' + b5_resp + '</ol><p><b>Factory es creacional</b>, igual que Singleton y Builder: vienen del libro de Gamma, de desarrollo. En QA los usamos para los datos y la configuración. Page Object y Screenplay sí son patrones de automatización de pruebas. Page Object no es «el viejo»: es el más usado y el que recomienda la documentación de Playwright. Screenplay no lo reemplaza: una tarea usa páginas por dentro. Un framework <b>combina</b> varios patrones, uno por problema.</p>')}
</div>
</section>

<section id="config">
<div class="card c-peach">
<p class="paso">gancho · 2 min</p>
<h2>El secreto salió del código <span class="acc">y quedó en la evidencia</span></h2>
<p>El reporte de ParaBank que vimos el jueves está publicado. Abran una prueba → <b>View Trace</b> → el paso que escribe la clave. Ahí está: <code>Clave123</code>.</p>
<a class="boton blanco" href="{PAGES}reportes/parabank/index.html">Abrir el reporte de ParaBank</a>
<p>Es una clave de práctica en un sitio público. En un proyecto del banco, eso es un <b>incidente</b>: el reporte se comparte, se adjunta y se archiva.</p>
<p class="nota">Y un detalle que casi nadie sabe: sacar la clave del código no la saca del trace. El trace guarda lo que se escribió. Por eso el trace de un sistema real es evidencia confidencial: no se publica ni se pega en la IA.</p>
</div>
{ficha(F['config'])}
<div class="card">
<p class="paso">ejemplo resuelto · <code>src/config/entorno.ts</code></p>
<div class="grid2"><div><h3>Hoy</h3>{codigo(ENTORNO_HOY)}<p class="nota">Si falta la variable, usa el valor por defecto. Para practicar está bien. Para UAT, una clave que falta debe frenar todo, no usar una «por defecto».</p></div>
<div><h3>Después del reto 1</h3>{codigo(ENTORNO_DESPUES)}<p class="nota">La prueba no cambia: sigue pidiendo <code>entorno.urlBase</code>. Cambia cómo se arma y que nadie lo puede modificar.</p></div></div>
</div>
<div class="card c-yel">
<p class="paso">demo · 2 min · pasa sola, falla en la corrida</p>
<h3 style="margin-top:0">¿Por qué se congela?</h3>
<div class="grid2"><div>{codigo(DEMO_LUIS)}</div><div>{codigo(SALIDA_LUIS)}<p>Corrida sola, la B <b>pasa</b>. En la corrida completa <b>falla</b>, porque la A le cambió el usuario. Es «la prueba que a veces falla» que todos conocen.</p></div></div>
<p>Con <code>Object.freeze</code>, el editor la frena antes de correr: <code>Cannot assign to 'usuario' because it is a read-only property</code>. Y si alguien la corre igual: <code>TypeError: Cannot assign to read only property 'usuario'</code>.</p>
<p><b>Lo que se queda entre pruebas es un objeto compartido</b>, como <code>entorno</code>: por eso se congela. La fábrica es lo contrario: cada llamada entrega un objeto nuevo, y <code>...cambios</code> solo pisa lo que esa prueba pidió.</p>
<p class="nota"><b>¿Y <code>usuarios.ana</code> no debería generarse?</b> Depende de quién más usa el dato. En el Banco Demo, Ana existe siempre y sus saldos se reinician: es un dato con nombre, en un solo lugar, que se cambia por ambiente (<code>USUARIO_BANCO</code>). En un sitio compartido como ParaBank sí se genera (<code>fabricaDeClientes</code>), porque otro lo podría tocar.</p>
</div>
<div class="card c-lav">
<p class="paso">comprobación · 2 min</p>
<h3 style="margin-top:0">Pasan de QA a UAT. ¿Esto cambia?</h3>
<div class="meta">{A_LA_VEZ}</div>
{clasificador('cambia', CAMBIA, [('C', 'Cambia: configuración'), ('P', 'No cambia: es la prueba')])}
</div>
</section>

<section id="postman">
<div class="card c-cyan">
<h2>Postman · <span class="acc">un pedido, dos ambientes</span></h2>
<div class="meta"><span class="chip">6:15 · parejas · 10 min</span><span class="chip">terminado = el mismo pedido en verde en QA y en UAT</span></div>
<p>El <i>environment</i> de Postman es exactamente lo mismo que <code>src/config/</code>: el pedido no cambia y la variable <code>{{{{urlBase}}}}</code> decide a qué ambiente va. Estos dos «ambientes» son archivos de práctica publicados en GitHub Pages: no son del banco ni de ParaBank.</p>
<ol class="pasos">{pasos_postman}</ol>
{PLAN_B_POSTMAN}
</div>
<div class="card">
<p class="paso">comprobación · a la vez</p>
<p><b>1.</b> ¿Qué capa del framework cambia si cambio de ambiente? · <b>2.</b> ¿En qué columna pusieron la clave?</p>
{revelar('postman-resp', 'Ver las respuestas', '<p><b>1.</b> Solo la configuración: <code>src/config/</code>. Las pruebas, las páginas y las fábricas no cambian. <b>2.</b> Local, sin compartir: se queda en su equipo (Postman nuevo: <i>Value</i> sin ☁; anterior: <i>current value</i>). Nunca compartida, y nunca en el workspace del equipo.</p>')}
</div>
</section>

<section id="reto1">
<div class="card c-lime">
<p class="paso">laboratorio · reto 1 · salas · 2 tramos de 6 min</p>
<h2>Ambientes con <span class="acc">controles de banco</span></h2>
<p>En el laboratorio, <code>src/config/ambientes.ts</code> con la función <code>configurarAmbiente(nombre, variables)</code>. <b>Cada paso tiene su propia prueba</b> y no depende de los otros.</p>
<ol class="pasos">{pasos_reto1}</ol>
<ul class="lista"><li><b>Tramo 1 (6 min):</b> pasos 1 y 2. Al final, en el chat: «Sala X: n de 4».</li>
<li><b>Tramo 2 (6 min):</b> pasos 3 y 4.</li></ul>
<a class="boton" href="{LABORATORIO}">Abrir el laboratorio de la S6</a>
<p class="nota">Con el repo instalado: <code>npx.cmd playwright test --project=retos-s06</code>. En el laboratorio, <code>process.env</code> es un objeto de prueba: nada sale del navegador.</p>
</div>
</section>

<section id="localizadores">
{ficha(F['localizadores'])}
<div class="card">
<p class="paso">la escalera · de más robusto a nunca</p>
<ol class="escalera">{escalera_html}</ol>
<p class="nota">Ojo con <code>name</code>: por defecto busca un pedazo del nombre, sin importar mayúsculas. <code>{{ name: 'Recargar', exact: true }}</code> exige el nombre completo.</p>
</div>
<div class="card c-lav">
<p class="paso">práctica · 3 min · ordenen la escalera</p>
<h3 style="margin-top:0">Cinco localizadores de la pantalla Recargas: ¿en qué peldaño está cada uno?</h3>
<div class="meta">{A_LA_VEZ}</div>
<p>1 = el más robusto · 5 = nunca. En el chat, cinco números en el orden de las filas; por ejemplo: <b>«1 2 3 4 5»</b>.</p>
{clasificador('orden', ordenar, OPC_ORDEN)}
</div>
<div class="card c-yel">
<p class="paso">demo · el rediseño · <code>/recargas?rediseno=1</code></p>
<h3 style="margin-top:0">Desarrollo «solo cambió el diseño»</h3>
<ul class="lista">{rediseno_html}</ul>
<p>Nuestra propia <code>PaginaRecargas</code> usa <code>page.locator('#saldo')</code>: con el rediseño, <b>se cae</b>. Así se ve en el patio de localizadores:</p>
<table class="apilar"><thead><tr><th>Localizador</th><th>Hoy</th><th>Rediseño</th><th></th></tr></thead><tbody>{patio_html}</tbody></table>
<p class="nota">Los números son elementos encontrados. 1 es lo correcto; 0 es «no encontrado»; más de 1 es «modo estricto»: Playwright no adivina cuál quieres.</p>
<h3>Un hallazgo en nuestro propio repo</h3>
<p>En <code>tests/recargas/recargas.spec.ts</code>, línea {N_ESCAPADA}:</p>
{codigo(LINEA_ESCAPADA)}
<p><b>¿En qué capa debería vivir ese localizador?</b></p>
{revelar('escapado', 'Ver la respuesta', '<p>En el <b>Page Object</b>. El peldaño está bien (rol y nombre); el problema es <b>dónde vive</b>. Hoy el botón está en dos lugares: si cambia su nombre, hay que corregir dos archivos, y uno se olvida. Es el mismo defecto del tercer fragmento de «¿es un buen Page Object?» de la S5: el localizador en la prueba. La corrección es una línea: <code>botonRecargar</code> público (<code>readonly</code>) y la prueba usa <code>paginaRecargas.botonRecargar</code>.</p>')}
</div>
</section>

<section id="reto2">
<div class="card c-lime">
<p class="paso">laboratorio · reto 2 + patio · salas · 2 tramos de 6 min</p>
<h2>El Page Object heredado <span class="acc">que no sobrevive al rediseño</span></h2>
<p>Otro equipo les deja <code>src/paginas/heredadas/PaginaRecargasHeredada.ts</code>. Funciona hoy, pero tiene 5 localizadores frágiles. Cámbienlos por robustos y prueben contra la pantalla de hoy y contra el rediseño. <b>Un localizador = una prueba.</b></p>
<table class="apilar"><tbody>{fragiles_html}</tbody></table>
<ul class="lista"><li><b>Tramo 1 (6 min):</b> en la pestaña <b>Patio de localizadores</b>, prueben su localizador en «hoy» y en «rediseño» hasta ver 1 y 1. Luego los localizadores 1 a 3. En el chat: «Sala X: n de 5».</li>
<li><b>Tramo 2 (6 min):</b> los localizadores 4 y 5.</li></ul>
<a class="boton" href="{LABORATORIO}">Abrir el laboratorio de la S6</a>
<p class="nota">El patio es <b>simplificado: Playwright real hace más</b>. Sirve para practicar <code>getByRole</code>, <code>getByLabel</code>, <code>getByText</code>, <code>getByTestId</code> y <code>locator()</code> con el modo estricto. Con el repo instalado: <code>npx.cmd playwright test --project=retos-s06-ui</code>. Para mirar una pantalla con F12, solo el Banco Demo o ParaBank: nunca un sistema del banco.</p>
</div>
</section>

<section id="esperas">
<div class="card c-peach">
<p class="paso">predice · 2 min</p>
<h2>¿Qué pasa <span class="acc">sin <code>await</code>?</span></h2>
<div class="meta">{A_LA_VEZ}</div>
{codigo(SIN_AWAIT['codigo'])}
<p class="opciones">{sin_await_ops}</p>
{revelar('await-res', 'Ver lo que pasó al correrla', f'<p><b>{SIN_AWAIT["ok"]})</b> {a_html(SIN_AWAIT["lectura"])}</p>' + codigo(SIN_AWAIT['error']) + f'<p>{a_html(SIN_AWAIT["peor"])}</p>')}
</div>
{ficha(F['esperas'])}
<div class="card c-lav">
<p class="paso">comprobación · 3 min · ¿cuál es robusta?</p>
<h3 style="margin-top:0">Tres maneras de revisar el saldo después de recargar</h3>
<p>En las tres, <code>{html.escape(ROBUSTA_ANTES)}</code></p>
<div class="meta">{A_LA_VEZ}</div>
{clasificador('robusta', robusta, [('si', 'Robusta'), ('no', 'Frágil')])}
<p class="nota"><b>¿Cuánto espera Playwright?</b> Cada <code>expect</code>, 5 segundos. Cada prueba completa, 30 (<code>Test timeout of 30000ms exceeded</code>). Si 4 pruebas se quedan esperando algo que nunca llega, son 4 × 30 segundos: los «2 minutos» de una corrida que se cuelga.</p>
</div>
</section>

<section id="cp">
<div class="card c-cyan">
<h2>Tu CP → <span class="acc">una prueba</span></h2>
<div class="meta"><span class="chip">7:17 · 18 min</span><span class="chip">piso: la tabla · techo: el prompt en su Copilot</span></div>
<p>Su caso manual ya es casi una prueba. Cada línea se traduce a una pieza del framework:</p>
<p><span class="tipo t-ambiente">{TIPOS["ambiente"]}</span> <span class="tipo t-pre">{TIPOS["pre"]}</span> <span class="tipo t-paso">{TIPOS["paso"]}</span> <span class="tipo t-dato">{TIPOS["dato"]}</span> <span class="tipo t-esperado">{TIPOS["esperado"]}</span></p>
<p class="nota">Usamos casos del Banco Demo, nunca casos del ALM del banco. El ALM (<i>Application Lifecycle Management</i>) es donde viven sus CP en el trabajo: OpenText ALM/Quality Center, Jira con Xray o Azure Test Plans. Su ID va en el nombre de la prueba: eso es trazabilidad.</p>
</div>
<h3>Los casos del Banco Demo</h3>
<div class="cps">{cps_html}</div>
<div class="card">
<p class="paso">ejemplo resuelto · CP-101, línea por línea</p>
<table class="trad"><thead><tr><th>Tipo</th><th>Lo que dice el caso</th><th>Cómo queda en la prueba</th></tr></thead><tbody>{modelo_filas}</tbody></table>
{codigo(MODELO_CODIGO)}
<p class="nota"><b>Página o tarea, sin importar dónde se valide.</b> Una acción de página es una interacción en una pantalla: <code>recargar()</code> llena y pulsa. Una tarea es un paso de negocio con nombre que puede juntar varias pantallas o servicios: «iniciar sesión» (login + SMS + código) o «recargar con código» (pantalla + buzón + confirmar).</p>
<p class="nota"><b>Los datos, fijos y con nombre.</b> <code>valida()</code> siempre entrega Claro, 3001234567 y $10.000, porque una prueba que falla tiene que poder repetirse igual. Aleatorio solo cuando sirve (el cliente único de ParaBank) y siempre reproducible. Si una regla cambia, se cambia el valor en un solo lugar: la fábrica.</p>
</div>
<div class="card c-lime">
<p class="paso">piso · tu turno · 10 min</p>
<h3 style="margin-top:0">Elijan un caso y tradúzcanlo</h3>
<p><label for="cp-elegido"><b>Mi caso:</b></label> <select id="cp-elegido" class="cp-sel">{opciones_cp}</select></p>
{practica_html}
<p><b>Terminaron cuando cada fila tiene su traducción.</b> Copien la tabla y péguenla en el chat.</p>
</div>
<div class="card c-yel">
<p class="paso">techo · para quien terminó</p>
<h3 style="margin-top:0">El mismo caso, con el prompt de la plantilla en su Copilot</h3>
<ol class="pasos"><li>Abran <a href="{PLANTILLA}">la plantilla</a> y copien el prompt.</li>
<li>Péguenlo en el asistente que su empresa aprobó, y al final pongan su caso («Copiar el caso», arriba).</li>
<li>Pasen lo que devuelva por la <a href="#cotejo">lista de cotejo</a>. Si una línea no cumple, pídanle que la corrija con la regla de la lista.</li></ol>
<p class="nota">Un voluntario deja su prueba lista: a las 7:40 la corremos en vivo contra el Banco Demo. Al asistente solo va el caso del Banco Demo: nada del banco.</p>
</div>
</section>

<section id="cotejo">
<div class="card c-lav">
<h2>Lista de cotejo · <span class="acc">¿la subo o no la subo?</span></h2>
<div class="meta"><span class="chip">7:35 · 5 min</span><span class="chip">la revisa una persona, no una herramienta</span></div>
<p>Sirve para cualquier prueba: la suya, la de un compañero o la que escribió una IA. Que no salte ninguna alerta no la hace buena: la lista es para pensar, no para contar.</p>
<ul class="checks">{cotejo_html}</ul>
<p class="contador" id="cotejo-cuenta" aria-live="polite"></p>
</div>
<div class="card">
<p class="paso">práctica · revisen esta prueba con la lista</p>
<p>Una prueba de ejemplo para el CP-103 (celular de 6 dígitos), del estilo de lo que devuelve un asistente sin contexto. ¿Qué ítems de la lista incumple?</p>
{codigo(PRUEBA_A_REVISAR, numerado=True)}
{revelar('defectos', 'Ver lo que encontramos', '<ul class="lista">' + defectos_html + '</ul><p class="nota">Compárenla con la traducción del CP-103 de arriba: los mismos pasos, cada uno en su capa.</p>')}
</div>
<div class="card c-yel">
<p class="paso">7:40 · prueba en vivo</p>
<p>El instructor corre la prueba del voluntario contra el Banco Demo, después de leerla con la lista. Si sale roja, la pregunta es una sola: <b>¿rojo del sistema o rojo del script?</b> Si el esperado sale de la regla y el sistema no la cumple (como el CP-106), es un hallazgo. Si el script buscó algo que no existe, se corrige el script.</p>
</div>
</section>

<section id="boleto">
<div class="card c-lime">
<h2>Boleto de salida</h2>
<div class="meta"><span class="chip">7:45 · 6 min</span>{A_LA_VEZ}</div>
<p>Las cuatro letras en orden, en el chat, todos al mismo tiempo.</p>
<ol class="boleto">{b6_items}</ol>
{revelar('b6-resp', 'Ver las respuestas', '<ol class="boleto">' + b6_resp + '</ol>')}
</div>
<div class="card c-lav">
<h3 style="margin-top:0">Mi CP es…</h3>
<p>Completen la frase con un caso del Banco Demo y péguenla en el chat.</p>
<div class="frase">Mi CP es <select id="f-cp" aria-label="Mi caso">{opciones_cp_todas}</select>: su paso clave se vuelve <input id="f-paso" aria-label="El paso clave" placeholder="getByRole('button', …)"> y su esperado se vuelve <input id="f-esp" aria-label="El esperado" placeholder="await expect(…)"></div>
<p><button type="button" class="grande" id="copiar-frase">Copiar mi frase</button><span class="ok" id="frase-ok"></span></p>
</div>
</section>

<section id="cierre">
<div class="card">
<h2>Para su proyecto: <span class="acc">la plantilla</span></h2>
<div class="meta"><span class="chip">7:51</span></div>
<p>Les prometí un repo aparte; como no todos pueden clonar, aquí está en una página que sí abren. Quien tenga GitHub la encuentra en <code>plantilla/</code>.</p>
<a class="boton" href="{PLANTILLA}">Abrir la plantilla</a>
<p>Trae un framework mínimo con las mismas capas (configuración congelada, un Page Object con localizadores por rol y etiqueta, una fábrica, fixtures y la prueba CP-101) y el prompt para su Copilot. Apunta al Banco Demo publicado en Pages: corre sin servidor local.</p>
</div>
<div class="card c-yel">
<p class="paso">3 min · bitácora de revisión</p>
<h3 style="margin-top:0">Lo que revisé hoy</h3>
<p>Para quien presente una <b>revisión</b> el día final, y para todos: tres líneas sobre una prueba que revisaron hoy (la suya, la de la IA o la del repo).</p>
<textarea id="bitacora" aria-label="Bitácora de revisión" placeholder="Revisé…&#10;Encontré (ítem de la lista de cotejo)…&#10;Lo mejoraría así…"></textarea>
<p><button type="button" data-copiar="bitacora">Copiar mi bitácora</button><span class="ok" data-copiado="bitacora"></span></p>
<p class="nota">En el repo: las fichas de hoy en <code>docs/configuracion-y-localizadores.md</code>, los retos en <code>retos/S06.md</code>. Lo que escriban aquí queda solo en su navegador mientras la página esté abierta.</p>
</div>
</section>
<p class="nota">Página de práctica del Bootcamp QA · Knot Academy. No carga nada de internet salvo las fuentes. Los datos son de práctica: nunca escriban aquí datos reales.</p>
</div>
<script>{JS}</script>
</body>
</html>
'''
salida = RAIZ / 'laboratorio' / 'actividades_S6.html'
salida.write_text(HTML, encoding='utf-8')
if PARA_ENVIAR.is_dir():
    shutil.copyfile(salida, PARA_ENVIAR / 'actividades_S6.html')

# ---------- docs/configuracion-y-localizadores.md: las mismas fichas, para leer en el repo ----------
md = ['# Configuración, ambientes, localizadores y esperas (S6)', '',
      'Tres fichas que construyen sobre las capas de la S3 (ver [arquitectura.md](arquitectura.md)) y los patrones de la S5 '
      '(ver [patrones.md](patrones.md)). Este archivo lo genera `laboratorio/generar/generar_actividades_s6.py` '
      'desde `fichas_s6.py`, la misma fuente de las actividades y del deck: si cambias una ficha, cámbiala allí.', '',
      '| Ficha | Capa | Dónde verlo |', '|---|---|---|',
      '| Configuración y ambientes | `src/config/` | `ambientes.ts` (reto 1), `entorno.ts`, `.env.ejemplo` |',
      '| Localizadores robustos | `src/paginas/` | `PaginaRecargas.ts`, `heredadas/PaginaRecargasHeredada.ts` (reto 2) |',
      '| Esperas | `src/paginas/` y `tests/` | `PaginaRecargas.esperarResultado()`, las aserciones de `tests/recargas/` |', '']
for f in FICHAS:
    md += [f'## {f["nombre"]}', '', f'*{f["desde"]}*', '', '| | |', '|---|---|']
    md += [f'| **{et}** | {f[k]} |' for k, et in FILAS_FICHA]
    md.append('')
md += ['## La escalera de localizadores', '', '| Peldaño | Ejemplo | Cuándo |', '|---|---|---|']
md += [f'| {n + 1} · {p} | `{e}` | {c} |' for n, (p, e, c) in enumerate(ESCALERA)]
md += ['', f'Hallazgo del propio repo: `tests/recargas/recargas.spec.ts:{N_ESCAPADA}` busca el botón «Recargar» por su cuenta '
       '(`page.getByRole(...)` dentro de la prueba). El peldaño está bien; el lugar no: el localizador va en `PaginaRecargas`.', '',
       '## Esperas: lo que pasó al correrlo', '',
       'Contra el Banco Demo local, con Playwright 1.63:', '',
       '- `expect(locator).toHaveText(...)` **sin** `await` al final de la prueba: falla en una décima de segundo con '
       '`Received: ""` y `session closed`. El error no dice «te faltó el await».',
       '- `paginaRecargas.recargar(...)` **sin** `await`: pasó 4 de 4 veces, por suerte. Por eso es peor.',
       '- `expect(await saldo.innerText()).toBe(...)`: falló con `Received: "…"` (el saldo todavía cargaba). No reintenta.',
       '- `await expect(saldo).toHaveText(...)`: pasa; reintenta hasta 5 s.', '',
       '## Lista de cotejo de una prueba', '']
md += [f'{n + 1}. {t}' for n, t in enumerate(COTEJO)]
md += ['', '## Casos del Banco Demo (CP-101 a CP-106)', '',
       'Para practicar la traducción «paso → localizador, dato → fábrica, esperado → `expect`, ambiente → `entorno`». '
       'Son casos del Banco Demo: nunca se usan casos del ALM del banco.', '',
       '| CP | Caso | Precondición | Resultado esperado |', '|---|---|---|---|']
md += [f'| {cp["id"]} | {cp["titulo"]} | {cp["pre"]} | {cp["esperado"]}{" " + cp["nota"] if cp.get("nota") else ""} |' for cp in CPS]
md += ['', f'Traducción completa del {MODELO["id"]}:', '', '| Tipo | Lo que dice el caso | Cómo queda en la prueba |', '|---|---|---|']
md += [f'| {TIPOS[t]} | {c} | {p} |' for t, c, p in MODELO['filas']]
md += ['', '## Postman: un pedido, dos ambientes', '',
       f'- Ambientes de práctica (archivos estáticos en Pages): QA `{AMBIENTES["QA"]}` y UAT `{AMBIENTES["UAT"]}`, cada uno con `salud.json` y `cuentas.json`.',
       f'- Colección y ambientes para importar: `{POSTMAN["coleccion"]}`, `{POSTMAN["QA"]}`, `{POSTMAN["UAT"]}`.',
       '- Variables: `urlBase`, `nombreAmbiente` y `clave` (secreta, vacía).',
       '- Reglas: un workspace aparte (nunca el del equipo) y la clave solo como valor local, sin compartir: lo compartido (la nube ☁ en Postman nuevo, el *initial value* en el anterior) se sincroniza.', '',
       '## Fuentes', '',
       '- Playwright, «Locators» y «Best practices» (playwright.dev/docs/locators, playwright.dev/docs/best-practices): prioridad de `getByRole` y de los atributos que ve el usuario.',
       '- Playwright, «Auto-waiting» (playwright.dev/docs/actionability) y «Assertions» (playwright.dev/docs/test-assertions): 5 s por `expect`; «Timeouts»: 30 s por prueba. La documentación de `page.waitForTimeout` dice que no se use en pruebas reales porque son inestables.',
       '- Postman, «Variables» y «Share variable values» (learning.postman.com): el valor local no se sincroniza; el compartido (antes *initial value*) sí.',
       '- OWASP, «Secrets Management Cheat Sheet»: los secretos fuera del código y del control de versiones.', '']
(RAIZ / 'docs' / 'configuracion-y-localizadores.md').write_text('\n'.join(md), encoding='utf-8')
print(f'actividades_S6.html y docs/configuracion-y-localizadores.md listos (localizador escapado en la línea {N_ESCAPADA})')
