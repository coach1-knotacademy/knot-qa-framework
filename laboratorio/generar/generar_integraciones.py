"""Genera laboratorio/integraciones.html (en Pages: integraciones.html): el kit «del ticket a la prueba, y del reporte al ticket».

Usa el mismo molde visual que proyecto.html (generar_proyecto.py). Deja una copia en ../para_enviar/ con los enlaces
completos de Pages. El ejemplo del ensayo de reportar-a-trello.js se lee de verdad: se corre el script en modo ensayo.

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_integraciones.py
"""
import html, re, subprocess, sys
from pathlib import Path

D = Path(__file__).parent
sys.path.insert(0, str(D))
from generar_proyecto import pagina, boton_copiar, revelar, RAIZ, PARA_ENVIAR, enlace
from fichas_s7 import PAGES  # noqa: E402
from fichas_s6 import a_html  # noqa: E402

e = lambda t: html.escape(t, quote=True)
TABLERO = 'https://trello.com/b/d6wfT3VM/bootcamp-qa-casos-para-automatizar'
REPO = 'https://github.com/coach1-knotacademy/knot-qa-framework'

PASOS = [
  ('1 · El caso vive en el tablero', 'Una tarjeta por CP: el ID en el título (`CP-501 · …`) y el escenario en Gherkin en la descripción. Es lo mismo que una historia en Jira con su caso en Xray.', 'lav'),
  ('2 · La IA lo lee por MCP', 'El asistente se conecta al tablero con un servidor **MCP** y lee la tarjeta: no hay que copiar y pegar.', 'cyan'),
  ('3 · La IA escribe la prueba', 'Con el prompt de la plantilla (`PROMPT.md`): las capas, localizadores por rol, datos de la fábrica, la URL del entorno, **sin inventar el esperado**. Tú la lees con la lista de cotejo.', 'lime'),
  ('4 · La prueba corre', 'En tu equipo (`npx.cmd playwright test -g "CP-501"`) o en GitHub Actions en cada cambio (`.github/workflows/pruebas.yml`).', 'yel'),
  ('5 · El resultado vuelve al ticket', '`node scripts/reportar-a-trello.js --publicar` comenta el resultado en la tarjeta del CP y la mueve a «Verde» o a «Rojo». El líder ve el estado sin abrir el reporte.', 'peach'),
]

MCP = [
  ('Playwright MCP', 'Microsoft', 'La IA maneja un navegador real por el árbol de accesibilidad (los mismos roles y nombres de la escalera). Sirve para explorar una pantalla y proponer localizadores.'),
  ('GitHub MCP', 'GitHub', 'La IA lee issues y pull requests, y el estado de las corridas de Actions.'),
  ('Atlassian (Jira y Confluence)', 'Atlassian', 'La IA lee la historia y sus criterios de aceptación en Jira, o la documentación en Confluence.'),
  ('Trello', 'conector de Trello', 'La IA lee y escribe tarjetas: es el que usa la demo del curso.'),
]

PROMPT_LEER = """Eres un QA que automatiza con Playwright y TypeScript en el framework de este repositorio (capas: tests/, src/paginas/, src/datos/, src/config/, src/soporte/).
1. Lee en el tablero «Bootcamp QA · Casos para automatizar» la tarjeta CP-501.
2. Escribe la prueba en tests/toolshop/ siguiendo PROMPT.md: el ID en el título y en { tag: '@CP-501' }, un test.step por cada paso del escenario, localizadores por rol o etiqueta dentro del Page Object, datos de la fábrica y la URL del entorno.
3. No inventes el resultado esperado: si la tarjeta no lo dice, escribe // TODO: confirmar con negocio.
4. Al final, lista lo que supusiste."""

PROMPT_REPORTAR = """Corre la prueba del CP-501 y, con el resultado, comenta en la tarjeta CP-501 del tablero: estado (verde o rojo), duración y, si falló, la primera línea del error y si parece rojo del sistema, del script o del ambiente. Mueve la tarjeta a la lista que corresponda. No pegues datos personales ni claves en el comentario."""

