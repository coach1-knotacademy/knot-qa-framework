"""La S9 (¿rojo del sistema, del script o del ambiente?) y el ensayo de la S10: UNA sola fuente.

La usan:
  - laboratorio/generar/generar_actividades_s9.py  → actividades_S9.html, plantilla de láminas y docs/triage.md
  - laboratorio/generar/generar_proyecto.py        → la guía de estudio (S9)
  - ../sesion_09/generar_deck_S9.py                → el deck del instructor
Decisiones en ../../../sesion_09/council_S9.md (veredicto). Salas ALEATORIAS y sin capitán (decisión del instructor, 26 nov).

Marcado mínimo: `código`, **negrita** y *cursiva*. a_html() lo pasa a HTML; en Markdown queda tal cual.
"""
from fichas_s6 import a_html, PAGES  # noqa: F401
from fichas_s7 import REPO, PROYECTO, GUIA  # noqa: F401
from fichas_s8 import ACTIVIDADES as ACTIVIDADES_S8, CPS_PAGINA, VIA_ESPECIFICADOR  # noqa: F401

ACTIVIDADES = PAGES + 'actividades-s9.html'
LAMINAS = PAGES + 'laminas-s10.html'
REPORTE_TRIAGE = PAGES + 'reportes/triage/index.html'

TEMA = 'Errores, registro y CI: ¿rojo del sistema, del script o del ambiente?'
OBJETIVO = 'Ante un rojo, decir en qué caja va (sistema, script o ambiente) y con qué evidencia (el trace, la consola o la regla del negocio).'
IDEA_FUERZA = 'Un rojo no es un bug hasta que sabes de quién es.'
FRASE_GANCHO = ('Daily del martes: «en desarrollo pasa y en QA no». El dev dice ambiente, infra dice script y QA dice bug. '
                'Hoy salen sabiendo quién tiene razón y con qué evidencia.')
FRASE_REGLA = 'Antes de abrir un bug, díganme la caja y la línea que lo prueba.'
FRASE_FLAKY = 'Un reintento que pasa no es un verde: es un aviso de *flaky*. Pregunten siempre cuántas pasaron al segundo intento.'
FRASE_ENSAYO = 'Este ensayo no se califica: es la última vez que alguien les puede decir qué falta, a tiempo para arreglarlo aquí, hoy.'
FRASE_CIERRE = ('Un rojo no es un bug hasta que sabes de quién es. Y una prueba no es tuya hasta que la puedes contar en seis minutos. '
                'El jueves 10, cuéntenla.')
FRASE_CHAT = 'Lo que no está en el chat principal no pasó.'

# ─────────────────────────── 6:00 · La línea de llegada (autodiagnóstico) ───────────────────────────
LLEGADA = ('En el chat, una línea: **confirmo: individual o en equipo con ___ · del criterio de listo me falta: ___** '
           '(los números del 1 al 7 del kit de proyecto).')
LLEGADA_EJEMPLO = 'confirmo: en equipo con ___ · del criterio de listo me falta: 5, 6'

# ─────────────────────────── 6:15 · La ficha de las tres cajas ───────────────────────────
FICHA = {
  'id': 'triage', 'titulo': 'Triage: sistema, script o ambiente', 'color': 'peach',
  'problema': 'Un rojo llega al daily y cada uno culpa a otro: el desarrollador dice ambiente, infraestructura dice script, QA dice bug. Se pierde un día, y el bug real (si lo hay) sigue ahí.',
  'idea': 'Todo rojo cae en una de **tres cajas**, y la caja se decide con **evidencia**, no con intuición: **sistema** (el esperado sale de la regla y el sistema no la cumple), **script** (la prueba está mal: localizador, `await`, dato) o **ambiente** (lo que la prueba necesita no está: una clave, un servicio, tiempo).',
  'partes': '`tests/triage-s09/` (los 4 rojos, en el proyecto `triage`, que solo corre si se pide) · `src/soporte/registro.ts` (el registro de la corrida con `test.info().attach`) · `src/soporte/hallazgos.ts` (el bug conocido, registrado) · el trace y el reporte.',
  'si': 'Hay un rojo y alguien tiene que decidir a quién va el ticket: a desarrollo, a QA o a infraestructura.',
  'no': 'Se «arregla» un rojo subiendo el *timeout*, agregando `retries` o con `test.slow()` sin saber la caja: eso lo esconde.',
  'lider': 'Un rojo sin caja es ruido; con caja y evidencia es un reporte. El ticket lleva la caja, la línea que lo prueba y el ID del caso.',
  'ia': '«Este es el mensaje de error y el último paso del trace de una prueba de Playwright: ___. ¿En qué caja va (sistema, script o ambiente)? Dame la línea exacta que lo prueba y qué evidencia falta para estar seguro. No inventes lo que no está en el texto.»',
}
CAJAS = [
  ('Sistema', 'El esperado sale de la **regla del negocio** y el sistema no la cumple.', 'Esperado contra obtenido de una regla: `Expected: 1500000 · Received: 1480000`.', 'Ticket a desarrollo, con la regla y el ID del caso.'),
  ('Script', 'La **prueba** está mal: el localizador, el `await`, el dato o el esperado mal escrito.', 'El localizador no aparece: `waiting for locator(...)` hasta `Test timeout of 30000ms exceeded`, y en la captura el elemento sí está, en otro lugar de la pantalla.', 'Lo arregla QA: es su código.'),
  ('Ambiente', 'Lo que la prueba **necesita** no está: una clave, un servicio, la red o el tiempo de respuesta.', 'Falta una clave, `401`, conexión rechazada, o en la red del trace una petición sin respuesta (pendiente o cancelada).', 'Ticket a infraestructura o al dueño del servicio, con la hora y la petición.'),
]

