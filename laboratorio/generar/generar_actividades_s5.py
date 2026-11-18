"""Genera laboratorio/actividades_S5.html: las actividades de la clase S5, en una sola página, sin internet.

Toma el código real del repo (la prueba que escribió la IA, Page Object vs. Screenplay) para que la página
nunca quede desactualizada. Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_actividades_s5.py
"""
import html, json, re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
leer = lambda r: (RAIZ / r).read_text(encoding='utf-8')

LOGO = re.search(r'<img src="(data:image/png;base64,[^"]+)"', (D / 'plantilla.html').read_text(encoding='utf-8')).group(1)

def bloque_de_prueba(ruta, titulo):
    """Saca un test(...) completo de un archivo, por su título."""
    s = leer(ruta)
    i = s.index(f"test('{titulo}'")
    j = s.index('\n});', i) + 4
    return s[i:j]

def codigo(texto, numerado=False):
    lineas = texto.rstrip('\n').split('\n')
    if numerado:
        return '<pre class="code num">' + ''.join(f'<span class="ln">{html.escape(l) or " "}</span>' for l in lineas) + '</pre>'
    return '<pre class="code">' + html.escape('\n'.join(lineas)) + '</pre>'

IA_SIN = leer('docs/ia-s5/1_sin_contexto.spec.ts').split('\n')
IA_SIN = '\n'.join(l for l in IA_SIN if not l.startswith('// Generado') and not l.startswith('// SOLO') and not l.startswith('// Nota de la IA') and not l.startswith('// las etiquetas') and not l.startswith('// el OTP')).strip()
IA_CON = leer('docs/ia-s5/2_con_contexto.spec.ts').split('\n')
IA_CON = '\n'.join(l for l in IA_CON if not l.startswith('// ')).strip()
POM = bloque_de_prueba('tests/parabank/cuentas.spec.ts', 'transfiere $25 entre sus cuentas y los dos saldos cambian')
SP = bloque_de_prueba('tests/parabank/screenplay.spec.ts', 'Ana abre una cuenta de ahorros y se pasa $50')

# Ronda 1: los 7 elementos del caso manual y dónde viven en el framework.
FILAS = [
  ('La dirección del ambiente de pruebas: <code>http://127.0.0.1:4000</code>', 'C',
   'Configuración. Vive una sola vez en <code>src/config/entorno.ts</code>. Si mañana el ambiente cambia, se corrige ahí.'),
  ('El usuario <code>ana</code> y la clave <code>Clave123</code>', 'D',
   'Datos. Salen de <code>usuarios.ana</code>. La prueba no escribe la clave a mano.'),
  ('Escribir usuario y clave y pulsar <b>Ingresar</b>', 'P',
   'Pantalla. Es <code>PaginaLogin.ingresar()</code>. Los localizadores viven ahí y en ningún otro lado.'),
  ('Iniciar sesión completa: login, leer el SMS y escribir el código', 'T',
   'Tarea. Son varios pasos de pantalla con un nombre de negocio: <code>iniciarSesionPorUi()</code>. En Screenplay sería una tarea <code>IniciarSesion</code>.'),
  ('Operador <b>Claro</b>, celular <code>3001234567</code> y valor <b>$60.000</b>', 'D',
   'Datos. Es <code>fabricaDeRecargas.grande()</code>: la fábrica sabe que «grande» es más de $50.000.'),
  ('Elegir operador, escribir celular y valor, y pulsar <b>Recargar</b>', 'P',
   'Pantalla. Es <code>PaginaRecargas.recargar(recarga)</code>.'),
  ('Recarga con código: pedirlo, leerlo del SMS y confirmar', 'T',
   'Tarea. Un paso de negocio que junta pantalla y buzón. Si la regla del código cambia, se corrige en un solo lugar.'),
]
NOMBRE = {'P': 'Pantalla', 'T': 'Tarea', 'D': 'Datos', 'C': 'Configuración'}

filas_html = ''.join(
  f'<tr data-ok="{ok}"><td class="n">{i + 1}</td><td>{txt}<div class="exp" hidden>{exp}</div></td>'
  f'<td class="opc">' + ''.join(f'<button type="button" data-v="{k}">{NOMBRE[k]}</button>' for k in 'PTDC') + '</td></tr>'
  for i, (txt, ok, exp) in enumerate(FILAS))

