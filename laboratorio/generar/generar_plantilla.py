"""Genera laboratorio/plantilla.html: la plantilla del framework (carpeta plantilla/) en una página que todos pueden abrir.

Muestra cada archivo de plantilla/ (árbol + contenido, con botón Copiar), el prompt de PROMPT.md (botón Copiar),
la lista de cotejo (de fichas_s6.py, la misma fuente de las actividades y el deck) y las reglas.
scripts/construir-sitio.js la publica como sitio/plantilla.html.
Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_plantilla.py
"""
import html, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
sys.path.insert(0, str(D))
from fichas_s6 import COTEJO, a_html, PAGES, LABORATORIO  # noqa: E402

PLANTILLA = RAIZ / 'plantilla'
IGNORAR = {'node_modules', 'test-results', 'playwright-report', 'blob-report', '.DS_Store', 'package-lock.json'}
# El orden en que conviene leerlos: primero cómo usarla, después las capas de abajo hacia arriba, al final la prueba.
ORDEN = ['README.md', 'package.json', 'playwright.config.ts', 'tsconfig.json', '.gitignore', '.env.ejemplo',
         'src/config/ambientes.ts', 'src/config/entorno.ts', 'src/paginas/PaginaBase.ts', 'src/paginas/PaginaRecargas.ts',
         'src/datos/fabricaDeRecargas.ts', 'src/flujos/sesion.ts', 'src/soporte/fixtures.ts', 'tests/CP-101-recarga.spec.ts',
         '.github/copilot-instructions.md', 'PROMPT.md']
QUE_ES = {
  'README.md': 'Cómo usarla, paso a paso',
  'package.json': 'Solo @playwright/test y typescript',
  'playwright.config.ts': 'La configuración de Playwright: el ambiente da la dirección',
  'tsconfig.json': 'Configuración de TypeScript',
  '.gitignore': 'Lo que nunca se sube (incluido .env)',
  '.env.ejemplo': 'El modelo de las variables, sin valores',
  'src/config/ambientes.ts': 'Catálogo de ambientes, producción bloqueada, configuración congelada',
  'src/config/entorno.ts': 'La configuración de la corrida (entorno.urlBase, entorno.usuario, entorno.clave)',
  'src/paginas/PaginaBase.ts': 'Lo que tienen en común todas las pantallas',
  'src/paginas/PaginaRecargas.ts': 'Un Page Object de ejemplo, con localizadores por rol y etiqueta',
  'src/datos/fabricaDeRecargas.ts': 'Los datos de prueba, con nombres de negocio',
  'src/flujos/sesion.ts': 'Abrir la sesión sin pasar por las pantallas de ingreso',
  'src/soporte/fixtures.ts': 'Las piezas que recibe cada prueba',
  'tests/CP-101-recarga.spec.ts': 'Una prueba que sale de un caso manual (el ID va en el nombre)',
  '.github/copilot-instructions.md': 'Las reglas que tu Copilot lee solo, en este proyecto',
  'PROMPT.md': 'El prompt para pedirle a tu Copilot una prueba nueva',
}

archivos = sorted((p.relative_to(PLANTILLA).as_posix() for p in PLANTILLA.rglob('*')
                   if p.is_file() and not (set(p.relative_to(PLANTILLA).parts) & IGNORAR)),
                  key=lambda r: (ORDEN.index(r) if r in ORDEN else len(ORDEN), r))
faltan = [r for r in ORDEN if r not in archivos]
assert not faltan, f'Faltan en plantilla/: {faltan}'


def ancla(ruta):
    return 'f-' + re.sub(r'[^a-z0-9]+', '-', ruta.lower()).strip('-')


def arbol():
    """El árbol de carpetas, como lo muestra el Explorador de VS Code, con enlaces a cada archivo."""
    nodos = {}
    for r in archivos:
        d = nodos
        partes = r.split('/')
        for p in partes[:-1]:
            d = d.setdefault(p + '/', {})
        d[partes[-1]] = r
    lineas = []

    def pintar(d, prefijo):
        claves = sorted(d, key=lambda k: (not k.endswith('/'), k.lower()))
        for i, k in enumerate(claves):
            ultimo = i == len(claves) - 1
            rama = prefijo + ('└── ' if ultimo else '├── ')
            if isinstance(d[k], dict):
                lineas.append(f'<span class="rama">{html.escape(rama)}</span><b>{html.escape(k)}</b>')
                pintar(d[k], prefijo + ('    ' if ultimo else '│   '))
            else:
                lineas.append(f'<span class="rama">{html.escape(rama)}</span><a href="#{ancla(d[k])}">{html.escape(k)}</a>')
    lineas.append('<b>plantilla/</b>')
    pintar(nodos, '')
    return '\n'.join(lineas)