# ¿En qué caja va? (a la vez, por el mensaje de error; correctas mezcladas: b, c, a)
EN_QUE_CAJA = [
  ("`Error: Falta CLAVE_BANCO para el ambiente qa. Defínela en la terminal` — y no corrió ninguna prueba", ['sistema', 'ambiente', 'script'], 'b',
   'Falló al cargar la configuración, en el segundo cero: no hay trace. Lo que falta es del ambiente. Fallar de inmediato (S6) es lo correcto.'),
  ("`waiting for locator('xpath=/html/body/main/form[1]/select')` … `Test timeout of 30000ms exceeded`, y en la captura la lista «Operador» está ahí, en otro contenedor", ['sistema', 'ambiente', 'script'], 'c',
   'La lista está, en otro lugar: el XPath dependía de cómo estaba armada la pantalla. El localizador es de la prueba: script. Con `getByLabel(\'Operador\')` no se habría roto.'),
  ('`Expected: 1500000 · Received: 1480000` en el saldo, después de un operador que no responde', ['sistema', 'script', 'ambiente'], 'a',
   'La regla dice que el cliente no pierde la plata. El sistema no la cumple: BUG-04, sistema.'),
]

# ─────────────────────────── Los 4 rojos (tests/triage-s09/, proyecto «triage») ───────────────────────────
ROJOS = [
  {'n': 1, 'caja': 'sistema', 'titulo': 'El operador no responde y el saldo baja',
   'como': 'El CP-106 **sin** la marca `hallazgoEsperado`: el operador simulado no responde (número de pruebas `3000000504`).',
   'evidencia': 'La **regla del negocio**: el cliente no pierde la plata. Esperado $1.500.000, obtenido $1.480.000 (por API, el saldo real). En la red, `POST recargas` responde 504: ese es el escenario del caso (el operador no responde), no la falla. La caja la decide la regla.',
   'aprende': 'En la suite, el mismo caso sale como **falla esperada**: es el cuarto estado. Un bug conocido, registrado con su ID (BUG-04), que no ensucia la corrida y avisa si un día se arregla.'},
  {'n': 2, 'caja': 'script', 'titulo': 'El rediseño rompe un localizador',
   'como': '`REDISENO=1` cambia la pantalla y la prueba usa `PaginaRecargasHeredada`, con los localizadores de antes.',
   'evidencia': 'El **trace**: `selectOption` espera un XPath que nunca aparece, hasta que vence el límite de la prueba (30 s). En la captura, la lista «Operador» está ahí, con el mismo nombre, en otro contenedor.',
   'aprende': 'La escalera de la S6: rol y nombre sobreviven al rediseño; el localizador frágil, no.'},
  {'n': 3, 'caja': 'ambiente', 'titulo': 'Falta la clave',
   'como': 'Se corre contra el ambiente `qa` sin la clave en la terminal: `npm.cmd run triage:sin-clave`.',
   'evidencia': '**No hay trace**: todo cae en el segundo cero y la **consola** dice qué clave falta. Esa ausencia también es evidencia.',
   'aprende': 'Fallar de inmediato (S6) y el `throw` de la configuración: falla la corrida entera, no una prueba.'},
  {'n': 4, 'caja': 'ambiente', 'titulo': 'El saldo tarda más que el expect',
   'como': '`page.route` demora el servicio de saldos 7 segundos; el `expect` espera 5.',
   'evidencia': 'En la **red** del trace, la petición de saldos (`GET cuentas`) no tiene respuesta: sale cancelada, sin duración ni tamaño, y el `expect` venció a los 5 s. El servicio no respondió a tiempo. El localizador `#saldo` sí se encontró (el call log dice «14 × locator resolved»): no es del script. Con `--retries=1` y la demora solo en el primer intento, el reporte dice **1 flaky**.',
   'aprende': 'Ni `test.slow()` (triplica el *timeout* de la prueba, no el del `expect`) ni subir el *timeout* lo arreglan: es un ticket al ambiente, con la hora y la petición.'},
]
SALAS = [('Sala 1', [1, 4]), ('Sala 2', [2, 3]), ('Sala 3', [3, 4]), ('Sala 4', [1, 2])]
SALAS_NOTA = 'Cada rojo lo ven dos salas: si no coinciden en la caja, ese es el debate de la vuelta.'
LINEA_SALA = 'Sala X · rojo N · caja: ___ · evidencia: ___ (la línea del trace, de la consola o la regla)'
ROLES_SALA = ('Salas **aleatorias**. **Pega en el chat** quien va primero en orden alfabético; **cuida el reloj** el segundo. '
              'Si a los 60 segundos nadie pegó, pega el siguiente.')
