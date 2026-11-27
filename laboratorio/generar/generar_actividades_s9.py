"""Genera laboratorio/actividades_S9.html (las actividades de la clase S9) y docs/triage.md.

La página va en el orden de la clase (ver HORARIO en fichas_s9.py): la línea de llegada, la ficha de las tres cajas,
«¿en qué caja va?», el mírame (con el flaky y «en una línea»), sin instalar, los 4 rojos, las salas, tu proyecto,
el modelo de charla, el ensayo (con la tarjeta y un cronómetro de 90 s), el boleto y la plantilla de láminas.
El contenido sale de fichas_s9.py, la misma fuente del deck y de la guía de estudio.

La evidencia NO se inventa: los mensajes de cada rojo se leen del reporte del triage (reportes/triage/, lo genera
`npm run triage:generar`) y de reportes/triage/rojo3-consola.txt. Las capturas van incrustadas en la página
(data:image/png): así abren con doble clic aunque GitHub o trace.playwright.dev estén bloqueados en la red del banco.
Los estilos son los de la S7 (se leen de generar_actividades_s7.py): el mismo visual Knot.
Todos los enlaces van completos a Pages, así la copia de ../para_enviar/ es el mismo archivo y funciona con doble clic.
No carga nada de internet (solo las fuentes de Google, y si no cargan se usan las del sistema).

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_actividades_s9.py
"""
import ast, base64, html, io, json, re, shutil, sys, zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
sys.path.insert(0, str(D))
from fichas_s7 import FILAS, CRITERIO_LISTO, PROYECTO, GUIA  # noqa: E402
from fichas_s9 import (PAGES, REPO, ACTIVIDADES_S8, CPS_PAGINA, LAMINAS, REPORTE_TRIAGE, TEMA, OBJETIVO, IDEA_FUERZA,  # noqa: E402
                       FRASE_GANCHO, FRASE_REGLA, FRASE_FLAKY, FRASE_ENSAYO, FRASE_CIERRE, FRASE_CHAT, LLEGADA, LLEGADA_EJEMPLO,
                       FICHA, CAJAS, EN_QUE_CAJA, ROJOS, SALAS, SALAS_NOTA, LINEA_SALA, ROLES_SALA, ANUNCIO_8, ANUNCIO_12,
                       CRITERIO_SALA, MIRAME, UNA_LINEA, FUENTES_FRASES, SIN_INSTALAR, PROYECTO_S9, PROYECTO_ESPECIFICADOR,
                       MODELO, MODELO_FRASE, ENSAYO, TARJETA_FEEDBACK, PREGUNTAS_ENSAYO, CREDITOS_NOTA, FORMATO_S10, BOLETO,
                       HORARIO, CI_FRASE, FUENTES, a_html)

LOGO = re.search(r'<img src="(data:image/png;base64,[^"]+)"', (D / 'plantilla.html').read_text(encoding='utf-8')).group(1)
PARA_ENVIAR = RAIZ.parent / 'para_enviar'
TRIAGE = RAIZ / 'reportes' / 'triage'
TRIAGE_PAGES = PAGES + 'reportes/triage/'
HORA = {texto: h for h, texto, _, _ in HORARIO}
e = lambda t: html.escape(t, quote=True)


def hora(empieza):
    """La hora del bloque del HORARIO cuyo texto empieza así (una sola fuente para las horas)."""
    for texto, h in HORA.items():
        if re.sub(r'\*\*', '', texto).startswith(empieza):
            return h
    raise SystemExit(f'No encontré «{empieza}» en HORARIO de fichas_s9.py')


def css_de_la_s7():
    """El CSS de las actividades de la S7, leído de su generador (sin ejecutarlo): el mismo visual Knot."""
    arbol = ast.parse((D / 'generar_actividades_s7.py').read_text(encoding='utf-8'))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and any(getattr(t, 'id', '') == 'CSS' for t in nodo.targets):
            return ast.literal_eval(nodo.value)
    raise SystemExit('No encontré CSS en generar_actividades_s7.py')


# ─────────────────────────── La evidencia real (reportes/triage/) ───────────────────────────
def reporte():
    """Lee el reporte HTML del triage (el zip incrustado) y devuelve, por título de prueba: testId, traces y error-context."""
    indice = TRIAGE / 'index.html'
    if not indice.exists():
        raise SystemExit('Falta reportes/triage/index.html: corre «npm run triage:generar» antes de generar la página.')
    m = re.search(r'id="playwrightReportBase64">data:application/zip;base64,([A-Za-z0-9+/=]+)', indice.read_text(encoding='utf-8'))
    if not m:
        raise SystemExit('No encontré los datos del reporte en reportes/triage/index.html (¿cambió el formato del reporte HTML?)')
    z = zipfile.ZipFile(io.BytesIO(base64.b64decode(m.group(1))))
    pruebas = {}
    for nombre in z.namelist():
        if nombre == 'report.json':
            continue
        for t in json.loads(z.read(nombre))['tests']:
            adjuntos = [a for r in t['results'] for a in r['attachments']]
            pruebas[t['title']] = {
                'testId': t['testId'], 'resultado': t['outcome'],
                'traces': [r_a['path'] for r in t['results'] for r_a in r['attachments'] if r_a['name'] == 'trace' and r_a.get('path')],
                'contexto': next((a['path'] for a in adjuntos if a['name'] == 'error-context' and a.get('path')), None),
            }
    return pruebas


PRUEBAS = reporte()


def prueba(prefijo):
    hallados = [p for t, p in PRUEBAS.items() if t.startswith(prefijo)]
    assert len(hallados) == 1, f'En el reporte del triage no hay una sola prueba que empiece con «{prefijo}»'
    return hallados[0]


def error_del_reporte(prefijo):
    """El mensaje literal: los bloques de código de «# Error details» del error-context que guardó Playwright."""
    p = prueba(prefijo)
    assert p['contexto'], f'La prueba «{prefijo}» no tiene error-context en el reporte'
    texto = (TRIAGE / p['contexto']).read_text(encoding='utf-8')
    seccion = texto.split('# Error details', 1)[1].split('\n# ', 1)[0]
    bloques = re.findall(r'```(\w*)\n(.*?)```', seccion, re.S)
    return '\n\n'.join(b.strip('\n') for lang, b in bloques if lang == '').strip()


def error_de_la_consola():
    """El rojo 3 no tiene trace: el mensaje es la consola. El error y las líneas de la pila que son del repo."""
    lineas = (TRIAGE / 'rojo3-consola.txt').read_text(encoding='utf-8').split('\n')
    utiles = [l for l in lineas if l.startswith('Error') or (re.match(r'\s+at ', l) and not re.search(r'node:internal|node_modules|\(node:', l))]
    assert utiles and utiles[0].startswith('Error: Falta CLAVE_BANCO'), 'rojo3-consola.txt no dice «Falta CLAVE_BANCO»'
    return '\n'.join(utiles + ['    … (y el resto de la pila de Node)'])


MENSAJE = {1: error_del_reporte('rojo 1 ·'), 2: error_del_reporte('rojo 2 ·'), 3: error_de_la_consola(), 4: error_del_reporte('rojo 4 ·')}
assert 'Expected: 1500000' in MENSAJE[1] and 'Received: 1480000' in MENSAJE[1], 'El mensaje del rojo 1 no es esperado contra obtenido'
assert "xpath=/html/body/main/form[1]/select" in MENSAJE[2] and 'Test timeout of 30000ms exceeded' in MENSAJE[2], 'El mensaje del rojo 2 cambió'
assert 'Timeout:  5000ms' in MENSAJE[4], 'El mensaje del rojo 4 no dice el tiempo del expect'