prompt_md = (PLANTILLA / 'PROMPT.md').read_text(encoding='utf-8')
m = re.search(r'^Actúa como', prompt_md, re.M)
assert m, 'PROMPT.md cambió: no encuentro la línea que empieza con «Actúa como»'
inicio = m.start()
assert inicio > 0, 'PROMPT.md cambió: no encuentro «Actúa como»'
prompt = prompt_md[inicio:].strip() + '\n'

tarjetas = []
for r in archivos:
    texto = (PLANTILLA / r).read_text(encoding='utf-8')
    n = texto.count('\n') + (0 if texto.endswith('\n') else 1)
    tarjetas.append(f'''<article class="card archivo" id="{ancla(r)}">
<div class="arch-cab"><div><h3><code>plantilla/{html.escape(r)}</code></h3><p class="nota">{html.escape(QUE_ES.get(r, ''))} · {n} líneas</p></div>
<button type="button" class="copiar" data-copiar="c-{ancla(r)}">Copiar</button></div>
<pre class="code{' prosa' if r.endswith('.md') else ''}" id="c-{ancla(r)}">{html.escape(texto)}</pre>
</article>''')

LOGO = re.search(r'<img src="(data:image/png;base64,[^"]+)"', (D / 'plantilla.html').read_text(encoding='utf-8')).group(1)
cotejo = '\n'.join(f'<li><label class="check"><input type="checkbox"><span>{a_html(c)}</span></label></li>' for c in COTEJO)