DEFECTOS = [
  ('Línea 3', 'La dirección del sitio está escrita a mano (<code>BASE</code>).', 'Configuración única: <code>entorno.ts</code> y rutas relativas.'),
  ('Línea 7', 'Inventó la ruta <code>/login</code>, que no existe: <b>la prueba se cae aquí</b>, esperando el campo Usuario.', 'Page Object: <code>PaginaLogin.ruta</code> ya sabe la dirección real.'),
  ('Líneas 8–9, 29–30', 'Usuario, clave, celular y valor escritos a mano. La clave queda en el código.', 'Factory: <code>usuarios.ana</code> y <code>fabricaDeRecargas.grande()</code>.'),
  ('Líneas 8–31', 'Todos los localizadores dentro de la prueba, y uno inventado (línea 25): <code>getByTestId(\'saldo\')</code>.', 'Page Object: <code>PaginaRecargas</code>.'),
  ('Líneas 13–21', 'Lee el código del SMS buscando 6 números en toda la página del buzón: se rompe si cambia el texto.', 'Flujo/Tarea: <code>iniciarSesionPorUi()</code> y <code>cliente.leerCodigo()</code>.'),
  ('Línea 34', 'No sabe que una recarga de $60.000 <b>pide código</b>: «Recarga exitosa» nunca aparecería.', 'Nadie se lo contó. Con el repo, la IA lo sacó de la regla de negocio.'),
]
defectos_html = ''.join(f'<li><b>{l}</b> · {d}<br><span class="fix">→ {f}</span></li>' for l, d, f in DEFECTOS)

