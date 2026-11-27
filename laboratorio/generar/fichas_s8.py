"""La S8 (una prueba, muchos datos, y el reporte que lee negocio): UNA sola fuente.

La usan:
  - laboratorio/generar/generar_actividades_s8.py  → actividades_S8.html y docs/datos-y-reportes.md
  - laboratorio/generar/generar_proyecto.py        → la vía de especificador y la guía de estudio (índice del video de la S7)
  - ../sesion_08/generar_deck_S8.py                → el deck del instructor
Decisiones en ../../../sesion_08/council_S8.md (veredicto). Retro en ../../../sesion_07/retro_S7.md.

Marcado mínimo: `código`, **negrita** y *cursiva*. a_html() lo pasa a HTML; en Markdown queda tal cual.
Las filas de las tablas de las salas se verificaron contra banco-demo/reglas.js (validarRecarga) el 26 nov.
"""
from fichas_s6 import a_html, PAGES  # noqa: F401
from fichas_s7 import REPO, PROYECTO, GUIA, ACTIVIDADES as ACTIVIDADES_S7, LABORATORIO_S6  # noqa: F401

ACTIVIDADES = PAGES + 'actividades-s8.html'
CPS_PAGINA = PAGES + 'cps.html'

TEMA = 'Data Driven Testing y el reporte como evidencia'
OBJETIVO = 'Tu tabla de Ejemplos convertida en N pruebas, cada una con su nombre en el reporte que lee negocio.'
IDEA_FUERZA = 'Negocio no firma código: firma la tabla y lee el reporte. La fila de la tabla es la fila del reporte.'
FRASE_GANCHO = ('El jueves les prometí reportes que lea negocio. ¿Cuántas pruebas escriben para los montos fuera de rango? '
                'Hoy escriben una, y el reporte les devuelve tres, cada una con su nombre.')
FRASE_CIERRE = ('Hoy escribieron las dos cosas que negocio lee: la tabla y el reporte. '
                'El jueves algo se pone rojo, y la pregunta es otra: ¿es culpa del sistema, del script o del ambiente?')
REGLA_EJEMPLOS = '**Mismos pasos, otro dato, el mismo tipo de «Entonces».** Si una fila cambia el camino o el resultado, es otro Esquema.'
FRASE_CHAT = 'Lo que no está en el chat principal no pasó.'

# ─────────────────────────── 6:00 · El rescate (lo que no quedó guardado en la S7) ───────────────────────────
RESCATE_MENSAJE = ('Antes de saludar, una línea cada uno en el chat: **vía · tu CP · solo o en equipo (con quién) · tu frase**. '
                   'Sin esa línea no puedo armar el 10 de diciembre.')
RESCATE_EJEMPLO = 'D · especificador · CP-104 · en equipo con ___ · Pruebo los montos de recarga; el riesgo es cobrar de más; lo cubre una tabla de Ejemplos.'
RESCATE_NOTA = ('Las salas de la S7 no se graban ni se transcriben, y el revisor guarda solo en el navegador de quien escribe. '
                'Si tu sala escribió algo, está en el chat de tu sala: cópialo al chat principal.')

# ─────────────────────────── 6:12 · Las correcciones del instructor (de pie, una vez) ───────────────────────────
CORRECCIONES_INTRO = 'Antes de seguir, tres correcciones mías del jueves.'
CORRECCIONES = [
  ('Las esperas', 'Dije que el `expect` espera 30 segundos.',
   'El `expect` sobre un localizador **reintenta hasta 5 segundos**; **30 es el límite de toda la prueba**. Los clics esperan a que el botón se pueda usar, dentro de esos 30.',
   'playwright.dev/docs/test-timeouts'),
  ('El «Y» en el Cuando', 'Dije que el «Y» en el Cuando hacía fallar la prueba.',
   'Me equivoqué: **el «Y» es para leer mejor**. Cucumber no mira la palabra; los pasos corren en orden, uno por uno, y el «Y» no cambia ninguna espera.',
   'cucumber.io/docs/gherkin/reference'),
  ('El Entonces sin dato', 'Dije que en el Entonces las dos eran correctas.',
   '**Solo la A, la que tiene el dato** («ve el mensaje «El celular debe tener 10 dígitos y empezar por 3»»). Un «Entonces» que no se puede reprobar («el sistema responde correctamente») no es un esperado.',
   ''),
]
CORRECCIONES_CIERRE = 'En QA, un error que se corrige a tiempo es un hallazgo; uno que se esconde llega a producción.'
FOTO_VIDEO = ('`innerText` espera a que aparezca el elemento y le toma una **foto**. `toHaveText` sigue mirando hasta que el texto sea el esperado: es un **video**. '
              'Para el comprobante, que ya no cambia, la foto sirve (así lo hace `PaginaRecargas.esperarResultado`); para el saldo, que se mueve, va el video.')
