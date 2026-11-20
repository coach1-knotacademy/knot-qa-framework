# Configuración, ambientes, localizadores y esperas (S6)

Tres fichas que construyen sobre las capas de la S3 (ver [arquitectura.md](arquitectura.md)) y los patrones de la S5 (ver [patrones.md](patrones.md)). Este archivo lo genera `laboratorio/generar/generar_actividades_s6.py` desde `fichas_s6.py`, la misma fuente de las actividades y del deck: si cambias una ficha, cámbiala allí.

| Ficha | Capa | Dónde verlo |
|---|---|---|
| Configuración y ambientes | `src/config/` | `ambientes.ts` (reto 1), `entorno.ts`, `.env.ejemplo` |
| Localizadores robustos | `src/paginas/` | `PaginaRecargas.ts`, `heredadas/PaginaRecargasHeredada.ts` (reto 2) |
| Esperas | `src/paginas/` y `tests/` | `PaginaRecargas.esperarResultado()`, las aserciones de `tests/recargas/` |

## Configuración y ambientes

*En la S3, `entorno.ts` ya era un solo lugar para la dirección del banco. En la S5 le pusimos nombre: Singleton. Hoy le ponemos los controles que exige un banco.*

| | |
|---|---|
| **El problema que ya sufrías a mano** | El caso pasa en QA y falla en UAT «porque allá la clave es otra». Alguien corre la regresión contra el ambiente equivocado. Y la clave de prueba termina escrita en un Excel, en un correo o en la evidencia. |
| **La idea, en una frase** | Un ambiente es un **control**, no solo una URL. La prueba es la misma en QA y en UAT. Lo que cambia (dirección, usuario, clave y **datos**) vive en **un solo lugar**, **congelado** y **sin secretos en el código**. |
| **Sus partes, en el repo** | `src/config/ambientes.ts`: el catálogo `local | qa | uat` y `configurarAmbiente(nombre, variables)` · `src/config/entorno.ts`: el resultado, congelado con `Object.freeze` · las variables de la terminal: `$env:AMBIENTE = 'qa'` y `$env:CLAVE_BANCO = '...'` · `.env.ejemplo`: los nombres de las variables, sin valores. |
| **Sí, cuando** | Todo lo que cambia entre QA, UAT y preproducción: dirección, usuarios, claves, tiempos y los datos de cada ambiente. Es el *environment* de Postman, pero para todo el framework. |
| **No, cuando** | Una clave escrita en el código o en el *initial value* de Postman, que se sincroniza con la nube. Un objeto de configuración que una prueba puede modificar, porque daña a la siguiente. Y **nunca** un ambiente `produccion` en el catálogo. |
| **La frase para tu líder** | «Las pruebas no pueden correr contra producción por error. Si falta una clave, se nota en el primer segundo. Y ningún secreto queda en el repo.» |
| **Cómo pedírselo a la IA** | «La dirección y las claves salen de `entorno`. No las escribas en la prueba ni inventes una URL.» |

## Localizadores robustos

*En la S5 los localizadores se fueron al Page Object: son lo que la pantalla **tiene**. Hoy vemos cuál elegir para que sobreviva a un rediseño.*

| | |
|---|---|
| **El problema que ya sufrías a mano** | Desarrollo «solo cambió el diseño» y se cae la regresión entera, aunque para el cliente la pantalla hace exactamente lo mismo. |
| **La idea, en una frase** | Busca cada elemento **como lo busca una persona**: por su rol y su nombre, por la etiqueta del campo o por su texto. Si no hay nada visible y estable, usa un `data-testid` **pactado con desarrollo**. CSS y XPath, nunca. |
| **Sus partes, en el repo** | `getByRole('button', { name: 'Recargar' })` · `getByLabel('Número de celular')` · `getByText('Recarga exitosa')` · `getByTestId('saldo-disponible')`. Todos son `private` dentro del Page Object, en `src/paginas/`. |
| **Sí, cuando** | Siempre, empezando por el peldaño más alto de la escalera. Además pruebas accesibilidad: si `getByLabel` no encuentra el campo, un lector de pantalla tampoco. |
| **No, cuando** | Clases CSS (cambian con el diseño), `nth-child` (cambia con el orden), XPath absoluto (cambia con cualquier contenedor) e ids que cambian con cada versión. Tampoco un localizador dentro de la prueba: vive en el Page Object. |
| **La frase para tu líder** | «Si rediseñan la pantalla y el negocio no cambió, la regresión sigue en verde. Si se cae, es porque algo cambió para el cliente.» |
| **Cómo pedírselo a la IA** | «Localizadores por rol o etiqueta. Si no hay, pide un `data-testid`. Nada de CSS, XPath ni `nth-child`.» |

## Esperas

*La pregunta del jueves: «¿el tiempo de espera se puede programar?». Sí se puede, pero casi nunca hace falta.*

