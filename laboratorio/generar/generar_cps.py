"""Genera laboratorio/cps.html (en Pages: cps.html): TODOS los casos de prueba del curso en una sola página.

Para que en clase siempre se sepa de qué CP se habla: el Banco Demo (CP-101 a CP-106, con la sala de cada uno en la S7)
y los kits (tienda CP-501…, voz CP-301…, móvil CP-401…). Los CP del Banco Demo se muestran como caso manual (no
la solución en Gherkin: esa es la práctica de las salas); los de los kits se leen de sus .feature.

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_cps.py
"""
import html, re, sys
from pathlib import Path

D = Path(__file__).parent
sys.path.insert(0, str(D))
from generar_proyecto import pagina, RAIZ, PARA_ENVIAR, enlace  # noqa: E402
from fichas_s7 import PAGES, CPS as CPS_S7, a_html  # noqa: E402
from fichas_s8 import SALAS as SALAS_S8, CP_NUEVO  # noqa: E402

e = lambda t: html.escape(t, quote=True)
SALA = {'CP-102': 'Sala 1', 'CP-103': 'Sala 2', 'CP-104': 'Sala 3', 'CP-105': 'Sala 4', 'CP-106': 'Sala 5'}
# S8: cada sala hace la tabla de Ejemplos de un CP (fichas_s8.SALAS). El CP-107 es nuevo en la S8.
SALA_S8 = {s['id']: s for s in SALAS_S8}
CPS = CPS_S7 + [CP_NUEVO] if CP_NUEVO['id'] not in {c['id'] for c in CPS_S7} else CPS_S7
assert all(cp in {c['id'] for c in CPS} for cp in SALA_S8), 'Una sala de la S8 tiene un CP que no está en la lista'


def escenarios(ruta):
    """Devuelve [(id, título, texto Gherkin)] de un .feature, un bloque por etiqueta @CP-xxx."""
    lineas = (RAIZ / ruta).read_text(encoding='utf-8').split('\n')
    salida, actual = [], None
    for l in lineas:
        t = l.strip()
        if t.startswith('@') and re.search(r'@CP-\d+', t) and len(re.findall(r'@CP-\d+', t)) == 1:
            actual = {'id': re.search(r'CP-\d+', t).group(0), 'lineas': [t]}
            salida.append(actual)
            continue
        if actual is None:
            continue
        if t.startswith('#') or (not t and len(actual['lineas']) > 2 and not actual['lineas'][-1]):
            continue
        if t.startswith('@'):
            actual = None
            continue
        actual['lineas'].append(t if t.startswith(('Escenario', 'Esquema')) else '  ' + t if t else '')
    res = []
    for s in salida:
        cuerpo = '\n'.join(x for x in s['lineas']).strip()
        titulo = next((x.split(':', 1)[1].strip() for x in s['lineas'] if x.startswith('Escenario')), '')
        res.append((s['id'], titulo, cuerpo))
    return res


def tabla_voz():
    """Los CP de voz están en un Esquema del escenario: se muestra la tabla de Ejemplos."""
    texto = (RAIZ / 'especificaciones/cobranza-voz.feature').read_text(encoding='utf-8')
    filas = [l.strip() for l in texto.split('\n') if l.strip().startswith('|')]
    cab = [c.strip() for c in filas[0].strip('|').split('|')]
    cuerpo = [[c.strip() for c in f.strip('|').split('|')] for f in filas[1:]]
    pasos = [l.strip() for l in texto.split('\n') if re.match(r'\s*(Dado|Cuando|Entonces|Y)\b', l)]
    return cab, cuerpo, pasos


