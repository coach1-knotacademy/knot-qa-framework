"""Genera laboratorio/web_real.html: el kit «web real» (una tienda de práctica y un formulario público real).

Decisiones en ../../../sesion_07/council_casos_reales.md (veredicto del presidente, 25 nov).
El código que muestra la página se LEE de los archivos del repo (el .feature, el Page Object y la prueba):
si cambia el código, se vuelve a generar y la página queda al día.
La evidencia (salida de las corridas y capturas) vive en laboratorio/generar/web_real_evidencia/.

En Pages se publica como web-real.html (scripts/construir-sitio.js). Los enlaces del sitio van relativos;
en la copia de ../para_enviar/ apuntan a la dirección completa de Pages, para que funcionen con doble clic.
No carga nada de internet (solo las fuentes de Google, y si no cargan se usan las del sistema).

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_web_real.py
"""
import base64, sys
from pathlib import Path

D = Path(__file__).parent
sys.path.insert(0, str(D))
# El mismo visual Knot de proyecto.html: el CSS, los tokens, el logo y el armazón de la página salen de ahí.
from generar_proyecto import RAIZ, PARA_ENVIAR, RELATIVO, pagina, boton_copiar, revelar, enlace, e  # noqa: E402
from fichas_s6 import a_html, PAGES, ESCALERA  # noqa: E402
from fichas_s7 import REPO  # noqa: E402

EVIDENCIA = D / 'web_real_evidencia'
TOOLSHOP = 'https://practicesoftwaretesting.com'
SITIO = {'proyecto': 'proyecto.html', 'actividades_s7': 'actividades-s7.html', 'lab_s6': 'laboratorio-s6.html', 'plantilla': 'plantilla.html'}

leer = lambda ruta: (RAIZ / ruta).read_text(encoding='utf-8').rstrip()
evidencia = lambda nombre: (EVIDENCIA / nombre).read_text(encoding='utf-8').rstrip()


def imagen(nombre, alt):
    datos = base64.b64encode((EVIDENCIA / nombre).read_bytes()).decode()
    tipo = 'jpeg' if nombre.endswith('.jpg') else 'png'
    return f'<img class="captura" src="data:image/{tipo};base64,{datos}" alt="{e(alt)}">'


def codigo(id_, texto, titulo, archivo=None):
    ver = f' <a class="boton blanco chico" href="{REPO}/blob/main/{archivo}">Ver en GitHub</a>' if archivo else ''
    return (f'<div class="cab"><div><p class="paso">{titulo}</p>' + (f'<p class="nota"><code>{e(archivo)}</code></p>' if archivo else '') +
            f'</div><div style="flex:none">{boton_copiar(id_)}{ver}</div></div><pre class="code" id="{id_}">{e(texto)}</pre>')


CSS_EXTRA = """
img.captura { display:block; width:100%; height:auto; border:2px solid var(--ink); border-radius:10px; margin:8px 0; background:#fff; }
figure { margin:0; } figcaption { font-size:14px; color:var(--muted); }
.salida { max-height:420px; }
.sello { display:inline-block; font:400 13px var(--f-display); border:2px solid var(--ink); border-radius:999px; padding:2px 10px; background:var(--lime); }
.sello.rojo { background:var(--peach); }
table.casos td:first-child { font-family:var(--f-display); white-space:nowrap; }
"""

# Los casos de la Toolshop, para hacerlos a mano en el navegador. (CP, lo que haces, lo que debe pasar)
A_MANO = [
  ('CP-501', 'En el catálogo, escribe <code>Pliers</code> en <b>Search</b> y pulsa <b>Search</b>.',
   'Sale el título «Searched for: Pliers» y todos los productos dicen «Pliers».'),
  ('CP-502', 'Vuelve al inicio (Home) y marca la categoría <b>Hammer</b> en «By category».',
   'Quedan solo martillos: todos los nombres dicen «Hammer» (Sledgehammer también cuenta).'),
  ('CP-503', 'Anota el precio de <b>Combination Pliers</b> en el catálogo y abre su detalle.',
   'El detalle muestra el mismo nombre, una descripción y el <b>mismo precio</b> del catálogo.'),
  ('CP-504', 'Abre <b>Pliers</b>, sube la cantidad a 2 con <b>+</b>, pulsa <b>Add to cart</b> y entra al carrito (el ícono de arriba).',
   'El carrito dice cantidad 2 y el total es 2 × el precio unitario ($12.01 → $24.02). <b>No sigas al pago.</b>'),
  ('CP-505', 'Abre <b>Contact</b> y pulsa <b>Send</b> sin escribir nada.',
   'Debajo de cada campo: «First name is required», «Email is required», «Message is required»…'),
  ('CP-506', 'En <b>Contact</b>, escribe el correo <code>ana.prueba@</code> y pulsa <b>Send</b>.',
   '«Email format is invalid».'),
  ('CP-507', 'Abre <b>Sign in</b> y pulsa <b>Login</b> sin escribir nada.',
   '«Email is required» y «Password is required».'),
]