ANUNCIO_8 = 'Minuto 8: peguen en el chat de la sala el primer rojo con su caja y su evidencia (la línea de la página).'
ANUNCIO_12 = 'Minuto 12: faltan 3 minutos. Peguen el segundo rojo. Al volver, la misma persona pega los dos en el chat principal.'
CRITERIO_SALA = '**Terminaron cuando los dos rojos tienen caja y evidencia** en el chat de la sala, con la línea pegable.'

# El mírame (6:25, corte duro en el minuto 10)
MIRAME = [
  ('Rojo 2 con su trace', '`npx.cmd playwright test --project=triage -g "rojo 2"` (tarda unos 30 s) y abrir el trace', 'El XPath que espera y la captura donde la lista «Operador» está en otro contenedor.'),
  ('Rojo 4 con su trace', '`npx.cmd playwright test --project=triage -g "rojo 4"`', 'La pestaña de red: la petición de saldos sin respuesta cuando vence el `expect`.'),
  ('El flaky', '`npx.cmd playwright test --project=triage -g "flaky" --retries=1`', 'El reporte dice «1 flaky»: falló la primera vez y pasó al reintentar. En el repo, `retries` es 0: aquí se muestra a propósito.'),
]
UNA_LINEA = [
  ('`test.info().attach`', 'Pega un valor o un archivo a la prueba y el reporte lo muestra: es el **registro de la corrida** (`registrar()` en `src/soporte/registro.ts`). No es un log que se imprime: queda con la prueba.'),
  ('`test.slow()`', 'Triplica el *timeout* de **la prueba**, no el del `expect`, que sigue en 5 s. Es para una prueba lenta a propósito, no para tapar un rojo.'),
  ('`retries`', 'En el repo es 0. En un pipeline se usa `process.env.CI ? 2 : 0`, y cada *flaky* es una alerta con ticket, no un verde.'),
]
FUENTES_FRASES = [
  ('Flaky: falló la primera vez y pasó al reintentar.', 'playwright.dev/docs/test-retries'),
  ('on-first-retry graba el trace solo en el primer reintento.', 'playwright.dev/docs/trace-viewer'),
  ('trace.playwright.dev carga el trace en tu navegador y no lo envía a ningún servidor.', 'playwright.dev/docs/trace-viewer'),
  ('test.slow() triplica el timeout de la prueba, no el del expect.', 'playwright.dev/docs/test-annotations'),
  ('El expect espera 5 segundos por defecto.', 'playwright.dev/docs/test-timeouts'),
  ('attach pega un valor o un archivo a la prueba, y el reporte lo muestra.', 'playwright.dev/docs/api/class-testinfo'),
  ('test.fail(): la prueba tiene que fallar; si un día pasa, avisa.', 'playwright.dev/docs/test-annotations'),
]
SIN_INSTALAR = [
  'Las **capturas numeradas** de cada rojo en esta página: la acción, el error y la red.',
  'El **reporte del triage** publicado en Pages: abre el trace de cada rojo sin subir nada.',
  'Extra: el zip de cada trace en **trace.playwright.dev** (se abre en tu navegador; puede estar bloqueado en tu equipo).',
]