# Las capturas: incrustadas, para que abran sin red. (nombre, rótulo, texto alternativo)
CAPTURAS = {
  1: [('rojo1-1-accion.png', '1 · la acción', 'Trace del rojo 1 (CP-106), pestaña Call: la última acción, Expect toBe, en rojo, con el esperado 1500000. En la pantalla del Banco Demo se recargó a Claro el número 3000000504 por 20000; el aviso dice «El operador no responde. Intenta más tarde.» y el saldo disponible ya dice $1.480.000.'),
      ('rojo1-2-error.png', '2 · el error', 'Trace del rojo 1, pestaña Errors: Error: expect(received).toBe(expected). Expected: 1500000. Received: 1480000. Señala rojo1-sistema.spec.ts, línea 44.'),
      ('rojo1-3-red.png', '3 · la red', 'Trace del rojo 1, pestaña Network filtrada por /api/: login, buzón y otp con 200; GET cuentas con 200; POST recargas con 504 (el operador simulado no responde, que es justo lo que prueba el caso) y otro GET cuentas con 200: el servicio de saldos respondió.')],
  2: [('rojo2-1-accion.png', '1 · la acción', 'Trace del rojo 2, pestaña Call: la acción Select option con el localizador xpath=/html/body/main/form[1]/select, en rojo, duró 30 s. En la pantalla rediseñada, la lista «Operador» sí está, al lado de «Número de celular».'),
      ('rojo2-2-error.png', '2 · el error', "Trace del rojo 2, pestaña Errors: Test timeout of 30000ms exceeded. Error: locator.selectOption: Test timeout of 30000ms exceeded. Call log: waiting for locator('xpath=/html/body/main/form[1]/select'). Señala PaginaRecargasHeredada.ts, línea 65."),
      ('rojo2-3-red.png', '3 · la red', 'Trace del rojo 2, pestaña Network sin filtro: login, buzón, otp, la página recargas, estilos.css y comun.js, todos con 200. El sistema respondió: la página cargó bien.')],
  3: [('rojo3-1-consola.png', '1 · la consola', "Consola del rojo 3: con AMBIENTE=qa y sin CLAVE_BANCO, npx.cmd playwright test --project=triage dice «Error: Falta CLAVE_BANCO para el ambiente qa. Defínela en la terminal: $env:CLAVE_BANCO = '...'», desde src/config/ambientes.ts, línea 80. No corrió ninguna prueba: no hay trace, ni captura, ni reporte.")],
  4: [('rojo4-1-accion.png', '1 · la acción', "Trace del rojo 4, pestaña Call: la acción Expect toHaveText sobre locator('#saldo'), en rojo, duró 5.0 s, con el esperado $1.500.000. En la pantalla, el saldo disponible todavía muestra «…»."),
      ('rojo4-2-error.png', '2 · el error', 'Trace del rojo 4, pestaña Errors: expect(locator).toHaveText falló. Locator #saldo, Expected "$1.500.000", Received "…", Timeout 5000ms; el localizador se encontró 14 veces y siempre decía «…».'),
      ('rojo4-3-red.png', '3 · la red', 'Trace del rojo 4, pestaña Network filtrada por cuentas: una sola petición, GET cuentas, en rojo, con estado cancelado, sin duración ni tamaño: el servicio de saldos nunca respondió.')],
  'reporte': [('reporte-1-resumen.png', 'el reporte', 'El reporte del triage: All 4, Passed 0, Failed 3, Flaky 1, Skipped 1. Fallan el rojo 4 (5.2 s), el rojo 1 (3.0 s) y el rojo 2 (30.1 s); el flaky aparece con el triángulo amarillo (6.2 s).')],
  'flaky': [('flaky-1-reporte.png', 'el flaky', 'El flaky en el reporte: Run, en rojo, 5.2 s, y Retry #1, en verde, 1.0 s. El error del primer intento: toHaveText en #saldo, Expected "$1.500.000", Received "…", Timeout 5000ms.')],
}


def data_uri(nombre):
    ruta = TRIAGE / 'capturas' / nombre
    assert ruta.exists(), f'Falta la captura reportes/triage/capturas/{nombre}: corre «npm run triage:generar»'
    return 'data:image/png;base64,' + base64.b64encode(ruta.read_bytes()).decode('ascii')


def capturas(clave, numeradas=True):
    figs = ''.join(
        f'<figure class="captura"><button type="button" class="ampliar" data-ampliar data-pie="{e(rotulo)}">'
        f'<img src="{data_uri(nombre)}" alt="{e(alt)}" loading="lazy" width="1400" height="900"><span class="lupa" aria-hidden="true">Ampliar ⤢</span></button>'
        f'<figcaption>{"<b>" + e(rotulo) + "</b>" if numeradas else e(rotulo)}</figcaption></figure>'
        for nombre, rotulo, alt in CAPTURAS[clave])
    return f'<div class="capturas n{len(CAPTURAS[clave])}">{figs}</div>'


def trace_en_reporte(ruta_zip):
    """El mismo enlace que arma el botón «View Trace» del reporte: el visor del reporte con la dirección completa del zip."""
    return f'{TRIAGE_PAGES}trace/index.html?trace={TRIAGE_PAGES}{ruta_zip}'


def en_trace_playwright(zip_publicado):
    return f'https://trace.playwright.dev/?trace={TRIAGE_PAGES}traces/{zip_publicado}'


# ─────────────────────────── Piezas de la página (las mismas de la S8) ───────────────────────────
def codigo(texto, clase='code prosa'):
    return f'<pre class="{clase}">' + html.escape(texto.rstrip('\n')) + '</pre>'


def clasificador(cid, filas, opciones):
    trs = ''.join(
        f'<tr data-ok="{ok}"><td class="n">{n + 1}</td><td>{txt}<div class="exp" hidden>{exp}</div></td>'
        f'<td class="opc">' + ''.join(f'<button type="button" data-v="{k}">{et}</button>' for k, et in opciones) + '</td></tr>'
        for n, (txt, ok, exp) in enumerate(filas))
    return (f'<table class="clasif" id="t-{cid}"><tbody>{trs}</tbody></table>'
            f'<p><button type="button" class="grande" data-revisar="{cid}">Revisar</button>'
            f'<button type="button" data-reiniciar="{cid}">Reiniciar</button><span class="puntaje" id="p-{cid}" aria-live="polite"></span></p>')


def revelar(rid, boton, contenido, clase='grande'):
    return f'<p><button type="button" class="{clase}" data-revelar="{rid}" aria-expanded="false" aria-controls="{rid}">{boton}</button></p><div id="{rid}" hidden>{contenido}</div>'


ABC = [(k, k) for k in 'abc']


def preguntas(cid, lista, etiqueta='Ver las respuestas', previo=''):
    filas = [(f'<b>{previo}{a_html(p)}</b><p class="opciones">' + '<br>'.join(f'<b>{"abc"[k]})</b> {a_html(o)}' for k, o in enumerate(ops)) + '</p>',
              ok, f'<b>{ok})</b> {a_html(por)}') for p, ops, ok, por in lista]
    letras = ' '.join(ok for _, _, ok, _ in lista)
    resp = f'<p class="letras">{letras}</p><ol class="boleto">' + ''.join(f'<li><b>{ok}</b> · {a_html(por)}</li>' for _, _, ok, por in lista) + '</ol>'
    return clasificador(cid, filas, ABC) + revelar(f'{cid}-resp', etiqueta, resp)


def boton_copiar(bid, texto='Copiar'):
    return f'<button type="button" class="grande" id="{bid}">{texto}</button><span class="ok" id="{bid}-ok" aria-live="polite"></span>'


A_LA_VEZ = '<span class="chip">respondan a la vez: escriban sin enviar · «3, 2, 1, envíen»</span>'
CAJA_CLASE = {'sistema': 'k-sistema', 'script': 'k-script', 'ambiente': 'k-ambiente'}


def chip_caja(caja):
    return f'<span class="caja {CAJA_CLASE[caja]}">{e(caja)}</span>'