PAGINA = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plantilla del framework</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&amp;family=Nunito:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;600&amp;display=swap" rel="stylesheet">
<style>
:root {{ --bg:#f7f6f2; --surface:#fff; --ink:#1d2130; --muted:#454a58; --morado:#8b55f6; --morado-osc:#5b34c9; --neon:#8be000;
  --lav:#e7defe; --lime:#e2f7c9; --peach:#ffdccf; --cyan:#d3f4f7; --yellow:#fffccb;
  --f-display:"Archivo Black","Arial Black",Impact,sans-serif; --f-body:"Nunito","Segoe UI",system-ui,sans-serif; --f-mono:"JetBrains Mono",Consolas,"Cascadia Mono",Menlo,monospace; color-scheme: light; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background-color:var(--bg); background-image:radial-gradient(#d9d6cc 1.2px, transparent 1.2px); background-size:22px 22px; color:var(--ink); font:16px/1.5 var(--f-body); }}
.wrap {{ max-width:1100px; margin:0 auto; padding:0 16px 48px; }}
.knot-bar {{ display:flex; align-items:center; justify-content:space-between; gap:12px; padding:14px 0 0; font:800 14px/1.4 var(--f-body); flex-wrap:wrap; }}
.knot-bar span {{ display:flex; align-items:center; gap:8px; }} .knot-bar img {{ height:26px; }} .knot-bar small {{ font-weight:600; color:var(--muted); }}
h1, h2, h3 {{ font-family:var(--f-display); font-weight:400; letter-spacing:-.01em; line-height:1.15; text-wrap:balance; }}
h1 {{ font-size:clamp(28px,5vw,44px); margin:22px 0 8px; }} h1 .acc, h2 .acc {{ color:var(--morado-osc); }}
h2 {{ font-size:clamp(22px,3.4vw,30px); margin:0 0 8px; }} h3 {{ font-size:15px; line-height:1.35; margin:0; overflow-wrap:anywhere; }}
h3 code {{ background:none; padding:0; font-size:15px; }}
.lead {{ font-size:18px; max-width:760px; margin:0 0 6px; }}
nav.top {{ position:sticky; top:0; z-index:5; background:var(--bg); padding:10px 0; display:flex; gap:8px; flex-wrap:wrap; border-bottom:2px solid var(--ink); margin:18px 0; }}
nav.top a {{ color:var(--ink); text-decoration:none; border:2px solid var(--ink); border-radius:999px; padding:4px 12px; font-weight:800; font-size:14px; background:var(--surface); }}
nav.top a:hover {{ background:var(--lav); }}
@media (max-width:820px) {{ nav.top {{ position:static; }} }}
section {{ margin:30px 0; scroll-margin-top:80px; }}
.card {{ background:var(--surface); border:2px solid var(--ink); border-radius:14px; box-shadow:5px 5px 0 var(--ink); padding:18px 20px; margin:14px 0; min-width:0; overflow-wrap:anywhere; }}
@media (max-width:480px) {{ .card {{ padding:14px; }} }}
.c-lav {{ background:var(--lav); }} .c-peach {{ background:var(--peach); }} .c-lime {{ background:var(--lime); }} .c-yel {{ background:var(--yellow); }}
.promesa {{ font-size:19px; line-height:1.45; font-weight:700; margin:0; }}
code {{ font-family:var(--f-mono); font-size:.88em; background:#efece3; border-radius:5px; padding:1px 5px; overflow-wrap:anywhere; }}
pre.code {{ max-width:100%; max-height:520px; font:13px/1.55 var(--f-mono); background:#1f2331; color:#e8ebf2; border:2px solid var(--ink); border-radius:12px; padding:14px; overflow:auto; margin:12px 0 0; white-space:pre; tab-size:2; }}
pre.code.prosa {{ white-space:pre-wrap; overflow-wrap:anywhere; }}
pre.arbol {{ font:14px/1.6 var(--f-mono); background:var(--surface); color:var(--ink); border:2px solid var(--ink); border-radius:12px; padding:14px; overflow:auto; margin:0; white-space:pre; }}
pre.arbol a {{ color:var(--morado-osc); font-weight:600; }} pre.arbol .rama {{ color:#8c8778; }}
.arch-cab {{ display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap; }}
.arch-cab > div {{ min-width:0; flex:1 1 240px; }}
.nota {{ color:var(--muted); font-size:14px; margin:4px 0 0; }}
button.copiar, button.grande {{ font:800 14px/1.35 var(--f-body); border:2px solid var(--ink); border-radius:10px; background:var(--neon); color:var(--ink); box-shadow:3px 3px 0 var(--ink); padding:7px 14px; cursor:pointer; flex:none; }}
button.copiar:hover, button.grande:hover {{ background:var(--lime); }}
button.copiado {{ background:var(--lav); }}
button:focus-visible, a:focus-visible, input:focus-visible {{ outline:3px solid var(--morado-osc); outline-offset:2px; }}
ul.reglas {{ margin:8px 0 0; padding-left:22px; }} ul.reglas li {{ margin:8px 0; }}
ul.checks {{ list-style:none; padding-left:0; margin:8px 0 0; }} ul.checks li {{ margin:8px 0; }}
.check {{ display:flex; gap:10px; align-items:flex-start; cursor:pointer; }} .check input {{ width:20px; height:20px; margin-top:3px; flex:none; accent-color:var(--morado-osc); }}
.grid2 {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:16px; }} .grid2 > .card {{ margin:0; }}
@media (max-width:820px) {{ .grid2 {{ grid-template-columns:minmax(0,1fr); }} }}
a {{ color:var(--morado-osc); }}
</style>
</head>
<body>
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · S6 · la plantilla de tu framework</small></div>
<h1>La plantilla de <span class="acc">tu framework</span></h1>
<p class="lead">Un framework mínimo y propio, con las mismas capas del <code>knot-qa-framework</code>: configuración, páginas, datos, flujos, soporte y pruebas. Corre contra el Banco Demo publicado; no hace falta levantar ningún servidor.</p>
<div class="card c-lav"><p class="promesa">Les prometí un repo aparte; como no todos pueden clonar, aquí está en una página que sí abren. Quien tenga GitHub la encuentra en <code>plantilla/</code> del proyecto.</p></div>
<nav class="top" aria-label="Secciones"><a href="#reglas">Reglas</a><a href="#prompt">El prompt</a><a href="#cotejo">Lista de cotejo</a><a href="#archivos">Archivos</a></nav>

<section id="reglas">
<h2>Antes de usarla, <span class="acc">dos reglas</span></h2>
<div class="grid2">
<div class="card c-peach"><h3>Solo sitios de práctica</h3><ul class="reglas">
<li><b>Solo Banco Demo o ParaBank</b>; nunca sistemas, datos, pantallas ni casos del ALM del banco.</li>
<li>Al prompt, a Copilot o a cualquier IA no se le pegan casos, capturas, logs ni datos del trabajo. Para practicar, los CP-101 a CP-106 del Banco Demo.</li>
<li>La clave nunca va en el código: llega por la terminal (<code>$env:CLAVE_BANCO</code>) y el <code>.env</code> no se sube.</li></ul></div>
<div class="card c-yel"><h3>Lo que la IA escribe se lee antes de correrlo</h3><ul class="reglas">
<li>Se revisa con la lista de cotejo, línea por línea, antes de la primera corrida.</li>
<li>Si una prueba falla, no se cambia la aserción para que pase: primero se averigua si es un defecto.</li>
<li>Al final, pídele que liste lo que supuso, y confírmalo con la regla de negocio.</li></ul></div>
</div>
</section>

<section id="prompt">
<h2>El prompt para <span class="acc">tu Copilot</span></h2>
<div class="card">
<div class="arch-cab"><div><p>Copia el prompt (desde «Actúa como» hasta el final) y reemplaza solo lo que está entre <code>[corchetes]</code>. Funciona aunque tu Copilot no vea el proyecto: todo lo que necesita saber va adentro.</p></div>
<button type="button" class="grande" data-copiar="c-prompt">Copiar el prompt</button></div>
<pre class="code prosa" id="c-prompt">{html.escape(prompt)}</pre>
<p class="nota">El archivo completo, con sus instrucciones de uso, es <a href="#{ancla('PROMPT.md')}"><code>plantilla/PROMPT.md</code></a>.</p>
</div>
</section>

<section id="cotejo">
<h2>Lista de <span class="acc">cotejo</span> de una prueba</h2>
<div class="card c-lime">
<p>La lee una persona, no una herramienta. Úsala con cada prueba nueva, la escribas tú o la IA.</p>
<ul class="checks">
{cotejo}
</ul>
</div>
</section>

<section id="archivos">
<h2>Los <span class="acc">archivos</span>, uno por uno</h2>
<p class="nota">Cópialos a una carpeta fuera de OneDrive, con estos mismos nombres y carpetas. El <code>README.md</code> dice cómo correrla; si en tu equipo no se puede instalar nada, practica en el <a href="{LABORATORIO}">laboratorio de la S6</a>.</p>
<div class="card"><pre class="arbol">{arbol()}</pre></div>
{chr(10).join(tarjetas)}
</section>
<p class="nota">Página generada desde la carpeta <code>plantilla/</code> del proyecto con <code>laboratorio/generar/generar_plantilla.py</code>. Si un archivo cambia, se vuelve a generar.</p>
</div>
<script>
(function () {{
  function copiar(texto) {{
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(texto).catch(function () {{ return aMano(texto); }});
    return aMano(texto);
  }}
  function aMano(texto) {{
    return new Promise(function (ok, no) {{
      var t = document.createElement('textarea'); t.value = texto; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.left = '-9999px';
      document.body.appendChild(t); t.select();
      try {{ document.execCommand('copy') ? ok() : no(); }} catch (e) {{ no(e); }} finally {{ document.body.removeChild(t); }}
    }});
  }}
  Array.prototype.forEach.call(document.querySelectorAll('[data-copiar]'), function (b) {{
    var original = b.textContent;
    b.addEventListener('click', function () {{
      var texto = document.getElementById(b.getAttribute('data-copiar')).textContent;
      copiar(texto).then(function () {{ b.textContent = 'Copiado'; b.classList.add('copiado'); }}, function () {{ b.textContent = 'Selecciónalo y usa Ctrl + C'; }})
        .then(function () {{ setTimeout(function () {{ b.textContent = original; b.classList.remove('copiado'); }}, 1800); }});
    }});
  }});
}})();
</script>
</body>
</html>
'''
(RAIZ / 'laboratorio' / 'plantilla.html').write_text(PAGINA, encoding='utf-8')
print('plantilla.html listo:', len(archivos), 'archivos')
