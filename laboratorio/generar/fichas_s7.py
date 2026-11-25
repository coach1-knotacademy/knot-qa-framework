"""La S7 (Gherkin sobre el framework), el kit de proyecto y la guía de estudio: UNA sola fuente.

La usan:
  - laboratorio/generar/generar_actividades_s7.py  → actividades_S7.html y docs/gherkin-y-bdd.md
  - laboratorio/generar/generar_proyecto.py        → proyecto.html (kit de proyecto) y guia-estudio.html
  - ../sesion_07/generar_deck_S7.py                → el deck del instructor
Así nunca dicen cosas distintas. Decisiones en ../../../sesion_07/council_S7.md (veredicto).

Marcado mínimo: `código`, **negrita** y *cursiva*. a_html() lo pasa a HTML; en Markdown queda tal cual.
"""
from fichas_s6 import a_html, PAGES, FILAS, BOLETO as BOLETO_S6, CPS, COTEJO, ESCALERA  # noqa: F401

REPO = 'https://github.com/coach1-knotacademy/knot-qa-framework'
ACTIVIDADES = PAGES + 'actividades-s7.html'
PROYECTO = PAGES + 'proyecto.html'
GUIA = PAGES + 'guia-estudio.html'
PLANTILLA = PAGES + 'plantilla.html'

TEMA = 'Estructura del framework y Gherkin / BDD'
IDEA_FUERZA = 'Gherkin es tu CP con otra sintaxis: dice QUÉ pasa en el negocio. Las capas del framework dicen CÓMO.'
FRASE_GANCHO = 'Gherkin no es para la máquina: es lo que el líder firma antes de que automatices.'
FRASE_CIERRE = ('Hoy su CP quedó escrito para que lo firme negocio y lo ejecute el framework. '
                'El martes, ese mismo escenario con muchos datos: una prueba, diez casos.')
OBJETIVO = 'Tu CP en Gherkin, mapeado a las capas del framework.'

# ─────────────────────────── Ficha (mismo formato que la S5 y la S6) ───────────────────────────
FICHA = {
  'id': 'gherkin', 'titulo': 'Gherkin y BDD', 'color': 'lime',
  'problema': 'El CP del Excel lo entiende quien lo escribió; el script, solo quien sabe código. Negocio aprueba uno, QA automatiza otro, y con el tiempo dicen cosas distintas.',
  'idea': 'Un escenario de Gherkin es el CP escrito para que lo lean negocio, QA y la máquina: **Dado** (la precondición), **Cuando** (lo que hace el cliente), **Entonces** (el resultado esperado, con el dato).',
  'partes': '`especificaciones/recargas.feature` (los escenarios, con la etiqueta `@CP-101`) · `tests/recargas/CP-101-gherkin.spec.ts` (cada paso es un `test.step`) · `src/screenplay/recargas/RecargarDesdeLaPantalla.ts` (la tarea que ejecuta el «Cuando»).',
  'si': 'El caso tiene reglas de negocio que alguien tiene que aprobar (montos, límites, bloqueos) y lo van a leer personas que no programan.',
  'no': 'Es una prueba técnica que solo lee QA (un contrato de API, un cálculo): ahí basta un `test()` con buen nombre. Y un Gherkin con clics («hago clic en…») es peor que no tener Gherkin.',
  'lider': 'El escenario es el contrato: lo firma negocio, lleva el ID del ALM y corre sobre las mismas capas. Si cambia la pantalla, el escenario no se toca.',
  'ia': '«Convierte este CP del Banco Demo en un escenario de Gherkin en español: Dado, Cuando y Entonces, sin clics ni localizadores, máximo 5 pasos, con la etiqueta @CP-xxx y el resultado esperado con el dato exacto. Si falta el esperado, escribe TODO: no lo inventes.»',
}

# BDD ≠ Gherkin ≠ herramienta (la precisión del docente de maestría)
TRES_COSAS = [
  ('BDD', 'una **práctica de equipo**: descubrir el comportamiento con ejemplos (los «tres amigos»: negocio, desarrollo y QA), formularlo y automatizarlo.', 'Hoy solo **formulamos**.'),
  ('Gherkin', 'el **lenguaje** de los escenarios: `Característica`, `Escenario`, `Dado`, `Cuando`, `Entonces`, `Y`, `Pero`. En español con `# language: es`.', 'Es lo que escriben hoy.'),
  ('Cucumber · playwright-bdd', 'las **herramientas** que leen el `.feature` y llaman a un código por cada paso.', 'Hoy no se instalan: cada paso es un `test.step` y corre igual.'),
]
FRASE_BANCO = ('En el banco, BDD casi siempre es Gherkin escrito por QA, no los tres amigos en una sala. '
               'Aun así vale: el valor real es la trazabilidad. `@CP-101` en el escenario es la fila del ALM (o de Xray).')