# ─────────────────────────── Datos que cruzan las secciones ───────────────────────────
POR_N = {r['n']: r for r in ROJOS}
SALAS_DE = {r['n']: [s for s, ns in SALAS if r['n'] in ns] for r in ROJOS}
assert all(len(v) == 2 for v in SALAS_DE.values()), 'Cada rojo lo ven dos salas (SALAS_NOTA)'
assert {r['caja'] for r in ROJOS} == {'sistema', 'script', 'ambiente'}, 'Los rojos cubren las tres cajas'

MOLDE_SALA = LINEA_SALA.split(' (')[0]
assert MOLDE_SALA.count('___') == 2 and MOLDE_SALA.startswith('Sala X · rojo N'), f'LINEA_SALA cambió de forma: {LINEA_SALA}'
PISTA_SALA = LINEA_SALA[len(MOLDE_SALA):].strip(' ()')

m = re.search(r'«(Mi CP[^»]+)»', PROYECTO_S9)
assert m and m.group(1).count('___') == 3, 'PROYECTO_S9 ya no trae la línea «Mi CP · falla: ___ · caja: ___ · evidencia: ___»'
MOLDE_PROYECTO = m.group(1)

m = re.search(r'\*\*(confirmo: .+?)\*\*', LLEGADA)
assert m and m.group(1).count('___') == 2, 'LLEGADA ya no trae «confirmo: … ___ · … ___»'
MOLDE_LLEGADA = m.group(1)


# ─────────────────────────── Secciones ───────────────────────────
def seccion_llegada():
    criterio = ''.join(
        f'<label class="check chico"><input type="checkbox" class="falta" value="{n}"> <span><b>{n}</b> · {a_html(t)}</span></label>'
        for n, (t, _) in enumerate(CRITERIO_LISTO, 1))
    return f'''<section id="llegada">
<div class="card c-yel">
<h2>La línea de llegada · <span class="acc">una cada uno</span></h2>
<div class="meta"><span class="chip">{hora('Llegada')} · antes de saludar</span><span class="chip">en el chat principal</span></div>
<p class="frase-grande">{a_html(LLEGADA)}</p>
<p class="nota">Por ejemplo: <code>{e(LLEGADA_EJEMPLO)}</code></p>
<div class="rescate">
<label>Cómo presento <select id="l-modo"><option value="">elige…</option><option value="individual">individual</option><option value="equipo">en equipo</option></select></label>
<label id="l-con-caja" hidden>Con quién <input id="l-con" type="text" placeholder="los nombres de tu equipo" autocomplete="off"></label>
<fieldset class="ancho criterio-listo"><legend>Del criterio de listo me falta (marca lo que <b>no</b> tienes todavía)</legend>{criterio}</fieldset>
</div>
<p class="paso" style="margin-top:12px">así queda en el chat</p>
<p class="linea-chat" id="llegada-linea"></p>
<p>{boton_copiar("copiar-llegada", "Copiar mi línea")}</p>
<p class="nota">Los siete puntos son los del <a href="{PROYECTO}#listo">criterio de listo del kit de proyecto</a>. Lo que marques queda solo en este navegador.</p>
<p class="criterio"><b>{a_html(FRASE_CHAT)}</b></p>
</div>
</section>'''


def seccion_ficha():
    ficha_html = ''.join(f'<div class="fk">{et}</div><div class="fv">{a_html(FICHA[k])}</div>' for k, et in FILAS)
    cajas = ''.join(f'<tr><td data-k="La caja">{chip_caja(c.lower())}</td><td data-k="Qué es">{a_html(q)}</td>'
                    f'<td data-k="Cómo se ve el mensaje">{a_html(v)}</td><td data-k="A quién va el ticket">{a_html(t)}</td></tr>'
                    for c, q, v, t in CAJAS)
    return f'''<section id="ficha">
<div class="card c-peach">
<p class="paso">gancho · {hora('Gancho')}</p>
<p class="frase-grande" style="margin:0">«{a_html(FRASE_GANCHO)}»</p>
</div>
<div class="card">
<div class="meta"><span class="chip">{hora('Ficha de las tres cajas')}</span><span class="chip">las tres cajas</span></div>
<h2>¿Sistema, script <span class="acc">o ambiente?</span></h2>
<table class="apilar cajas"><thead><tr><th>La caja</th><th>Qué es</th><th>Cómo se ve el mensaje</th><th>A quién va el ticket</th></tr></thead><tbody>{cajas}</tbody></table>
<p class="frase-grande">«{a_html(FRASE_REGLA)}»</p>
</div>
<div class="card ficha-card"><div class="meta"><span class="chip">ficha · {hora('Ficha de las tres cajas')}</span></div>
<h2>{e(FICHA["titulo"])}</h2>
<div class="ficha">{ficha_html}</div></div>
</section>'''


def seccion_en_que_caja():
    return f'''<section id="en-que-caja">
<div class="card c-lav">
<p class="paso">comprobación · {hora('Ficha de las tres cajas')}</p>
<h2>¿En qué caja va? <span class="acc">Solo con el mensaje</span></h2>
<div class="meta">{A_LA_VEZ}</div>
<p>Tres letras en el chat, en orden, al mismo tiempo. Las respuestas, cuando el instructor lo diga.</p>
{preguntas('enque', EN_QUE_CAJA)}
</div>
</section>'''


def seccion_mirame():
    flaky = prueba('flaky ·')
    filas = ''.join(f'<tr><td data-k="Qué"><b>{a_html(q)}</b></td><td data-k="El comando">{a_html(c)}</td><td data-k="Qué se ve">{a_html(v)}</td></tr>'
                    for q, c, v in MIRAME)
    una = ''.join(f'<tr><td data-k="La pieza" class="pieza">{a_html(p)}</td><td data-k="En una línea">{a_html(t)}</td></tr>' for p, t in UNA_LINEA)
    fuentes = ''.join(f'<li>{a_html(f)} <a class="nota" href="https://{u}">({e(u)})</a></li>' for f, u in FUENTES_FRASES)
    intentos = ''.join(f'<a class="boton blanco chico" href="{TRIAGE_PAGES}traces/flaky-intento{i}.zip" download>Zip del intento {i}</a>' for i in (1, 2))
    return f'''<section id="mirame">
<div class="card">
<h2>Mírame · <span class="acc">el trace, la red y el flaky</span></h2>
<div class="meta"><span class="chip">mírame · {hora('Mírame')} · 10 min</span><span class="chip">lo corre el instructor</span></div>
<table class="apilar"><thead><tr><th>Qué</th><th>El comando</th><th>Qué se ve</th></tr></thead><tbody>{filas}</tbody></table>
<p class="nota">En Windows va con <code>npx.cmd</code> y <code>npm.cmd</code>. Si no puedes instalar, todo lo que se ve aquí está en el reporte publicado y en las capturas de abajo.</p>
</div>
<div class="grid2">
<div class="card c-yel"><p class="paso">el reporte del triage</p>{capturas('reporte', numeradas=False)}
<p><a class="boton chico" href="{REPORTE_TRIAGE}">Abrir el reporte</a></p></div>
<div class="card c-peach"><p class="paso">el flaky: falló y pasó al reintentar</p>{capturas('flaky', numeradas=False)}
<p><a class="boton chico" href="{REPORTE_TRIAGE}#?testId={flaky["testId"]}">El flaky en el reporte</a>{intentos}</p></div>
</div>
<div class="card c-lime"><p class="paso">el flaky</p><p class="frase-grande" style="margin:0">«{a_html(FRASE_FLAKY)}»</p></div>
<div class="card">
<p class="paso">en una línea</p>
<table class="apilar"><thead><tr><th>La pieza</th><th>En una línea</th></tr></thead><tbody>{una}</tbody></table>
<details><summary>De dónde sale cada frase</summary><ul class="lista">{fuentes}</ul></details>
</div>
</section>'''


