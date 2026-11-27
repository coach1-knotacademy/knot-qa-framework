# Datos y reportes: Data Driven Testing sobre el framework (S8)

Construye sobre las capas de la S3 (ver [arquitectura.md](arquitectura.md)), la fábrica de la S5 (ver [patrones.md](patrones.md)) y los escenarios de la S7 (ver [gherkin-y-bdd.md](gherkin-y-bdd.md)). Este archivo lo genera `laboratorio/generar/generar_actividades_s8.py` desde `fichas_s8.py`, la misma fuente de las actividades y del deck: si cambias algo, cámbialo allí.

**Negocio no firma código: firma la tabla y lee el reporte. La fila de la tabla es la fila del reporte.**

Objetivo de la sesión: Tu tabla de Ejemplos convertida en N pruebas, cada una con su nombre en el reporte que lee negocio.

| Pieza | Dónde verla |
|---|---|
| Los Esquemas del escenario con sus Ejemplos | `especificaciones/recargas-datos.feature` |
| Las filas con nombre (los datos de la tabla) | `src/datos/fabricaDeRecargas.ts` (`rechazosPorMonto`, `paraCadaOperador`) |
| Un `test()` por fila, con título único y `@CP-104` | `tests/recargas/CP-104-limites.spec.ts` |
| El revisor de escenarios (dice cuántas pruebas salen) | `laboratorio/revisor-escenarios.js` · `npm.cmd run revisar-escenarios` |

## Esquema del escenario y Data Driven Testing

| | |
|---|---|
| **El problema que ya sufrías a mano** | El CP-103 y el CP-104 se prueban con varios datos. Escribir una prueba por dato es copiar y pegar: cuando cambia un paso, hay que arreglarlo en diez lugares, y negocio no ve de un vistazo qué datos se probaron. |
| **La idea, en una frase** | Los pasos se escriben **una vez** con `<marcadores>`; cada fila de la tabla `Ejemplos` es **una prueba**. En Playwright, un `for` sobre una lista de la fábrica crea un `test()` por fila, con un **título único** que lleva el dato. |
| **Sus partes, en el repo** | `especificaciones/recargas-datos.feature` (los Esquemas) · `src/datos/fabricaDeRecargas.ts` (`rechazosPorMonto()`, las filas con nombre) · `tests/recargas/CP-104-limites.spec.ts` (el `for` con título único y `@CP-104`). |
| **Sí, cuando** | La regla es la misma y cambia el dato: límites, operadores, formatos, tipos de cliente. Y negocio quiere ver la lista de casos. |
| **No, cuando** | Las filas siguen caminos distintos (una pide código y otra no) o tienen otro tipo de resultado: eso es otro Esquema. Ni datos aleatorios que nadie puede repetir. |
| **La frase para tu líder** | La tabla es lo que firma negocio y cada fila es una línea del reporte. Agregar un caso es agregar una fila, no una prueba. |
| **Cómo pedírselo a la IA** | «Convierte este escenario en un Esquema del escenario con Ejemplos: pasos con &lt;marcadores&gt;, una columna por dato, el dato en el título y 3 filas que pasen por los mismos pasos (incluye el borde). Si una fila cambia el resultado, sepárala en otro Esquema y dime por qué.» |

## La regla de los Ejemplos

**Mismos pasos, otro dato, el mismo tipo de «Entonces».** Si una fila cambia el camino o el resultado, es otro Esquema.

| Sala | CP | Columnas | Filas | Lo que se discute |
|---|---|---|---|---|
| Sala 1 | CP-103 · Celular mal escrito | `celular` · `caso` | 300123 · 6 dígitos; 30012345678 · 11 dígitos; 2001234567 · empieza por 2 | Tres datos, un mismo mensaje: ¿hacen falta las tres filas? Sí: cada una prueba un pedazo distinto de la regla (corto, largo y prefijo). Si se quita una, ese error puede volver sin que nadie lo vea. |
| Sala 2 | CP-104 · Monto fuera de rango | `monto` · `mensaje` | $999 · La recarga mínima es $1.000; $100.001 · La recarga máxima es $100.000; $150.000 · La recarga máxima es $100.000 | ¿Por qué $99.999 no va en esta tabla? Porque todo monto de más de $50.000 pide código de seguridad: $99.999 sigue otro camino y tiene otro «Entonces». Va en el Esquema del CP-102. |
| Sala 3 | CP-101 · Recarga válida sin código | `monto` · `saldo_final` | $1.000 · $1.499.000; $10.000 · $1.490.000; $50.000 · $1.450.000 | ¿Y $50.001? Pide código: otro camino, otro Esquema (el CP-102). $50.000 es el borde: el último monto que no pide código. |
| Sala 4 | CP-105 · Límite diario | `ya_recargo` · `monto` | $190.000 · $20.000; $200.000 · $1.000; $160.000 · $50.000 | ¿El dato del «Dado» también va en la tabla? ¿Y $180.000 + $20.000? Sí, el «Dado» también lleva dato. $180.000 + $20.000 da exactamente $200.000 y **pasa** (el límite es «más de»): otro resultado, otro Esquema. |
| Sala 5 | CP-107 · Una recarga por operador | `operador` | Claro; Movistar; Tigo; WOM | Esto ya existe en el repo (`fabricaDeRecargas.paraCadaOperador`). ¿Para qué escribir la tabla? Porque la tabla es la especificación que firma negocio: el día que llegue un operador nuevo, se agrega una fila y negocio la ve. |