# El CP-101 en tres idiomas (el gancho)
TRES_IDIOMAS = {
  'manual': ['**CP-101 · Recarga normal a celular**',
             'Precondición: Ana inició sesión. Saldo de Ahorros: $1.500.000.',
             '1. Ir a «Recargar celular».',
             '2. Elegir Claro, escribir el celular 3001234567 y el valor $10.000.',
             '3. Pulsar «Recargar».',
             'Esperado: comprobante con «Recarga exitosa». Saldo de Ahorros: $1.490.000.'],
  'gherkin': """@CP-101
Escenario: Una recarga normal da comprobante y descuenta de Ahorros
  Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
  Cuando recarga $10.000 a un celular Claro 3001234567
  Entonces ve el comprobante «Recarga exitosa»
  Y su saldo de Ahorros queda en $1.490.000""",
  'prueba': """test('CP-101 · Recarga normal a celular', { tag: '@CP-101' }, async ({ page, cliente, paginaRecargas }) => {
  const ana = Actor.llamado('Ana').puede(NavegarLaWeb.con(page));

  await test.step('Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros', async () => {
    await abrirConSesion(page, cliente, usuarios.ana);
    await paginaRecargas.abrir();
    await expect(paginaRecargas.saldoDisponible).toHaveText('$1.500.000');
  });
  await test.step('Cuando recarga $10.000 a un celular Claro 3001234567', async () => {
    await ana.intenta(RecargarDesdeLaPantalla.celular('3001234567').por(10_000).con('Claro'));
  });
  await test.step('Entonces ve el comprobante «Recarga exitosa»', async () => {
    expect(await ana.pregunta(ResultadoDeLaRecarga.queVio())).toContain('Recarga exitosa');
  });
  await test.step('Y su saldo de Ahorros queda en $1.490.000', async () => {
    await expect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000');
  });
});""",
}

# ¿Cuál es declarativo? (respuesta a la vez; las letras correctas van mezcladas: b, a, c)
DECLARATIVO = [
  ('El «Cuando» del CP-101', [
    '«Cuando hago clic en el botón Recargar»',
    '«Cuando recarga $10.000 a un celular Claro 3001234567»',
    '«Cuando lleno el campo Valor con 10000 y pulso Enter»'], 'b',
    'Dice **qué hace el cliente**. Las otras dos cuentan la pantalla: con el rediseño de la S6 se caen, y el líder no las puede firmar.'),
  ('El «Entonces» del CP-103', [
    '«Entonces ve el mensaje «El celular debe tener 10 dígitos y empezar por 3»»',
    '«Entonces aparece el div #error en rojo»',
    '«Entonces el sistema responde correctamente»'], 'a',
    'Tiene el **dato exacto** que se verifica. La b es un localizador; la c no dice qué es «correctamente»: nadie la puede reprobar.'),
  ('El «Dado» de cualquier CP', [
    '«Dado que abro el navegador, entro a /login, escribo ana y la clave, y pongo el código del SMS»',
    '«Dado que espero 5 segundos a que cargue la página»',
    '«Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros»'], 'c',
    'La precondición es un **estado del negocio**. Cómo se llega a ese estado (login, SMS) lo sabe la capa de flujos; la espera fija nunca es un paso.'),
]

# Del escenario a las capas (el bloque de mapeo)
MAPEO = [
  ('`@CP-101` (la etiqueta)', 'Trazabilidad', 'El título y la etiqueta de la prueba', "`{ tag: '@CP-101' }` · se corre con `-g \"CP-101\"`"),
  ('**Dado** · la precondición', '`src/flujos/` + `src/config/`', 'Un flujo o una tarea; usuario y clave del entorno', '`await abrirConSesion(page, cliente, usuarios.ana)`'),
  ('**Cuando** · lo que hace el cliente', '`src/screenplay/` → `src/paginas/`', 'Una **tarea** que usa el Page Object por dentro', "`await ana.intenta(RecargarDesdeLaPantalla.celular('3001234567').por(10_000))`"),
  ('El dato ($10.000, Claro)', '`src/datos/`', 'La fábrica: solo se escribe lo que cambia', '`fabricaDeRecargas.valida({ monto: 10_000 })`'),
  ('**Entonces** · el esperado', '`tests/`', 'Un `expect` por resultado; lo que está en pantalla, con una aserción que reintenta', "`await expect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000')`"),
  ('El ambiente (no aparece en el escenario)', '`src/config/`', 'La configuración de la S6', "`$env:AMBIENTE = 'qa'`"),
]
REGLA_MAPEO = 'Un paso, una línea de código: si un paso necesita 10 líneas en la prueba, falta una tarea.'