def seccion_sin_instalar():
    items = ''.join(f'<li>{a_html(x)}</li>' for x in SIN_INSTALAR)
    return f'''<section id="sin-instalar">
<div class="card c-cyan">
<h2>Sin instalar <span class="acc">nada</span></h2>
<ol class="lista">{items}</ol>
<p><a class="boton" href="{REPORTE_TRIAGE}">El reporte del triage</a><a class="boton blanco" href="https://trace.playwright.dev/">trace.playwright.dev</a></p>
<p class="nota">El reporte abre los traces en Pages, sin subir nada. Si en tu equipo no abre, quédate con las capturas: son la misma evidencia. Para ampliar una captura, haz clic en ella.</p>
</div>
</section>'''


def tarjeta_rojo(r):
    n = r['n']
    salas = ' y '.join(SALAS_DE[n])
    if n == 3:
        p = prueba('rojo 3 ·')
        enlaces = (f'<p class="sin-trace"><b>No hay trace.</b> La configuración falló al cargar, en el segundo cero: no se abrió el navegador. '
                   f'Esa ausencia también es evidencia.</p>'
                   f'<p><a class="boton blanco chico" href="{REPORTE_TRIAGE}#?testId={p["testId"]}">El rojo 3 en el reporte (saltado: no corre allí)</a></p>')
    else:
        p = prueba(f'rojo {n} ·')
        assert p['traces'], f'El rojo {n} no tiene trace en el reporte'
        zipn = f'rojo{n}.zip'
        assert (TRIAGE / 'traces' / zipn).exists(), f'Falta reportes/triage/traces/{zipn}'
        enlaces = (f'<p><a class="boton chico" href="{trace_en_reporte(p["traces"][-1])}">Abrir el trace en el reporte</a>'
                   f'<a class="boton blanco chico" href="{REPORTE_TRIAGE}#?testId={p["testId"]}">La prueba en el reporte</a>'
                   f'<a class="boton blanco chico" href="{TRIAGE_PAGES}traces/{zipn}" download>Descargar {zipn}</a>'
                   f'<a class="boton blanco chico" href="{en_trace_playwright(zipn)}">Abrir en trace.playwright.dev</a></p>')
    oculto = (f'<div class="revelado"><p class="paso">la caja</p><p>{chip_caja(r["caja"])}</p>'
              f'<dl><dt>Cómo se provocó</dt><dd>{a_html(r["como"])}</dd><dt>La evidencia</dt><dd>{a_html(r["evidencia"])}</dd>'
              f'<dt>Lo que se aprende</dt><dd>{a_html(r["aprende"])}</dd></dl></div>')
    return f'''<article class="card rojo" id="rojo-{n}" aria-labelledby="rojo-{n}-t">
<div class="meta"><span class="chip rojo-n">rojo {n}</span><span class="chip">lo ven: {e(salas)}</span></div>
<h3 id="rojo-{n}-t" style="margin-top:4px">{e(r["titulo"])}</h3>
<p class="paso">el mensaje{" · la consola" if n == 3 else ""}</p>
{codigo(MENSAJE[n])}
<p class="paso">{"la captura" if n == 3 else "las capturas: la acción, el error y la red"}</p>
{capturas(n)}
{enlaces}
{revelar(f"rev-{n}", "Revelar la caja y la evidencia", oculto, clase="")}
</article>'''


def seccion_rojos():
    return f'''<section id="rojos">
<div class="card c-lav">
<h2>Los 4 rojos · <span class="acc">la evidencia real</span></h2>
<p>Cuatro pruebas que fallan a propósito en <code>tests/triage-s09/</code>. De cada una: el mensaje tal como salió, las capturas numeradas y su trace. <b>La caja va escondida</b>: primero la deciden en la sala, después la revelan.</p>
<p class="nota">{a_html(SALAS_NOTA)}</p>
</div>
{"".join(tarjeta_rojo(r) for r in ROJOS)}
</section>'''


def panel_sala(sala, ns):
    sid = sala.split()[-1]
    filas = ''
    for n in ns:
        opciones = '<option value="">caja…</option>' + ''.join(f'<option value="{c}">{c}</option>' for c in ('sistema', 'script', 'ambiente'))
        filas += (f'<div class="linea-rojo" data-rojo="{n}"><p class="paso"><a href="#rojo-{n}">rojo {n} · {e(POR_N[n]["titulo"])}</a></p>'
                  f'<div class="rescate"><label>Caja <select id="c-{sid}-{n}" data-campo="caja">{opciones}</select></label>'
                  f'<label class="ancho2">Evidencia <input id="v-{sid}-{n}" data-campo="evidencia" type="text" autocomplete="off" placeholder="{e(PISTA_SALA)}"></label></div>'
                  f'<p class="linea-chat" data-linea></p>'
                  f'<p><button type="button" class="grande" data-copiar-rojo="{n}">Copiar el rojo {n}</button><span class="ok" aria-live="polite"></span></p></div>')
    return (f'<div class="sala-panel" data-sala="{sid}" hidden><h3 style="margin-top:0">{e(sala)} · rojos {" y ".join(str(n) for n in ns)}</h3>{filas}'
            f'<p><button type="button" data-copiar-sala>Copiar los dos (para el chat principal)</button><span class="ok" aria-live="polite"></span></p></div>')


def seccion_salas():
    filas = ''.join(f'<tr><td data-k="Sala"><b>{e(s)}</b></td><td data-k="Rojos">' + ' · '.join(f'<a href="#rojo-{n}">rojo {n}</a>' for n in ns) + '</td></tr>'
                    for s, ns in SALAS)
    opciones = ''.join(f'<option value="{s.split()[-1]}">{e(s)} · rojos {" y ".join(str(n) for n in ns)}</option>' for s, ns in SALAS)
    return f'''<section id="salas">
<div class="card c-cyan">
<h2>Las salas · <span class="acc">dos rojos cada una</span></h2>
<div class="meta"><span class="chip">salas {hora('Salas, 15 min')} · 15 min</span><span class="chip">aleatorias</span></div>
<div class="grid2">
<div><table class="apilar salas"><thead><tr><th>Sala</th><th>Rojos</th></tr></thead><tbody>{filas}</tbody></table>
<p class="nota">{a_html(SALAS_NOTA)}</p></div>
<div><p class="paso">los roles</p><p style="margin-top:0">{a_html(ROLES_SALA)}</p>
<ul class="lista nota"><li>{a_html(ANUNCIO_8)}</li><li>{a_html(ANUNCIO_12)}</li></ul></div>
</div>
<p class="criterio">{a_html(CRITERIO_SALA)}</p>
</div>
<div class="card" id="linea-sala">
<p class="paso">la línea pegable</p>
<p class="linea-chat molde">{e(LINEA_SALA)}</p>
<p><label for="s-sala"><b>Mi sala:</b></label> <select id="s-sala" class="cp-sel">{opciones}</select></p>
<p class="nota">Lo que escriban se guarda solo en este navegador, un borrador por sala: cambiar de sala no borra el de otra.</p>
{"".join(panel_sala(s, ns) for s, ns in SALAS)}
<p class="nota" id="estado-sala" aria-live="polite"></p>
</div>
</section>'''