def cps(base):
    s = lambda r: enlace(r, base)
    def salas_de(cid):
        partes = [f'<span class="sala">{SALA[cid]} en la S7</span>'] if cid in SALA else []
        partes += [f'<span class="sala">{SALA_S8[cid]["sala"]} en la S8</span>'] if cid in SALA_S8 else []
        partes += ['<span class="sala">nuevo en la S8</span>'] if cid == CP_NUEVO['id'] else []
        return ''.join(' · ' + x for x in partes)

    def ejemplos_s8(cid):
        """La tabla de Ejemplos que la sala de la S8 convierte en pruebas (los datos, no la solución en Gherkin)."""
        if cid not in SALA_S8:
            return ''
        s8 = SALA_S8[cid]
        return (f'<p class="paso" style="margin-top:12px">{s8["sala"]} en la S8 · su tabla de Ejemplos</p>'
                '<table class="ejemplos"><thead><tr>' + ''.join(f'<th>{e(c)}</th>' for c in s8['columnas']) + '</tr></thead><tbody>'
                + ''.join('<tr>' + ''.join(f'<td>{e(v)}</td>' for v in f) + '</tr>' for f in s8['filas']) + '</tbody></table>'
                f'<p class="nota">{len(s8["filas"])} filas: salen {len(s8["filas"])} pruebas, una por fila, con el mismo «Entonces».</p>')

    banco = ''.join(
        f'<article class="card cp" id="{c["id"]}"><p class="paso">{c["id"]}{salas_de(c["id"])}</p>'
        f'<h3>{e(c["titulo"])}</h3><p><b>Precondición:</b> {a_html(c["pre"])}</p>'
        f'<ol>{"".join(f"<li>{a_html(p)}</li>" for p in c["pasos"])}</ol><p><b>Esperado:</b> {a_html(c["esperado"])}</p>'
        + (f'<p class="nota">{a_html(c["nota"])}</p>' if c.get('nota') else '') + ejemplos_s8(c['id']) + '</article>'
        for c in CPS)
    salas_s8 = ' · '.join(f'{s8["sala"]} {s8["id"]}' for s8 in SALAS_S8)

    def bloque(ruta):
        return ''.join(f'<article class="card cp" id="{i}"><p class="paso">{i}</p><h3>{e(t)}</h3><pre class="code">{e(g)}</pre></article>'
                       for i, t, g in escenarios(ruta))

    cab, filas, pasos = tabla_voz()
    voz = ('<div class="card"><p class="paso">los pasos (los mismos para las 6 llamadas)</p><pre class="code">' + e('\n'.join(pasos)) + '</pre>'
           '<table class="apilar"><thead><tr>' + ''.join(f'<th>{e(c)}</th>' for c in cab) + '</tr></thead><tbody>'
           + ''.join('<tr id="' + e(f[0]) + '">' + ''.join(f'<td data-k="{e(cab[k])}">{e(v)}</td>' for k, v in enumerate(f)) + '</tr>' for f in filas)
           + '</tbody></table><p class="nota">El CP-305 está en rojo a propósito: el agente no avisa que la llamada se graba (VOZ-01).</p></div>')

    indice = ' '.join(f'<a href="#{c["id"]}">{c["id"]}</a>' for c in CPS)
    cuerpo = f'''
<h1>Los casos <span class="acc">de prueba</span></h1>
<p class="lead">Todos los CP del curso en una sola página, para saber siempre de qué caso se habla. Déjala abierta en una pestaña durante la clase.</p>
<div class="rotulo">Son casos de sistemas de práctica. Nunca se usan casos del ALM del banco.</div>
<nav class="top" aria-label="Casos"><a href="#banco">Banco Demo · CP-101 a CP-107</a><a href="#tienda">Tienda · CP-501 a CP-507</a><a href="#voz">Voz · CP-301 a CP-306</a><a href="#movil">Móvil · CP-401 a CP-404</a></nav>

<section id="banco">
<h2>Banco Demo · <span class="acc">recargas</span></h2>
<p>Los de la S6 a la S8. En la S7 cada sala escribe el suyo en Gherkin: <b>Sala 1 CP-102 · Sala 2 CP-103 · Sala 3 CP-104 · Sala 4 CP-105 · Sala 5 CP-106</b>. En la S8 cada sala convierte una tabla de Ejemplos en pruebas: <b>{salas_s8}</b>. El CP-101 es el modelo resuelto. Ir a: {indice}</p>
<p><a class="boton" href="{s("banco/recargas.html")}">Abrir Recargas en el Banco Demo</a> <span class="nota">usuario <code>ana</code> · clave <code>Clave123</code> · el código solo sale para más de $50.000</span></p>
<div class="grid2">{banco}</div>
</section>

<section id="tienda">
<h2>Tienda · <span class="acc">kit web real</span></h2>
<p>Practice Software Testing, una tienda pública hecha para practicar. <a href="{s("web-real.html")}">Abrir el kit</a> · <a href="https://practicesoftwaretesting.com">abrir la tienda</a></p>
<div class="grid2">{bloque("especificaciones/toolshop.feature")}</div>
</section>

<section id="voz">
<h2>Voz · <span class="acc">agente de cobranza</span></h2>
<p>Un Esquema del escenario: los pasos se escriben una vez y cada fila es un CP. <a href="{s("voz.html")}">Abrir el kit (escuchar las llamadas)</a></p>
{voz}
</section>

<section id="movil">
<h2>Móvil · <span class="acc">kit Appium</span></h2>
<p>La SauceLabs My Demo App (Android, pública, hecha para practicar). <a href="{s("movil.html")}">Abrir el kit</a></p>
<div class="grid2">{bloque("movil/especificaciones/tienda.feature")}</div>
</section>'''
    return pagina('Los casos de prueba', 'los CP del curso', cuerpo, generador='generar_cps.py')


if __name__ == '__main__':
    RELATIVO = re.compile(r'href="(?!https?://|#|data:)([^"]+)"')
    (RAIZ / 'laboratorio' / 'cps.html').write_text(cps(''), encoding='utf-8')
    local = cps(PAGES)
    assert not RELATIVO.findall(local), RELATIVO.findall(local)
    if PARA_ENVIAR.is_dir():
        (PARA_ENVIAR / 'cps.html').write_text(local, encoding='utf-8')
    print('cps.html listo (y su copia en para_enviar/)')