PREGUNTA_FOTO_VIDEO = ('El saldo tarda 2 segundos en actualizarse. ¿Foto o video?',
                       ["`expect(await saldo.innerText()).toBe('$1.490.000')`", "`await expect(saldo).toHaveText('$1.490.000')`"], 'b',
                       'El video: `toHaveText` reintenta hasta 5 s. La foto se toma una vez, quizá antes de que el saldo cambie.')
PRECISION_CLAVE = 'Si la clave falta, la prueba falla. Nunca trae un valor por defecto en el código.'
PRECISION_BANCO = 'En los escenarios del Banco Demo se escribe «el banco». Se diseña, no se pega.'

# ─────────────────────────── 6:17 · La ficha (mismo formato que la S5 a la S7) ───────────────────────────
FICHA = {
  'id': 'ddt', 'titulo': 'Esquema del escenario y Data Driven Testing', 'color': 'cyan',
  'problema': 'El CP-103 y el CP-104 se prueban con varios datos. Escribir una prueba por dato es copiar y pegar: cuando cambia un paso, hay que arreglarlo en diez lugares, y negocio no ve de un vistazo qué datos se probaron.',
  'idea': 'Los pasos se escriben **una vez** con `<marcadores>`; cada fila de la tabla `Ejemplos` es **una prueba**. En Playwright, un `for` sobre una lista de la fábrica crea un `test()` por fila, con un **título único** que lleva el dato.',
  'partes': '`especificaciones/recargas-datos.feature` (los Esquemas) · `src/datos/fabricaDeRecargas.ts` (`rechazosPorMonto()`, las filas con nombre) · `tests/recargas/CP-104-limites.spec.ts` (el `for` con título único y `@CP-104`).',
  'si': 'La regla es la misma y cambia el dato: límites, operadores, formatos, tipos de cliente. Y negocio quiere ver la lista de casos.',
  'no': 'Las filas siguen caminos distintos (una pide código y otra no) o tienen otro tipo de resultado: eso es otro Esquema. Ni datos aleatorios que nadie puede repetir.',
  'lider': 'La tabla es lo que firma negocio y cada fila es una línea del reporte. Agregar un caso es agregar una fila, no una prueba.',
  'ia': '«Convierte este escenario en un Esquema del escenario con Ejemplos: pasos con <marcadores>, una columna por dato, el dato en el título y 3 filas que pasen por los mismos pasos (incluye el borde). Si una fila cambia el resultado, sepárala en otro Esquema y dime por qué.»',
}

# ¿Cuántas pruebas salen de esta tabla? (a la vez; correctas mezcladas)
CUANTAS = [
  ('Un Esquema con `Ejemplos` de 1 fila de títulos y 4 filas de datos', ['5', '4', '1'], 'b',
   'La primera fila son los nombres de las columnas. Cada fila de datos es una prueba.'),
  ('Dos bloques `Ejemplos` en el mismo Esquema: uno con 3 filas de datos y otro con 2', ['2', '3', '5'], 'c',
   'Los bloques se suman: 5 pruebas. Sirve para separar «montos bajos» y «montos altos» con su etiqueta.'),
  ('Un `Escenario:` (no dice «Esquema») con una tabla `Ejemplos` de 3 filas de datos', ['3', '1', '0: es un error'], 'a',
   'Salen 3. Desde Gherkin 6, «Escenario» y «Esquema del escenario» son sinónimos. Igual se escribe «Esquema del escenario» para que se lea que es una plantilla: el revisor lo avisa.'),
]