def seccion_proyecto():
    opciones = '<option value="">caja…</option>' + ''.join(f'<option value="{c}">{c}</option>' for c in ('sistema', 'script', 'ambiente'))
    return f'''<section id="proyecto">
<div class="card c-peach">
<h2>Tu proyecto · <span class="acc">una falla provocada y clasificada</span></h2>
<div class="meta"><span class="chip">{hora('Tu proyecto')} · 20 min fijos · en la sala principal</span></div>
<p class="frase-grande">{a_html(PROYECTO_S9)}</p>
<div class="rescate">
<label>Mi CP <input id="p-cp" type="text" placeholder="CP-104" autocomplete="off"></label>
<label>Caja <select id="p-caja">{opciones}</select></label>
<label class="ancho">La falla <input id="p-falla" type="text" placeholder="qué cambiaste o rompiste a propósito" autocomplete="off"></label>
<label class="ancho">La evidencia <input id="p-evidencia" type="text" placeholder="la línea del trace, de la consola o la regla" autocomplete="off"></label>
</div>
<p class="paso" style="margin-top:12px">así queda en el chat</p>
<p class="linea-chat" id="proyecto-linea"></p>
<p>{boton_copiar("copiar-proyecto", "Copiar mi línea")}</p>
<p class="criterio"><b>Vía de especificador.</b> {a_html(PROYECTO_ESPECIFICADOR)}</p>
<p><a class="boton" href="{LAMINAS}">Abrir la plantilla de láminas (la lámina 4 es tu falla)</a><a class="boton blanco" href="{ACTIVIDADES_S8}#revisor">Tu tabla de la S8 en el revisor</a></p>
</div>
</section>'''


def seccion_modelo():
    partes = ''.join(f'<div class="card parte"><p class="paso">{k}</p><h3 style="margin-top:0">{e(t)}</h3><p style="margin:0">{a_html(x)}</p></div>'
                     for k, (t, x) in enumerate(MODELO, 1))
    return f'''<section id="modelo">
<div class="card c-lime">
<h2>El modelo · <span class="acc">3 minutos, en cuatro partes</span></h2>
<div class="meta"><span class="chip">{hora('El modelo del instructor')} · cronometrado</span></div>
<p class="frase-grande">{a_html(MODELO_FRASE)}</p>
</div>
<div class="grid4">{partes}</div>
</section>'''


def seccion_ensayo():
    tarjeta = ''.join(f'<li>{a_html(t)}</li>' for t in TARJETA_FEEDBACK)
    checks = ''.join(f'<li><label class="check"><input type="checkbox" class="preg-ensayo"> <span>{a_html(p)}</span></label></li>' for p in PREGUNTAS_ENSAYO)
    return f'''<section id="ensayo">
<div class="card c-yel">
<h2>El ensayo · <span class="acc">90 segundos cada uno</span></h2>
<div class="meta"><span class="chip">{hora('Ensayo en las mismas salas')} · en las mismas salas</span><span class="chip">no se califica</span></div>
<p class="frase-grande">{a_html(ENSAYO)}</p>
<p class="criterio"><b>«{a_html(FRASE_ENSAYO)}»</b></p>
</div>
<div class="grid2">
<div class="card crono" id="crono">
<p class="paso">el cronómetro</p>
<div class="crono-modo" role="group" aria-label="Duración">
<button type="button" data-dur="90" aria-pressed="true">90 s · presentar</button><button type="button" data-dur="30" aria-pressed="false">30 s · feedback</button>
</div>
<p class="reloj" id="reloj" role="timer" aria-label="Tiempo que queda">1:30</p>
<p><button type="button" class="grande" id="crono-iniciar">Iniciar</button><button type="button" id="crono-reiniciar">Reiniciar</button></p>
<p class="nota" id="crono-aviso" aria-live="assertive"></p>
<p class="nota">Lo lleva quien queda último en orden alfabético. Avisa en voz alta a los 30 segundos y al final.</p>
</div>
<div class="card">
<p class="paso">la tarjeta de feedback · 30 s</p>
<ol class="tarjeta">{tarjeta}</ol>
<p class="paso">mientras escuchas</p>
<ul class="checks">{checks}</ul>
<p><button type="button" id="preg-limpiar">Desmarcar (siguiente persona)</button></p>
</div>
</div>
</section>'''


def seccion_boleto():
    return f'''<section id="boleto">
<div class="card c-lime">
<h2>Boleto de salida</h2>
<div class="meta"><span class="chip">{hora('Boleto a la vez')}</span>{A_LA_VEZ}</div>
<p>Las cuatro letras en orden, en el chat, todos al mismo tiempo. La cuarta es un rojo que no han visto.</p>
{preguntas('b9', BOLETO)}
</div>
</section>'''


def seccion_cierre():
    return f'''<section id="laminas">
<div class="card c-peach">
<h2>La S10 · <span class="acc">tus seis láminas</span></h2>
<p>{a_html(FORMATO_S10)}</p>
<p class="nota">{a_html(CREDITOS_NOTA)}</p>
<p><a class="boton enorme" href="{LAMINAS}">Abrir la plantilla de láminas</a><a class="boton blanco" href="{PROYECTO}#charla">La charla en el kit de proyecto</a></p>
</div>
<div class="card">
<h2>Cierre</h2>
<div class="meta"><span class="chip">{hora('CI en una captura')}</span></div>
<p>{a_html(CI_FRASE)}</p>
<p class="frase-grande">{a_html(FRASE_CIERRE)}</p>
<p class="nota">En el repo: la ficha de hoy en <a href="{REPO}/blob/main/docs/triage.md"><code>docs/triage.md</code></a>, los rojos en <code>tests/triage-s09/</code> y el registro de la corrida en <code>src/soporte/registro.ts</code>.</p>
</div>
</section>'''