# ¿Qué capa ejecuta este paso? (comprobación a la vez de la segunda parte; correctas: c, a, b)
QUE_CAPA = [
  ('«Dado que hoy ya recargó $200.000»', [
    'Un `expect` en la prueba', 'El Page Object, haciendo 4 recargas por la pantalla', 'Una preparación por API (`cliente.recargar(...)` 4 veces)'], 'c',
    'Una precondición se **prepara**, no se prueba: por API es más rápido y más estable. Lo que se prueba es el «Cuando» de hoy.'),
  ('«Cuando recarga $60.000 a un celular Claro 3001234567»', [
    'Una tarea (`RecargarDesdeLaPantalla`) que usa `PaginaRecargas` por dentro', 'El `expect`', 'La configuración'], 'a',
    'El «Cuando» es una **tarea**: el paso de negocio. Por dentro usa el Page Object, que sabe en qué campo va cada dato.'),
  ('«Y su saldo de Ahorros queda en $1.440.000»', [
    'La fábrica de datos', "`await expect(paginaRecargas.saldoDisponible).toHaveText('$1.440.000')`", "`page.waitForTimeout(2000)` y después leer el saldo"], 'b',
    'El esperado es un `expect` que **reintenta solo**. La espera fija es adivinar; la fábrica da datos de entrada, no resultados.'),
]

# Las tres precisiones que se dicen hoy, tal cual (dentro del bloque de mapeo)
PRECISIONES = [
  ('name', 'El `name` de `getByRole`',
   '`name` es el **nombre accesible**. En un botón es su texto visible, salvo que tenga `aria-label`, que lo reemplaza. No es el atributo `name` del HTML. Y busca un pedazo, sin importar mayúsculas: «Recargar ahora» también pasa; `exact: true` exige el nombre completo.'),
  ('po', 'Page Object y Screenplay',
   'Page Object organiza **pantallas**; Screenplay organiza **tareas**. No compiten: la tarea `RecargarDesdeLaPantalla` usa `PaginaRecargas` por dentro. Page Object es la base; Screenplay se suma cuando hay varios actores (el cliente y el aprobador) o el mismo paso corre por varios canales.'),
  ('await', 'El `await` en cada paso',
   'Todo lo que le pide algo al navegador lleva `await`: las acciones y los `expect` sobre localizadores. El localizador **no** lleva `await`: no hace nada hasta que se usa. Sin `await`, el resultado depende de la suerte: a veces pasa (la acción alcanzó a terminar) y a veces falla con un mensaje que no dice la causa (`Test ended`, `session closed`). Una prueba que pasa por suerte no es evidencia.'),
]

# Rosetta: lo de hoy en el framework que van a heredar en el banco (Java + Selenium + Cucumber/Serenity)
ROSETTA = [
  ('El escenario', '`especificaciones/recargas.feature`', 'El mismo `.feature`: Gherkin es igual en los dos'),
  ('Un paso', "`test.step('Cuando recarga…')` (o `When(...)` con playwright-bdd)", '`@Cuando("recarga {int} a un celular {word} {string}")` en Cucumber-JVM'),
  ('La tarea', '`ana.intenta(RecargarDesdeLaPantalla.celular(...))`', '`actor.attemptsTo(Recargar.celular(...))` en Serenity Screenplay'),
  ('La memoria del actor', "`actor.recuerda('clave', valor)` / `actor.recuerdo('clave')`", '`actor.remember("clave", valor)` / `actor.recall("clave")`'),
  ('El Page Object', "`PaginaRecargas` con `getByRole('button', { name: 'Recargar' })`", '`Target.the("botón Recargar").located(By...)` o un `PageObject` con `@FindBy`'),
  ('La espera', 'Automática, y `await expect(...)` reintenta', '`WebDriverWait` con `ExpectedConditions`. Nunca mezclar la espera implícita con la explícita'),
  ('Las piezas de cada prueba', 'Los fixtures (`test.extend`)', 'Hooks `@Before` e inyección (PicoContainer o Spring)'),
  ('El reporte', 'El reporte HTML de Playwright: pasos, trace, video', 'El reporte de Serenity o Allure'),
]
ROSETTA_FRASE = 'Lo que se transfiere no es la sintaxis, es la idea: escenario de negocio, tarea con nombre, página que esconde el cómo, esperar un estado y nunca un tiempo.'