# ─────────────────────────── 6:31 · Las salas (un tramo de 18 min) ───────────────────────────
# Cada sala: (sala, id, título del CP, columnas, filas, la pregunta que se discute, la respuesta, la solución en Gherkin)
SALAS = [
  {'sala': 'Sala 1', 'id': 'CP-103', 'titulo': 'Celular mal escrito',
   'arranque': 'Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros\nCuando recarga $10.000 al celular <celular>',
   'columnas': ['celular', 'caso'],
   'filas': [['300123', '6 dígitos'], ['30012345678', '11 dígitos'], ['2001234567', 'empieza por 2']],
   'pregunta': 'Tres datos, un mismo mensaje: ¿hacen falta las tres filas?',
   'respuesta': 'Sí: cada una prueba un pedazo distinto de la regla (corto, largo y prefijo). Si se quita una, ese error puede volver sin que nadie lo vea.',
   'solucion': """@CP-103
Esquema del escenario: Un celular mal escrito se rechaza: <celular> (<caso>)
  Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
  Cuando recarga $10.000 al celular <celular>
  Entonces ve el mensaje «El celular debe tener 10 dígitos y empezar por 3»
  Y su saldo de Ahorros sigue en $1.500.000

  Ejemplos:
    | celular     | caso          |
    | 300123      | 6 dígitos     |
    | 30012345678 | 11 dígitos    |
    | 2001234567  | empieza por 2 |"""},
  {'sala': 'Sala 2', 'id': 'CP-104', 'titulo': 'Monto fuera de rango',
   'arranque': 'Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros\nCuando recarga <monto> a un celular Claro 3001234567',
   'columnas': ['monto', 'mensaje'],
   'filas': [['$999', 'La recarga mínima es $1.000'], ['$100.001', 'La recarga máxima es $100.000'], ['$150.000', 'La recarga máxima es $100.000']],
   'pregunta': '¿Por qué $99.999 no va en esta tabla?',
   'respuesta': 'Porque todo monto de más de $50.000 pide código de seguridad: $99.999 sigue otro camino y tiene otro «Entonces». Va en el Esquema del CP-102.',
   'solucion': """@CP-104
Esquema del escenario: Un monto fuera de rango se rechaza: <monto>
  Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
  Cuando recarga <monto> a un celular Claro 3001234567
  Entonces ve el mensaje «<mensaje>»
  Y su saldo de Ahorros sigue en $1.500.000

  Ejemplos:
    | monto    | mensaje                       |
    | $999     | La recarga mínima es $1.000   |
    | $100.001 | La recarga máxima es $100.000 |
    | $150.000 | La recarga máxima es $100.000 |"""},
  {'sala': 'Sala 3', 'id': 'CP-101', 'titulo': 'Recarga válida sin código',
   'arranque': 'Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros\nCuando recarga <monto> a un celular Claro 3001234567',
   'columnas': ['monto', 'saldo_final'],
   'filas': [['$1.000', '$1.499.000'], ['$10.000', '$1.490.000'], ['$50.000', '$1.450.000']],
   'pregunta': '¿Y $50.001?',
   'respuesta': 'Pide código: otro camino, otro Esquema (el CP-102). $50.000 es el borde: el último monto que no pide código.',
   'solucion': """@CP-101
Esquema del escenario: Una recarga sin código da comprobante y descuenta: <monto>
  Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
  Cuando recarga <monto> a un celular Claro 3001234567
  Entonces ve el comprobante «Recarga exitosa» con «Valor: <monto>»
  Y su saldo de Ahorros queda en <saldo_final>

  Ejemplos:
    | monto   | saldo_final |
    | $1.000  | $1.499.000  |
    | $10.000 | $1.490.000  |
    | $50.000 | $1.450.000  |"""},
  {'sala': 'Sala 4', 'id': 'CP-105', 'titulo': 'Límite diario',
   'arranque': 'Dado que Ana tiene la sesión abierta y hoy ya recargó <ya_recargo>\nCuando recarga <monto> a un celular Claro 3001234567',
   'columnas': ['ya_recargo', 'monto'],
   'filas': [['$190.000', '$20.000'], ['$200.000', '$1.000'], ['$160.000', '$50.000']],
   'pregunta': '¿El dato del «Dado» también va en la tabla? ¿Y $180.000 + $20.000?',
   'respuesta': 'Sí, el «Dado» también lleva dato. $180.000 + $20.000 da exactamente $200.000 y **pasa** (el límite es «más de»): otro resultado, otro Esquema.',
   'solucion': """@CP-105
Esquema del escenario: Pasado el límite diario no se puede recargar: <ya_recargo> + <monto>
  Dado que Ana tiene la sesión abierta y hoy ya recargó <ya_recargo>
  Cuando recarga <monto> a un celular Claro 3001234567
  Entonces ve el mensaje «Superaste el límite diario de recargas ($200.000)»

  Ejemplos:
    | ya_recargo | monto   |
    | $190.000   | $20.000 |
    | $200.000   | $1.000  |
    | $160.000   | $50.000 |"""},
  {'sala': 'Sala 5', 'id': 'CP-107', 'titulo': 'Una recarga por operador',
   'arranque': 'Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros\nCuando recarga $10.000 a un celular <operador> 3001234567',
   'columnas': ['operador'],
   'filas': [['Claro'], ['Movistar'], ['Tigo'], ['WOM']],
   'pregunta': 'Esto ya existe en el repo (`fabricaDeRecargas.paraCadaOperador`). ¿Para qué escribir la tabla?',
   'respuesta': 'Porque la tabla es la especificación que firma negocio: el día que llegue un operador nuevo, se agrega una fila y negocio la ve.',
   'solucion': """@CP-107
Esquema del escenario: Cada operador recibe la recarga: <operador>
  Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
  Cuando recarga $10.000 a un celular <operador> 3001234567
  Entonces ve el comprobante «Recarga exitosa» con «<operador> · 3001234567»
  Y su saldo de Ahorros queda en $1.490.000

  Ejemplos:
    | operador |
    | Claro    |
    | Movistar |
    | Tigo     |
    | WOM      |"""},
]
CP_NUEVO = {'id': 'CP-107', 'titulo': 'Una recarga por operador',
            'pre': 'Ana inició sesión. Saldo de Ahorros: $1.500.000.',
            'pasos': ['Ir a «Recargar celular».', 'Elegir el operador (Claro, Movistar, Tigo o WOM), escribir el celular 3001234567 y el valor $10.000.', 'Pulsar «Recargar».'],
            'esperado': 'Comprobante con «Recarga exitosa» y el operador elegido. El saldo de Ahorros queda en $1.490.000.'}