HTML = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Actividades S5 Patrones</title>
<style>
:root {{ --bg:#f7f6f2; --surface:#fff; --ink:#1d2130; --muted:#454a58; --morado:#8b55f6; --morado-osc:#5b34c9; --neon:#8be000;
  --lav:#e7defe; --lime:#e2f7c9; --peach:#ffdccf; --cyan:#d3f4f7; --yellow:#fffccb; --ok:#2f7d32; --bad:#c62828;
  --f-display:"Archivo Black","Arial Black",Impact,sans-serif; --f-body:"Nunito","Segoe UI",system-ui,sans-serif; --f-mono:"JetBrains Mono",Consolas,"Cascadia Mono",Menlo,monospace; color-scheme: light; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background-color:var(--bg); background-image:radial-gradient(#d9d6cc 1.2px, transparent 1.2px); background-size:22px 22px; color:var(--ink); font:16px/1.5 var(--f-body); }}
.wrap {{ max-width:1100px; margin:0 auto; padding:0 16px 48px; }}
.knot-bar {{ display:flex; align-items:center; justify-content:space-between; gap:12px; padding:14px 0 0; font:800 14px var(--f-body); flex-wrap:wrap; }}
.knot-bar span {{ display:flex; align-items:center; gap:8px; }} .knot-bar img {{ height:26px; }} .knot-bar small {{ font-weight:600; color:var(--muted); }}
h1, h2, h3 {{ font-family:var(--f-display); font-weight:400; letter-spacing:-.01em; line-height:1.15; }}
h1 {{ font-size:clamp(28px,5vw,44px); margin:22px 0 6px; }} h1 .acc, h2 .acc {{ color:var(--morado); }}
h2 {{ font-size:clamp(22px,3.4vw,30px); margin:0 0 6px; }} h3 {{ font-size:19px; margin:0 0 6px; }}
.lead {{ font-size:18px; max-width:760px; }}
nav.top {{ position:sticky; top:0; z-index:5; background:var(--bg); padding:10px 0; display:flex; gap:8px; flex-wrap:wrap; border-bottom:2px solid var(--ink); margin-bottom:18px; }}
nav.top a {{ color:var(--ink); text-decoration:none; border:2px solid var(--ink); border-radius:999px; padding:4px 12px; font-weight:800; font-size:14px; background:var(--surface); }}
nav.top a:hover {{ background:var(--lav); }}
section {{ margin:26px 0; scroll-margin-top:70px; }}
.card {{ background:var(--surface); border:2px solid var(--ink); border-radius:14px; box-shadow:5px 5px 0 var(--ink); padding:18px 20px; margin:14px 0; }}
.c-lav {{ background:var(--lav); }} .c-lime {{ background:var(--lime); }} .c-peach {{ background:var(--peach); }} .c-cyan {{ background:var(--cyan); }} .c-yel {{ background:var(--yellow); }}
.meta {{ display:flex; gap:8px; flex-wrap:wrap; margin:6px 0 10px; }}
.chip {{ border:2px solid var(--ink); border-radius:999px; padding:2px 10px; font-weight:800; font-size:13px; background:var(--surface); }}
.grid2 {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:16px; }} .grid2 > * {{ min-width:0; }} .card {{ min-width:0; overflow-wrap:anywhere; }} @media (max-width:820px) {{ .grid2 {{ grid-template-columns:minmax(0,1fr); }} }}
code {{ font-family:var(--f-mono); font-size:.88em; background:#efece3; border-radius:5px; padding:1px 5px; }}
pre.code {{ max-width:100%; overflow-wrap:normal; font:13px/1.55 var(--f-mono); background:#1f2331; color:#e8ebf2; border:2px solid var(--ink); border-radius:12px; padding:14px; overflow:auto; margin:10px 0; }}
pre.num {{ counter-reset:l; }} pre.num .ln {{ display:block; }} pre.num .ln::before {{ counter-increment:l; content:counter(l); display:inline-block; width:2.4em; color:#8c93a8; }}
table {{ width:100%; border-collapse:collapse; }} td {{ border-top:2px solid var(--ink); padding:10px 8px; vertical-align:top; }}
td.n {{ font-family:var(--f-display); width:2em; }} td.opc {{ width:1%; white-space:nowrap; }}
@media (max-width:820px) {{ td.opc {{ white-space:normal; }} table, tbody, tr, td {{ display:block; }} td.n {{ width:auto; border-top:2px solid var(--ink); padding-bottom:0; }} td:not(.n) {{ border-top:0; }} }}
button {{ font:800 14px var(--f-body); border:2px solid var(--ink); border-radius:10px; background:var(--surface); color:var(--ink); padding:6px 10px; margin:2px; cursor:pointer; }}
button:hover {{ background:var(--lav); }} button.sel {{ background:var(--morado); color:#fff; }}
button.grande {{ background:var(--neon); box-shadow:3px 3px 0 var(--ink); padding:9px 16px; font-size:15px; }}
tr.bien td {{ background:#eefbe3; }} tr.mal td {{ background:#ffe9e3; }} .exp {{ margin-top:6px; font-size:14px; }}
.puntaje {{ font-weight:800; margin-left:10px; }}
ol.pasos li, ul.lista li {{ margin:6px 0; }} .fix {{ color:var(--morado-osc); font-weight:700; }}
.nota {{ color:var(--muted); font-size:14px; }}
a.boton {{ display:inline-block; text-decoration:none; color:var(--ink); background:var(--neon); border:2px solid var(--ink); border-radius:10px; box-shadow:3px 3px 0 var(--ink); padding:9px 16px; font-weight:800; margin:4px 6px 4px 0; }}
a.boton.blanco {{ background:var(--surface); }}
.frase {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; font-size:17px; }}
.frase input {{ font:16px var(--f-body); border:2px solid var(--ink); border-radius:8px; padding:6px 8px; min-width:180px; }}
.ok {{ color:var(--ok); font-weight:800; }}
</style>
</head>
<body>
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · S5 · patrones de diseño</small></div>
<h1>De tu caso manual a un <span class="acc">framework que se mantiene</span></h1>
<p class="lead">Las actividades de hoy, en orden. Todo funciona sin instalar nada. Lo que hagamos se dice en el chat de Teams.</p>
<nav class="top" aria-label="Actividades">
<a href="#ronda1">1 · Caso manual</a><a href="#ronda2">2 · Fábrica</a><a href="#ronda3">3 · La IA</a><a href="#screenplay">Screenplay</a><a href="#real">Sitio real</a><a href="#proyecto">Tu proyecto</a>
</nav>

<section id="ronda1">
<div class="card c-lav">
<h2>Ronda 1 · ¿Dónde vive cada cosa de tu caso?</h2>
<div class="meta"><span class="chip">en parejas · 10 min</span><span class="chip">quien hace pruebas manuales dicta, quien programa marca</span></div>
<p>Este es un caso de prueba manual, como los que ya escriben. Para cada elemento, marquen dónde viviría en el framework. <b>Terminaron cuando las 7 filas tienen columna.</b> Después, «Revisar».</p>
<div style="border-top:2px solid var(--ink);border-bottom:2px solid var(--ink);padding:10px 0;margin:10px 0">
<h3>CP-021 · Recarga de $60.000 a celular con código</h3>
<p><b>Precondición:</b> Ana tiene $1.500.000 en Ahorros. <b>Resultado esperado:</b> comprobante «Recarga exitosa» y el saldo baja $60.000.</p>
</div>
<table><tbody id="tabla1">{filas_html}</tbody></table>
<p><button type="button" class="grande" id="revisar1">Revisar</button><span class="puntaje" id="puntaje1"></span></p>
<p class="nota">Pantalla = Page Object · Tarea = un paso de negocio (flujo o Screenplay) · Datos = Factory · Configuración = un solo lugar para el ambiente.</p>
</div>
</section>

<section id="ronda2">
<div class="card c-lime">
<h2>Ronda 2 · Tu primera fábrica</h2>
<div class="meta"><span class="chip">en parejas · 8 min</span><span class="chip">terminado = verde</span></div>
<p>En la Ronda 1, los datos eran la columna más repetida. Ahora los ponemos en una fábrica. El modelo (recargas) ya está hecho; ustedes hacen la de transferencias, paso a paso. <b>Cada paso tiene su propia prueba.</b></p>
<a class="boton" href="laboratorio-s5.html">Abrir el laboratorio de la S5</a>
<p class="nota">Con el repo instalado: <code>npx.cmd playwright test reto1 --project=retos-s05</code>. Al minuto 4, en el chat: «1» voy bien · «2» atascado · «3» listo.</p>
</div>
</section>

<section id="ronda3">
<div class="card c-peach">
<h2>Ronda 3 · Esto lo escribió una IA</h2>
<div class="meta"><span class="chip">en salas · 12 min</span><span class="chip">líderes: son el jurado</span></div>
<p>Le pedimos a una IA una prueba de la recarga de $60.000, <b>sin dejarle ver el repo</b>. Este es su código, tal cual. Encuentren <b>3 defectos</b> y, para cada uno, el patrón que lo corrige. Escríbanlos en el chat con el número de línea.</p>
{codigo(IA_SIN, numerado=True)}
<p><button type="button" class="grande" id="ver3">Mostrar lo que encontramos</button></p>
<div id="defectos" hidden>
<h3>Lo que tiene (y lo que pasó al correrla)</h3>
<ul class="lista">{defectos_html}</ul>
<h3>El mismo pedido, con la IA dentro del repo</h3>
<p>Leyó <code>.github/copilot-instructions.md</code> y los Page Objects. <b>Resultado al correrla: verde.</b> Agregó sola el paso del código, porque lo encontró en la regla.</p>
{codigo(IA_CON)}
</div>
</div>
<div class="card c-yel">
<h3>¿Y si le pedimos «déjamela en verde»?</h3>
<p>A otra IA le pedimos una prueba de regresión de una transferencia de $100.000 desde Corriente: «explora cómo se comporta la app hoy y déjamela en verde». No la dejó verde. Respondió:</p>
<p><i>«La app reporta total $100.400, pero a la Corriente solo le descontó $100.000. Si hubiera puesto 150.000, habría quedado verde, pero se estaría dando por bueno el comportamiento actual sin confirmar la regla de negocio.»</i></p>
<p><b>Pregunta para el chat:</b> ¿quién decide si el saldo correcto es $150.000 o $149.600? ¿La IA, la pantalla o la regla?</p>
<p class="nota">Una herramienta que graba «lo que ve» habría puesto $150.000 y la prueba saldría verde validando un bug. Las tres pruebas, con el resultado de correrlas, están en <code>docs/ia-s5/</code> del repo.</p>
</div>
</section>

<section id="screenplay">
<div class="card c-cyan">
<h2>Screenplay · la misma prueba, contada de otra forma</h2>
<div class="meta"><span class="chip">solo leer · 3 min</span><span class="chip">voten en el chat: 1 o 2</span></div>
<p>Las dos prueban «transferir entre mis cuentas» en ParaBank. ¿Cuál se parece más a un caso de prueba manual de ustedes?</p>
<h3>1 · Page Object</h3>{codigo(POM)}
<h3>2 · Screenplay</h3>{codigo(SP)}
<p><b>Page Object organiza pantallas. Screenplay organiza tareas.</b> Se pueden usar juntos: una tarea puede usar un Page Object por dentro. Para su proyecto, Screenplay es opcional.</p>
</div>
<div class="card">
<h3>¿Y el Singleton?</h3>
<div class="grid2">
<div><p class="ok">Sí: una sola configuración.</p><p>La dirección del ambiente y sus datos viven en un solo lugar (<code>entorno.ts</code>). Un módulo de TypeScript ya es único: no hace falta escribir la clase.</p></div>
<div><p style="color:var(--bad);font-weight:800">No: un navegador único para todas las pruebas.</p><p>Se mezclan sesiones y cookies, y una prueba daña a la siguiente. Viene de Selenium; Playwright ya crea un navegador limpio por prueba.</p></div>
</div>
</div>
</section>

<section id="real">
<div class="card c-lime">
<h2>Un sitio real: ParaBank</h2>
<p>El mismo framework, en un banco de práctica real en internet. Cada prueba deja video, pantallazos y el paso a paso (trace). Busquen la prueba roja: ¿por qué falló?</p>
<a class="boton" href="reportes/parabank/index.html">Ver el reporte de ParaBank</a><a class="boton blanco" href="https://parabank.parasoft.com/parabank/index.htm">Abrir ParaBank</a><a class="boton blanco" href="banco/index.html">Abrir el Banco Demo (Recargas)</a>
<h3>Bloqueos reales que encontramos (y cómo los maneja el framework)</h3>
<ul class="lista">
<li><b>Límite de peticiones.</b> ParaBank está detrás de Cloudflare: con demasiadas peticiones seguidas responde <b>HTTP 429</b> y bloquea 5 minutos. El framework va de a una prueba, con pausa, y si llega un 429 lo dice claro.</li>
<li><b>Datos compartidos.</b> Cualquier persona del mundo usa ParaBank. Si todas las pruebas usan «el usuario de siempre», se pisan. La fábrica crea un cliente nuevo por corrida.</li>
<li><b>Bugs reales.</b> ParaBank deja transferir más de lo que hay y acepta montos negativos (PB-01 y PB-02). Las pruebas dicen lo que <i>debería</i> pasar.</li>
<li><b>Código extra y límite diario</b> en las recargas del Banco Demo: como una billetera real.</li>
<li><b>Un tercero que no responde.</b> Si el operador no contesta, ¿se pierde la plata? En el Banco Demo, sí (BUG-04). Y con <code>page.route</code> se puede «apagar» un servicio para probar qué pasa.</li>
</ul>
<p class="nota">ParaBank es público: nunca escriban ahí datos reales. Lo mismo con la IA: solo el repo de práctica o un sitio público, nunca pantallas ni datos del banco.</p>
</div>
</section>

<section id="proyecto">
<div class="card c-lav">
<h2>Tu proyecto del 3 de diciembre</h2>
<p>Escriban su frase y péguenla en el chat. Piensen en un flujo de su trabajo, pero <b>descríbanlo con palabras</b>: sin nombres de sistemas internos, sin datos ni pantallas reales.</p>
<div class="frase">Quiero automatizar <input id="p1" placeholder="el flujo de…"> en <input id="p2" placeholder="ParaBank, el Banco Demo…"> usando <input id="p3" placeholder="Page Object, una fábrica…"></div>
<p><button type="button" class="grande" id="copiar">Copiar mi frase</button> <span id="copiado" class="ok"></span></p>
</div>
</section>
<p class="nota">Página de práctica del Bootcamp QA · Knot Academy. No carga nada de internet.</p>
</div>
<script>
(function () {{
  var filas = document.querySelectorAll('#tabla1 tr');
  filas.forEach(function (tr) {{
    tr.querySelectorAll('button').forEach(function (b) {{
      b.addEventListener('click', function () {{
        tr.querySelectorAll('button').forEach(function (x) {{ x.classList.remove('sel'); }});
        b.classList.add('sel'); tr.classList.remove('bien', 'mal');
      }});
    }});
  }});
  document.getElementById('revisar1').addEventListener('click', function () {{
    var bien = 0, marcadas = 0;
    filas.forEach(function (tr) {{
      var sel = tr.querySelector('button.sel');
      tr.classList.remove('bien', 'mal');
      tr.querySelector('.exp').hidden = false;
      if (!sel) return;
      marcadas++;
      if (sel.getAttribute('data-v') === tr.getAttribute('data-ok')) {{ bien++; tr.classList.add('bien'); }} else tr.classList.add('mal');
    }});
    document.getElementById('puntaje1').textContent = bien + ' de ' + filas.length + ' bien' + (marcadas < filas.length ? ' (faltan ' + (filas.length - marcadas) + ' por marcar)' : '');
  }});
  document.getElementById('ver3').addEventListener('click', function () {{ document.getElementById('defectos').hidden = false; this.hidden = true; }});
  document.getElementById('copiar').addEventListener('click', function () {{
    var v = function (id) {{ return document.getElementById(id).value.trim() || '___'; }};
    var frase = 'Quiero automatizar ' + v('p1') + ' en ' + v('p2') + ' usando ' + v('p3') + '.';
    var listo = function () {{ document.getElementById('copiado').textContent = 'Copiada: ' + frase; }};
    if (navigator.clipboard) navigator.clipboard.writeText(frase).then(listo, listo); else listo();
  }});
}})();
</script>
</body>
</html>
'''
(RAIZ / 'laboratorio' / 'actividades_S5.html').write_text(HTML, encoding='utf-8')
print('actividades_S5.html listo')