| | |
|---|---|
| **El problema que ya sufrías a mano** | En manual uno espera «a que cargue» mirando la pantalla. En la prueba alguien escribe «espera 10 segundos». Si el sistema tarda 11, falla. Si tarda 1, se pierden 9 en cada prueba, todas las noches. |
| **La idea, en una frase** | **Playwright ya espera solo.** Cada acción espera a que el elemento esté visible y habilitado. Cada `await expect(...)` reintenta hasta que se cumpla (5 segundos por defecto). Tu trabajo es poner `await` en cada paso. |
| **Sus partes, en el repo** | `await`: cada acción del navegador devuelve una *promesa* («ya te respondo»), y `await` quiere decir «espera la respuesta antes de seguir» · las acciones (`click`, `fill`) esperan solas · las aserciones que reintentan: `await expect(locator).toHaveText(...)` · los tiempos: 5 s por `expect` y 30 s por prueba (`Test timeout of 30000ms exceeded`). |
| **Sí, cuando** | Si un sistema es lento de verdad, el tiempo se sube **en un solo lugar** (`expect: { timeout }` en `playwright.config.ts`) o solo en esa aserción (`{ timeout: 10_000 }`). Y la lentitud se reporta como hallazgo. |
| **No, cuando** | `page.waitForTimeout(10000)`: hace la prueba lenta e inestable a la vez. Tampoco `expect(await locator.innerText())`, que lee una sola vez y no reintenta. Ni un paso sin `await`: a veces pasa por suerte, y eso es peor. |
| **La frase para tu líder** | «Las pruebas esperan lo justo: no fallan porque el sistema tardó un segundo más, ni pierden minutos esperando por si acaso.» |
| **Cómo pedírselo a la IA** | «Sin `waitForTimeout`. Pon `await` en cada paso y usa `await expect(locator)` con aserciones que reintentan.» |

## La escalera de localizadores

| Peldaño | Ejemplo | Cuándo |
|---|---|---|
| 1 · Rol + nombre | `getByRole('button', { name: 'Recargar' })` | Botones, enlaces, títulos y casillas: lo que la persona ve y para qué sirve. Es lo que recomienda la documentación de Playwright. |
| 2 · Etiqueta | `getByLabel('Número de celular')` | Campos de un formulario que tienen su `<label>`. |
| 3 · Texto | `getByText('Recarga exitosa')` | Mensajes y textos que no son controles. |
| 4 · Test-id pactado | `getByTestId('saldo-disponible')` | Cuando no hay nada visible y estable, como un valor que cambia (el saldo). Se pacta con desarrollo y no cambia con el diseño. |
| 5 · CSS o XPath: nunca | `locator('.btn-azul') · locator('form > input:nth-child(4)') · locator('xpath=/html/body/main/form/button')` | Dependen de cómo está pintada la pantalla, no de lo que hace. Se caen con el primer rediseño. |

Hallazgo del propio repo: `tests/recargas/recargas.spec.ts:76` busca el botón «Recargar» por su cuenta (`page.getByRole(...)` dentro de la prueba). El peldaño está bien; el lugar no: el localizador va en `PaginaRecargas`.

## Esperas: lo que pasó al correrlo

Contra el Banco Demo local, con Playwright 1.63:

- `expect(locator).toHaveText(...)` **sin** `await` al final de la prueba: falla en una décima de segundo con `Received: ""` y `session closed`. El error no dice «te faltó el await».
- `paginaRecargas.recargar(...)` **sin** `await`: pasó 4 de 4 veces, por suerte. Por eso es peor.
- `expect(await saldo.innerText()).toBe(...)`: falló con `Received: "…"` (el saldo todavía cargaba). No reintenta.
- `await expect(saldo).toHaveText(...)`: pasa; reintenta hasta 5 s.

## Lista de cotejo de una prueba

1. El nombre lleva el ID del caso (`CP-101 · …`) y dice qué se espera.
2. La dirección sale de `entorno` (o de `baseURL`). No hay ninguna URL escrita en la prueba.
3. No hay claves, tokens ni datos reales en el código.
4. Los localizadores viven en el Page Object, no en la prueba.
5. Cada localizador está en el peldaño más alto posible: rol y nombre, etiqueta, texto o test-id. Ni CSS, ni XPath, ni `nth-child`.
6. Los datos salen de la fábrica, con nombre de negocio: nada de montos ni celulares a mano.
7. Cada acción y cada `expect` sobre la página llevan `await`.
8. No hay `waitForTimeout`: las aserciones son de las que reintentan (`await expect(locator)…`).
9. El esperado sale de la regla de negocio, no de lo que mostró la pantalla. Si no se conoce: `// TODO: confirmar con la regla`.
10. Usa solo lo que ya está en el proyecto: ningún `npm install` nuevo.

## Casos del Banco Demo (CP-101 a CP-106)