CRITERIO_SALA = ('**Terminaron cuando el revisor dice 0 errores y «Salen N pruebas».** '
                 'Con el botón «Copiar para el chat» pegan en el chat de la sala: «Sala 2 · CP-104 · 0 errores · salen 3 pruebas» y el escenario.')
QUIEN_PEGA = 'Como las salas son aleatorias, en cada sala pega en el chat **quien va primero en orden alfabético** (por el nombre que muestra Teams).'
ANUNCIO_10 = 'Minuto 10: quien va primero en orden alfabético pega en el chat de la sala lo que tienen, con el botón «Copiar para el chat», aunque no esté terminado.'
ANUNCIO_15 = 'Minuto 15: faltan 3 minutos. Peguen la versión final en el chat de la sala. Al volver, la misma persona la pega en el chat principal.'
CP_106_NOTA = 'El CP-106 (el operador no responde, BUG-04) no va en el DDT: es un solo dato. Entra en el triage de la S9.'

# ─────────────────────────── 7:07 · Tu proyecto (20 min fijos, en la sala principal) ───────────────────────────
PROYECTO_S8 = ('Tu CP como **Esquema del escenario** con **3 filas que pasan por los mismos pasos** (incluye el borde: el último valor que todavía da ese resultado). '
               'Pásalo por el revisor y pega en el chat principal: «Mi CP · 3 filas · 0 errores».')
