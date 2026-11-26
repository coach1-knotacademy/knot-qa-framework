"""Genera laboratorio/movil.html: el kit móvil para participantes (Appium + WebdriverIO + TypeScript sobre una app pública de práctica).

No corre nada en el navegador: explica las piezas de Appium, muestra el código REAL del kit (leído de movil/src y movil/tests),
la escalera de localizadores móviles, la demo grabada (capturas y video de una corrida real) y la Rosetta TypeScript ↔ Java.
Las tablas de la escalera, los casos y la Rosetta salen de movil/README.md: si cambia una fila, se cambia allí.

En Pages se publica como movil.html, con la demo en movil/evidencias/demo/ del sitio (rutas relativas).
La copia de ../para_enviar/movil.html lleva esas rutas y los enlaces del sitio con la dirección completa de Pages,
para que funcione con doble clic. No carga nada de internet salvo las fuentes de Google (y si no cargan se usan las del sistema).
El CSS y los tokens son los de proyecto.html (generar_proyecto.py) y el logo, el de la plantilla.

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_movil.py
"""
import html, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
MOVIL = RAIZ / 'movil'
sys.path.insert(0, str(D))
from fichas_s6 import PAGES, a_html  # noqa: E402

PARA_ENVIAR = RAIZ.parent / 'para_enviar'
GITHUB = 'https://github.com/coach1-knotacademy/knot-qa-framework/blob/main/'
GITHUB_ARBOL = 'https://github.com/coach1-knotacademy/knot-qa-framework/tree/main/'
e = lambda t: html.escape(str(t), quote=True)

# El visual Knot: el mismo CSS de proyecto.html y el logo de la plantilla.
CSS_BASE = re.search(r'^CSS = """(.*?)"""', (D / 'generar_proyecto.py').read_text(encoding='utf-8'), re.S | re.M).group(1)
LOGO = re.search(r'<img src="(data:image/png;base64,[^"]+)"', (D / 'plantilla.html').read_text(encoding='utf-8')).group(1)

# La demo grabada: archivos de movil/evidencias/demo/ (se publican en el sitio con la misma ruta).
DEMO = 'movil/evidencias/demo/'
CAPTURAS = [
  ('01-sesion-abierta.png', 'CP-401', 'Entró: el menú ya ofrece «Log Out».'),
  ('02-usuario-bloqueado.png', 'CP-402', 'Usuario bloqueado: «Sorry this user has been locked out.»'),
  ('03-carrito-total.png', 'CP-404', 'Dos mochilas: «2 Items» y total «$ 59.98».'),
]
VIDEO, PORTADA = 'demo-tienda.mp4', 'demo-tienda-portada.jpg'
for archivo in [c[0] for c in CAPTURAS] + [VIDEO, PORTADA]:
    assert (MOVIL / 'evidencias' / 'demo' / archivo).is_file(), f'falta movil/evidencias/demo/{archivo}: corre las pruebas y arma la demo'
PESO_VIDEO = (MOVIL / 'evidencias' / 'demo' / VIDEO).stat().st_size

# La corrida con la que se grabó la demo (verificada en el emulador).
CORRIDA = {
  'fecha': '25 nov 2026',
  'resultado': '4 passing',
  'dispositivo': 'emulador Android 17 (API 37)',
  'versiones': 'Appium 3.2.0 · UiAutomator2 7.0.0 · WebdriverIO 9.29.1 · Node 22 · app 2.3.0',
}

README = (MOVIL / 'README.md').read_text(encoding='utf-8')


def tabla_del_readme(titulo):
    """Las filas de la tabla que está debajo del título '## titulo' en movil/README.md (sin encabezado ni separador)."""
    bloque = re.search(r'^## ' + re.escape(titulo) + r'.*?\n(.*?)(?=^## |\Z)', README, re.S | re.M).group(1)
    filas = [l for l in bloque.splitlines() if l.startswith('|')]
    celdas = lambda l: [c.strip() for c in re.split(r'(?<!\\)\|', l.strip().strip('|'))]
    return celdas(filas[0]), [celdas(l) for l in filas[2:]]


def leer(ruta):
    return (MOVIL / ruta).read_text(encoding='utf-8')