Para practicar la traducción «paso → localizador, dato → fábrica, esperado → `expect`, ambiente → `entorno`». Son casos del Banco Demo: nunca se usan casos del ALM del banco.

| CP | Caso | Precondición | Resultado esperado |
|---|---|---|---|
| CP-101 | Recarga normal a celular | Ana inició sesión. Saldo de Ahorros: $1.500.000. | Comprobante con «Recarga exitosa». El saldo de Ahorros queda en $1.490.000. |
| CP-102 | Recarga de más de $50.000 con código | Ana inició sesión. Saldo de Ahorros: $1.500.000. | Antes de recargar, el banco pide el «Código de seguridad». Con el código del buzón: comprobante con «Valor: $60.000» y saldo de Ahorros en $1.440.000. |
| CP-103 | Celular de 6 dígitos | Ana inició sesión. Saldo de Ahorros: $1.500.000. | Mensaje «El celular debe tener 10 dígitos y empezar por 3». El saldo no cambia: $1.500.000. |
| CP-104 | Recarga por encima del máximo | Ana inició sesión. Saldo de Ahorros: $1.500.000. | Mensaje «La recarga máxima es $100.000». No pide código (el máximo se revisa antes). El saldo no cambia: $1.500.000. |
| CP-105 | Límite diario de recargas | Ana inició sesión y hoy ya recargó $200.000 (4 recargas de $50.000). | Mensaje «Superaste el límite diario de recargas ($200.000)». |
| CP-106 | El operador no responde | Ana inició sesión. Saldo de Ahorros: $1.500.000. | Mensaje «El operador no responde. Intenta más tarde.». El cliente no pierde la plata: el saldo de Ahorros sigue en $1.500.000. Hoy esta prueba sale **roja**: el Banco Demo descuenta el saldo igual (BUG-04). Es un rojo **del sistema**, no del script: el esperado sale de la regla, no de lo que hace la pantalla. |

Traducción completa del CP-101:

| Tipo | Lo que dice el caso | Cómo queda en la prueba |
|---|---|---|
| ambiente → entorno | En el ambiente de pruebas (local, QA o UAT) | `entorno.urlBase`, que llega a la prueba como `baseURL`. La prueba no escribe la dirección: `$env:AMBIENTE = 'qa'` la cambia. |
| precondición → tarea | Ana inició sesión (usuario, clave y el código del buzón) | `await abrirConSesion(page, cliente, usuarios.ana)`: una **tarea**, porque junta login, SMS y código. |
| paso → localizador | Ir a «Recargar celular» | `await paginaRecargas.abrir()` |
| dato → fábrica | Claro, 3001234567, $10.000 | `fabricaDeRecargas.valida()` |
| paso → localizador | Elegir operador, escribir celular y valor, y pulsar «Recargar» | `await paginaRecargas.recargar(recarga)`. Por dentro: `getByLabel('Operador')`, `getByLabel('Número de celular')`, `getByLabel('Valor de la recarga')` y `getByRole('button', { name: 'Recargar' })`. |
| esperado → expect | «Recarga exitosa» | `expect(await paginaRecargas.esperarResultado()).toContain('Recarga exitosa')` |
| esperado → expect | Saldo de Ahorros: $1.490.000 | `await expect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000')` |

## Postman: un pedido, dos ambientes

- Ambientes de práctica (archivos estáticos en Pages): QA `https://coach1-knotacademy.github.io/knot-qa-framework/ambientes/qa` y UAT `https://coach1-knotacademy.github.io/knot-qa-framework/ambientes/uat`, cada uno con `salud.json` y `cuentas.json`.
- Colección y ambientes para importar: `https://coach1-knotacademy.github.io/knot-qa-framework/postman/Bootcamp-S6.postman_collection.json`, `https://coach1-knotacademy.github.io/knot-qa-framework/postman/QA.postman_environment.json`, `https://coach1-knotacademy.github.io/knot-qa-framework/postman/UAT.postman_environment.json`.
- Variables: `urlBase`, `nombreAmbiente` y `clave` (secreta, vacía).
- Reglas: un workspace aparte (nunca el del equipo) y la clave solo en *current value*: el *initial value* se sincroniza con la nube.

## Fuentes

- Playwright, «Locators» y «Best practices» (playwright.dev/docs/locators, playwright.dev/docs/best-practices): prioridad de `getByRole` y de los atributos que ve el usuario.
- Playwright, «Auto-waiting» (playwright.dev/docs/actionability) y «Assertions» (playwright.dev/docs/test-assertions): 5 s por `expect`; «Timeouts»: 30 s por prueba. La documentación de `page.waitForTimeout` dice que no se use en pruebas reales porque son inestables.
- Postman, «Variables» y «Managing environments» (learning.postman.com): *initial value* se comparte; *current value* es local.
- OWASP, «Secrets Management Cheat Sheet»: los secretos fuera del código y del control de versiones.