# Boleto de salida de la S7 (4 preguntas a la vez; correctas: b, a, c, b)
BOLETO = [
  ('¿Dónde va el ID del caso del ALM en Gherkin?',
   ['en el título de la `Característica`', 'en una etiqueta `@CP-102` encima del `Escenario`', 'en un comentario al final del archivo'], 'b',
   'La etiqueta viaja con el escenario hasta el reporte: es la fila de la matriz de trazabilidad.'),
  ('«Cuando hago clic en Recargar». ¿Qué tiene de malo?',
   ['describe la pantalla y no el negocio: se rompe con el rediseño y negocio no lo puede firmar', 'nada: es más claro', 'le falta el `await`'], 'a',
   'Declarativo: «Cuando recarga $10.000 a un celular Claro». El clic es asunto del Page Object.'),
  ('El paso «Cuando recarga $10.000…», ¿qué lo ejecuta?',
   ['el escenario llama directo a los localizadores', 'el `expect`', 'una tarea de Screenplay que usa el Page Object por dentro'], 'c',
   'Screenplay y Page Object se combinan: la tarea es el paso de negocio, la página sabe el cómo.'),
  ('¿Qué hace `test.step(\'Dado que…\')`?',
   ['lee el archivo `.feature` y lo ejecuta', 'agrupa el código del paso y el reporte lo muestra con ese texto', 'reemplaza el `await`'], 'b',
   'Es la forma de ejecutar Gherkin sin instalar nada más. Para leer el `.feature` directo están playwright-bdd o Cucumber.'),
]

# Horario de la S7 (presupuesto 80/120: ~80 min de contenido, dos controles y colchón al final)
HORARIO = [
  ('5:55', 'Salas creadas a mano (5, con capitán)', '—', ''),
  ('6:00', 'Portada · boleto de la S6 a la vez, para quien ya llegó', 'Boleto S6 (c a c b)', 'Absorbe la llegada tarde'),
  ('6:08', 'Gancho: el CP-101 en tres idiomas', '—', FRASE_GANCHO),
  ('6:12', 'Ficha Gherkin y BDD · «¿cuál es declarativo?» a la vez', '3 letras (b a c)', ''),
  ('6:20', 'Mírame: el CP-101 en el revisor y corriendo con `test.step`', '—', 'El reporte muestra los pasos'),
  ('6:25', '**Salas, tramo 1 (8 min):** su CP en Gherkin, en el revisor', '«Sala X: 0 errores»', 'Un CP por sala: CP-102 a CP-106'),
  ('6:33', 'Vuelta: dos salas leen su escenario', 'Revisor en pantalla', 'CP-102: ¿uno o dos escenarios?'),
  ('6:40', 'Del escenario a las capas, con las 3 precisiones', '—', '**Control 6:50**: si no empezó el mapeo, se salta la vuelta'),
  ('6:50', 'Pausa', '', ''),
  ('6:57', '**Salas, tramo 2 (8 min):** cada paso a su capa', '«Sala X: 6 de 6»', 'La tabla de mapeo de las actividades'),
  ('7:05', '«¿Qué capa ejecuta este paso?» a la vez · Rosetta (2 min)', '3 letras (c a b)', ''),
  ('7:15', '**Tu proyecto (20 min, fijo)**', 'La frase en el chat y un escenario en el revisor', '**Control 7:30**: a las 7:35 empieza el boleto, pase lo que pase'),
  ('7:35', 'Boleto de la S7 a la vez', '4 letras (b a c b)', ''),
  ('7:42', 'Cierre: la frase, el martes y la guía de estudio', '—', FRASE_CIERRE),
  ('7:47', 'Preguntas y anécdotas (colchón)', '', 'Hasta las 8:00'),
]
CORTE = 'Si vas tarde, se corta en este orden: la Rosetta → la comprobación de las 7:05 (a una sola pregunta) → la vuelta de las 6:33 (una sola sala) → el mírame (solo la captura del reporte).'
NO_SE_CORTA = 'No se cortan nunca: los dos tramos de sala, el proyecto y el boleto.'

# ─────────────────────────── El proyecto final ───────────────────────────
PREGUNTA_GUIA = '¿Qué parte de mi caso de prueba le confío a una máquina, y con qué evidencia?'
FRASE_PROYECTO = 'Pruebo ___; el riesgo es ___; mi framework lo cubre con ___.'