def bloque_de_prueba(cp):
    """El it() completo de un caso, tal como está en tests/tienda.spec.ts."""
    fuente = leer('tests/tienda.spec.ts')
    m = re.search(r"^  it\('@" + cp + r".*?^  }\);\n", fuente, re.S | re.M)
    assert m, f'no encontré el it() del {cp} en tests/tienda.spec.ts'
    return '\n'.join(l[2:] if l.startswith('  ') else l for l in m.group(0).rstrip().splitlines())


def codigo(texto):
    return f'<pre class="code">{e(texto)}</pre>'


CSS_MOVIL = """
.piezas { display:flex; align-items:stretch; gap:8px; margin:12px 0; }
.pieza { flex:1 1 0; min-width:0; background:var(--surface); border:2px solid var(--ink); border-radius:12px; box-shadow:3px 3px 0 var(--ink); padding:10px 12px; }
.pieza b { display:block; font:400 17px var(--f-display); color:var(--morado-osc); }
.pieza span { display:block; font-size:14px; }
.pieza.cliente { background:var(--lav); } .pieza.servidor { background:var(--lime); } .pieza.driver { background:var(--yellow); } .pieza.dispositivo { background:var(--cyan); }
.une { flex:none; align-self:center; text-align:center; font-weight:800; font-size:12px; color:var(--muted); line-height:1.1; }
.une::before { content:"→"; display:block; font:400 22px var(--f-display); color:var(--ink); }
@media (max-width:820px) { .piezas { flex-direction:column; } .une::before { content:"↓"; } }
.capturas { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }
@media (max-width:820px) { .capturas { grid-template-columns:minmax(0,1fr) minmax(0,1fr); } }
@media (max-width:480px) { .capturas { grid-template-columns:minmax(0,1fr); } .capturas img { max-width:240px; margin:0 auto; } }
figure { margin:0; } figure.card { margin:0; padding:10px; }
figure img { display:block; width:100%; height:auto; border:2px solid var(--ink); border-radius:10px; background:#fff; }
figcaption { font-size:14px; margin-top:8px; } figcaption b { color:var(--morado-osc); }
.video { display:grid; grid-template-columns:minmax(0,300px) minmax(0,1fr); gap:18px; align-items:start; }
@media (max-width:820px) { .video { grid-template-columns:minmax(0,1fr); } .video video { max-width:320px; } }
video { display:block; width:100%; height:auto; border:2px solid var(--ink); border-radius:12px; background:#1f2331; }
.verde { color:var(--ok); font-weight:800; }
table.rosetta td code { font-size:.8em; }
.antes td:first-child { font-weight:800; }
"""