JIRA = [
  ('El CP', 'Tarjeta con `CP-501` en el título', 'Un *Test* de Xray (o una historia con su caso)'),
  ('El escenario', 'La descripción, en Gherkin', 'El *Test* tipo Cucumber de Xray, o el campo de criterios de aceptación'),
  ('La IA lee el caso', 'Conector MCP de Trello', 'Servidor MCP de Atlassian (si tu organización lo permite)'),
  ('El resultado', '`reportar-a-trello.js` comenta y mueve', 'Se importa el reporte (JUnit XML: reporter `junit` de Playwright) a una *Test Execution* de Xray, por API o desde el pipeline'),
  ('Dónde corre', 'Tu equipo o GitHub Actions', 'El pipeline de tu equipo (Azure DevOps, Jenkins, GitHub Actions)'),
]

REGLAS = [
  'Conecta la IA solo a tableros y repos **de práctica**, o a los de tu trabajo **si tu organización lo autoriza** y con el asistente aprobado. Nunca pegues tickets, datos ni pantallas de un cliente en una IA no aprobada.',
  'Las claves (`TRELLO_KEY`, `TRELLO_TOKEN`, tokens de Jira o GitHub) van en `.env` o en los secretos del pipeline. Nunca en el código, en el ticket ni en el chat.',
  'La IA escribe el *cómo*; el *esperado* lo decide una persona. Si la tarjeta no tiene esperado, la prueba no se inventa uno.',
  'El comentario automático no lleva datos personales: estado, duración, primera línea del error y enlace al reporte.',
  'En Copilot de VS Code, los servidores MCP se usan en el modo agente y tu organización puede tenerlos deshabilitados por política: pregunta antes a TI.',
]


def ensayo():
    """Corre el reportero en modo ensayo para mostrar una salida real (si hay resultados.json)."""
    try:
        r = subprocess.run(['node', 'scripts/reportar-a-trello.js'], cwd=RAIZ, capture_output=True, text=True, timeout=30)
        salida = (r.stdout or r.stderr).strip()
        salida = re.sub(r'\d{4}-\d\d-\d\dT[\d:.]+Z', '2026-11-26T00:00:00Z', salida)
        lineas = salida.split('\n')
        return '\n'.join(lineas[:18]) + ('\n…' if len(lineas) > 18 else '')
    except Exception as ex:  # noqa: BLE001
        return f'(no se pudo correr el ensayo: {ex})'