# ─────────────────────────── 7:07 · Tu proyecto (20 min fijos, en la sala principal) ───────────────────────────
PROYECTO_S9 = ('**Una falla provocada en tu CP y clasificada**: cambia una fila de tu tabla de la S8 (un esperado, un dato) o rompe algo a propósito, '
               'mira el rojo y di su caja con su evidencia. Arma tu **lámina de la falla** con la plantilla. '
               'Pega en el chat principal: «Mi CP · falla: ___ · caja: ___ · evidencia: ___».')
PROYECTO_ESPECIFICADOR = 'Si vas por la vía de especificador, ya tienes tu prueba hecha: cambia una fila de tus Ejemplos y predice el rojo antes de correrlo.'

# ─────────────────────────── 7:27 · El modelo del instructor (3 min, cronometrado) y el ensayo ───────────────────────────
MODELO = [
  ('El problema', 'Pruebo las recargas a celular; el riesgo es que el cliente pierda plata si el operador falla.'),
  ('La evidencia', 'El mapa de capas con mi pieza resaltada, el reporte con el CP-106 y la línea que lo prueba: esperado $1.500.000, obtenido $1.480.000.'),
  ('La decisión', 'Lo verifico por API y no por la pantalla, porque la pantalla pinta lo que le dicen. Y no automaticé la conciliación con el operador real: no hay ambiente de pruebas.'),
  ('El lunes', 'El lunes, en mi equipo, cada rojo del daily llega con su caja y su línea.'),
]
MODELO_FRASE = 'Lo que vieron tiene cuatro partes: problema, evidencia, decisión y lunes. Su lámina 1 empieza igual.'
ENSAYO = ('En las **mismas salas** (Teams conserva la asignación): cada persona, **90 segundos** con su apertura y su falla; '
          'quien queda último en orden alfabético lleva el cronómetro. Después, **30 segundos de feedback** con la tarjeta.')
TARJETA_FEEDBACK = ['Entendí que tu CP prueba ___.', 'Lo que más me convenció fue ___.', 'Yo cortaría ___.']
PREGUNTAS_ENSAYO = ['¿Dijo la caja de su falla?', '¿Mostró evidencia (y no código)?', '¿Terminó a tiempo?']

# La plantilla de láminas de la S10 (laminas-s10.html)
LAMINAS_S10 = [
  ('1 · El problema', 'Tu caso en una frase, sin datos del banco: «Pruebo ___; el riesgo es ___».'),
  ('2 · El mapa', 'Las capas del framework con tu pieza resaltada.'),
  ('3 · Tu CP', 'El escenario (o la tabla de Ejemplos), la prueba o el mapeo, y la captura del reporte.'),
  ('4 · La falla', 'La falla provocada: el mensaje, la caja y la línea que lo prueba.'),
  ('5 · La decisión y el límite', 'Una decisión de diseño y su porqué, y qué NO automatizaste y por qué.'),
  ('6 · El lunes', 'Qué harías el lunes en tu equipo con esto.'),
]
CREDITOS_NOTA = 'Si vas por la vía de especificador, la lámina 1 lleva la línea de créditos: «Escenarios, datos y aceptación: ___ · Código: instructor, con ayuda de IA».'
FORMATO_S10 = ('Individual: unos 6 minutos más 2 de preguntas. En equipo (2 a 4 personas): unos 12 minutos más 3, y cada persona presenta su CP. '
               'La demo es el reporte ya generado y las capturas, no una corrida en vivo.')

# ─────────────────────────── 7:44 · Boleto de la S9 (a la vez; correctas: c, a, b, c). La 4 es un rojo nuevo ───────────────────────────
BOLETO = [
  ('Una prueba falló la primera vez y pasó al reintentar. ¿Qué es?',
   ['un verde', 'un rojo del sistema', 'un *flaky*: una alerta que hay que investigar'], 'c',
   FRASE_FLAKY),
  ('El rojo del ambiente sin clave no dejó trace. ¿Cuál es la evidencia?',
   ['la consola: falló en el segundo cero y dice qué falta', 'no hay evidencia: hay que repetirla', 'la captura de la pantalla'], 'a',
   'La ausencia de trace también dice algo: no llegó a abrir el navegador.'),
  ('El saldo tarda 7 s y el `expect` espera 5. ¿Qué haces primero?',
   ['`test.slow()`', 'mirar la red del trace y abrir el ticket al ambiente con la hora y la petición', 'subir `retries` a 3'], 'b',
   '`test.slow()` no cambia el *timeout* del `expect`, y los reintentos lo esconden.'),
  ('Un rojo nuevo: la transferencia responde `401 Unauthorized` en QA y en desarrollo pasa. ¿Qué caja?',
   ['sistema', 'script', 'ambiente: la credencial o el permiso de ese ambiente'], 'c',
   'Mismo código, otro ambiente, una credencial que no sirve: ambiente. La evidencia es el 401 y en qué ambiente pasa.'),
]