El CP-106 (el operador no responde, BUG-04) no va en el DDT: es un solo dato. Entra en el triage de la S9.

## El reporte que lee negocio

| Paso | Qué se hace | Qué se ve |
|---|---|---|
| Correr | `npx.cmd playwright test -g "@CP-104" --project=recargas` (en Mac o Linux: `npx`) | Salen 3 pruebas por API y una por la pantalla. |
| Abrir | `npm.cmd run reporte` (en Mac o Linux: `npm`) | Una línea por fila, con su título: «CP-104 · $150.000 → «La recarga máxima es $100.000»». |
| Filtrar | Escribir `@CP-104` en el buscador del reporte | Solo las pruebas de ese caso: la fila del ALM. |
| Abrir una fila | Clic en una línea | Sus pasos (`test.step`, con el texto del Gherkin) y, en la de la pantalla, la captura: la evidencia de ese dato. |

**El error provocado.** Se quita el monto del título: las filas de $100.001 y $150.000 quedan con el mismo nombre (las dos dicen «La recarga máxima es $100.000») y **Playwright se niega a correr: no corre ninguna prueba** («duplicate test title»). El título único no es estética: es lo que hace que cada fila tenga su línea en el reporte.

Allure se muestra en una sola captura: necesita Java y no se puede instalar en sus equipos. El reporte HTML de Playwright trae lo mismo que pide negocio.

## Lo preciso (las esperas, el «Y» y el «Entonces»)

- **Las esperas.** El `expect` sobre un localizador **reintenta hasta 5 segundos**; **30 es el límite de toda la prueba**. Los clics esperan a que el botón se pueda usar, dentro de esos 30. (playwright.dev/docs/test-timeouts)
- **El «Y» en el Cuando.** **El «Y» es para leer mejor**. Cucumber no mira la palabra; los pasos corren en orden, uno por uno, y el «Y» no cambia ninguna espera. (cucumber.io/docs/gherkin/reference)
- **El Entonces sin dato.** **Solo la A, la que tiene el dato** («ve el mensaje «El celular debe tener 10 dígitos y empezar por 3»»). Un «Entonces» que no se puede reprobar («el sistema responde correctamente») no es un esperado.
- **Foto o video.** `innerText` espera a que aparezca el elemento y le toma una **foto**. `toHaveText` sigue mirando hasta que el texto sea el esperado: es un **video**. Para el comprobante, que ya no cambia, la foto sirve (así lo hace `PaginaRecargas.esperarResultado`); para el saldo, que se mueve, va el video.
- **La clave.** Si la clave falta, la prueba falla. Nunca trae un valor por defecto en el código.
- **En los escenarios.** En los escenarios del Banco Demo se escribe «el banco». Se diseña, no se pega.

## Rosetta: una prueba por fila en Java + Cucumber o Serenity

| La pieza | Gherkin (hoy) | En el banco (Java · Cucumber · Serenity) | Playwright |
|---|---|---|---|
| La tabla | `Esquema del escenario` + `Ejemplos` | `Scenario Outline` + `Examples` (Cucumber-JVM, Serenity) | Un `for` sobre `fabricaDeRecargas.rechazosPorMonto()` |
| El dato en el paso | `<monto>` | `@Cuando("recarga {int} a un celular {word}")` | `rechazo.monto` |
| Una prueba por fila | La herramienta expande la tabla | El runner expande `Examples`; JUnit `@CsvSource` o TestNG `@DataProvider` | Un `test()` por fila, con título único |
| Lo que nunca | Un `for` dentro de un paso | Un `for` dentro de una *step definition*: una sola prueba, la primera falla tapa las demás | Un solo `test()` con un ciclo adentro |

El `<monto>` en el título del escenario es tu título único.

## Fuentes

- Playwright, «Parameterize tests» (playwright.dev/docs/test-parameterize): un `test()` por dato, con título único.
- Playwright, «Timeouts» (playwright.dev/docs/test-timeouts): 30 s por prueba y 5 s por `expect`.
- Playwright, «Reporters · HTML reporter» (playwright.dev/docs/test-reporters#html-reporter) y «Annotations · Tag tests» (playwright.dev/docs/test-annotations).
- Cucumber, «Gherkin Reference» (cucumber.io/docs/gherkin/reference): Scenario Outline, Examples y And/But; en español, «Esquema del escenario» y «Ejemplos».
- ISTQB, CTFL v4.0: partición de equivalencia y análisis de valores límite.