CSS_EXTRA = """
/* S8: las líneas pegables */
.linea-chat { font:600 15px/1.5 var(--f-mono); background:var(--surface); border:2px dashed var(--ink); border-radius:10px; padding:8px 12px; margin:10px 0; overflow-wrap:anywhere; }
.linea-chat.molde { color:var(--muted); font-weight:400; }
.rescate { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:10px 14px; }
.rescate label { display:flex; flex-direction:column; gap:4px; font-weight:800; font-size:14px; min-width:0; }
.rescate .ancho { grid-column:1 / -1; }
.rescate input, .rescate select { font:16px var(--f-body); border:2px solid var(--ink); border-radius:8px; padding:6px 8px; background:var(--surface); color:var(--ink); min-width:0; width:100%; }
@media (min-width:641px) { .linea-rojo .rescate { grid-template-columns:minmax(0,1fr) minmax(0,3fr); } }
@media (max-width:640px) { .rescate { grid-template-columns:minmax(0,1fr); } }
a.chip { color:var(--ink); text-decoration:none; } a.chip:hover { background:var(--lav); }
a.boton.chico { padding:5px 11px; font-size:14px; box-shadow:2px 2px 0 var(--ink); }
/* S9: las cajas, los rojos y las capturas */
.caja { display:inline-block; border:2px solid var(--ink); border-radius:999px; padding:3px 12px; font:400 15px var(--f-display); text-transform:uppercase; letter-spacing:.03em; }
.k-sistema { background:var(--peach); } .k-script { background:var(--lav); } .k-ambiente { background:var(--cyan); }
.revelado .caja { font-size:20px; }
table.cajas td:first-child { width:9em; }
@media (max-width:820px) { table.cajas td:first-child { width:auto; } }
.rojo-n { background:var(--bad); color:#fff; border-color:var(--ink); }
.capturas { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:8px 0 12px; }
.capturas.n1 { grid-template-columns:minmax(0,1fr); }
.c-yel .capturas.n1, .c-peach .capturas.n1 { margin-bottom:6px; }
@media (max-width:820px) { .capturas { grid-template-columns:minmax(0,1fr); } }
figure.captura { margin:0; min-width:0; }
figure.captura figcaption { font-size:14px; margin-top:4px; }
button.ampliar { display:block; position:relative; width:100%; padding:0; margin:0; border:2px solid var(--ink); border-radius:10px; overflow:hidden; background:var(--surface); cursor:zoom-in; }
button.ampliar img { display:block; width:100%; height:auto; }
button.ampliar .lupa { position:absolute; right:6px; bottom:6px; background:var(--surface); border:2px solid var(--ink); border-radius:999px; padding:1px 8px; font-size:12px; }
button.ampliar:hover .lupa, button.ampliar:focus-visible .lupa { background:var(--neon); }
dialog.visor { width:min(96vw,1500px); max-height:94vh; padding:0; border:2px solid var(--ink); border-radius:14px; box-shadow:6px 6px 0 var(--ink); background:var(--surface); }
dialog.visor::backdrop { background:rgba(29,33,48,.72); }
.visor-barra { position:sticky; top:0; display:flex; gap:8px; align-items:center; justify-content:space-between; flex-wrap:wrap; padding:8px 12px; background:var(--yellow); border-bottom:2px solid var(--ink); }
.visor-cuerpo { overflow:auto; max-height:calc(94vh - 60px); }
.visor-cuerpo img { display:block; width:100%; height:auto; }
.visor-cuerpo.real img { width:auto; max-width:none; }
.visor-alt { padding:8px 12px; margin:0; font-size:14px; color:var(--muted); }
.sin-trace { border:2px dashed var(--ink); border-radius:10px; padding:8px 12px; background:var(--yellow); }
.revelado { border-top:2px solid var(--ink); margin-top:6px; padding-top:6px; }
.revelado dt { font-weight:800; color:var(--morado-osc); margin-top:8px; } .revelado dd { margin:2px 0 0; }
.criterio-listo { border:2px solid var(--ink); border-radius:10px; padding:8px 12px; margin:0; background:var(--surface); min-width:0; }
.criterio-listo legend { font-weight:800; font-size:14px; padding:0 4px; }
.check.chico { margin:4px 0; font-size:15px; }
td.pieza { width:12em; white-space:nowrap; } @media (max-width:820px) { td.pieza { width:auto; white-space:normal; } }
.linea-rojo { border-top:2px solid var(--ink); padding-top:8px; margin-top:8px; }
#salas a, #rojos a:not(.boton), .revelado a { color:var(--morado-osc); }
.sala-panel { margin-top:10px; }
.grid4 { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; } .grid4 > .card { margin:0; }
@media (max-width:980px) { .grid4 { grid-template-columns:minmax(0,1fr) minmax(0,1fr); } } @media (max-width:560px) { .grid4 { grid-template-columns:minmax(0,1fr); } }
.parte .paso { font-size:28px; }
.crono .reloj { font:400 clamp(56px,10vw,96px)/1 var(--f-display); margin:10px 0; font-variant-numeric:tabular-nums; color:var(--ink); }
.crono.poco .reloj { color:var(--bad); } .crono.fin { background:var(--peach); }
.crono-modo button[aria-pressed="true"] { background:var(--morado-osc); color:#fff; }
ol.tarjeta { padding-left:22px; font:400 clamp(17px,2.2vw,20px)/1.4 var(--f-display); } ol.tarjeta li { margin:8px 0; }
"""