VIAS = [
  {'id': 'A', 'nombre': 'Mi framework', 'verbo': 'Construir', 'color': 'lime',
   'para': 'Quien puede correr Node en su equipo, o quiere trabajar en el laboratorio del navegador.',
   'que': 'Arranca de la **plantilla** y le agrega tus CP: escenario en Gherkin, prueba con `test.step`, datos en la fábrica y evidencia en el reporte.',
   'ejemplos': ['Migrar un Page Object heredado por la escalera de localizadores (el antes y el después).',
                'Ambientes que fallan en QA y no en desarrollo: una prueba de salud del ambiente antes de la suite y fallas clasificadas en sistema, script o ambiente.']},
  {'id': 'B', 'nombre': 'Revisión del framework', 'verbo': 'Revisar', 'color': 'cyan',
   'para': 'Quien no puede instalar nada en su equipo. Vale lo mismo que la A.',
   'que': 'Toma el `knot-qa-framework` (o una prueba escrita por una IA) y explica qué patrón usa cada pieza, qué defectos encuentra y cómo lo mejoraría. La evidencia corre en el **laboratorio del navegador** y en el **revisor de escenarios**.',
   'ejemplos': ['El hallazgo del buzón: `leerUltimoCodigo` promete «el más reciente» y solo busca el código de ingreso.',
                'El localizador que se escapó del Page Object en `tests/recargas/recargas.spec.ts`.']},
  {'id': 'C', 'nombre': 'Diseño de un caso que no es web', 'verbo': 'Diseñar', 'color': 'peach',
   'para': 'Quien prueba algo que no es una página: agentes de voz, servicios, procesos por lotes, apps.',
   'que': 'Tus CP en Gherkin, qué se automatiza y qué no (y por qué), qué **habilidad** cambiaría en Screenplay (la transcripción en lugar del navegador) y qué evidencia pediría una auditoría. Lo que se codifica, va sobre un gemelo público.',
   'ejemplos': ['Agente de voz con IA: se afirma sobre la transcripción y su registro, no sobre el audio. Las grabaciones son datos personales: nunca salen de su sistema.',
                'Un servicio que en QA llama al servicio equivocado: el escenario es el mismo; cambia la habilidad (la API).']},
]

FICHA_PROYECTO = [
  ('Nombre del proyecto', 'Recargas sin sorpresas'),
  ('Vía', 'A · Mi framework'),
  ('La frase', 'Pruebo las recargas a celular; el riesgo es que el cliente pierda plata si el operador falla; mi framework lo cubre con el CP-106 y un reporte con evidencia.'),
  ('El problema (sin datos ni nombres del banco)', 'Las recargas se prueban a mano en cada entrega y el caso del operador caído casi nunca se corre.'),
  ('Dónde se codifica (gemelo público)', 'Banco Demo (`/recargas`)'),
  ('Los CP (2 o 3)', 'CP-101 recarga normal · CP-104 por encima del máximo · CP-106 operador caído'),
  ('Qué NO se automatiza, y por qué', 'La conciliación con el operador real: no hay un ambiente de pruebas del operador. Se revisa a mano una vez por entrega.'),
  ('De dónde salen los datos', 'De la fábrica (`fabricaDeRecargas`): números de prueba con nombre. Nunca datos de producción.'),
]

MATRIZ = {
  'columnas': ['CP (ID del ALM)', 'Escenario (.feature)', 'Prueba o mapeo', 'Evidencia', 'Estado'],
  'ejemplo': [
    ['CP-101', 'Una recarga normal da comprobante y descuenta de Ahorros', '`tests/recargas/CP-101-gherkin.spec.ts`', 'Reporte HTML: los 4 pasos en verde', 'Verde'],
    ['CP-106', 'Si el operador no responde, el cliente no pierde la plata', 'Mapeo a `RecargarDesdeLaPantalla` + `cliente.saldoDeAhorros()`', 'Trace del rojo: el saldo bajó a $1.480.000', 'Rojo **del sistema** (BUG-04)'],
  ],
}

CRITERIO_LISTO = [
  ('La ficha', 'Completa, con la frase del proyecto, y sin datos, pantallas ni nombres del banco.'),
  ('Trazabilidad', 'De 2 a 3 CP de punta a punta: ID → escenario → prueba (o mapeo, en las vías B y C) → evidencia.'),
  ('Escenarios declarativos', 'Pasan el revisor de escenarios sin errores: Dado, Cuando y Entonces, sin clics ni localizadores, y un esperado con el dato.'),
  ('El mapa de capas', 'Cada paso dice qué capa lo ejecuta y con qué pieza (tarea, página, fábrica, `expect`, configuración).'),
  ('Una corrida con evidencia', 'Verde con `-g "CP-xxx"` en tu equipo o en el laboratorio, con el reporte o la captura. En la vía C: el mapeo leído con la lista de cotejo.'),
  ('Una falla clasificada', 'Una falla provocada y explicada: ¿rojo del sistema, del script o del ambiente? (se trabaja en la S9).'),
  ('Una decisión y un límite', 'Una decisión de diseño que defiendes (un localizador, un *timeout*, el ambiente) y qué NO automatizaste, y por qué.'),
]