def integraciones(base):
    s = lambda r: enlace(r, base)
    pasos = ''.join(f'<div class="card c-{c}" style="margin:0"><p class="paso">{e(t)}</p><p style="margin:0">{a_html(d)}</p></div>' for t, d, c in PASOS)
    mcp = ''.join(f'<tr><td data-k="Servidor"><b>{e(n)}</b></td><td data-k="De quién">{e(q)}</td><td data-k="Para qué">{a_html(d)}</td></tr>' for n, q, d in MCP)
    jira = ''.join(f'<tr><td><b>{e(a)}</b></td><td data-k="En el curso (Trello)">{a_html(b)}</td><td data-k="En tu trabajo (Jira + Xray)">{a_html(c)}</td></tr>' for a, b, c in JIRA)
    reglas = ''.join(f'<li>{a_html(r)}</li>' for r in REGLAS)
    cuerpo = f'''
<h1>Del ticket a la prueba, <span class="acc">y del reporte al ticket</span></h1>
<p class="lead">Tus casos ya viven en una herramienta (Jira, Xray, Trello, Azure). Este kit conecta esa herramienta con el framework: la IA lee el caso, escribe la prueba, la prueba corre y el resultado vuelve al ticket. Lo que cambia en tu trabajo: el estado de la regresión se ve donde ya mira el líder.</p>
<div class="rotulo">Objetivo: entender el flujo completo y poder repetirlo con la herramienta de tu equipo. Sin instalar nada: lo ves con el tablero del curso. Con Node: corres el reportero.</div>

<section id="flujo">
<h2>El flujo, <span class="acc">en cinco pasos</span></h2>
<div class="grid2">{pasos}</div>
</section>

<section id="mcp">
<div class="card">
<h2 style="margin-top:0">¿Qué es <span class="acc">MCP</span>?</h2>
<p>El <b>Model Context Protocol</b> es un estándar abierto para que un asistente de IA use herramientas de afuera con permisos: leer un ticket, abrir un navegador, consultar un repositorio. Cada herramienta ofrece un <b>servidor MCP</b>; el asistente (Copilot en modo agente, Claude u otro) se conecta a él. Sin MCP, copias y pegas el caso en el chat; con MCP, la IA lo lee del sistema donde vive.</p>
<table class="apilar"><thead><tr><th>Servidor MCP</th><th>De quién</th><th>Para qué en QA</th></tr></thead><tbody>{mcp}</tbody></table>
</div>
</section>

<section id="tablero">
<h2>El tablero <span class="acc">del curso</span></h2>
<p>«Bootcamp QA · Casos para automatizar», en Trello, con cuatro listas: <b>Por automatizar</b> → <b>En automatización</b> → <b>Verde</b> / <b>Rojo: hallazgo</b> (sistema, script o ambiente). Cada tarjeta es un CP de los kits (tienda, móvil, voz) con su escenario en Gherkin.</p>
<p><a class="boton" href="{TABLERO}">Abrir el tablero</a> <span class="nota">Es privado: el instructor lo muestra en pantalla, o te invita si lo pides.</span></p>
</section>

<section id="prompts">
<h2>Los prompts, <span class="acc">listos para copiar</span></h2>
<div class="card">
<p class="paso">paso 2 y 3 · que la IA lea el caso y escriba la prueba</p>
<pre class="code prosa" id="p-leer">{e(PROMPT_LEER)}</pre>
<p>{boton_copiar("p-leer")}</p>
</div>
<div class="card">
<p class="paso">paso 5 · que la IA reporte el resultado al ticket</p>
<pre class="code prosa" id="p-reportar">{e(PROMPT_REPORTAR)}</pre>
<p>{boton_copiar("p-reportar")}</p>
</div>
</section>

<section id="reportero">
<h2>Sin IA: <span class="acc">el reportero</span></h2>
<p>El paso 5 también se puede hacer con un script, que es lo que corre en un pipeline: <code>scripts/reportar-a-trello.js</code> lee <code>resultados.json</code> (el reporte JSON que ya genera Playwright), junta las pruebas por su <code>@CP-xxx</code> y comenta en la tarjeta cuyo título empieza con ese ID.</p>
<pre class="code">npx.cmd playwright test --project=toolshop
node scripts/reportar-a-trello.js              # ENSAYO: muestra lo que haría, no toca Trello
node scripts/reportar-a-trello.js --publicar   # publica: TRELLO_KEY, TRELLO_TOKEN y TRELLO_TABLERO en .env</pre>
{revelar("ensayo", "Ver una salida real del ensayo", '<pre class="code">' + e(ensayo()) + '</pre>')}
</section>

<section id="jira">
<h2>Lo mismo con <span class="acc">Jira y Xray</span></h2>
<table class="apilar"><thead><tr><th></th><th>En el curso (Trello)</th><th>En tu trabajo (Jira + Xray)</th></tr></thead><tbody>{jira}</tbody></table>
<p class="nota">La idea es la misma: el ID del caso es el puente. Por eso desde la S3 va en el título de la prueba y desde la S7 en la etiqueta del escenario.</p>
</section>

<section id="reglas">
<div class="card c-yel">
<h2 style="margin-top:0">Las <span class="acc">reglas</span></h2>
<ul class="lista">{reglas}</ul>
</div>
</section>

<section id="enlaces">
<h2>Lo que <span class="acc">vas a usar</span></h2>
<ul class="lista">
<li><a href="{s("plantilla.html")}">La plantilla y su PROMPT.md</a></li>
<li><a href="{s("web-real.html")}">El kit web real (los CP-501… de la tienda)</a></li>
<li><a href="{s("proyecto.html")}">El kit de tu proyecto</a></li>
<li><a href="{REPO}/blob/main/scripts/reportar-a-trello.js">reportar-a-trello.js en el repo</a></li>
<li><a href="{REPO}/blob/main/.github/workflows/pruebas.yml">El pipeline del curso (GitHub Actions)</a></li>
</ul>
</section>'''
    return pagina('Integraciones · del ticket a la prueba', 'kit de integraciones', cuerpo, generador='generar_integraciones.py')


if __name__ == '__main__':
    RELATIVO = re.compile(r'href="(?!https?://|#|data:)([^"]+)"')
    (RAIZ / 'laboratorio' / 'integraciones.html').write_text(integraciones(''), encoding='utf-8')
    local = integraciones(PAGES)
    assert not RELATIVO.findall(local), RELATIVO.findall(local)
    assert 'claude.ai' not in local
    if PARA_ENVIAR.is_dir():
        (PARA_ENVIAR / 'integraciones.html').write_text(local, encoding='utf-8')
    print('integraciones.html listo (y su copia en para_enviar/)')