# Lo que se probó en el sistema real. (prueba, qué verifica, resultado)
REAL_PROBADO = [
  ('A11Y-01 · getByLabel', '`getByLabel(\'Número de celular\')` no encuentra el campo, los tres campos no tienen nombre accesible y la causa es un id repetido.', 'hallazgo confirmado'),
  ('Formulario vacío', '«Continuar» está deshabilitado y la casilla antibots no está marcada.', 'verde'),
  ('Confirmación distinta', 'Con 3000000000 y 3000000001 sale «¡Ups! Esos dos números no coinciden, porfa revísalos.» y «Continuar» sigue deshabilitado. El mensaje no está asociado al campo (A11Y-02).', 'verde + hallazgo'),
  ('Celular corto', 'Con 300 sale «Este no parece un número de celular válido».', 'verde'),
  ('Valor mínimo', 'Con $0 sale «Debes ingresar mín. [$1]»; con $1 (el límite) el aviso desaparece.', 'verde'),
  ('Datos válidos', 'Con celular, confirmación y $10.000 válidos, «Continuar» sigue deshabilitado: falta el banco y el antibots, que no se tocan.', 'verde'),
]

NO_SE_AUTOMATIZA = [
  ('La casilla «Confirmo que soy una persona real»', 'Es un control antibots. Existe justo para que un robot no pase. Automatizarlo sería atacar el control, no probarlo. En un sistema propio, el equipo pide a desarrollo una llave de pruebas o un ambiente sin antibots; nunca se «salta».'),
  ('«Continuar» y el pago por PSE', 'Del otro lado hay un banco y dinero real. Pagar no es una prueba de validación: es una transacción. Eso se prueba en el ambiente de pruebas del dueño del sistema, con su permiso.'),
  ('Lo que pasa después (el banco, el comprobante)', 'Es producción de un tercero: no tenemos su permiso, ni datos de prueba, ni un ambiente para hacerlo. Ningún gerente firma evidencia sacada de producción ajena.'),
  ('Carga, estrés o muchas corridas', 'Cien corridas seguidas contra producción ajena parecen un ataque. Se corrió pocas veces, de a una prueba y con pausa.'),
]

ETICA = [
  '**Sin carga ni estrés.** Una prueba a la vez (`workers: 1`), con pausa, y pocas corridas. El sitio no es tuyo.',
  '**Sin enviar.** Solo validaciones: se mira lo que el formulario dice antes de mandar. Nunca «Continuar».',
  '**Sin datos reales.** Celulares de prueba evidentes, como `3000000000`. Nunca el tuyo ni el de un cliente.',
  '**Respeta el antibots.** Si el sistema pregunta «¿eres una persona?», ahí se detiene la automatización, a propósito.',
  '**Producción ajena no es tu ambiente de pruebas.** Lo que se muestra aquí es un ejemplo de lectura y validación. Para tu trabajo: el ambiente de pruebas de tu equipo y con permiso.',
  '**En el banco, nunca sus sistemas desde aquí.** Ni datos, ni pantallas, ni grabaciones del banco, tampoco en la IA.',
]