PROYECTO_ESPECIFICADOR = 'Si vas por la vía de especificador, **aquí entregas tu Gherkin**: lo que llegue después ya no entra.'

# La vía nueva del proyecto (decidida el 26 nov, council S8)
VIA_ESPECIFICADOR = {
  'id': 'D', 'nombre': 'Especificador', 'verbo': 'Especificar', 'color': 'lav',
  'para': 'Quien quiere llevarse lo que hace un analista de QA en un equipo real: escribir el caso para que otro lo automatice sin preguntar.',
  'que': 'Tú escribes el escenario, la tabla de Ejemplos y el esperado; el instructor escribe el código, con ayuda de una IA, **reutilizando los pasos y las tareas que ya existen** (como máximo un paso nuevo). Tú aceptas el código: lo lees junto al escenario y en la S9 provocas y clasificas una falla en tu prueba.',
  'limites': ['1 CP por persona o por equipo, sobre un gemelo público (Banco Demo o un kit).',
              'El Gherkin se entrega en el bloque del proyecto de la S8, en clase.',
              'La medida de calidad: si el instructor tuvo que preguntar algo, el Gherkin no estaba listo.'],
  'defensa': 'En la S10 cambias una fila de Ejemplos y predices qué se pone rojo, y dices qué capa ejecuta cada paso.',
  'creditos': 'Escenarios, datos y aceptación: [tu nombre] · Código: instructor, con ayuda de IA',
  'ejemplos': ['Los montos de recarga del CP-104 con su borde.', 'Las frases obligatorias de una llamada del kit de voz, como tabla.'],
}

# ─────────────────────────── 7:27 · El reporte que lee negocio (este bloque es el que se corta) ───────────────────────────
REPORTE_PASOS = [
  ('Correr', '`npx.cmd playwright test -g "@CP-104" --project=recargas` (en Mac o Linux: `npx`)', 'Salen 3 pruebas por API y una por la pantalla.'),
  ('Abrir', '`npm.cmd run reporte` (en Mac o Linux: `npm`)', 'Una línea por fila, con su título: «CP-104 · $150.000 → «La recarga máxima es $100.000»».'),
  ('Filtrar', 'Escribir `@CP-104` en el buscador del reporte', 'Solo las pruebas de ese caso: la fila del ALM.'),
  ('Abrir una fila', 'Clic en una línea', 'Sus pasos (`test.step`, con el texto del Gherkin) y, en la de la pantalla, la captura: la evidencia de ese dato.'),
]
ERROR_PROVOCADO = ('Se quita el monto del título: las filas de $100.001 y $150.000 quedan con el mismo nombre (las dos dicen «La recarga máxima es $100.000») y **Playwright se niega a correr: no corre ninguna prueba** («duplicate test title»). '
                   'El título único no es estética: es lo que hace que cada fila tenga su línea en el reporte.')
ALLURE_NOTA = 'Allure se muestra en una sola captura: necesita Java y no se puede instalar en sus equipos. El reporte HTML de Playwright trae lo mismo que pide negocio.'
ROSETTA_DDT = [
  ('La tabla', '`Esquema del escenario` + `Ejemplos`', '`Scenario Outline` + `Examples` (Cucumber-JVM, Serenity)', 'Un `for` sobre `fabricaDeRecargas.rechazosPorMonto()`'),
  ('El dato en el paso', '`<monto>`', '`@Cuando("recarga {int} a un celular {word}")`', '`rechazo.monto`'),
  ('Una prueba por fila', 'La herramienta expande la tabla', 'El runner expande `Examples`; JUnit `@CsvSource` o TestNG `@DataProvider`', 'Un `test()` por fila, con título único'),
  ('Lo que nunca', 'Un `for` dentro de un paso', 'Un `for` dentro de una *step definition*: una sola prueba, la primera falla tapa las demás', 'Un solo `test()` con un ciclo adentro'),
]
ROSETTA_FRASE = 'El `<monto>` en el título del escenario es tu título único.'