JS = """
(function () {
  function guardar(clave, valor) { try { localStorage.setItem(clave, valor); } catch (e) {} }
  function recuperar(clave) { try { return localStorage.getItem(clave); } catch (e) { return null; } }
  function leerJSON(clave) { try { return JSON.parse(recuperar(clave) || 'null'); } catch (e) { return null; } }
  var DATOS = JSON.parse(document.getElementById('datos-s9').textContent);

  // Clasificadores (los mismos de la S5 a la S8), con Reiniciar
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
      if (resp && b) { resp.hidden = true; b.hidden = false; b.setAttribute('aria-expanded', 'false'); }
    });
  });
  document.querySelectorAll('[data-revelar]').forEach(function (boton) {
    boton.addEventListener('click', function () {
      var caja = document.getElementById(boton.getAttribute('data-revelar'));
      caja.hidden = false; boton.setAttribute('aria-expanded', 'true'); boton.hidden = true;
    });
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
  function llenar(molde, valores) { var i = 0; return molde.replace(/___/g, function () { var v = (valores[i++] || '').trim(); return v || '___'; }); }

  // ---------- La línea de llegada ----------
  var modo = document.getElementById('l-modo'), con = document.getElementById('l-con'), conCaja = document.getElementById('l-con-caja');
  var faltas = document.querySelectorAll('input.falta'), lineaLlegada = document.getElementById('llegada-linea');
  function armarLlegada() {
    conCaja.hidden = modo.value !== 'equipo';
    var quien = modo.value === 'individual' ? 'individual' : modo.value === 'equipo' ? 'en equipo con ' + (con.value.trim() || '___') : '___';
    var marcadas = []; faltas.forEach(function (c) { if (c.checked) marcadas.push(c.value); });
    var molde = DATOS.llegada.replace(/individual o en equipo con ___/, '@@');
    return llenar(molde, [marcadas.join(', ')]).replace('@@', quien);
  }
  function pintarLlegada() {
    lineaLlegada.textContent = armarLlegada();
    var marcadas = []; faltas.forEach(function (c) { if (c.checked) marcadas.push(c.value); });
    guardar('s9-llegada', JSON.stringify({ modo: modo.value, con: con.value, faltan: marcadas }));
  }
  var ll = leerJSON('s9-llegada');
  if (ll) { modo.value = ll.modo || ''; con.value = ll.con || ''; faltas.forEach(function (c) { c.checked = (ll.faltan || []).indexOf(c.value) > -1; }); }
  [modo, con].forEach(function (c) { c.addEventListener('input', pintarLlegada); c.addEventListener('change', pintarLlegada); });
  faltas.forEach(function (c) { c.addEventListener('change', pintarLlegada); });
  lineaLlegada.textContent = armarLlegada();
  document.getElementById('copiar-llegada').addEventListener('click', function () { copiar(armarLlegada(), document.getElementById('copiar-llegada-ok')); });

  // ---------- Las salas: un borrador por sala (s9-sala-1, s9-sala-2…) ----------
  var selSala = document.getElementById('s-sala'), estadoSala = document.getElementById('estado-sala');
  function clave(s) { return 's9-sala-' + s; }
  function lineaDe(sala, fila) {
    var n = fila.getAttribute('data-rojo');
    var caja = fila.querySelector('[data-campo="caja"]').value, ev = fila.querySelector('[data-campo="evidencia"]').value;
    return llenar(DATOS.moldeSala.replace('Sala X', 'Sala ' + sala).replace('rojo N', 'rojo ' + n), [caja, ev]);
  }
  function panel(s) { return document.querySelector('.sala-panel[data-sala="' + s + '"]'); }
  function pintarSala(s) { panel(s).querySelectorAll('.linea-rojo').forEach(function (f) { f.querySelector('[data-linea]').textContent = lineaDe(s, f); }); }
  function guardarSala(s) {
    var b = {};
    panel(s).querySelectorAll('.linea-rojo').forEach(function (f) {
      b[f.getAttribute('data-rojo')] = { caja: f.querySelector('[data-campo="caja"]').value, evidencia: f.querySelector('[data-campo="evidencia"]').value };
    });
    guardar(clave(s), JSON.stringify(b));
  }
  document.querySelectorAll('.sala-panel').forEach(function (p) {
    var s = p.getAttribute('data-sala'), b = leerJSON(clave(s)) || {};
    p.querySelectorAll('.linea-rojo').forEach(function (f) {
      var d = b[f.getAttribute('data-rojo')] || {};
      f.querySelector('[data-campo="caja"]').value = d.caja || '';
      f.querySelector('[data-campo="evidencia"]').value = d.evidencia || '';
      f.querySelectorAll('[data-campo]').forEach(function (c) {
        var cambio = function () { pintarSala(s); guardarSala(s); };
        c.addEventListener('input', cambio); c.addEventListener('change', cambio);
      });
      f.querySelector('[data-copiar-rojo]').addEventListener('click', function (ev) { copiar(lineaDe(s, f), ev.currentTarget.nextElementSibling); });
    });
    p.querySelector('[data-copiar-sala]').addEventListener('click', function (ev) {
      var lineas = []; p.querySelectorAll('.linea-rojo').forEach(function (f) { lineas.push(lineaDe(s, f)); });
      copiar(lineas.join('\\n'), ev.currentTarget.nextElementSibling);
    });
    pintarSala(s);
  });
  function abrirSala(s) {
    document.querySelectorAll('.sala-panel').forEach(function (p) { p.hidden = p.getAttribute('data-sala') !== s; });
    guardar('s9-sala', s);
    var b = leerJSON(clave(s)), algo = b && Object.keys(b).some(function (k) { return b[k].caja || b[k].evidencia; });
    estadoSala.textContent = (algo ? 'Su borrador de la Sala ' : 'La Sala ') + s + ': rojos ' + DATOS.salas[s].join(' y ') + '.';
  }
  var salaGuardada = recuperar('s9-sala');
  if (salaGuardada && DATOS.salas[salaGuardada]) selSala.value = salaGuardada;
  selSala.addEventListener('change', function () { abrirSala(selSala.value); });
  abrirSala(selSala.value);

  // ---------- Tu proyecto ----------
  var pc = ['p-cp', 'p-falla', 'p-caja', 'p-evidencia'].map(function (id) { return document.getElementById(id); });
  var lineaProyecto = document.getElementById('proyecto-linea');
  function armarProyecto() {
    var cp = pc[0].value.trim().toUpperCase();
    return llenar(DATOS.moldeProyecto, [pc[1].value, pc[2].value, pc[3].value]).replace(/^Mi CP/, 'Mi ' + (cp || 'CP'));
  }
  function pintarProyecto() { lineaProyecto.textContent = armarProyecto(); guardar('s9-proyecto', JSON.stringify(pc.map(function (c) { return c.value; }))); }
  var pg = leerJSON('s9-proyecto'); if (pg) pc.forEach(function (c, i) { if (pg[i] !== undefined) c.value = pg[i]; });
  pc.forEach(function (c) { c.addEventListener('input', pintarProyecto); c.addEventListener('change', pintarProyecto); });
  lineaProyecto.textContent = armarProyecto();
  document.getElementById('copiar-proyecto').addEventListener('click', function () { copiar(armarProyecto(), document.getElementById('copiar-proyecto-ok')); });

  // ---------- Las capturas: ampliar ----------
  var visor = document.getElementById('visor'), vImg = document.getElementById('visor-img'), vPie = document.getElementById('visor-pie');
  var vAlt = document.getElementById('visor-alt'), vCuerpo = document.getElementById('visor-cuerpo'), vReal = document.getElementById('visor-real');
  var origen = null;
  document.querySelectorAll('[data-ampliar]').forEach(function (b) {
    b.addEventListener('click', function () {
      var img = b.querySelector('img'); origen = b;
      vImg.src = img.src; vImg.alt = img.alt; vPie.textContent = b.getAttribute('data-pie'); vAlt.textContent = img.alt;
      vCuerpo.classList.remove('real'); vReal.setAttribute('aria-pressed', 'false');
      if (visor.showModal) visor.showModal(); else visor.setAttribute('open', '');
    });
  });
  function cerrarVisor() { if (visor.close) visor.close(); else visor.removeAttribute('open'); }
  document.getElementById('visor-cerrar').addEventListener('click', cerrarVisor);
  visor.addEventListener('click', function (ev) { if (ev.target === visor) cerrarVisor(); });
  visor.addEventListener('close', function () { if (origen) origen.focus(); });
  vReal.addEventListener('click', function () { var r = vCuerpo.classList.toggle('real'); vReal.setAttribute('aria-pressed', r ? 'true' : 'false'); });

  // ---------- El cronómetro del ensayo ----------
  var reloj = document.getElementById('reloj'), crono = document.getElementById('crono'), aviso = document.getElementById('crono-aviso');
  var bIniciar = document.getElementById('crono-iniciar'), duracion = 90, queda = 90, fin = 0, tic = null;
  function mmss(s) { return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2); }
  function pintar() {
    reloj.textContent = mmss(queda);
    crono.classList.toggle('poco', queda <= 10 && queda > 0); crono.classList.toggle('fin', queda === 0);
  }
  function parar() { clearInterval(tic); tic = null; bIniciar.textContent = queda > 0 && queda < duracion ? 'Seguir' : 'Iniciar'; }
  function paso() {
    var antes = queda;
    queda = Math.max(0, Math.ceil((fin - Date.now()) / 1000));
    if (queda !== antes) {
      pintar();
      if (duracion > 30 && antes > 30 && queda <= 30 && queda > 0) aviso.textContent = 'Quedan 30 segundos.';
      if (queda === 0) { aviso.textContent = '¡Tiempo!'; parar(); }
    }
  }
  bIniciar.addEventListener('click', function () {
    if (tic) { parar(); aviso.textContent = 'En pausa: quedan ' + queda + ' segundos.'; return; }
    if (queda === 0) queda = duracion;
    fin = Date.now() + queda * 1000; aviso.textContent = 'Corriendo: ' + queda + ' segundos.';
    tic = setInterval(paso, 200); bIniciar.textContent = 'Pausar'; pintar();
  });
  function reiniciar() { parar(); queda = duracion; aviso.textContent = ''; pintar(); bIniciar.textContent = 'Iniciar'; }
  document.getElementById('crono-reiniciar').addEventListener('click', reiniciar);
  document.querySelectorAll('[data-dur]').forEach(function (b) {
    b.addEventListener('click', function () {
      duracion = parseInt(b.getAttribute('data-dur'), 10);
      document.querySelectorAll('[data-dur]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      reiniciar();
    });
  });
  pintar();
  document.getElementById('preg-limpiar').addEventListener('click', function () { document.querySelectorAll('input.preg-ensayo').forEach(function (c) { c.checked = false; }); });
})();
"""

NAV = ''.join(f'<a href="#{a}">{t}</a>' for a, t in [
    ('llegada', 'Llegada'), ('ficha', 'Las tres cajas'), ('en-que-caja', '¿En qué caja?'), ('mirame', 'Mírame'), ('sin-instalar', 'Sin instalar'),
    ('rojos', 'Los 4 rojos'), ('salas', 'Salas'), ('proyecto', 'Tu proyecto'), ('modelo', 'El modelo'), ('ensayo', 'Ensayo'),
    ('boleto', 'Boleto'), ('laminas', 'Láminas S10')]) + f'<a href="{CPS_PAGINA}" style="background:var(--neon)">📋 Los CP</a>'

ENLACES = [('Los CP del curso', CPS_PAGINA, ''), ('Reporte del triage', REPORTE_TRIAGE, ' blanco'), ('Plantilla de láminas', LAMINAS, ' blanco'),
           ('Kit de proyecto', PROYECTO, ' blanco'), ('Actividades S8', ACTIVIDADES_S8, ' blanco'), ('Guía de estudio', GUIA, ' blanco')]
enlaces_html = ''.join(f'<a class="boton{c}" href="{u}">{t}</a>' for t, u, c in ENLACES)

DATOS = json.dumps({
    'llegada': MOLDE_LLEGADA, 'moldeSala': MOLDE_SALA, 'moldeProyecto': MOLDE_PROYECTO,
    'salas': {s.split()[-1]: ns for s, ns in SALAS},
}, ensure_ascii=False).replace('</', '<\\/')