# La escalera de la S6, peldaño por peldaño, en los dos sitios. (en la Toolshop, en el formulario real)
ESCALERA_REAL = [
  ("`getByRole('button', { name: 'Add to cart' })` · `getByRole('checkbox', { name: 'Hammer' })`",
   "`getByRole('button', { name: 'Continuar' })` sí funciona: el botón tiene nombre. Los campos, no: salen como `spinbutton` sin nombre."),
  ("`getByLabel('Email address')` · `getByLabel('First name')`: cada campo tiene su `<label>`.",
   "`getByLabel('Número de celular')` → **0 elementos**. La etiqueta existe, pero apunta a un id repetido (el del envoltorio, no el del campo)."),
  ("`getByText('Email format is invalid')` para los mensajes de validación.",
   "`getByText('¡Ups! Esos dos números no coinciden, porfa revísalos.')` para el mensaje. Funciona."),
  ("`getByTestId('cart-total')`: el sitio trae `data-test` pactados. En la configuración: `testIdAttribute: 'data-test'`.",
   "No hay test-id. Lo que usamos: `getByRole('spinbutton').nth(0)`. Rol sí, nombre no: **depende del orden**, como `nth-child`. Por eso el Page Object revisa que haya exactamente 2 campos numéricos antes de escribir."),
  ("No hizo falta.",
   "`locator('input#phoneNumber')` también funcionaría, pero ese id ya está repetido una vez: no es un contrato. No se usa."),
]