# ─────────────────────────── 7:42 · Boleto de la S8 (4 preguntas a la vez; correctas: c, a, b, c) ───────────────────────────
BOLETO = [
  ('Tu tabla del CP-104 tiene $999, $100.001 y $150.000. ¿Puedes agregar $99.999 como otra fila?',
   ['sí, es otro monto', 'sí, si se le cambia el mensaje', 'no: pide código, sigue otro camino y va en otro Esquema'], 'c',
   'Mismos pasos, otro dato, el mismo tipo de «Entonces».'),
  ('¿Qué hace que cada fila tenga su línea en el reporte?',
   ['un título único por prueba, con el dato', 'el `await`', 'la etiqueta `@CP-104`'], 'a',
   'Sin el dato en el título, las pruebas se llaman igual y Playwright no corre. La etiqueta agrupa; el título distingue.'),
  ('El saldo tarda 2 segundos en cambiar. ¿Qué va en el «Entonces»?',
   ["`expect(await saldo.innerText()).toBe(…)`", "`await expect(saldo).toHaveText(…)`", '`await page.waitForTimeout(3000)`'], 'b',
   'El video: reintenta hasta 5 s. La foto se toma una vez; la espera fija adivina.'),
  ('Negocio pide probar un operador nuevo. ¿Qué cambias?',
   ['una prueba nueva copiada de la de Claro', 'el Page Object', 'una fila en la tabla (y en la fábrica)'], 'c',
   'Agregar un caso es agregar una fila. Es lo que firma negocio.'),
]

# ─────────────────────────── Horario (presupuesto 80/120; la pausa es el muro) ───────────────────────────
HORARIO = [
  ('5:50', 'Chats de sala de la S7 revisados; la tabla «Sala N → CP» lista en la página', '—', 'Las salas se crean en el momento, no antes'),
  ('6:00', '**Rescate** en el chat, antes de saludar', 'Una línea por persona', 'A las 6:12 cuentas en voz alta y lees los nombres que faltan'),
  ('6:12', 'Las tres correcciones (de pie, una vez) · foto o video, a la vez', '1 letra (b)', CORRECCIONES_CIERRE),
  ('6:17', 'Gancho · ficha del Esquema (3 min) · «¿cuántas pruebas salen?» a la vez · mírame en el revisor', '3 letras (b c a)', FRASE_GANCHO),
  ('6:28', 'Crear 5 salas con **Automáticamente** (aleatorio), límite de 18 min, y abrirlas. El número de sala dice el CP (Sala 2 = CP-104)', '—', 'Pega en el chat quien va primero en orden alfabético'),
  ('6:31', '**Salas, un tramo de 18 min:** los Ejemplos de su CP, con anuncios en el minuto 10 y en el 15', '«Sala X · CP · 0 errores · salen N pruebas»', ''),
  ('6:49', 'Vuelta: «5 de 5» en el chat principal; 2 salas en pantalla y el resto desde el chat', '—', '**Control 6:50**: si van tarde, se proyecta una sola sala'),
  ('7:00', '**Pausa: es el muro**', '', 'Lo que no terminó se corta antes de este punto'),
  ('7:07', '**Tu proyecto (20 min fijos, en la sala principal)**', '«Mi CP · 3 filas · 0 errores»', 'Quien va por la vía de especificador entrega aquí su Gherkin'),
  ('7:27', 'El reporte que lee negocio: `CP-104-limites`, el filtro, la fila, el error del título duplicado · Rosetta (1 min)', '—', '**Control 7:30: este es el bloque que se corta**'),
  ('7:42', 'Boleto de la S8 a la vez; solo se discuten los votos repartidos', '4 letras (c a b c)', ''),
  ('7:50', 'Cierre', '—', FRASE_CIERRE),
  ('7:55', 'Colchón', '', 'Hasta las 8:00'),
]
CORTE = 'Si vas tarde, se corta en este orden: la Rosetta → el error provocado → el bloque del reporte entero (queda la captura en la guía de estudio) → la vuelta (una sola sala).'
NO_SE_CORTA = 'No se cortan nunca: el rescate, las correcciones, el tramo de salas, la pausa, el proyecto y el boleto.'