def construir():
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Actividades S9 Triage</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&amp;family=Nunito:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;600&amp;display=swap" rel="stylesheet">
<style>{css_de_la_s7() + CSS_EXTRA}</style>
</head>
<body>
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · S9 · {e(TEMA)}</small></div>
<h1>¿Rojo del <span class="acc">sistema</span>, del <span class="acc">script</span> o del <span class="acc">ambiente</span>?</h1>
<p class="idea">{a_html(IDEA_FUERZA)}</p>
<div class="card c-lime objetivo"><b class="k">Objetivo de hoy</b> <span class="frase-grande" style="margin:0">{a_html(OBJETIVO)}</span></div>
<div class="card c-cyan">
<p style="margin-top:0"><b>Abran estos enlaces y respondan en el chat ✅ si cargan o ❌ si alguno no carga (digan cuál):</b></p>
{enlaces_html}
<p class="nota">Todo funciona sin instalar nada. Si GitHub no abre en su red, el instructor sube los archivos al chat: se abren con doble clic en Edge, y las capturas van dentro de la página.</p>
</div>
<nav class="top" aria-label="Actividades">{NAV}</nav>

{seccion_llegada()}
{seccion_ficha()}
{seccion_en_que_caja()}
{seccion_mirame()}
{seccion_sin_instalar()}
{seccion_rojos()}
{seccion_salas()}
{seccion_proyecto()}
{seccion_modelo()}
{seccion_ensayo()}
{seccion_boleto()}
{seccion_cierre()}
<p class="nota">Página de práctica del Bootcamp QA · Knot Academy, generada con <code>laboratorio/generar/generar_actividades_s9.py</code>. No carga nada de internet salvo las fuentes. Los datos son de práctica: nunca escriban aquí datos, pantallas ni casos del banco. Lo que escriban queda solo en este navegador.</p>
</div>
<dialog class="visor" id="visor" aria-labelledby="visor-pie">
<div class="visor-barra"><b id="visor-pie"></b><span><button type="button" id="visor-real" aria-pressed="false">Tamaño real</button><button type="button" class="grande" id="visor-cerrar">Cerrar</button></span></div>
<div class="visor-cuerpo" id="visor-cuerpo"><img id="visor-img" alt="" data-impeccable-ignore="broken-image"></div>
<p class="visor-alt" id="visor-alt"></p>
</dialog>
<script type="application/json" id="datos-s9">{DATOS}</script>
<script>{JS}</script>
</body>
</html>
'''


# ─────────────────────────── docs/triage.md ───────────────────────────
def sin_html(linea):
    """En GitHub, un <marcador> suelto se lee como etiqueta de HTML y desaparece: fuera de `código` va como &lt;marcador&gt;."""
    return '`'.join(p if k % 2 else p.replace('<', '&lt;').replace('>', '&gt;') for k, p in enumerate(linea.split('`')))


def markdown():
    md = ['# Triage de fallas: ¿rojo del sistema, del script o del ambiente? (S9)', '',
          'Construye sobre las capas de la S3 (ver [arquitectura.md](arquitectura.md)), la configuración y los localizadores de la S6 '
          '(ver [configuracion-y-localizadores.md](configuracion-y-localizadores.md)) y el reporte de la S8 (ver [datos-y-reportes.md](datos-y-reportes.md)). '
          'Este archivo lo genera `laboratorio/generar/generar_actividades_s9.py` desde `fichas_s9.py`, la misma fuente de las actividades y del deck: si cambias algo, cámbialo allí. '
          'Los mensajes de error son los reales: se leen del reporte del triage (`npm run triage:generar`).', '',
          f'**{IDEA_FUERZA}**', '', f'Objetivo de la sesión: {OBJETIVO}', '',
          f'> {FRASE_REGLA}', '',
          '| Pieza | Dónde verla |', '|---|---|',
          '| Los 4 rojos (proyecto `triage`, solo corre si se pide) | `tests/triage-s09/` · `npx.cmd playwright test --project=triage` |',
          '| El registro de la corrida (`test.info().attach`) | `src/soporte/registro.ts` |',
          '| El bug conocido, registrado (la falla esperada) | `src/soporte/hallazgos.ts` |',
          '| El `throw` de la configuración (falla de inmediato) | `src/config/ambientes.ts` |',
          f'| El reporte con los traces | [{REPORTE_TRIAGE}]({REPORTE_TRIAGE}) |',
          f'| Las actividades de la clase | [{PAGES}actividades-s9.html]({PAGES}actividades-s9.html) |', '',
          f'## {FICHA["titulo"]}', '', '| | |', '|---|---|']
    md += [f'| **{et}** | {FICHA[k]} |' for k, et in FILAS]
    md += ['', '## Las tres cajas', '', '| La caja | Qué es | Cómo se ve el mensaje | A quién va el ticket |', '|---|---|---|---|']
    md += [f'| **{c}** | {q} | {v} | {t} |' for c, q, v, t in CAJAS]
    md += ['', '## Los 4 rojos', '']
    for r in ROJOS:
        n = r['n']
        md += [f'### Rojo {n} · {r["titulo"]} · caja: **{r["caja"]}**', '',
               '```', MENSAJE[n], '```', '',
               f'- **Cómo se provoca.** {r["como"]}',
               f'- **La evidencia.** {r["evidencia"]}',
               f'- **Lo que se aprende.** {r["aprende"]}',
               f'- **Lo ven:** {" y ".join(SALAS_DE[n])}.']
        capt = ' · '.join(f'[{rot}]({TRIAGE_PAGES}capturas/{nom})' for nom, rot, _ in CAPTURAS[n])
        md += [f'- **Capturas:** {capt}' + ('' if n == 3 else f' · [el trace]({TRIAGE_PAGES}traces/rojo{n}.zip) (zip, para trace.playwright.dev)'), '']
    md += ['## Las salas', '', SALAS_NOTA, '', '| Sala | Rojos |', '|---|---|']
    md += [f'| {s} | {" y ".join(str(n) for n in ns)} |' for s, ns in SALAS]
    md += ['', f'La línea pegable: `{LINEA_SALA}`', '', ROLES_SALA, '',
           '## El mírame', '', '| Qué | El comando | Qué se ve |', '|---|---|---|']
    md += [f'| {q} | {c} | {v} |' for q, c, v in MIRAME]
    md += ['', f'> {FRASE_FLAKY}', '', '## En una línea', '', '| La pieza | En una línea |', '|---|---|']
    md += [f'| {p} | {t} |' for p, t in UNA_LINEA]
    md += ['', '## Las frases y de dónde salen', '']
    md += [f'- {f} ({u})' for f, u in FUENTES_FRASES]
    md += ['', '## Tu proyecto', '', PROYECTO_S9, '', PROYECTO_ESPECIFICADOR, '', '## Fuentes', '']
    md += [f'- {f}' for f in FUENTES]
    md.append('')
    salida, en_bloque = [], False
    for l in md:
        for sub in l.split('\n'):
            if sub.startswith('```'):
                en_bloque = not en_bloque
                salida.append(sub)
            else:
                salida.append(sub if en_bloque else '> ' + sin_html(sub[2:]) if sub.startswith('> ') else sin_html(sub))
    return '\n'.join(salida)


# ─────────────────────────── Salida ───────────────────────────
RELATIVO = re.compile(r'(?:href|src)="(?!https?://|#|data:)([^"]+)"')

if __name__ == '__main__':
    HTML = construir()
    assert not RELATIVO.findall(HTML), f'Enlaces relativos (no funcionan con doble clic): {RELATIVO.findall(HTML)}'
    assert 'claude.ai' not in HTML, 'Enlace de claude.ai'
    salida = RAIZ / 'laboratorio' / 'actividades_S9.html'
    salida.write_text(HTML, encoding='utf-8')
    if PARA_ENVIAR.is_dir():
        shutil.copyfile(salida, PARA_ENVIAR / 'actividades_S9.html')
    (RAIZ / 'docs' / 'triage.md').write_text(markdown(), encoding='utf-8')
    print(f'actividades_S9.html ({len(HTML) // 1024} KB, {sum(len(v) for v in CAPTURAS.values())} capturas incrustadas) y docs/triage.md listos; '
          f'copia en para_enviar: {PARA_ENVIAR.is_dir()}')