def construir(base):
    s = lambda clave: enlace(SITIO[clave], base)
    corrida_toolshop = evidencia('corrida_toolshop.txt')
    corrida_real = evidencia('corrida_sistema_real.txt')
    error_label = evidencia('error_getbylabel.txt')
    diagnostico = evidencia('diagnostico_etiquetas.json')

    a_mano = ''.join(f'<tr><td data-k="CP">{cp}</td><td data-k="Qué haces">{haces}</td><td data-k="Qué debe pasar">{pasa}</td></tr>' for cp, haces, pasa in A_MANO)
    probado = ''.join(
        f'<tr><td data-k="Prueba"><b>{e(p)}</b></td><td data-k="Qué verifica">{a_html(q)}</td>'
        f'<td data-k="Resultado"><span class="sello{" rojo" if "hallazgo" in r else ""}">{e(r)}</span></td></tr>' for p, q, r in REAL_PROBADO)
    no_auto = ''.join(f'<tr><td data-k="Qué"><b>{e(q)}</b></td><td data-k="Por qué no">{a_html(p)}</td></tr>' for q, p in NO_SE_AUTOMATIZA)
    etica = ''.join(f'<li>{a_html(r)}</li>' for r in ETICA)
    escalera = ''.join(
        f'<li class="peldano p{n}"><span class="num">{n}</span><div><b>{e(nombre)}</b><br><code>{e(ejemplo)}</code>'
        f'<div class="grid2" style="margin-top:8px"><div><p class="paso">en la toolshop</p>{a_html(tienda)}</div>'
        f'<div><p class="paso">en el formulario real</p>{a_html(real)}</div></div></div></li>'
        for n, ((nombre, ejemplo, _), (tienda, real)) in enumerate(zip(ESCALERA, ESCALERA_REAL), 1))

    comandos = ('npx.cmd playwright test --project=toolshop\n'
                'npx.cmd playwright test --project=toolshop -g "CP-504"\n'
                'npx.cmd playwright test --project=toolshop --headed\n'
                'npx.cmd playwright show-report\n'
                'npm.cmd run revisar-escenarios -- especificaciones/toolshop.feature')

    cuerpo = f'''<h1>Kit · <span class="acc">web real</span></h1>
<p class="lead">Salir del Banco Demo: una tienda en línea de verdad, hecha para practicar, y el formulario público de un sistema real en producción. El mismo framework por capas, otro sitio, otro negocio.</p>
<p class="rotulo">Todo se trabaja en clase; avanzar por tu cuenta es opcional.</p>
<nav class="top" aria-label="Secciones">
<a href="#objetivo">Objetivo</a><a href="#a-mano">A mano</a><a href="#gherkin">Escenarios</a><a href="#codigo">El código</a><a href="#evidencia">Evidencia</a><a href="#correr">Correrlo</a><a href="#real">Sistema real</a><a href="#no">Qué no se automatiza</a><a href="#escalera">La escalera</a><a href="#etica">Ética</a><a href="#enlaces">Enlaces</a>
</nav>

<section id="objetivo">
<div class="card c-lav">
<p class="paso">el objetivo</p>
<p class="pregunta">Probar un sitio que no hicimos nosotros, con las mismas capas, y saber dónde parar.</p>
<div class="grid2" style="margin-top:12px">
<div><h2 style="font-size:24px;margin:0 0 6px">A · La Toolshop (tú)</h2><p><a href="{TOOLSHOP}">Practice Software Testing</a> es una tienda de herramientas pública, <b>hecha para practicar automatización</b>. Comercio electrónico, no banca: buscar, filtrar, ver el detalle, el carrito y los formularios. Siete casos, CP-501 a CP-507.</p></div>
<div><h2 style="font-size:24px;margin:0 0 6px">B · Un sistema real (el instructor)</h2><p>El formulario público de recarga de Nequi por PSE: <b>producción de un tercero, con dinero real</b>. Solo se miran sus validaciones, sin enviar nada. Lo corre el instructor en la demo; aquí ves qué se probó, qué se encontró y dónde se detiene.</p></div>
</div>
</div>
</section>

<section id="a-mano">
<h2>Primero, <span class="acc">a mano</span></h2>
<p>Sin instalar nada: abre el sitio en el navegador y recorre los casos como lo harías en tu trabajo. Cada fila es un CP con su resultado esperado.</p>
<div class="card">
<a class="boton" href="{TOOLSHOP}">Abrir la Toolshop</a>
<table class="apilar casos" style="margin-top:10px"><thead><tr><th>CP</th><th>Qué haces</th><th>Qué debe pasar</th></tr></thead><tbody>{a_mano}</tbody></table>
<p class="nota">El sitio es público y compartido: verás categorías y marcas raras («qa-…») que crean otras personas al practicar. No compres nada, no crees cuentas y no escribas datos reales.</p>
</div>
<div class="card c-yel">
<h3 style="margin-top:0">Si tu equipo te deja abrir F12</h3>
<ol class="pasos">
<li>Clic derecho sobre el buscador → <b>Inspeccionar</b>. Mira el <code>&lt;label&gt;</code> y el atributo <code>data-test</code>: son lo que usa el Page Object.</li>
<li>En la pestaña <b>Elements</b>, a la derecha, abre <b>Accessibility</b>: ves el <b>rol</b> y el <b>nombre</b> del elemento. Si el nombre está vacío, <code>getByRole</code> con nombre y <code>getByLabel</code> no lo van a encontrar.</li>
<li>Haz lo mismo en el carrito sobre la cantidad: se llama «Quantity for Pliers». Ese nombre accesible es el que busca la prueba.</li>
</ol>
<p class="nota">Si F12 está bloqueado, no pasa nada: el código y la evidencia de abajo muestran lo mismo.</p>
</div>
</section>

<section id="gherkin">
<div class="card">
{codigo("feature", leer("especificaciones/toolshop.feature"), "los escenarios en gherkin", "especificaciones/toolshop.feature")}
<p class="nota">Pasaron por el revisor de escenarios de la S7 sin errores: <code>npm.cmd run revisar-escenarios -- especificaciones/toolshop.feature</code>. El esperado sale de la regla (total = precio × cantidad), no de copiar lo que mostró la pantalla.</p>
</div>
</section>

<section id="codigo">
<h2>El código, <span class="acc">por capas</span></h2>
<p>Las mismas capas del framework de la S3, en <code>src/sitios/toolshop/</code>: la configuración (<code>entorno.ts</code>, con la dirección), los datos (<code>fabricaDeLaTienda.ts</code>), las páginas (<code>paginas/</code>, una por pantalla) y las piezas de cada prueba (<code>fixtures.ts</code>). La prueba solo dice el negocio.</p>
<div class="card">
{codigo("po", leer("src/sitios/toolshop/paginas/PaginaCatalogo.ts"), "el page object del catálogo", "src/sitios/toolshop/paginas/PaginaCatalogo.ts")}
<p class="nota">Fíjate en <code>todosLosProductosDicen</code>: la lista se actualiza <b>después</b> de buscar. Al explorar el sitio, el primer script buscó «Thor Hammer», leyó la lista <b>vieja</b> y abrió «Combination Pliers». La prueba lo resuelve con <code>expect.poll</code>, que vuelve a preguntar hasta que aparece la lista nueva. Es una espera real, no un <code>waitForTimeout</code>.</p>
<p class="nota">Y un error real de la primera corrida: el CP-501 se quedó minutos esperando el evento <code>load</code> de la página, porque un recurso de un tercero (chat, analítica) no terminaba de cargar. Por eso <code>abrir()</code> (en <code>PaginaToolshop.ts</code>) espera solo <code>domcontentloaded</code> y cada prueba espera lo que de verdad necesita. En un sitio real, eso pasa.</p>
</div>
<div class="card">
{codigo("prueba", leer("tests/toolshop/carrito.spec.ts"), "la prueba del carrito (cp-504)", "tests/toolshop/carrito.spec.ts")}
</div>
</section>

<section id="evidencia">
<h2>La evidencia <span class="acc">de la corrida</span></h2>
<div class="card">
<p class="paso">la salida de <code>npx.cmd playwright test --project=toolshop</code></p>
<pre class="code salida">{e(corrida_toolshop)}</pre>
<p class="nota">Cada prueba deja su pantallazo y su trace (<code>trace: 'on'</code>): en el reporte (<code>npx.cmd playwright show-report</code>) se abre paso a paso, con el texto de cada paso de Gherkin.</p>
</div>
<div class="grid2">
<figure class="card"><p class="paso">cp-504 · el carrito</p>{imagen("toolshop_carrito.jpg", "Carrito de la Toolshop con 2 unidades de Pliers y total de $24.02")}<figcaption>2 unidades de Pliers a $12.01: total $24.02. La prueba se detiene aquí: no paga.</figcaption></figure>
<figure class="card"><p class="paso">cp-505 · el contacto vacío</p>{imagen("toolshop_contacto.jpg", "Formulario de contacto con los mensajes de campos obligatorios")}<figcaption>Debajo de cada campo obligatorio, su mensaje (en la captura, el final del formulario: «Subject is required» y «Message is required»).</figcaption></figure>
</div>
</section>

<section id="correr">
<div class="card c-lime">
<div class="cab"><div><h2>Correrlo <span class="acc">con Node</span></h2><p>Si tu equipo tiene Node y el repo del curso. Necesita internet (es un sitio público) y va de a una prueba.</p></div><div style="flex:none">{boton_copiar("comandos", "Copiar los comandos")}</div></div>
<pre class="code" id="comandos">{e(comandos)}</pre>
<ul class="lista">
<li>El proyecto <code>toolshop</code> <b>no entra en la corrida por defecto</b> ni en la verificación de clase: solo corre si lo pides, como ParaBank. Así nada se cae porque falte internet.</li>
<li>¿No te deja descargar Chromium? Usa el Edge instalado: <code>$env:PW_CHANNEL="msedge"</code> en PowerShell antes del comando.</li>
<li>¿Otro idioma en la tienda? La configuración fija <code>locale: 'en-US'</code>: los textos esperados están en inglés porque así los muestra el sitio.</li>
</ul>
</div>
</section>

<section id="real">
<h2>El caso del <span class="acc">sistema real</span></h2>
<p>El formulario público de recarga de Nequi por PSE. Es producción de un tercero, con dinero real: solo se miraron sus validaciones, de a una prueba y pocas veces. Lo corre el instructor; nadie más lo necesita correr.</p>
<div class="card">
<h3 style="margin-top:0">Qué se probó</h3>
<table class="apilar"><thead><tr><th>Prueba</th><th>Qué verifica</th><th>Resultado</th></tr></thead><tbody>{probado}</tbody></table>
<pre class="code salida">{e(corrida_real)}</pre>
</div>
<div class="card c-peach">
<h3 style="margin-top:0">Qué se encontró: los campos no tienen nombre accesible</h3>
<p>En el árbol de accesibilidad, el celular, la confirmación y el valor salen como <code>spinbutton</code> y <code>textbox</code> <b>sin nombre</b>. Por eso lo primero que escribiría cualquiera (y lo que propone la IA) falla:</p>
<pre class="code prosa">{e(error_label)}</pre>
<p><b>La causa, en el HTML:</b> el <code>id</code> se repite. El componente <code>&lt;nequi-input id="phoneNumber"&gt;</code> y el <code>&lt;input id="phoneNumber"&gt;</code> de adentro tienen el mismo id, y <code>&lt;label for="phoneNumber"&gt;</code> apunta al primero, que es un envoltorio y no un campo. La prueba lo deja medido:</p>
<pre class="code">{e(diagnostico)}</pre>
<p><b>Lo que esto significa para una persona:</b> un lector de pantalla dice «campo de número» sin decir cuál. No es un problema de la prueba: <b>es un hallazgo de accesibilidad</b>. Y el mensaje de error tampoco está asociado al campo (sin <code>aria-describedby</code>): se ve, pero no se anuncia.</p>
<hr style="border:0;border-top:2px solid var(--ink);margin:14px 0 10px">
<p class="paso">la recomendación profesional</p>
<p style="margin:0"><b>«Pedir a desarrollo un <code>&lt;label for&gt;</code> que apunte al <code>&lt;input&gt;</code> (con un id único) o un <code>aria-label</code>. Arregla la prueba y, además, es accesibilidad.»</b> Mientras tanto, la prueba usa un localizador un peldaño más abajo y lo protege (ver la escalera).</p>
</div>
<div class="card">
<h3 style="margin-top:0">Otras cosas que vio la exploración (sin automatizar)</h3>
<ul class="lista">
<li>El aviso del mínimo dice «Debes ingresar mín. <b>[$1]</b>», con corchetes: parece una plantilla de texto sin terminar. Es cosmético; se reporta igual.</li>
<li>El formulario no muestra un valor máximo: $999.999.999 no da aviso. Si hay tope, se valida después de «Continuar», que no pulsamos. <b>No lo sabemos, y no lo inventamos.</b></li>
<li>Un celular de 10 dígitos que empieza por 1 no da aviso; uno de 11 dígitos queda inválido, pero sin mensaje. Son preguntas para el negocio, no bugs confirmados.</li>
</ul>
</div>
<figure class="card"><p class="paso">hasta aquí llega la automatización</p>{imagen("sistema_real_hasta_aqui.jpg", "Formulario de recarga con datos de prueba, la casilla antibots sin marcar y Continuar deshabilitado")}<figcaption>Captura tomada por la prueba, con el celular de prueba 3000000000. La casilla antibots sin marcar y «Continuar» deshabilitado. La marca es de su dueño: aquí solo es evidencia de la prueba.</figcaption></figure>
</section>

<section id="no">
<div class="card">
<h2>Qué <span class="acc">no se automatiza</span>, y por qué</h2>
<p>Saber dónde parar también es parte del trabajo de un QA. Esto se decidió antes de escribir la primera línea:</p>
<table class="apilar"><thead><tr><th>Qué</th><th>Por qué no</th></tr></thead><tbody>{no_auto}</tbody></table>
<p class="nota">El código lo hace cumplir: el Page Object del formulario real <b>no tiene</b> un método para pulsar «Continuar» ni para marcar la casilla. Si no existe el método, ninguna prueba lo puede hacer por error.</p>
</div>
</section>

<section id="escalera">
<h2>La escalera de la S6, <span class="acc">en un sitio real</span></h2>
<p>Los mismos cinco peldaños de los localizadores robustos. En la Toolshop se usan los de arriba; en el formulario real, el peldaño 2 no funciona y hay que bajar uno, sabiendo qué se arriesga.</p>
<ol class="escalera">{escalera}</ol>
</section>

<section id="etica">
<div class="card c-cyan">
<h2>Las reglas de <span class="acc">ética</span></h2>
<ul class="lista">{etica}</ul>
</div>
</section>

<section id="enlaces">
<h2>Lo que <span class="acc">vas a usar</span></h2>
<div class="card">
<a class="boton" href="{TOOLSHOP}">La Toolshop</a><a class="boton blanco" href="{REPO}/tree/main/src/sitios/toolshop">El código en GitHub</a><a class="boton blanco" href="{s("proyecto")}">El kit del proyecto final</a><a class="boton blanco" href="{s("actividades_s7")}">Actividades S7 · revisor de escenarios</a><a class="boton blanco" href="{s("lab_s6")}">Laboratorio S6 · la escalera</a>
<p class="nota">El sistema es de práctica; el problema, la técnica y la evidencia son reales.</p>
</div>
</section>'''
    html_ = pagina('Kit web real', 'kit · web real', cuerpo, generador='generar_web_real.py')
    return html_.replace('</style>', CSS_EXTRA + '</style>', 1)


if __name__ == '__main__':
    (RAIZ / 'laboratorio' / 'web_real.html').write_text(construir(''), encoding='utf-8')
    local = construir(PAGES)
    sueltos = RELATIVO.findall(local)
    assert not sueltos, f'web_real.html: enlaces relativos en la copia local: {sueltos}'
    assert 'claude.ai' not in local, 'web_real.html: enlace de claude.ai'
    if PARA_ENVIAR.is_dir():
        (PARA_ENVIAR / 'web_real.html').write_text(local, encoding='utf-8')
    print('web_real.html listo (y su copia en para_enviar/ con enlaces completos de Pages)')