# ─────────────────────────── La guía de estudio: el índice del video de la S7 (de la transcripción) ───────────────────────────
GUIA_S7 = {'s': 'S7', 'fecha': 'jue 26 nov', 'tema': 'Estructura del framework y Gherkin / BDD',
  'idea': 'Gherkin es tu CP con otra sintaxis: dice QUÉ pasa en el negocio. Las capas del framework dicen CÓMO.',
  'conceptos': ['Declarativo: lo que hace el cliente con el dato, nunca dónde hace clic', 'Cada paso de Gherkin es un `test.step`; el ID del caso va en la etiqueta exacta `@CP-101`', 'Cada paso tiene su capa: Dado → flujos y configuración, Cuando → tarea con Page Object, dato → fábrica, Entonces → `expect`'],
  'enlaces': [('Actividades S7', 'actividades-s7.html'), ('Los CP del curso', 'cps.html'), ('Gherkin y BDD', REPO + '/blob/main/docs/gherkin-y-bdd.md'), ('Presentación (PDF)', 'presentaciones/presentacion_S7.pdf')],
  'video': [('0:04', '¿Cómo se escribe un caso para que lo entienda negocio?'),
            ('3:26', 'Repaso de la S6: ambiente, clave, localizador y esperas'),
            ('15:44', 'El CP-101 en tres idiomas: manual, Gherkin y prueba'),
            ('21:00', '¿Cuál es declarativo? El Cuando, el Entonces y el Dado'),
            ('35:00', 'Cada paso de Gherkin es un `test.step`: el CP-101 corriendo'),
            ('39:19', '¿Cómo sabe el `await` cuánto esperar? (lo preciso está en la S8: 5 s el `expect`, 30 s la prueba)'),
            ('1:08:08', 'El CP-102 en el revisor: ¿uno o dos escenarios?'),
            ('1:22:53', 'Del escenario a las capas del framework'),
            ('1:24:35', '¿Qué capa ejecuta este paso?'),
            ('1:30:00', 'Rosetta: lo mismo en Cucumber y Selenium'),
            ('1:32:00', 'El proyecto: ¿qué parte de tu caso le confías a una máquina?'),
            ('1:36:00', 'Los kits: voz, móvil, web real e integraciones')]}
GUIA_S8 = {'s': 'S8', 'fecha': 'mar 1 dic', 'tema': 'Data Driven Testing y el reporte como evidencia',
  'idea': IDEA_FUERZA,
  'conceptos': ['Esquema del escenario y Ejemplos: los pasos una vez, una prueba por fila', 'Mismos pasos, otro dato, el mismo tipo de «Entonces»', 'El título único con el dato: cada fila es una línea del reporte'],
  'enlaces': [('Actividades S8', 'actividades-s8.html'), ('Datos y reportes', REPO + '/blob/main/docs/datos-y-reportes.md')], 'video': []}

# Fuentes (van en docs/datos-y-reportes.md)
FUENTES = [
  'Playwright, «Parameterize tests» (playwright.dev/docs/test-parameterize): un `test()` por dato, con título único.',
  'Playwright, «Timeouts» (playwright.dev/docs/test-timeouts): 30 s por prueba y 5 s por `expect`.',
  'Playwright, «Reporters · HTML reporter» (playwright.dev/docs/test-reporters#html-reporter) y «Annotations · Tag tests» (playwright.dev/docs/test-annotations).',
  'Cucumber, «Gherkin Reference» (cucumber.io/docs/gherkin/reference): Scenario Outline, Examples y And/But; en español, «Esquema del escenario» y «Ejemplos».',
  'ISTQB, CTFL v4.0: partición de equivalencia y análisis de valores límite.',
]
