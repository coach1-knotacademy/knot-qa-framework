"""Genera laboratorio/actividades_S5.html (las actividades de la clase S5) y docs/patrones.md (las fichas).

La página va en el orden de la clase: cada patrón trae su FICHA (el concepto), un EJEMPLO RESUELTO
sacado del repo y una PRÁCTICA corta con su comprobación. Las fichas salen de fichas_s5.py, la misma
fuente que usa el deck del instructor. Todo funciona sin internet.

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_actividades_s5.py
"""
import html, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
sys.path.insert(0, str(D))
from fichas_s5 import FICHAS, FILAS as FILAS_FICHA, LEYENDA, CP021, BOLETO, a_html  # noqa: E402

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

# ---------- Código real del repo (así la página nunca queda desactualizada) ----------
IA_SIN = '\n'.join(l for l in leer('docs/ia-s5/1_sin_contexto.spec.ts').split('\n')
                   if not l.startswith(('// Generado', '// SOLO', '// Nota de la IA', '// las etiquetas', '// el OTP'))).strip()
IA_CON = '\n'.join(l for l in leer('docs/ia-s5/2_con_contexto.spec.ts').split('\n') if not l.startswith('// ')).strip()
POM = bloque_de_prueba('tests/parabank/cuentas.spec.ts', 'transfiere $25 entre sus cuentas y los dos saldos cambian')
SP = bloque_de_prueba('tests/parabank/screenplay.spec.ts', 'Ana abre una cuenta de ahorros y se pasa $50')

s = leer('src/sitios/parabank/paginas/PaginaTransferir.ts')
PAGINA_EJEMPLO = s[s.index('/** "Transfer Funds"'):].strip()

s = leer('src/datos/fabricaDeRecargas.ts')
i = s.index('export const fabricaDeRecargas')
j = s.index('  /** Una recarga al número de pruebas')
FABRICA_EJEMPLO = (s[i:j].rstrip() + '\n  // … aOperadorCaido() y paraCadaOperador() siguen el mismo molde\n};')
FABRICA_EJEMPLO = re.sub(r'\n  /\*\*\n(   \*.*\n)+?   \*/', '', FABRICA_EJEMPLO)  # sin los comentarios largos: se leen en la ficha

s = leer('src/config/entorno.ts')
ENTORNO_EJEMPLO = s[s.index('export const entorno'):].strip()

assert "test('CP-021 ·" in leer('tests/recargas/recargas.spec.ts'), 'La prueba CP-021 cambió de nombre: revisa fichas_s5.CP021'

# ---------- Piezas de la página ----------
def clasificador(cid, filas, opciones):
    """filas: (texto_html, clave_correcta, explicacion_html). opciones: [(clave, etiqueta)]."""
    trs = ''.join(
        f'<tr data-ok="{ok}"><td class="n">{n + 1}</td><td>{txt}<div class="exp" hidden>{exp}</div></td>'
        f'<td class="opc">' + ''.join(f'<button type="button" data-v="{k}">{et}</button>' for k, et in opciones) + '</td></tr>'
        for n, (txt, ok, exp) in enumerate(filas))
    return (f'<table class="clasif" id="t-{cid}"><tbody>{trs}</tbody></table>'
            f'<p><button type="button" class="grande" data-revisar="{cid}">Revisar</button><span class="puntaje" id="p-{cid}"></span></p>')

def ficha(f):
    filas = ''.join(f'<div class="fk">{et}</div><div class="fv">{a_html(f[k])}</div>' for k, et in FILAS_FICHA)
    return (f'<div class="card ficha-card"><div class="meta"><span class="chip">ficha · 3 min</span><span class="chip">capa de la S3: <code>{f["capa"]}</code></span></div>'
            f'<h2>{f["nombre"]}</h2><p class="desde">{a_html(f["desde"])}</p><div class="ficha">{filas}</div></div>')

def revelar(rid, boton, contenido):
    return f'<p><button type="button" class="grande" data-revelar="{rid}">{boton}</button></p><div id="{rid}" hidden>{contenido}</div>'

A_LA_VEZ = '<span class="chip">respondan a la vez: escriban sin enviar · «3, 2, 1, envíen»</span>'
F = {f['id']: f for f in FICHAS}

# Cómo leer una prueba
leyenda_html = ''.join(f'<tr><td class="cod">{a_html(a)}</td><td>{a_html(b)}</td></tr>' for a, b in LEYENDA)
cp021_html = ''.join(f'<tr><td class="cod"><code>{html.escape(c)}</code></td><td>{a_html(n)}</td></tr>' for c, n in CP021)

