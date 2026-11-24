"""Las fichas de la S6 (configuración, localizadores y esperas): UNA sola fuente.

La usan: laboratorio/generar/generar_actividades_s6.py (actividades_S6.html y
docs/configuracion-y-localizadores.md) y el deck del instructor (sesion_06/generar_deck_S6.py).
Así nunca dicen cosas distintas.

Marcado mínimo: `código` y **negrita**. a_html() lo pasa a HTML; en Markdown queda tal cual.
"""
import html, re
from pathlib import Path

def a_html(texto):
    t = html.escape(texto, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    return re.sub(r'(?<![*\w])\*([^*\n]+)\*(?![*\w])', r'<i>\1</i>', t)

PAGES = 'https://coach1-knotacademy.github.io/knot-qa-framework/'
AMBIENTES = {
    'QA': PAGES + 'ambientes/qa',
    'UAT': PAGES + 'ambientes/uat',
}
POSTMAN = {
    'coleccion': PAGES + 'postman/Bootcamp-S6.postman_collection.json',
    'QA': PAGES + 'postman/QA.postman_environment.json',
    'UAT': PAGES + 'postman/UAT.postman_environment.json',
}
LABORATORIO = PAGES + 'laboratorio-s6.html'
PLANTILLA = PAGES + 'plantilla.html'
BANCO = PAGES + 'banco/'

# La frase con la que el instructor abre la sesión (una sola vez, sin repasar errores uno por uno).
FRASE_ABRIR = 'Como tester reporto mis propios defectos: hoy vamos a ver correr dos cosas que dije el jueves.'


def linea_escapada(raiz):
    """Número de línea del localizador que se escapó del Page Object en tests/recargas/recargas.spec.ts.

    Se calcula leyendo el archivo: si alguien agrega líneas arriba, la página no queda mintiendo.
    """
    lineas = (Path(raiz) / 'tests/recargas/recargas.spec.ts').read_text(encoding='utf-8').split('\n')
    for n, l in enumerate(lineas, 1):
        if "page.getByRole('button', { name: 'Recargar' })" in l:
            return n, l.strip()
    raise SystemExit('No encontré el localizador escapado en tests/recargas/recargas.spec.ts: revisa fichas_s6.linea_escapada')


# Las filas de cada ficha, siempre en el mismo orden (igual que en la S5).
FILAS = [
  ('problema', 'El problema que ya sufrías a mano'),
  ('idea', 'La idea, en una frase'),
  ('partes', 'Sus partes, en el repo'),
  ('si', 'Sí, cuando'),
  ('no', 'No, cuando'),
  ('lider', 'La frase para tu líder'),
  ('ia', 'Cómo pedírselo a la IA'),
]

FICHAS = [
  {
    'id': 'config', 'nombre': 'Configuración y ambientes', 'capa': 'src/config/',
    'desde': 'En la S3, `entorno.ts` ya era un solo lugar para la dirección del banco. En la S5 le pusimos nombre: Singleton. Hoy le ponemos los controles que exige un banco.',
    'problema': 'El caso pasa en QA y falla en UAT «porque allá la clave es otra». Alguien corre la regresión contra el ambiente equivocado. Y la clave de prueba termina escrita en un Excel, en un correo o en la evidencia.',
    'idea': 'Un ambiente es un **control**, no solo una URL. La prueba es la misma en QA y en UAT. Lo que cambia (dirección, usuario, clave y **datos**) vive en **un solo lugar**, **congelado** y **sin secretos en el código**.',
    'partes': '`src/config/ambientes.ts`: el catálogo `local | qa | uat` y `configurarAmbiente(nombre, variables)` · `src/config/entorno.ts`: el resultado, congelado con `Object.freeze` · las variables de la terminal: `$env:AMBIENTE = \'qa\'` y `$env:CLAVE_BANCO = \'...\'` · `.env.ejemplo`: los nombres de las variables, sin valores.',
    'si': 'Todo lo que cambia entre QA, UAT y preproducción: dirección, usuarios, claves, tiempos y los datos de cada ambiente. Es el *environment* de Postman, pero para todo el framework.',
    'no': 'Una clave escrita en el código o en un valor compartido de Postman, que se sincroniza con la nube. Un objeto de configuración que una prueba puede modificar, porque daña a la siguiente. Y **nunca** un ambiente `produccion` en el catálogo.',
    'lider': '«Las pruebas no pueden correr contra producción por error. Si falta una clave, se nota en el primer segundo. Y ningún secreto queda en el repo.»',
    'ia': '«La dirección y las claves salen de `entorno`. No las escribas en la prueba ni inventes una URL.»',
  },
  {
    'id': 'localizadores', 'nombre': 'Localizadores robustos', 'capa': 'src/paginas/',
    'desde': 'En la S5 los localizadores se fueron al Page Object: son lo que la pantalla **tiene**. Hoy vemos cuál elegir para que sobreviva a un rediseño.',
    'problema': 'Desarrollo «solo cambió el diseño» y se cae la regresión entera, aunque para el cliente la pantalla hace exactamente lo mismo.',
    'idea': 'Busca cada elemento **como lo busca una persona**: por su rol y su nombre, por la etiqueta del campo o por su texto. Si no hay nada visible y estable, usa un `data-testid` **pactado con desarrollo**. CSS y XPath, nunca.',
    'partes': '`getByRole(\'button\', { name: \'Recargar\' })` · `getByLabel(\'Número de celular\')` · `getByText(\'Recarga exitosa\')` · `getByTestId(\'saldo-disponible\')`. Todos son `private` dentro del Page Object, en `src/paginas/`.',
    'si': 'Siempre, empezando por el peldaño más alto de la escalera. Además pruebas accesibilidad: si `getByLabel` no encuentra el campo, un lector de pantalla tampoco.',
    'no': 'Clases CSS (cambian con el diseño), `nth-child` (cambia con el orden), XPath absoluto (cambia con cualquier contenedor) e ids que cambian con cada versión. Tampoco un localizador dentro de la prueba: vive en el Page Object.',
    'lider': '«Si rediseñan la pantalla y el negocio no cambió, la regresión sigue en verde. Si se cae, es porque algo cambió para el cliente.»',
    'ia': '«Localizadores por rol o etiqueta. Si no hay, pide un `data-testid`. Nada de CSS, XPath ni `nth-child`.»',
  },
  {
    'id': 'esperas', 'nombre': 'Esperas', 'capa': 'src/paginas/ y tests/',
    'desde': 'La pregunta del jueves: «¿el tiempo de espera se puede programar?». Sí se puede, pero casi nunca hace falta.',
    'problema': 'En manual uno espera «a que cargue» mirando la pantalla. En la prueba alguien escribe «espera 10 segundos». Si el sistema tarda 11, falla. Si tarda 1, se pierden 9 en cada prueba, todas las noches.',
    'idea': '**Playwright ya espera solo.** Cada acción espera a que el elemento esté visible y habilitado. Cada `await expect(...)` reintenta hasta que se cumpla (5 segundos por defecto). Tu trabajo es poner `await` en cada paso.',
    'partes': '`await`: cada acción del navegador devuelve una *promesa* («ya te respondo»), y `await` quiere decir «espera la respuesta antes de seguir» · las acciones (`click`, `fill`) esperan solas · las aserciones que reintentan: `await expect(locator).toHaveText(...)` · los tiempos: 5 s por `expect` y 30 s por prueba (`Test timeout of 30000ms exceeded`).',
    'si': 'Si un sistema es lento de verdad, el tiempo se sube **en un solo lugar** (`expect: { timeout }` en `playwright.config.ts`) o solo en esa aserción (`{ timeout: 10_000 }`). Y la lentitud se reporta como hallazgo.',
    'no': '`page.waitForTimeout(10000)`: hace la prueba lenta e inestable a la vez. Tampoco `expect(await locator.innerText())`, que lee una sola vez y no reintenta. Ni un paso sin `await`: a veces pasa por suerte, y eso es peor.',
    'lider': '«Las pruebas esperan lo justo: no fallan porque el sistema tardó un segundo más, ni pierden minutos esperando por si acaso.»',
    'ia': '«Sin `waitForTimeout`. Pon `await` en cada paso y usa `await expect(locator)` con aserciones que reintentan.»',
  },
]

# La escalera de localizadores, del más robusto al que nunca se usa. (peldaño, ejemplo, cuándo)
ESCALERA = [
  ('Rol + nombre', "getByRole('button', { name: 'Recargar' })",
   'Botones, enlaces, títulos y casillas: lo que la persona ve y para qué sirve. Es lo que recomienda la documentación de Playwright.'),
  ('Etiqueta', "getByLabel('Número de celular')",
   'Campos de un formulario que tienen su `<label>`.'),
  ('Texto', "getByText('Recarga exitosa')",
   'Mensajes y textos que no son controles.'),
  ('Test-id pactado', "getByTestId('saldo-disponible')",
   'Cuando no hay nada visible y estable, como un valor que cambia (el saldo). Se pacta con desarrollo y no cambia con el diseño.'),
  ('CSS o XPath: nunca', "locator('.btn-azul') · locator('form > input:nth-child(4)') · locator('xpath=/html/body/main/form/button')",
   'Dependen de cómo está pintada la pantalla, no de lo que hace. Se caen con el primer rediseño.'),
]

# Práctica: ordenar 5 localizadores de la pantalla Recargas. (código, peldaño correcto 1-5, explicación)
ORDENAR = [
  ("page.locator('xpath=/html/body/main/form/button')", '5',
   '<b>5 · nunca.</b> XPath absoluto: si agregan un contenedor, se cae.'),
  ("page.getByLabel('Número de celular')", '2',
   '<b>2 · etiqueta.</b> Lo que lee la persona junto al campo.'),
  ("page.getByTestId('saldo-disponible')", '4',
   '<b>4 · test-id pactado.</b> Sirve para el saldo, que no tiene un texto fijo. Sobrevive al rediseño porque se pactó con desarrollo.'),
  ("page.getByRole('button', { name: 'Recargar' })", '1',
   '<b>1 · rol y nombre.</b> Así busca el botón una persona, y también un lector de pantalla.'),
  ("page.getByText('Recarga exitosa')", '3',
   '<b>3 · texto.</b> Bien para un mensaje. Si el texto cambia, cambió algo que el cliente ve.'),
]

# «¿Cuál es robusta?»: tres maneras de revisar el saldo después de recargar. (código, 'si'|'no', explicación HTML)
# En los tres, saldo = paginaRecargas.saldoDisponible.
ROBUSTA_ANTES = 'const saldo = paginaRecargas.saldoDisponible;'
ROBUSTA = [
  ("await page.waitForTimeout(5000);\nexpect(await saldo.innerText())\n  .toBe('$1.490.000');", 'no',
   '<b>No.</b> Espera fija: siempre pierde 5 segundos, y si el banco tarda 6, falla igual. Además lee el saldo una sola vez.'),
  ("expect(await saldo.innerText())\n  .toBe('$1.490.000');", 'no',
   '<b>No.</b> Lee el saldo una sola vez y no reintenta. La corrimos contra el Banco Demo y falló con <code>Received: "…"</code>: el saldo todavía estaba cargando.'),
  ("await expect(saldo)\n  .toHaveText('$1.490.000');", 'si',
   '<b>Sí.</b> Reintenta hasta 5 segundos y pasa apenas aparece el valor. Si en 5 segundos no aparece, falla con un mensaje claro.'),
]

# «Predice qué pasa sin await»: el código y lo que pasó al correrlo (Playwright 1.63, Banco Demo local, 4 de 4 corridas).
SIN_AWAIT = {
  'codigo': "await paginaRecargas.recargar(fabricaDeRecargas.valida());\nexpect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000');   // sin await",
  'opciones': ['pasa: el saldo sí queda en $1.490.000',
               'falla, y el error no dice «te faltó el await»',
               'espera 5 segundos y pasa'],
  'ok': 'b',
  'error': 'Error: expect(locator).toHaveText(expected) failed\n\nLocator:  locator(\'#saldo\')\nExpected: "$1.490.000"\nReceived: ""\n  - waiting for locator(\'#saldo\')\n  - Protocol error (Runtime.callFunctionOn): Internal server error, session closed.',
  'lectura': 'Falla en una décima de segundo. Sin `await`, la prueba terminó y cerró el navegador antes de que la revisión acabara («session closed»). El error no menciona el `await`: hay que saber leerlo.',
  'peor': 'Y lo peor: si el que falta es el `await` de `recargar(...)`, la prueba **pasó** 4 de 4 veces, por suerte. Una prueba que pasa por suerte un día falla sin razón.',
}

# Lista de cotejo de una prueba (humana: la lee una persona, no una herramienta).
COTEJO = [
  'El nombre lleva el ID del caso (`CP-101 · …`) y dice qué se espera.',
  'La dirección sale de `entorno` (o de `baseURL`). No hay ninguna URL escrita en la prueba.',
  'No hay claves, tokens ni datos reales en el código.',
  'Los localizadores viven en el Page Object, no en la prueba.',
  'Cada localizador está en el peldaño más alto posible: rol y nombre, etiqueta, texto o test-id. Ni CSS, ni XPath, ni `nth-child`.',
  'Los datos salen de la fábrica, con nombre de negocio: nada de montos ni celulares a mano.',
  'Cada acción y cada `expect` sobre la página llevan `await`.',
  'No hay `waitForTimeout`: las aserciones son de las que reintentan (`await expect(locator)…`).',
  'El esperado sale de la regla de negocio, no de lo que mostró la pantalla. Si no se conoce: `// TODO: confirmar con la regla`.',
  'Usa solo lo que ya está en el proyecto: ningún `npm install` nuevo.',
]

# Una prueba de ejemplo para revisar con la lista de cotejo (escrita para esta actividad, del estilo de lo que
# devuelve un asistente sin contexto). (línea en la página, defecto, ítem de la lista que incumple)
PRUEBA_A_REVISAR = """import { test, expect } from '@playwright/test';

test('recarga con celular corto', async ({ page }) => {
  await page.goto('https://banco-demo.ejemplo/recargas');
  await page.locator('#usuario').fill('ana');
  await page.locator('#clave').fill('Clave123');
  await page.locator('button.principal').click();
  await page.waitForTimeout(8000);
  await page.locator('form > select').selectOption('Claro');
  await page.locator('form > input:nth-child(4)').fill('300123');
  await page.locator('#valor').fill('10000');
  await page.getByRole('button', { name: 'Recargar' }).click();
  expect(await page.locator('.error').innerText()).toContain('celular');
});"""
DEFECTOS_REVISAR = [
  ('Línea 3', 'El nombre no lleva el ID del caso ni el esperado completo.', 1),
  ('Línea 4', 'Dirección escrita a mano (y además inventada).', 2),
  ('Líneas 5–6', 'Usuario y clave escritos en el código; y entra sin el código del buzón.', 3),
  ('Líneas 5–13', 'Todos los localizadores dentro de la prueba.', 4),
  ('Líneas 5–11 y 13', 'Ids, una clase CSS, `form > select`, `nth-child` y `.error`: peldaño 5, se caen con el rediseño.', 5),
  ('Líneas 10–11', 'Celular y valor a mano: debía ser `fabricaDeRecargas.valida({ numero: \'300123\' })`.', 6),
  ('Línea 8', '`waitForTimeout(8000)`: 8 segundos perdidos en cada corrida.', 8),
  ('Línea 13', 'Lee una vez y no reintenta. Y «contiene celular» no es el esperado de la regla: el mensaje completo es «El celular debe tener 10 dígitos y empezar por 3».', 9),
]

# Boleto de salida de la S6. (pregunta, opciones, letra correcta, por qué)
BOLETO = [
  ('Mañana las mismas pruebas deben correr en UAT. ¿Qué cambias?',
   ['cada prueba', 'el Page Object', 'la variable `AMBIENTE` (la configuración)'], 'c',
   'Configuración: la prueba es la misma; cambia el ambiente, en un solo lugar.'),
  ('¿Dónde va la clave de UAT?',
   ['en una variable de la terminal o como valor local de Postman, sin compartir', 'en `entorno.ts`, como valor por defecto', 'como valor compartido del ambiente de Postman'], 'a',
   'Fuera del código y fuera de lo que se comparte: el valor compartido de Postman se sincroniza con la nube.'),
  ('Llega el rediseño de Recargas. ¿Qué localizador sigue funcionando?',
   ["`locator('#saldo')`", "`locator('form > button:nth-child(7)')`", "`getByRole('button', { name: 'Recargar' })`"], 'c',
   'Rol y nombre: el diseño cambió, el botón sigue siendo un botón que dice «Recargar».'),
  ('El saldo tarda 2 segundos en aparecer. ¿Qué es lo correcto?',
   ['`await page.waitForTimeout(3000)`', "`await expect(saldo).toHaveText('$1.490.000')`", "`expect(await saldo.innerText()).toBe('$1.490.000')`"], 'b',
   'La aserción reintenta sola hasta 5 segundos. La espera fija pierde tiempo, y la lectura única no reintenta.'),
]

# Los casos de prueba del Banco Demo para el ejercicio «tu CP → prueba». Nunca casos del ALM del banco.
# Cada fila de la traducción: (tipo, lo que dice el caso, cómo queda en la prueba).
TIPOS = {
  'ambiente': 'ambiente → entorno',
  'pre': 'precondición → tarea',
  'paso': 'paso → localizador',
  'dato': 'dato → fábrica',
  'esperado': 'esperado → expect',
}
_AMB = ('ambiente', 'En el ambiente de pruebas (local, QA o UAT)', '`entorno.urlBase`, que llega a la prueba como `baseURL`. La prueba no escribe la dirección: `$env:AMBIENTE = \'qa\'` la cambia.')
_PRE = ('pre', 'Ana inició sesión (usuario, clave y el código del buzón)', '`await abrirConSesion(page, cliente, usuarios.ana)`: una **tarea**, porque junta login, SMS y código.')
_ABRIR = ('paso', 'Ir a «Recargar celular»', '`await paginaRecargas.abrir()`')
_RECARGAR = ('paso', 'Elegir operador, escribir celular y valor, y pulsar «Recargar»',
             '`await paginaRecargas.recargar(recarga)`. Por dentro: `getByLabel(\'Operador\')`, `getByLabel(\'Número de celular\')`, `getByLabel(\'Valor de la recarga\')` y `getByRole(\'button\', { name: \'Recargar\' })`.')

CPS = [
  {
    'id': 'CP-101', 'titulo': 'Recarga normal a celular',
    'pre': 'Ana inició sesión. Saldo de Ahorros: $1.500.000.',
    'pasos': ['Ir a «Recargar celular».', 'Elegir Claro, escribir el celular 3001234567 y el valor $10.000.', 'Pulsar «Recargar».'],
    'esperado': 'Comprobante con «Recarga exitosa». El saldo de Ahorros queda en $1.490.000.',
    'filas': [_AMB, _PRE, _ABRIR,
              ('dato', 'Claro, 3001234567, $10.000', '`fabricaDeRecargas.valida()`'),
              _RECARGAR,
              ('esperado', '«Recarga exitosa»', "`expect(await paginaRecargas.esperarResultado()).toContain('Recarga exitosa')`"),
              ('esperado', 'Saldo de Ahorros: $1.490.000', "`await expect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000')`")],
  },
  {
    'id': 'CP-102', 'titulo': 'Recarga de más de $50.000 con código',
    'pre': 'Ana inició sesión. Saldo de Ahorros: $1.500.000.',
    'pasos': ['Ir a «Recargar celular».', 'Elegir Claro, escribir el celular 3001234567 y el valor $60.000.', 'Pulsar «Recargar».',
              'Leer el código de seguridad en el buzón de SMS, escribirlo y pulsar «Confirmar recarga».'],
    'esperado': 'Antes de recargar, el banco pide el «Código de seguridad». Con el código del buzón: comprobante con «Valor: $60.000» y saldo de Ahorros en $1.440.000.',
    'filas': [_AMB, _PRE, _ABRIR,
              ('dato', 'Claro, 3001234567, $60.000', '`fabricaDeRecargas.grande()`: «grande» quiere decir más de $50.000.'),
              _RECARGAR,
              ('esperado', 'Aparece el campo «Código de seguridad»', '`await expect(paginaRecargas.campoCodigo).toBeVisible()`'),
              ('paso', 'Leer el código del buzón y confirmar',
               '`await paginaRecargas.confirmar(await cliente.leerCodigo(usuarios.ana.usuario))`. Junta pantalla y buzón: si se repite, es una **tarea** («recargar con código»).'),
              ('esperado', 'Comprobante con «Valor: $60.000»', "`expect(await paginaRecargas.esperarResultado()).toContain('Valor: $60.000')`"),
              ('esperado', 'Saldo de Ahorros: $1.440.000', "`await expect(paginaRecargas.saldoDisponible).toHaveText('$1.440.000')`")],
  },
  {
    'id': 'CP-103', 'titulo': 'Celular de 6 dígitos',
    'pre': 'Ana inició sesión. Saldo de Ahorros: $1.500.000.',
    'pasos': ['Ir a «Recargar celular».', 'Elegir Claro, escribir el celular 300123 y el valor $10.000.', 'Pulsar «Recargar».'],
    'esperado': 'Mensaje «El celular debe tener 10 dígitos y empezar por 3». El saldo no cambia: $1.500.000.',
    'filas': [_AMB, _PRE, _ABRIR,
              ('dato', 'Claro, 300123, $10.000', "`fabricaDeRecargas.valida({ numero: '300123' })`: solo se escribe lo que le importa a esta prueba."),
              _RECARGAR,
              ('esperado', '«El celular debe tener 10 dígitos y empezar por 3»', "`expect(await paginaRecargas.esperarResultado()).toBe('El celular debe tener 10 dígitos y empezar por 3')`"),
              ('esperado', 'El saldo no cambia: $1.500.000', "`await expect(paginaRecargas.saldoDisponible).toHaveText('$1.500.000')`")],
  },
  {
    'id': 'CP-104', 'titulo': 'Recarga por encima del máximo',
    'pre': 'Ana inició sesión. Saldo de Ahorros: $1.500.000.',
    'pasos': ['Ir a «Recargar celular».', 'Elegir Claro, escribir el celular 3001234567 y el valor $150.000.', 'Pulsar «Recargar».'],
    'esperado': 'Mensaje «La recarga máxima es $100.000». No pide código (el máximo se revisa antes). El saldo no cambia: $1.500.000.',
    'filas': [_AMB, _PRE, _ABRIR,
              ('dato', 'Claro, 3001234567, $150.000', '`fabricaDeRecargas.valida({ monto: 150_000 })`'),
              _RECARGAR,
              ('esperado', '«La recarga máxima es $100.000»', "`expect(await paginaRecargas.esperarResultado()).toBe('La recarga máxima es $100.000')`"),
              ('esperado', 'No pide código', '`await expect(paginaRecargas.campoCodigo).toBeHidden()`'),
              ('esperado', 'El saldo no cambia: $1.500.000', "`await expect(paginaRecargas.saldoDisponible).toHaveText('$1.500.000')`")],
  },
  {
    'id': 'CP-105', 'titulo': 'Límite diario de recargas',
    'pre': 'Ana inició sesión y hoy ya recargó $200.000 (4 recargas de $50.000).',
    'pasos': ['Ir a «Recargar celular».', 'Elegir Claro, escribir el celular 3001234567 y el valor $1.000.', 'Pulsar «Recargar».'],
    'esperado': 'Mensaje «Superaste el límite diario de recargas ($200.000)».',
    'filas': [_AMB, _PRE,
              ('pre', 'Hoy ya recargó $200.000 (4 de $50.000)',
               '4 veces `await cliente.recargar(fabricaDeRecargas.valida({ monto: 50_000 }))`: se prepara por API, que es más rápido, y se verifica en la pantalla.'),
              _ABRIR,
              ('dato', 'Claro, 3001234567, $1.000', '`fabricaDeRecargas.valida({ monto: 1_000 })`'),
              _RECARGAR,
              ('esperado', '«Superaste el límite diario de recargas ($200.000)»',
               "`expect(await paginaRecargas.esperarResultado()).toBe('Superaste el límite diario de recargas ($200.000)')`")],
  },
  {
    'id': 'CP-106', 'titulo': 'El operador no responde',
    'pre': 'Ana inició sesión. Saldo de Ahorros: $1.500.000.',
    'pasos': ['Ir a «Recargar celular».', 'Elegir Claro, escribir el celular de prueba 3000000504 (el operador no responde) y el valor $20.000.', 'Pulsar «Recargar».'],
    'esperado': 'Mensaje «El operador no responde. Intenta más tarde.». El cliente no pierde la plata: el saldo de Ahorros sigue en $1.500.000.',
    'nota': 'Hoy esta prueba sale **roja**: el Banco Demo descuenta el saldo igual (BUG-04). Es un rojo **del sistema**, no del script: el esperado sale de la regla, no de lo que hace la pantalla.',
    'filas': [_AMB, _PRE, _ABRIR,
              ('dato', 'Claro, 3000000504, $20.000', '`fabricaDeRecargas.aOperadorCaido({ monto: 20_000 })`: el número de prueba vive en la fábrica.'),
              _RECARGAR,
              ('esperado', '«El operador no responde. Intenta más tarde.»', "`expect(await paginaRecargas.esperarResultado()).toBe('El operador no responde. Intenta más tarde.')`"),
              ('esperado', 'El saldo sigue en $1.500.000', '`expect(await cliente.saldoDeAhorros()).toBe(1_500_000)`: el saldo real del servicio, no el que pinta la página.')],
  },
]