# ─────────────────────────── Horario (la pausa es el muro) ───────────────────────────
HORARIO = [
  ('5:50', 'Reporte del triage abierto; la tabla «Sala N → rojos» lista en la página', '—', 'Las salas se crean en el momento, no antes'),
  ('6:00', 'Llegada: la línea «confirmo · del criterio de listo me falta» en el chat', 'Una línea por persona', 'A las 6:12 cuentas en voz alta'),
  ('6:12', 'Gancho', '—', FRASE_GANCHO),
  ('6:15', 'Ficha de las tres cajas · «¿en qué caja va?» a la vez, por el mensaje de error', '3 letras (b c a)', FRASE_REGLA),
  ('6:25', 'Mírame: el rojo 2 y el rojo 4 con su trace; el *flaky*; `attach` y `test.slow()` en una frase cada uno', '—', '**Corte duro a los 10 minutos**'),
  ('6:35', 'Crear 4 salas con **Automáticamente** (aleatorio), límite de 15 min, y abrirlas. El número de sala dice los rojos (Sala 1 = rojos 1 y 4)', '—', ROLES_SALA),
  ('6:38', '**Salas, 15 min:** dos rojos por sala, con anuncios en el minuto 8 y en el 12', '«Sala X · rojo N · caja · evidencia»', SALAS_NOTA),
  ('6:53', 'Vuelta: «4 de 4» en el chat principal; lo que no coincidió', '—', 'Se corta: las salas en pantalla'),
  ('7:00', '**Pausa: es el muro**', '', ''),
  ('7:07', '**Tu proyecto (20 min fijos, en la sala principal):** una falla provocada y clasificada, y su lámina', '«Mi CP · falla · caja · evidencia»', PROYECTO_ESPECIFICADOR),
  ('7:27', 'El modelo del instructor: 3 minutos con el cronómetro en pantalla', '—', MODELO_FRASE),
  ('7:30', '**Ensayo en las mismas salas:** 90 s cada uno y 30 s de feedback', 'La tarjeta', FRASE_ENSAYO),
  ('7:44', 'Boleto a la vez (con un rojo nuevo) · el orden de la S10 en el chat', '4 letras (c a b c)', ''),
  ('7:52', 'CI en una captura y cierre', '—', FRASE_CIERRE),
  ('7:57', 'Colchón', '', 'Hasta las 8:00'),
]
CI_FRASE = 'Esto lo corre una máquina en cada push: `pruebas.yml` corre `npm run verificar-clase` y deja el reporte y las evidencias. Es su job de Jenkins o de Azure DevOps.'
CORTE = 'Si vas tarde, se corta en este orden: la captura de CI → las salas en pantalla durante la vuelta → el *flaky* del mírame.'
NO_SE_CORTA = 'No se cortan nunca: la pausa, el proyecto, el ensayo y el boleto.'

# ─────────────────────────── La guía de estudio ───────────────────────────
GUIA_S9 = {'s': 'S9', 'fecha': 'jue 3 dic', 'tema': 'Errores, registro y CI',
  'idea': IDEA_FUERZA,
  'conceptos': ['Las tres cajas: sistema, script o ambiente, y la evidencia que decide (trace, consola o regla)', 'Un *flaky* es una alerta: falló y pasó al reintentar', 'El registro de la corrida (`attach`), el bug conocido (`test.fail`) y el pipeline (`pruebas.yml`)'],
  'enlaces': [('Actividades S9', 'actividades-s9.html'), ('Reporte del triage', 'reportes/triage/index.html'), ('Plantilla de láminas de la S10', 'laminas-s10.html'), ('Triage de fallas', REPO + '/blob/main/docs/triage.md')], 'video': []}

FUENTES = [
  'Playwright, «Retries» (playwright.dev/docs/test-retries): reintentos y pruebas *flaky*.',
  'Playwright, «Trace viewer» (playwright.dev/docs/trace-viewer): `on-first-retry` y trace.playwright.dev.',
  'Playwright, «Annotations» (playwright.dev/docs/test-annotations): `test.fail()` y `test.slow()`.',
  'Playwright, «TestInfo» (playwright.dev/docs/api/class-testinfo): `attach`.',
  'Playwright, «Continuous Integration» (playwright.dev/docs/ci): `retries` en CI.',
  'ISTQB, CTFL v4.0: defecto, falla y error; el informe de defectos.',
]