CHARLA = [
  ('30 s / 1 min', 'El problema', 'Tu caso en una frase, sin datos del banco. La pregunta guía, respondida.'),
  ('1 min / 2 min', 'El mapa', 'Las capas de tu framework con tu pieza resaltada.'),
  ('3 min / 5 min', 'Los CP', 'Tu CP (en equipo, cada persona el suyo): escenario → prueba (o mapeo) → evidencia. **La demo es el reporte ya generado**, no una corrida en vivo.'),
  ('1 min / 2 min', 'La decisión y el límite', 'Una decisión de diseño y su porqué, y qué no automatizaste y por qué.'),
  ('30 s / 1 min', 'El cierre', 'Qué harías el lunes en tu equipo con esto.'),
]
CHARLA_NOTA = ('**Tú eliges el formato.** Individual: unos 6 minutos más 2 de preguntas. En equipo (de 2 a 4 personas): unos 12 minutos más 3 de preguntas, '
               'y cada persona es dueña de un CP y lo presenta. Los tiempos de arriba van como «individual / equipo». '
               'Cuéntalo en la S8 para armar el orden del 10 de diciembre. Plan B si algo no abre: las capturas del reporte en las láminas.')

PLAN_PROYECTO = [
  ('S7', 'jue 26 nov', '20 min', 'Elegir la vía, escribir la frase del proyecto en el chat y el primer escenario de tu CP en el revisor.'),
  ('S8', 'mar 1 dic', '15 min', 'Los datos (los Ejemplos del escenario y la fábrica) y la primera evidencia: el reporte o la captura del laboratorio.'),
  ('S9', 'jue 3 dic', '30 min', 'Una falla provocada y clasificada, las láminas y un ensayo con cronómetro en las salas.'),
  ('S10', 'jue 10 dic', 'toda la sesión', 'Las presentaciones.'),
]
REGLAS_PROYECTO = [
  'El caso real de tu equipo **se diseña y se discute**; lo que se codifica va sobre un **gemelo público** (Banco Demo, ParaBank). Nunca se automatiza un sistema del banco.',
  'Nunca datos, pantallas, casos del ALM ni código del banco: ni en el proyecto, ni en el chat, ni en la IA.',
  'Las claves, fuera del código y del reporte (S6).',
  'Todo se trabaja en clase. Lo que quieras avanzar por tu cuenta es opcional.',
]

PLANTILLA_FEATURE = """# language: es
Característica: <lo que el cliente puede hacer>
  Como <rol>
  quiero <acción>
  para <beneficio>

  @CP-<ID del caso>
  Escenario: <el resultado, en una frase>
    Dado que <el estado del negocio antes: quién, con qué>
    Cuando <lo que hace el cliente, con el dato>
    Entonces <lo que ve o lo que pasa, con el dato exacto>"""