def pagina(base):
    """base = '' para el sitio (rutas relativas) o la dirección de Pages para la copia de para_enviar/."""
    demo = base + DEMO

    pasos_esc, filas_esc = tabla_del_readme('La escalera de localizadores móviles')
    clases = ['p1', 'p2', 'p3', 'p5']
    escalera = ''.join(
        f'<li class="peldano {clases[i]}"><span class="num">{e(f[0])}</span><div><b>{a_html(f[1])}</b>'
        + (f' · {a_html(f[2])}' if f[2] != '—' else '') + f'<br><span class="nota">{a_html(f[3])}</span></div></li>'
        for i, f in enumerate(filas_esc))

    _, filas_cp = tabla_del_readme('Los casos')
    casos = ''.join(
        f'<tr><td class="id" data-k="Caso">{e(f[0])}</td><td data-k="Escenario">{a_html(f[1])}</td><td data-k="Qué verifica">{a_html(f[2])}</td></tr>'
        for f in filas_cp)

    cab_ros, filas_ros = tabla_del_readme('Rosetta')
    rosetta = ''.join(
        '<tr>' + ''.join(f'<td data-k="{e(re.sub(r"[*`]", "", cab_ros[k]))}">{a_html(c.replace(chr(92) + "|", "|"))}</td>' for k, c in enumerate(f)) + '</tr>'
        for f in filas_ros)
    cab_rosetta = ''.join(f'<th>{a_html(c)}</th>' for c in cab_ros)

    capturas = ''.join(
        f'<figure class="card"><img src="{demo}{archivo}" alt="{e(texto)}" width="540" height="1200" loading="lazy">'
        f'<figcaption><b>{cp}</b> · {e(texto)}</figcaption></figure>'
        for archivo, cp, texto in CAPTURAS)

    cuerpo = f'''
<h1>Automatizar una app <span class="acc">en el celular</span></h1>
<p class="lead">Las mismas capas del framework (config, páginas, datos y pruebas) y el mismo Gherkin, ahora en una app Android. Con Appium, WebdriverIO y TypeScript: <code>async/await</code>, <code>expect</code> y Page Objects, como en Playwright.</p>
<nav class="top" aria-label="Secciones">
<a href="#objetivo">Objetivo</a><a href="#appium">Qué es Appium</a><a href="#app">La app</a><a href="#codigo">El código</a><a href="#escalera">La escalera</a><a href="#evidencias">Evidencias</a><a href="#rosetta">TS ↔ Java</a><a href="#quien">Para quién</a>
</nav>

<section id="objetivo">
<h2>Objetivo</h2>
<div class="card c-cyan">
<p><b>Al terminar puedes leer, explicar y (si tienes permisos) correr una prueba móvil hecha con las capas del curso:</b> qué hace cada pieza de Appium, cómo se busca un elemento en una pantalla de celular sin XPath y qué evidencia deja una corrida.</p>
<ul class="lista">
<li><b>4 casos en verde</b> sobre una app de práctica: login correcto, usuario bloqueado, usuario vacío y el total del carrito.</li>
<li><b>La escalera móvil</b>: accessibility id → resource-id → UiAutomator → XPath nunca.</li>
<li><b>Evidencia automática</b>: una captura por paso, otra si falla, y un video de cada prueba.</li>
<li><b>La traducción a Java</b>, que es lo que vas a encontrar en muchos equipos del banco.</li>
</ul>
<p class="nota">El sistema es de práctica; la técnica y la evidencia son reales.</p>
</div>
</section>

<section id="appium">
<h2>Qué es Appium: <span class="acc">cuatro piezas</span></h2>
<p>En Playwright, el código de la prueba y quien maneja el navegador vienen juntos. En Appium son <b>programas separados</b> que se hablan por la red. Por eso se abren <b>dos terminales</b>: una para el servidor y otra para las pruebas.</p>
<div class="piezas" role="img" aria-label="Cliente WebdriverIO, por HTTP al servidor Appium en el puerto 4723, que usa el driver UiAutomator2, que por adb maneja el dispositivo Android con la app">
<div class="pieza cliente"><b>Cliente</b><span>Tu prueba: WebdriverIO + TypeScript. Pide «toca esto», «lee aquello».</span></div>
<div class="une">HTTP<br>:4723</div>
<div class="pieza servidor"><b>Servidor</b><span>Appium. Recibe los pedidos y se los pasa al driver.</span></div>
<div class="une">usa</div>
<div class="pieza driver"><b>Driver</b><span>UiAutomator2: el «traductor» para Android (para iPhone sería XCUITest).</span></div>
<div class="une">adb</div>
<div class="pieza dispositivo"><b>Dispositivo</b><span>El emulador de Android Studio (o un celular de pruebas por USB) con la app instalada.</span></div>
</div>
<div class="grid2">
<div class="card"><p class="paso">terminal 1 · el servidor</p><pre class="code">npm.cmd run appium</pre><p class="nota">Se deja abierta. Si la cierras, las pruebas dicen «Appium no responde».</p></div>
<div class="card"><p class="paso">terminal 2 · las pruebas</p><pre class="code">npm.cmd test</pre><p class="nota">En PowerShell, <code>npm.cmd</code> evita el bloqueo de <code>npm.ps1</code> sin tocar ninguna política.</p></div>
</div>
</section>

<section id="app">
<h2>La app</h2>
<div class="card">
<p><b>SauceLabs My Demo App (Android, versión 2.3.0)</b>: una tienda <b>pública hecha para practicar automatización</b>. No es de ningún banco y no maneja dinero real. Trae usuarios de ejemplo en su propia pantalla de login, incluido uno <b>bloqueado a propósito</b>.</p>
<p>El APK no va en el repo (es de un tercero y pesa 18 MB): <code>npm.cmd run app</code> lo baja a <code>movil/apps/</code> con un script de Node que funciona en Windows y respeta el proxy (<code>HTTPS_PROXY</code>).</p>
</div>
<table class="apilar">
<thead><tr><th>Caso</th><th>Escenario (especificaciones/tienda.feature)</th><th>Qué verifica</th></tr></thead>
<tbody>{casos}</tbody>
</table>
</section>

<section id="codigo">
<h2>El código, <span class="acc">capa por capa</span></h2>
<p>Esto es el código real del kit, leído de los archivos. Fíjate en que <b>la prueba no tiene ni un localizador</b>: están en el Page Object.</p>
<div class="card"><p class="paso">src/paginas/PaginaLogin.ts · el Page Object</p>{codigo(leer('src/paginas/PaginaLogin.ts'))}</div>
<div class="card"><p class="paso">tests/tienda.spec.ts · el CP-402, un paso() por línea del Gherkin</p>{codigo(bloque_de_prueba('CP-402'))}
<p class="nota"><code>paso()</code> es el <code>test.step</code> de Playwright escrito a mano: imprime la línea del Gherkin en el reporte y deja su captura. <code>expect(…).toHaveText(…)</code> reintenta solo hasta que el texto aparece, igual que en Playwright.</p></div>
<div class="card c-yel"><p class="paso">dónde está cada capa</p>
<ul class="lista">
<li><b>config</b> · <code>movil/src/config/entorno.ts</code>: host, puerto, dispositivo y APK salen de variables o <code>.env</code>. Nada escrito en el código.</li>
<li><b>páginas</b> · <code>movil/src/paginas/</code>: <code>PaginaBase</code> (barra de arriba, heredada por todas), login, menú, catálogo, detalle y carrito.</li>
<li><b>datos</b> · <code>movil/src/datos/</code>: usuarios de ejemplo y productos, con el precio en centavos para que 29,99 × 2 dé 59,98 exacto.</li>
<li><b>pruebas</b> · <code>movil/tests/tienda.spec.ts</code>, con su Gherkin en <code>movil/especificaciones/tienda.feature</code>.</li>
</ul>
<p><a class="boton chico blanco" href="{GITHUB_ARBOL}movil">Ver la carpeta movil/ en GitHub</a></p>
</div>
</section>

<section id="escalera">
<h2>La escalera de localizadores <span class="acc">móviles</span></h2>
<p>La misma idea de la S6: se sube un peldaño <b>solo</b> si el de abajo no existe en esa pantalla.</p>
<ol class="escalera">{escalera}</ol>
<div class="card c-peach">
<p><b>Un error real que se corrigió:</b> el proyecto Java anterior buscaba <code>//*[contains(text(),'Login')]</code>. En UiAutomator2 eso no encuentra nada, porque en Android el texto es un <b>atributo</b> (<code>@text</code>), no un nodo de texto como en HTML. El reemplazo es el peldaño 3: <code>new UiSelector().text("Login")</code>.</p>
</div>
<p class="nota">¿Cómo ver qué tiene cada elemento? Con Appium Inspector (está en la guía) o con <code>await driver.getPageSource()</code>, que devuelve el árbol de la pantalla con <code>text</code>, <code>content-desc</code> y <code>resource-id</code>.</p>
</section>

<section id="evidencias">
<h2>Evidencias: <span class="acc">la demo grabada</span></h2>
<p>Una corrida real del {CORRIDA['fecha']} en un {CORRIDA['dispositivo']}: <span class="verde">{CORRIDA['resultado']}</span>. {CORRIDA['versiones']}.</p>
<div class="video card">
<video controls preload="metadata" playsinline muted poster="{demo}{PORTADA}" width="360" height="800" style="color:#fff">
<source src="{demo}{VIDEO}" type="video/mp4">
Tu navegador no reproduce el video: <a href="{demo}{VIDEO}" style="color:#fff">descárgalo aquí</a>.
</video>
<div>
<p class="paso">qué se ve en el video ({PESO_VIDEO // 1000} KB)</p>
<ol class="lista">
<li><b>CP-401</b>: abre el menú, entra con <code>bod@example.com</code> y el menú ya ofrece «Log Out».</li>
<li><b>CP-402</b>: el usuario bloqueado ve «Sorry this user has been locked out.».</li>
<li><b>CP-404</b>: abre la mochila, sube la cantidad a 2, la agrega y el carrito suma «$ 59.98».</li>
</ol>
<p>Nadie grabó la pantalla a mano: lo hace el kit en cada prueba con <code>driver.startRecordingScreen()</code> y <code>stopRecordingScreen()</code>, el grabador del propio Android.</p>
<p class="nota">Cada corrida deja en <code>movil/evidencias/corrida-&lt;fecha&gt;/&lt;CP&gt;/</code>: una captura por paso con el texto del Gherkin, <code>FALLO.png</code> si algo falla, <code>video.mp4</code> y <code>pasos.txt</code> con ✓ o ✗ en cada paso. Para esta demo se corrió con <code>PASO_LENTO=1200</code> (una pausa después de cada paso, como <code>slowMo</code> en Playwright) para que se pueda seguir con los ojos.</p>
</div>
</div>
<div class="capturas">{capturas}</div>
</section>

<section id="rosetta">
<h2>Rosetta: <span class="acc">TypeScript ↔ Java</span></h2>
<p>En muchos equipos del banco el móvil se automatiza en Java con <code>java-client</code> de Appium (Maven, JUnit o TestNG, a veces con Cucumber o Serenity). Las piezas son las mismas; cambia la sintaxis.</p>
<table class="apilar rosetta">
<thead><tr>{cab_rosetta}</tr></thead>
<tbody>{rosetta}</tbody>
</table>
</section>

<section id="quien">
<h2>Para quién es, <span class="acc">y el plan B</span></h2>
<div class="grid2">
<div class="card c-lime">
<p class="paso">plan A · correrlo</p>
<p><b>Para quien tiene permisos de administrador</b> (o un equipo que TI ya preparó): hay que instalar Android Studio y tener la virtualización encendida. Con buena red, de 1 a 2 horas.</p>
<ol class="lista">
<li>Lee primero el <b>paso 0</b> de la guía: virtualización, VDI, proxy y antivirus. Si alguno está cerrado, se le pide a TI.</li>
<li>Sigue la guía con las versiones fijadas.</li>
<li><code>npm.cmd run appium</code> en una terminal y <code>npm.cmd test</code> en otra.</li>
</ol>
<p><a class="boton" href="{GITHUB}movil/GUIA_INSTALACION_WINDOWS.md">Guía de instalación en Windows</a> <a class="boton blanco" href="{GITHUB}movil/README.md">README del kit</a></p>
<p class="nota">La guía trae prompts listos para tu Copilot («pega la salida de <code>appium driver doctor</code>…»). Nunca pegues datos del banco.</p>
</div>
<div class="card c-lav">
<p class="paso">plan B · sin instalar nada</p>
<p><b>Igual de válido.</b> El 80 % de lo que enseña el kit se aprende leyendo:</p>
<ol class="lista">
<li>Mira el <a href="#evidencias">video y las capturas</a> de la corrida.</li>
<li>Lee el <a href="#codigo">Page Object y la prueba</a> y ubica cada localizador en la <a href="#escalera">escalera</a>.</li>
<li>Compara con la <a href="#rosetta">Rosetta</a>: ¿cómo se vería en Java?</li>
<li>Escribe en Gherkin un caso móvil de tu trabajo (sin datos reales) con el mismo formato de <code>tienda.feature</code>.</li>
</ol>
<p class="nota">Las nubes de dispositivos (BrowserStack, Sauce Labs) piden cuenta: solo si tu empresa ya las contrata.</p>
</div>
</div>
</section>
'''
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kit móvil · Appium</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&amp;family=Nunito:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;600&amp;display=swap" rel="stylesheet">
<style>{CSS_BASE}{CSS_MOVIL}</style>
</head>
<body>
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · kit móvil</small></div>
{cuerpo}
<p class="nota">Página del Bootcamp QA · Knot Academy, generada con <code>laboratorio/generar/generar_movil.py</code>. No carga nada de internet salvo las fuentes y la demo grabada del bootcamp. La app es pública y de práctica: nunca escribas aquí datos reales.</p>
</div>
</body>
</html>
'''


if __name__ == '__main__':
    (RAIZ / 'laboratorio' / 'movil.html').write_text(pagina(''), encoding='utf-8')
    local = pagina(PAGES)
    assert 'claude.ai' not in local, 'movil.html: enlace de claude.ai'
    sueltos = re.findall(r'(?:href|src|poster)="(?!https?://|#|data:)([^"]+)"', local)
    assert not sueltos, f'movil.html: rutas relativas en la copia local: {sueltos}'
    if PARA_ENVIAR.is_dir():
        (PARA_ENVIAR / 'movil.html').write_text(local, encoding='utf-8')
    print('movil.html listo (laboratorio/ con la demo relativa y para_enviar/ con la demo en Pages)')