# Ronda 1: los 7 elementos del caso manual y dónde viven en el framework.
RONDA1 = [
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
OPC_R1 = [('P', 'Pantalla'), ('T', 'Tarea'), ('D', 'Datos'), ('C', 'Configuración')]

# Page Object · práctica: la pantalla Recargas, ¿lo tiene o lo sabe hacer?
POM_TIENE = [
  ('La lista «Operador»', 'T', 'Lo <b>tiene</b>: <code>private readonly listaOperador</code>.'),
  ('El campo «Número de celular»', 'T', 'Lo <b>tiene</b>: <code>campoNumero</code>, privado.'),
  ('Recargar: elegir operador, escribir número y valor, y pulsar Recargar', 'S', 'Lo <b>sabe hacer</b>: <code>recargar(recarga)</code>.'),
  ('El botón «Confirmar recarga»', 'T', 'Lo <b>tiene</b>: <code>botonConfirmar</code>, privado.'),
  ('Confirmar con el código que llegó por SMS', 'S', 'Lo <b>sabe hacer</b>: <code>confirmar(codigo)</code>.'),
  ('Esperar el comprobante o el error, y leerlo', 'S', 'Lo <b>sabe hacer</b>: <code>esperarResultado()</code>.'),
]
POM_ES = [
  (codigo("class PaginaRecargas extends PaginaBase {\n  private readonly botonRecargar = this.page.getByRole('button', { name: 'Recargar' });\n\n  async recargar(r: Recarga) {\n    // … llena los campos\n    await this.botonRecargar.click();\n  }\n}"), 'si',
   '<b>Sí.</b> Localizador privado y una acción con nombre de negocio. La prueba no sabe cómo se pulsa el botón.'),
  (codigo("async recargar(r: Recarga) {\n  await this.botonRecargar.click();\n  await expect(this.comprobante).toContainText('Recarga exitosa');\n}"), 'no',
   '<b>No.</b> Tiene <code>expect</code> adentro: la página decide qué está bien. Ya no sirve para probar la recarga con código ni el error del operador.'),
  (codigo("// dentro de la prueba\nawait page.getByLabel('Valor de la recarga').fill('60000');"), 'no',
   '<b>No.</b> El localizador está en la prueba: si cambia la etiqueta, hay que corregir cada prueba que la use.'),
]

# Screenplay · práctica
SP_PIEZAS = [
  ('<code>private readonly botonRecargar</code>', 'P', 'Página: lo que la pantalla tiene.'),
  ('<code>UsarLaBilletera.de(billetera)</code>', 'H', 'Habilidad: con qué hace las cosas el actor.'),
  ("<code>Transferir.desde('principal').hacia('ahorros').por(50)</code>", 'T', 'Tarea: un paso de negocio.'),
  ("<code>SaldoDe.cuenta('ahorros')</code>", 'Q', 'Pregunta: lo que se revisa contra el resultado esperado.'),
  ('<code>paginaRecargas.recargar(recarga)</code>', 'P', 'Página: una acción de una pantalla. Una tarea la puede usar por dentro.'),
  ('Confirmar la recarga grande con el código del SMS, contado como un paso de negocio', 'T', 'Tarea: junta pantalla y buzón con un nombre de negocio.'),
]
OPC_SP = [('P', 'Página'), ('H', 'Habilidad'), ('T', 'Tarea'), ('Q', 'Pregunta')]
SP_MODELO = """const ana = Actor.llamado('Ana').puede(UsarLaBilletera.de(billetera));  // quién y con qué

await ana.intenta(Recargar.celular('3001234567').por(60_000));          // qué hace

expect(await ana.pregunta(SaldoDisponible.enLaBilletera()))             // qué revisa
  .toBe(1_440_000);"""

# Singleton · práctica
SINGLE = [
  ('La dirección del ambiente (QA o UAT)', 'U', 'Una sola: <code>entorno.urlBase</code>. Si no, uno prueba en QA y otro en UAT.'),
  ('El navegador y sus cookies', 'N', 'Uno nuevo por prueba. Playwright ya lo hace solo. Compartirlo mezcla sesiones.'),
  ('El cliente de ParaBank que usan las pruebas', 'N', 'Uno nuevo, de la fábrica. En ParaBank es uno por corrida para no pasar el límite, y cada prueba abre sus propias cuentas.'),
  ('La sesión (el token) de Ana', 'N', 'Una por prueba. Compartida, una prueba puede ver la cuenta de otro cliente: incidente de confidencialidad.'),
  ('La pausa entre pruebas con ParaBank (5 segundos)', 'U', 'Una sola regla: <code>entornoParaBank.pausaEntrePruebasMs</code>. Se cambia en un lugar.'),
]
OPC_SI = [('U', 'Una sola'), ('N', 'Una nueva cada vez')]

DEFECTOS = [
  ('Línea 3', 'La dirección del sitio está escrita a mano (<code>BASE</code>).', 'Viola Singleton/configuración: <code>entorno.ts</code> y rutas relativas.'),
  ('Línea 7', 'Inventó la ruta <code>/login</code>, que no existe: <b>la prueba se cae aquí</b>, esperando el campo Usuario.', 'Viola Page Object: <code>PaginaLogin.ruta</code> ya sabe la dirección real.'),
  ('Líneas 8–9, 29–30', 'Usuario, clave, celular y valor escritos a mano. La clave queda en el código.', 'Viola Factory: <code>usuarios.ana</code> y <code>fabricaDeRecargas.grande()</code>.'),
  ('Líneas 8–31', 'Todos los localizadores dentro de la prueba, y uno inventado (línea 25): <code>getByTestId(\'saldo\')</code>.', 'Viola Page Object: <code>PaginaRecargas</code>.'),
  ('Líneas 13–21', 'Lee el código del SMS buscando 6 números en toda la página del buzón: se rompe si cambia el texto.', 'Le falta una tarea: <code>iniciarSesionPorUi()</code> y <code>cliente.leerCodigo()</code>.'),
  ('Línea 34', 'No sabe que una recarga de $60.000 <b>pide código</b>: «Recarga exitosa» nunca aparecería.', 'Nadie se lo contó. Con el repo, la IA lo sacó de la regla de negocio.'),
]
defectos_html = ''.join(f'<li><b>{l}</b> · {d}<br><span class="fix">→ {f}</span></li>' for l, d, f in DEFECTOS)

boleto_html = ''.join(
  f'<li><p><b>{a_html(p)}</b></p><p class="opciones">' + ' · '.join(f'<b>{"abc"[k]})</b> {a_html(o)}' for k, o in enumerate(ops)) + '</p></li>'
  for p, ops, ok, por in BOLETO)
boleto_resp = ''.join(f'<li><b>{ok}</b> · {a_html(por)}</li>' for p, ops, ok, por in BOLETO)

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
h1 {{ font-size:clamp(28px,5vw,44px); margin:22px 0 6px; }} h1 .acc, h2 .acc {{ color:var(--morado-osc); }}
h2 {{ font-size:clamp(22px,3.4vw,30px); margin:0 0 6px; }} h3 {{ font-size:19px; margin:14px 0 6px; }}
.lead {{ font-size:18px; max-width:760px; }}
nav.top {{ position:sticky; top:0; z-index:5; background:var(--bg); padding:10px 0; display:flex; gap:8px; flex-wrap:wrap; border-bottom:2px solid var(--ink); margin-bottom:18px; }}
nav.top a {{ color:var(--ink); text-decoration:none; border:2px solid var(--ink); border-radius:999px; padding:4px 12px; font-weight:800; font-size:14px; background:var(--surface); }}
nav.top a:hover {{ background:var(--lav); }}
section {{ margin:30px 0; scroll-margin-top:70px; }}
.card {{ background:var(--surface); border:2px solid var(--ink); border-radius:14px; box-shadow:5px 5px 0 var(--ink); padding:18px 20px; margin:14px 0; min-width:0; overflow-wrap:anywhere; }}
.c-lav {{ background:var(--lav); }} .c-lime {{ background:var(--lime); }} .c-peach {{ background:var(--peach); }} .c-cyan {{ background:var(--cyan); }} .c-yel {{ background:var(--yellow); }}
.meta {{ display:flex; gap:8px; flex-wrap:wrap; margin:6px 0 10px; }}
.chip {{ border:2px solid var(--ink); border-radius:999px; padding:2px 10px; font-weight:800; font-size:13px; background:var(--surface); }}
.grid2 {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:16px; }} .grid2 > * {{ min-width:0; }} @media (max-width:820px) {{ .grid2 {{ grid-template-columns:minmax(0,1fr); }} }}
code {{ font-family:var(--f-mono); font-size:.88em; background:#efece3; border-radius:5px; padding:1px 5px; }}
pre.code {{ max-width:100%; overflow-wrap:normal; font:13px/1.55 var(--f-mono); background:#1f2331; color:#e8ebf2; border:2px solid var(--ink); border-radius:12px; padding:14px; overflow:auto; margin:10px 0; }}
pre.num {{ counter-reset:l; }} pre.num .ln {{ display:block; }} pre.num .ln::before {{ counter-increment:l; content:counter(l); display:inline-block; width:2.4em; color:#8c93a8; }}
table {{ width:100%; border-collapse:collapse; }} td {{ border-top:2px solid var(--ink); padding:10px 8px; vertical-align:top; }}
td.n {{ font-family:var(--f-display); width:2em; }} td.opc {{ width:1%; white-space:nowrap; }} td.cod {{ width:44%; }} td.cod code {{ white-space:pre-wrap; }}
@media (max-width:820px) {{ td.opc {{ white-space:normal; }} table, tbody, tr, td {{ display:block; }} td.n {{ width:auto; border-top:2px solid var(--ink); padding-bottom:0; }} td:not(.n) {{ border-top:0; }} td.cod {{ width:auto; border-top:2px solid var(--ink); padding-bottom:0; }} }}
button {{ font:800 14px var(--f-body); border:2px solid var(--ink); border-radius:10px; background:var(--surface); color:var(--ink); padding:6px 10px; margin:2px; cursor:pointer; }}
button:hover {{ background:var(--lav); }} button.sel {{ background:var(--morado); color:#fff; }}
button.grande {{ background:var(--neon); box-shadow:3px 3px 0 var(--ink); padding:9px 16px; font-size:15px; }}
tr.bien td {{ background:#eefbe3; }} tr.mal td {{ background:#ffe9e3; }} .exp {{ margin-top:6px; font-size:14px; }}
.puntaje {{ font-weight:800; margin-left:10px; }}
ol.pasos li, ul.lista li, ol.boleto li {{ margin:6px 0; }} .fix {{ color:var(--morado-osc); font-weight:700; }}
.nota {{ color:var(--muted); font-size:14px; }}
a.boton {{ display:inline-block; text-decoration:none; color:var(--ink); background:var(--neon); border:2px solid var(--ink); border-radius:10px; box-shadow:3px 3px 0 var(--ink); padding:9px 16px; font-weight:800; margin:4px 6px 4px 0; }}
a.boton.blanco {{ background:var(--surface); }}
.frase {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; font-size:17px; }}
.frase input {{ font:16px var(--f-body); border:2px solid var(--ink); border-radius:8px; padding:6px 8px; min-width:180px; }}
textarea {{ width:100%; min-height:110px; font:15px/1.5 var(--f-body); border:2px solid var(--ink); border-radius:10px; padding:10px; }}
.ok {{ color:var(--ok); font-weight:800; }}
.ficha-card h2 {{ color:var(--morado-osc); }}
.ficha {{ display:grid; grid-template-columns:minmax(0,15em) minmax(0,1fr); border-top:2px solid var(--ink); }}
.ficha .fk, .ficha .fv {{ padding:9px 8px; border-bottom:1px solid #c9c5ba; }} .ficha .fk {{ font-weight:800; color:var(--morado-osc); }}
@media (max-width:820px) {{ .ficha {{ grid-template-columns:minmax(0,1fr); }} .ficha .fk {{ border-bottom:0; padding-bottom:0; }} }}
.desde {{ font-weight:700; }} .paso {{ font:400 15px var(--f-display); color:var(--morado-osc); margin:0 0 4px; }}
.opciones {{ margin:2px 0 8px; }}
</style>
</head>
<body>
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · S5 · patrones de diseño</small></div>
<h1>De tu caso manual a un <span class="acc">framework que se mantiene</span></h1>
<p class="lead">Las actividades de hoy, en el orden de la clase. Cada patrón tiene su <b>ficha</b> (el concepto), un <b>ejemplo</b> sacado del framework que empezamos en la S3, y una <b>práctica</b> corta. Todo funciona sin instalar nada.</p>
<nav class="top" aria-label="Actividades">
<a href="#leer">Cómo leer una prueba</a><a href="#ronda1">Ronda 1</a><a href="#pom">Page Object</a><a href="#factory">Factory</a><a href="#screenplay">Screenplay</a><a href="#singleton">Singleton</a><a href="#ronda3">La IA</a><a href="#proyecto">Tu proyecto</a><a href="#boleto">Boleto</a><a href="#real">Sitio real</a>
</nav>

<section id="leer">
<div class="card c-cyan">
<h2>Cómo leer una prueba <span class="acc">sin saber programar</span></h2>
<div class="meta"><span class="chip">2 min · para tener a mano toda la clase</span></div>
<p>No hace falta escribir TypeScript para entender una prueba. Con estas siete piezas se lee casi todo el framework.</p>
<table><tbody>{leyenda_html}</tbody></table>
</div>
<div class="card">
<h3>Los cuatro patrones, trabajando juntos en una sola prueba</h3>
<p>La prueba <code>CP-021</code> de <code>tests/recargas/recargas.spec.ts</code>, línea por línea. Antes de empezar, la sesión ya está abierta (un <b>flujo</b>) y la dirección del banco sale de la <b>configuración</b>.</p>
<table><tbody>{cp021_html}</tbody></table>
</div>
</section>

<section id="ronda1">
<div class="card c-lav">
<h2>Ronda 1 · ¿Dónde vive cada cosa de tu caso?</h2>
<div class="meta"><span class="chip">todos · 8 min</span>{A_LA_VEZ}</div>
<p>Este es un caso de prueba manual, como los que ya escriben. Para cada elemento, marquen dónde viviría en el framework. <b>Terminaron cuando las 7 filas tienen columna.</b> Después, «Revisar».</p>
<div style="border-top:2px solid var(--ink);border-bottom:2px solid var(--ink);padding:10px 0;margin:10px 0">
<h3 style="margin-top:0">CP-021 · Recarga de $60.000 a celular con código</h3>
<p><b>Precondición:</b> Ana tiene $1.500.000 en Ahorros. <b>Resultado esperado:</b> comprobante con «Valor: $60.000» y el saldo baja $60.000.</p>
</div>
{clasificador('r1', RONDA1, OPC_R1)}
<p class="nota">Pantalla = Page Object · Tarea = un paso de negocio (flujo o Screenplay) · Datos = Factory · Configuración = un solo lugar para el ambiente.</p>
</div>
</section>

<section id="pom">
{ficha(F['pom'])}
<div class="card">
<p class="paso">ejemplo resuelto · la pantalla «Transfer Funds» de ParaBank</p>
<p>Lo que la pantalla <b>tiene</b> son los localizadores <code>private</code>. Lo que <b>sabe hacer</b> es el método <code>transferir()</code>. La prueba nunca ve un localizador.</p>
{codigo(PAGINA_EJEMPLO)}
</div>
<div class="card c-lav">
<p class="paso">práctica · 6 min</p>
<h3 style="margin-top:0">La pantalla Recargas del Banco Demo: ¿lo tiene o lo sabe hacer?</h3>
<div class="meta">{A_LA_VEZ}</div>
{clasificador('pom1', POM_TIENE, [('T', 'Lo tiene'), ('S', 'Lo sabe hacer')])}
<h3>Comprobación: ¿esto es un buen Page Object?</h3>
{clasificador('pom2', POM_ES, [('si', 'Sí'), ('no', 'No')])}
</div>
</section>

<section id="factory">
{ficha(F['factory'])}
<div class="card">
<p class="paso">ejemplo resuelto · <code>src/datos/fabricaDeRecargas.ts</code></p>
<p><code>valida()</code> es el molde. <code>grande()</code> no repite nada: pide el molde y cambia solo el monto. Los tres puntos (<code>...cambios</code>) dejan que cada prueba cambie lo que le importa.</p>
{codigo(FABRICA_EJEMPLO)}
</div>
<div class="card c-lime">
<p class="paso">práctica · ronda 2 · salas · 2 tramos de 6 min</p>
<h2>Tu primera fábrica: transferencias</h2>
<p>El modelo (recargas) es el de arriba. Ustedes hacen la de transferencias, paso a paso. <b>Cada paso tiene su propia prueba</b> y no depende de los otros.</p>
<ol class="pasos"><li><b>Tramo 1 (6 min):</b> paso 1, <code>desdeCorriente()</code>, hasta ver 3 de 5 en verde. Al final, en el chat: «Sala X: n de 5».</li>
<li><b>Tramo 2 (6 min):</b> pasos 2 y 3, <code>alMontoMinimo()</code> y <code>aLaMismaCuenta()</code>.</li></ol>
<a class="boton" href="laboratorio-s5.html">Abrir el laboratorio de la S5</a>
<p class="nota">Con el repo instalado: <code>npx.cmd playwright test reto1 --project=retos-s05</code>.</p>
</div>
</section>

<section id="screenplay">
{ficha(F['screenplay'])}
<div class="card">
<p class="paso">ejemplo resuelto · la misma prueba, contada de dos formas</p>
<p>Las dos prueban «transferir entre mis cuentas» en ParaBank. <b>Page Object organiza pantallas. Screenplay organiza tareas.</b></p>
<div class="grid2"><div><h3>1 · Page Object</h3>{codigo(POM)}</div><div><h3>2 · Screenplay</h3>{codigo(SP)}</div></div>
</div>
<div class="card c-cyan">
<p class="paso">práctica · 7 min</p>
<h3 style="margin-top:0">a) El CP-021 contado por Ana, en 4 líneas</h3>
<p>Escríbanlo en palabras, como un caso manual: <b>Ana puede…</b> (con qué) · <b>Ana intenta…</b> (los pasos) · <b>Ana pregunta…</b> (lo que revisa) y el resultado esperado.</p>
<textarea aria-label="El CP-021 contado por Ana" placeholder="Ana puede…&#10;Ana intenta…&#10;Ana intenta…&#10;Ana pregunta… y debe ser…"></textarea>
{revelar('sp-modelo', 'Ver cómo queda con las piezas del repo', '<p>En palabras: <i>Ana puede usar la billetera · Ana intenta recargar $60.000 al 3001234567 · Ana pregunta su saldo disponible, y debe ser $1.440.000.</i></p>' + codigo(SP_MODELO) + '<p class="nota">Son las piezas reales del reto 2 (<code>src/screenplay/billetera/</code>). En la billetera de práctica la recarga grande no pide código: eso lo resuelve la tarea por dentro, no la prueba.</p>')}
<h3>b) Predice el error</h3>
<p>Si a Ana le quitamos la habilidad (<code>Actor.llamado('Ana')</code>, sin <code>.puede(...)</code>) y le pedimos que recargue, ¿qué dice Playwright?</p>
{revelar('sp-error', 'Ver el error real', codigo("Error: Ana no tiene la habilidad UsarLaBilletera. Dásela con .puede(...)") + '<p class="nota">Lo provocamos de verdad en el reto 2. El mensaje dice qué falta y cómo se arregla: así deben ser los errores de un buen framework.</p>')}
<h3>c) Comprobación: ¿qué pieza es?</h3>
<div class="meta">{A_LA_VEZ}</div>
{clasificador('sp', SP_PIEZAS, OPC_SP)}
</div>
</section>

<section id="singleton">
{ficha(F['singleton'])}
<div class="card">
<p class="paso">ejemplo resuelto · <code>src/config/entorno.ts</code></p>
<p>Un módulo de TypeScript se carga una sola vez: este objeto ya es único. Cada valor se puede cambiar con una variable de entorno sin tocar el código.</p>
{codigo(ENTORNO_EJEMPLO)}
</div>
<div class="card c-yel">
<p class="paso">práctica · 4 min</p>
<h3 style="margin-top:0">¿Una sola para toda la corrida, o una nueva cada vez?</h3>
<div class="meta">{A_LA_VEZ}</div>
{clasificador('si', SINGLE, OPC_SI)}
</div>
</section>

<section id="ronda3">
<div class="card c-peach">
<h2>Ronda 3 · El examen: esto lo escribió una IA</h2>
<div class="meta"><span class="chip">10 min · con las cuatro fichas</span><span class="chip">líderes: son el jurado</span></div>
<p>Le pedimos a una IA una prueba del CP-021, <b>sin dejarle ver el repo</b>. Este es su código, tal cual. Encuentren <b>3 defectos</b> y, para cada uno, <b>qué patrón viola</b> (miren el «No, cuando» de cada ficha). En el chat: <b>«línea 7 · viola Page Object»</b>.</p>
{codigo(IA_SIN, numerado=True)}
<p><button type="button" class="grande" data-revelar="defectos">Mostrar lo que encontramos</button></p>
<div id="defectos" hidden>
<h3>Lo que tiene (y lo que pasó al correrla)</h3>
<ul class="lista">{defectos_html}</ul>
<h3>El mismo pedido, con la IA dentro del repo</h3>
<p>Leyó <code>.github/copilot-instructions.md</code> y los Page Objects. <b>Resultado al correrla: verde.</b> Agregó sola el paso del código, porque lo encontró en la regla.</p>
{codigo(IA_CON)}
</div>
</div>
<div class="card c-yel">
<h3 style="margin-top:0">¿Y si le pedimos «déjamela en verde»?</h3>
<p>A otra IA le pedimos una prueba de regresión de una transferencia de $100.000 desde Corriente: «explora cómo se comporta la app hoy y déjamela en verde». No la dejó verde. Respondió:</p>
<p><i>«La app reporta total $100.400, pero a la Corriente solo le descontó $100.000. Si hubiera puesto 150.000, habría quedado verde, pero se estaría dando por bueno el comportamiento actual sin confirmar la regla de negocio.»</i></p>
<p><b>Pregunta para el chat:</b> ¿quién decide si el saldo correcto es $150.000 o $149.600? ¿La IA, la pantalla o la regla?</p>
<p class="nota">Una herramienta que graba «lo que ve» habría puesto $150.000 y la prueba saldría verde validando un bug. Las tres pruebas, con el resultado de correrlas, están en <code>docs/ia-s5/</code> del repo.</p>
<p class="nota"><b>Regla de uso:</b> solo el asistente que su empresa aprobó (por ejemplo, el Copilot corporativo). Si no hay uno aprobado, no se usa. Y a la IA solo va código de práctica o de un sitio público: nunca pantallas, datos ni logs del banco.</p>
</div>
</section>

<section id="proyecto">
<div class="card c-lav">
<h2>Tu proyecto del 3 de diciembre</h2>
<p>Escriban su frase y péguenla en el chat. Piensen en un caso de su trabajo, con su ID, pero <b>descríbanlo con palabras</b>: sin nombres de sistemas internos, sin datos ni pantallas reales.</p>
<div class="frase">Quiero automatizar <input id="p1" aria-label="El caso" placeholder="el caso CP-… de…"> en <input id="p2" aria-label="El sitio" placeholder="ParaBank, el Banco Demo…"> usando <input id="p3" aria-label="Los patrones" placeholder="Page Object, una fábrica…"></div>
<p><button type="button" class="grande" id="copiar">Copiar mi frase</button> <span id="copiado" class="ok"></span></p>
<p class="nota">¿No pueden instalar? Su entrega es una <b>revisión</b>: qué patrón usa cada pieza del framework (o de una prueba que escribió una IA), qué defectos tiene y cómo lo mejorarían. Las fichas de esta página son su guía.</p>
</div>
</section>

<section id="boleto">
<div class="card c-lime">
<h2>Boleto de salida</h2>
<div class="meta"><span class="chip">6 min · una pregunta por ficha</span>{A_LA_VEZ}</div>
<p>Respondan en el chat las cuatro letras, en orden, todos al mismo tiempo. Por ejemplo: <b>«a c b a»</b>.</p>
<ol class="boleto">{boleto_html}</ol>
{revelar('boleto-resp', 'Ver las respuestas', '<ol class="boleto">' + boleto_resp + '</ol><p class="nota">Lo que más falle es lo primero que repasamos en la S6.</p>')}
</div>
</section>

<section id="real">
<div class="card">
<h2>Un sitio real: ParaBank</h2>
<p>El mismo framework, en un banco de práctica real en internet. Cada prueba deja video, pantallazos y el paso a paso (trace): <b>la evidencia que hoy pegan a mano en Word</b>. Busquen la prueba roja: ¿por qué falló?</p>
<a class="boton" href="reportes/parabank/index.html">Ver el reporte de ParaBank</a><a class="boton blanco" href="https://parabank.parasoft.com/parabank/index.htm">Abrir ParaBank</a><a class="boton blanco" href="banco/index.html">Abrir el Banco Demo (Recargas)</a>
<h3>Bloqueos reales que encontramos (y cómo los maneja el framework)</h3>
<ul class="lista">
<li><b>Límite de peticiones.</b> ParaBank está detrás de Cloudflare: con demasiadas peticiones seguidas responde <b>HTTP 429</b> y bloquea 5 minutos. El framework va de a una prueba, con una pausa que vive en la configuración, y si llega un 429 lo dice claro.</li>
<li><b>Datos compartidos.</b> Cualquier persona del mundo usa ParaBank. Si todas las pruebas usan «el usuario de siempre», se pisan. La fábrica crea un cliente nuevo por corrida.</li>
<li><b>Bugs reales.</b> ParaBank deja transferir más de lo que hay y acepta montos negativos (PB-01 y PB-02). Las pruebas dicen lo que <i>debería</i> pasar.</li>
<li><b>Código extra y límite diario</b> en las recargas del Banco Demo, como en una billetera real.</li>
<li><b>Un tercero que no responde.</b> Si el operador no contesta, ¿se pierde la plata? En el Banco Demo, sí (BUG-04). Y con <code>page.route</code> se puede «apagar» un servicio para probar qué pasa.</li>
</ul>
<p class="nota">ParaBank es público: nunca escriban ahí datos reales.</p>
</div>
</section>
<p class="nota">Página de práctica del Bootcamp QA · Knot Academy. No carga nada de internet. Las fichas también están en el repo: <code>docs/patrones.md</code>.</p>
</div>
<script>
(function () {{
  document.querySelectorAll('table.clasif').forEach(function (tabla) {{
    tabla.querySelectorAll('tr').forEach(function (tr) {{
      tr.querySelectorAll('button').forEach(function (b) {{
        b.addEventListener('click', function () {{
          tr.querySelectorAll('button').forEach(function (x) {{ x.classList.remove('sel'); }});
          b.classList.add('sel'); tr.classList.remove('bien', 'mal');
        }});
      }});
    }});
  }});
  document.querySelectorAll('[data-revisar]').forEach(function (boton) {{
    boton.addEventListener('click', function () {{
      var id = boton.getAttribute('data-revisar');
      var filas = document.querySelectorAll('#t-' + id + ' tr');
      var bien = 0, marcadas = 0;
      filas.forEach(function (tr) {{
        var sel = tr.querySelector('button.sel');
        tr.classList.remove('bien', 'mal');
        tr.querySelector('.exp').hidden = false;
        if (!sel) return;
        marcadas++;
        if (sel.getAttribute('data-v') === tr.getAttribute('data-ok')) {{ bien++; tr.classList.add('bien'); }} else tr.classList.add('mal');
      }});
      document.getElementById('p-' + id).textContent = bien + ' de ' + filas.length + ' bien' + (marcadas < filas.length ? ' (faltan ' + (filas.length - marcadas) + ' por marcar)' : '');
    }});
  }});
  document.querySelectorAll('[data-revelar]').forEach(function (boton) {{
    boton.addEventListener('click', function () {{ document.getElementById(boton.getAttribute('data-revelar')).hidden = false; boton.hidden = true; }});
  }});
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

# ---------- docs/patrones.md: las mismas fichas, para leer en el repo ----------
md = ['# Patrones de diseño del framework (S5)', '',
      'Los cuatro patrones no son piezas nuevas: le ponen nombre y reglas a las capas que armamos en la S3 '
      '(ver [arquitectura.md](arquitectura.md)). Este archivo lo genera `laboratorio/generar/generar_actividades_s5.py` '
      'desde `fichas_s5.py`, la misma fuente de las actividades y del deck: si cambias una ficha, cámbiala allí.', '',
      '| Patrón | Capa de la S3 | Dónde verlo |', '|---|---|---|',
      '| Page Object | `src/paginas/` | `PaginaRecargas`, `src/sitios/parabank/paginas/` |',
      '| Factory | `src/datos/` | `fabricaDeRecargas`, `fabricaDeTransferencias`, `src/sitios/parabank/fabricaDeClientes.ts` |',
      '| Screenplay | `src/flujos/` → `src/screenplay/` | `Actor.ts`, `billetera/`, `src/sitios/parabank/screenplay/tareas.ts` |',
      '| Singleton | `src/config/` | `entorno.ts`, `src/sitios/parabank/entorno.ts` |',
      '| (Inyección de dependencias, S4) | `src/soporte/` | los fixtures: la prueba pide sus piezas |', '']
for f in FICHAS:
    md += [f'## {f["nombre"]}', '', f'*{f["desde"]}*', '', '| | |', '|---|---|']
    md += [f'| **{et}** | {f[k]} |' for k, et in FILAS_FICHA]
    md.append('')
md += ['## Cómo leer una prueba', '', '| Lo que ves | Cómo se lee |', '|---|---|']
md += [f'| {a} | {b} |' for a, b in LEYENDA]
md += ['', '## Los cuatro juntos: la prueba CP-021', '',
       'En `tests/recargas/recargas.spec.ts`. Se corre sola con `npx playwright test -g "CP-021"`.', '', '```ts']
md += [c for c, _ in CP021]
md += ['```', '', '| Línea | Qué patrón usa |', '|---|---|']
md += [f'| `{c.strip()}` | {n} |' for c, n in CP021 if n]
md += ['', '## Fuentes', '',
       '- Page Object: Martin Fowler, «PageObject» (martinfowler.com/bliki/PageObject.html).',
       '- Screenplay: Serenity/JS, «Screenplay Pattern» (serenity-js.org).',
       '- Factory y Singleton: Gamma, Helm, Johnson y Vlissides, *Design Patterns* (1994). En pruebas, la «fábrica de datos» '
       'es lo que también se llama *Object Mother* o *Test Data Builder*.', '']
(RAIZ / 'docs' / 'patrones.md').write_text('\n'.join(md), encoding='utf-8')
print('actividades_S5.html y docs/patrones.md listos')