# ─────────────────────────── La guía de estudio (repaso opcional) ───────────────────────────
# Videos: el instructor los sube al Drive del curso. Aquí va solo el índice por minuto (de la transcripción).
GUIA_SESIONES = [
  {'s': 'S1', 'fecha': 'mar 3 nov', 'tema': 'Pirámide de pruebas y estrategia',
   'idea': 'Cada riesgo se prueba en la capa más baja que te da confianza: muchas unitarias, varias de API, pocas de interfaz.',
   'conceptos': ['Pirámide, cono de helado y reloj de arena', 'Shift-left: el error se encuentra lo antes posible', 'Pipeline: la cadena que corre las pruebas en cada cambio'],
   'enlaces': [('Presentación (PDF)', 'presentaciones/presentacion_S1.pdf')], 'video': []},
  {'s': 'S2', 'fecha': 'jue 5 nov', 'tema': 'Criterios de selección, ROI y estimación',
   'idea': 'De lo que pruebas a mano, se automatiza lo que se repite, se puede verificar y tiene datos y ambiente confiables; y se hace la cuenta.',
   'conceptos': ['Las seis preguntas para decidir si se automatiza', 'ROI y punto de equilibrio (con el mantenimiento)', 'Valor límite, oráculo y prueba negativa'],
   'enlaces': [('Calculadora de selección y ROI', 'calculadora.html'), ('Presentación (PDF)', 'presentaciones/presentacion_S2.pdf')], 'video': []},
  {'s': 'S3', 'fecha': 'mar 10 nov', 'tema': 'Arquitectura por capas y orientación a objetos',
   'idea': 'Cada capa tiene un trabajo y las dependencias apuntan hacia abajo: la prueba dice qué, las páginas saben cómo.',
   'conceptos': ['Clase, objeto, herencia, encapsulamiento (lo privado es el localizador)', 'Las capas: tests, páginas, flujos, API, datos, configuración, soporte', 'Trazabilidad: el ID del caso va en el nombre de la prueba'],
   'enlaces': [('Arquitectura del framework', REPO + '/blob/main/docs/arquitectura.md'), ('Retos S3', REPO + '/blob/main/retos/S03.md'), ('Presentación (PDF)', 'presentaciones/presentacion_S3.pdf')], 'video': []},
  {'s': 'S4', 'fecha': 'mar 17 nov', 'tema': 'SOLID en el código de automatización',
   'idea': 'SOLID explica por qué las capas están así: cada cambio toca un solo lugar.',
   'conceptos': ['S: una responsabilidad · O: extender sin modificar · L: las hijas cumplen lo que promete la madre', 'I: interfaces pequeñas · D: la prueba pide sus piezas (fixtures)', 'Código legado: el antes, en `src/legado/`'],
   'enlaces': [('Laboratorio S4', 'laboratorio-s4.html'), ('Práctica extra S4', 'practica-extra-s4.html'), ('Retos S4', REPO + '/blob/main/retos/S04.md'), ('Presentación (PDF)', 'presentaciones/presentacion_S4.pdf')], 'video': []},
  {'s': 'S5', 'fecha': 'jue 19 nov', 'tema': 'Patrones: Page Object, Screenplay, Factory y Singleton',
   'idea': 'Los patrones le ponen nombre a lo que ya tenían las capas, y un framework usa varios: uno por problema.',
   'conceptos': ['Page Object (pantallas) y Screenplay (tareas) se combinan', 'Factory y Singleton son creacionales: datos nuevos en cada llamada, una sola configuración', 'El reporte de un sitio real (ParaBank): video, capturas y trace'],
   'enlaces': [('Actividades S5', 'actividades-s5.html'), ('Laboratorio S5', 'laboratorio-s5.html'), ('Reporte de ParaBank', 'reportes/parabank/index.html'), ('Fichas de patrones', REPO + '/blob/main/docs/patrones.md'), ('Presentación (PDF)', 'presentaciones/presentacion_S5.pdf')], 'video': []},
  {'s': 'S6', 'fecha': 'mar 24 nov', 'tema': 'Configuración, ambientes y localizadores robustos',
   'idea': 'Una prueba robusta no depende de dónde corre ni de cómo se ve la pantalla: si se cae por eso, el defecto es de la prueba.',
   'conceptos': ['Ambientes local, QA y UAT: producción bloqueada, clave por la terminal, configuración congelada', 'La escalera de localizadores: rol y nombre → etiqueta → texto → test-id pactado → CSS o XPath nunca', 'Playwright espera solo: `await expect(...)` reintenta; la espera fija es adivinar'],
   'enlaces': [('Actividades S6', 'actividades-s6.html'), ('Laboratorio S6 (retos y patio de localizadores)', 'laboratorio-s6.html'), ('Plantilla para tu proyecto', 'plantilla.html'), ('Configuración y localizadores', REPO + '/blob/main/docs/configuracion-y-localizadores.md'), ('Presentación (PDF)', 'presentaciones/presentacion_S6.pdf')],
   'video': [('0:00', 'La IA con el mismo CP, sin y con el framework; la plantilla y el prompt'),
             ('11:00', 'Repaso de patrones: ¿fábrica o Singleton?'),
             ('18:00', 'El secreto que quedó en la evidencia'),
             ('22:30', 'Ambientes: por qué en desarrollo pasa y en QA no'),
             ('28:45', 'Postman: un pedido, dos ambientes'),
             ('33:00', '¿Qué capa cambia si cambio de ambiente?'),
             ('37:45', '¿La clave queda local o compartida? (.env)'),
             ('41:50', 'Reto 1 del laboratorio: ambientes, paso a paso'),
             ('1:02:45', 'Paso 2: si falta la clave, falla de inmediato'),
             ('1:07:50', 'Pasos 3 y 4: producción bloqueada y configuración congelada'),
             ('1:12:30', 'Localizadores: la escalera y por qué rol y nombre van primero'),
             ('1:23:20', 'El rediseño de Recargas'),
             ('1:31:50', 'Esperas: `await` y *timeout*')]},
]

# Lo preciso (sin decir quién lo dijo): «se oye a veces / lo preciso es». Sale de las retros de la S5 y la S6.
LO_PRECISO = [
  ('Page Object es para proyectos chicos; Screenplay lo reemplaza.',
   'Page Object es la base. Screenplay se suma cuando hay varios actores o canales, y una tarea usa páginas por dentro: se combinan.'),
  ('El `name` de `getByRole` es el atributo `name` del botón.',
   'Es el **nombre accesible**: el texto visible del botón, salvo que tenga `aria-label`, que lo reemplaza. Busca un pedazo; `exact: true` exige el nombre completo.'),
  ('Sin `await` a veces funciona; lo que no es un flujo no lo necesita.',
   'Todo lo que le pide algo al navegador lleva `await`, siempre. Si una prueba hace dos cosas a la vez: `await Promise.all([...])`. Sin `await` puede pasar por suerte, o fallar con `Test ended` o `session closed`, que no dicen la causa.'),
  ('Si no le pones *timeout*, la prueba se queda esperando para siempre.',
   'Siempre hay un límite: 30 s por prueba y 5 s por `expect`. Para algo lento a propósito (un reporte pesado), `test.slow()` en esa prueba, no en toda la suite.'),
  ('A veces hay que decirle «espérese 10 segundos».',
   'Esa espera fija es el antipatrón: si tarda 11, falla; si tarda 1, pierdes 9. Playwright espera solo y `await expect(...)` reintenta.'),
  ('El `...cambios` de la fábrica mantiene los datos entre pruebas.',
   'Es lo contrario: cada llamada entrega un objeto **nuevo**, y `...cambios` solo pisa lo que esa prueba pide.'),
  ('El texto es tan frágil como el XPath.',
   'El texto es el peldaño 3: bien para un mensaje, y si cambia, cambió algo que ve el cliente. Los frágiles son el CSS y el XPath, que dependen de cómo está construida la pantalla.'),
  ('Un ambiente intermitente se arregla con `await`.',
   'Se clasifica: ¿rojo del sistema, del script o del ambiente? Con el trace, los reintentos (`retries`) y el registro de la corrida (S9).'),
  ('Playwright también sirve para apps de celular.',
   'Playwright automatiza web (también vista como celular). Para apps nativas se usa otra herramienta (Appium); la idea de buscar por lo que ve la persona sí se transfiere.'),
  ('ALM es «Advanced Life Cycle Management».',
   '*Application Lifecycle Management*: donde viven los CP (OpenText ALM / Quality Center, Jira con Xray, Azure Test Plans).'),
]

# ─────────────────────────── Las actividades de la S7 (lo que usa generar_actividades_s7.py) ───────────────────────────
LABORATORIO_S6 = PAGES + 'laboratorio-s6.html'   # el laboratorio en el navegador: editor y pruebas, sin Node

# El criterio de terminado del revisor (tramo 1 de las salas)
CRITERIO_REVISOR = ('**Terminaron cuando el revisor dice 0 errores.** En el chat: «Sala X: 0 errores». '
                    'Un «hago clic en…» o un «botón» cuenta como error: se reescribe con lo que hace el cliente. Los avisos (más de 5 pasos, dos «Cuando») no frenan, pero se discuten.')

# Tu mapeo (tramo 2 de las salas): cada paso de su escenario a su capa. Las capas del selector, en este orden.
CAPAS = ['src/flujos/', 'src/screenplay/', 'src/paginas/', 'src/datos/', 'tests/ (expect)', 'src/config/']
TU_MAPEO = ('Las 6 filas: los pasos de su escenario (Dado, Cuando, Entonces, Y) y, si sobran filas, el dato y el ambiente, '
            'como en la tabla del CP-101. Por cada fila: qué **capa** lo ejecuta y con qué **pieza** (la tarea, la página, la fábrica, el `expect`, la configuración).')
CRITERIO_MAPEO = '**Terminaron cuando las 6 filas tienen capa y pieza.** En el chat: «Sala X: 6 de 6».'

# Fuentes de la ficha (van en docs/gherkin-y-bdd.md)
FUENTES = [
  'Cucumber, «Gherkin Reference» (cucumber.io/docs/gherkin/reference): las palabras clave, también en español (`# language: es`).',
  'Seb Rose y Gáspár Nagy, *The BDD Books: Discovery* y *Formulation*: BDD es descubrir, formular y automatizar.',
  'Playwright, «test.step» (playwright.dev/docs/api/class-test#test-step) y «Annotations · Tag tests» (playwright.dev/docs/test-annotations): los pasos en el reporte y la etiqueta `@CP-101`.',
  'ISTQB, CTAL-TAE v2.0: la capa de definición de pruebas del gTAA.',
]
