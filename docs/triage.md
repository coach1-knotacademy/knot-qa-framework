# Triage de fallas: ¿rojo del sistema, del script o del ambiente? (S9)

Construye sobre las capas de la S3 (ver [arquitectura.md](arquitectura.md)), la configuración y los localizadores de la S6 (ver [configuracion-y-localizadores.md](configuracion-y-localizadores.md)) y el reporte de la S8 (ver [datos-y-reportes.md](datos-y-reportes.md)). Este archivo lo genera `laboratorio/generar/generar_actividades_s9.py` desde `fichas_s9.py`, la misma fuente de las actividades y del deck: si cambias algo, cámbialo allí. Los mensajes de error son los reales: se leen del reporte del triage (`npm run triage:generar`).

**Un rojo no es un bug hasta que sabes de quién es.**

Objetivo de la sesión: Ante un rojo, decir en qué caja va (sistema, script o ambiente) y con qué evidencia (el trace, la consola o la regla del negocio).

> Antes de abrir un bug, díganme la caja y la línea que lo prueba.

| Pieza | Dónde verla |
|---|---|
| Los 4 rojos (proyecto `triage`, solo corre si se pide) | `tests/triage-s09/` · `npx.cmd playwright test --project=triage` |
| El registro de la corrida (`test.info().attach`) | `src/soporte/registro.ts` |
| El bug conocido, registrado (la falla esperada) | `src/soporte/hallazgos.ts` |
| El `throw` de la configuración (falla de inmediato) | `src/config/ambientes.ts` |
| El reporte con los traces | [https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/index.html](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/index.html) |
| Las actividades de la clase | [https://coach1-knotacademy.github.io/knot-qa-framework/actividades-s9.html](https://coach1-knotacademy.github.io/knot-qa-framework/actividades-s9.html) |

## Triage: sistema, script o ambiente

| | |
|---|---|
| **El problema que ya sufrías a mano** | Un rojo llega al daily y cada uno culpa a otro: el desarrollador dice ambiente, infraestructura dice script, QA dice bug. Se pierde un día, y el bug real (si lo hay) sigue ahí. |
| **La idea, en una frase** | Todo rojo cae en una de **tres cajas**, y la caja se decide con **evidencia**, no con intuición: **sistema** (el esperado sale de la regla y el sistema no la cumple), **script** (la prueba está mal: localizador, `await`, dato) o **ambiente** (lo que la prueba necesita no está: una clave, un servicio, tiempo). |
| **Sus partes, en el repo** | `tests/triage-s09/` (los 4 rojos, en el proyecto `triage`, que solo corre si se pide) · `src/soporte/registro.ts` (el registro de la corrida con `test.info().attach`) · `src/soporte/hallazgos.ts` (el bug conocido, registrado) · el trace y el reporte. |
| **Sí, cuando** | Hay un rojo y alguien tiene que decidir a quién va el ticket: a desarrollo, a QA o a infraestructura. |
| **No, cuando** | Se «arregla» un rojo subiendo el *timeout*, agregando `retries` o con `test.slow()` sin saber la caja: eso lo esconde. |
| **La frase para tu líder** | Un rojo sin caja es ruido; con caja y evidencia es un reporte. El ticket lleva la caja, la línea que lo prueba y el ID del caso. |
| **Cómo pedírselo a la IA** | «Este es el mensaje de error y el último paso del trace de una prueba de Playwright: ___. ¿En qué caja va (sistema, script o ambiente)? Dame la línea exacta que lo prueba y qué evidencia falta para estar seguro. No inventes lo que no está en el texto.» |

## Las tres cajas

| La caja | Qué es | Cómo se ve el mensaje | A quién va el ticket |
|---|---|---|---|
| **Sistema** | El esperado sale de la **regla del negocio** y el sistema no la cumple. | Esperado contra obtenido de una regla: `Expected: 1500000 · Received: 1480000`. | Ticket a desarrollo, con la regla y el ID del caso. |
| **Script** | La **prueba** está mal: el localizador, el `await`, el dato o el esperado mal escrito. | El localizador no aparece: `waiting for locator(...)` hasta `Test timeout of 30000ms exceeded`, y en la captura el elemento sí está, en otro lugar de la pantalla. | Lo arregla QA: es su código. |
| **Ambiente** | Lo que la prueba **necesita** no está: una clave, un servicio, la red o el tiempo de respuesta. | Falta una clave, `401`, conexión rechazada, o en la red del trace una petición sin respuesta (pendiente o cancelada). | Ticket a infraestructura o al dueño del servicio, con la hora y la petición. |

## Los 4 rojos

### Rojo 1 · El operador no responde y el saldo baja · caja: **sistema**

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 1500000
Received: 1480000
```

- **Cómo se provoca.** El CP-106 **sin** la marca `hallazgoEsperado`: el operador simulado no responde (número de pruebas `3000000504`).
- **La evidencia.** La **regla del negocio**: el cliente no pierde la plata. Esperado $1.500.000, obtenido $1.480.000 (por API, el saldo real). En la red, `POST recargas` responde 504: ese es el escenario del caso (el operador no responde), no la falla. La caja la decide la regla.
- **Lo que se aprende.** En la suite, el mismo caso sale como **falla esperada**: es el cuarto estado. Un bug conocido, registrado con su ID (BUG-04), que no ensucia la corrida y avisa si un día se arregla.
- **Lo ven:** Sala 1 y Sala 4.
- **Capturas:** [1 · la acción](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/capturas/rojo1-1-accion.png) · [2 · el error](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/capturas/rojo1-2-error.png) · [3 · la red](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/capturas/rojo1-3-red.png) · [el trace](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/traces/rojo1.zip) (zip, para trace.playwright.dev)

### Rojo 2 · El rediseño rompe un localizador · caja: **script**

```
Test timeout of 30000ms exceeded.

Error: locator.selectOption: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('xpath=/html/body/main/form[1]/select')
```

- **Cómo se provoca.** `REDISENO=1` cambia la pantalla y la prueba usa `PaginaRecargasHeredada`, con los localizadores de antes.
- **La evidencia.** El **trace**: `selectOption` espera un XPath que nunca aparece, hasta que vence el límite de la prueba (30 s). En la captura, la lista «Operador» está ahí, con el mismo nombre, en otro contenedor.
- **Lo que se aprende.** La escalera de la S6: rol y nombre sobreviven al rediseño; el localizador frágil, no.
- **Lo ven:** Sala 2 y Sala 4.
- **Capturas:** [1 · la acción](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/capturas/rojo2-1-accion.png) · [2 · el error](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/capturas/rojo2-2-error.png) · [3 · la red](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/capturas/rojo2-3-red.png) · [el trace](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/traces/rojo2.zip) (zip, para trace.playwright.dev)

### Rojo 3 · Falta la clave · caja: **ambiente**

```
Error: Falta CLAVE_BANCO para el ambiente qa. Defínela en la terminal: $env:CLAVE_BANCO = '...'
    at claveDelAmbiente (src/config/ambientes.ts:80:21)
    at configurarAmbiente (src/config/ambientes.ts:105:12)
    at Object.<anonymous> (src/config/entorno.ts:28:42)
    at Object.<anonymous> (playwright.config.ts:2:1)
    … (y el resto de la pila de Node)
```

- **Cómo se provoca.** Se corre contra el ambiente `qa` sin la clave en la terminal: `npm.cmd run triage:sin-clave`.
- **La evidencia.** **No hay trace**: todo cae en el segundo cero y la **consola** dice qué clave falta. Esa ausencia también es evidencia.
- **Lo que se aprende.** Fallar de inmediato (S6) y el `throw` de la configuración: falla la corrida entera, no una prueba.
- **Lo ven:** Sala 2 y Sala 3.
- **Capturas:** [1 · la consola](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/capturas/rojo3-1-consola.png)

### Rojo 4 · El saldo tarda más que el expect · caja: **ambiente**

```
Error: expect(locator).toHaveText(expected) failed

Locator:  locator('#saldo')
Expected: "$1.500.000"
Received: "…"
Timeout:  5000ms

Call log:
  - Expect "toHaveText" locator('#saldo') with timeout 5000ms
  - waiting for locator('#saldo')
    14 × locator resolved to <strong id="saldo" data-testid="saldo-disponible">…</strong>
       - unexpected value "…"
```

- **Cómo se provoca.** `page.route` demora el servicio de saldos 7 segundos; el `expect` espera 5.
- **La evidencia.** En la **red** del trace, la petición de saldos (`GET cuentas`) no tiene respuesta: sale cancelada, sin duración ni tamaño, y el `expect` venció a los 5 s. El servicio no respondió a tiempo. El localizador `#saldo` sí se encontró (el call log dice «14 × locator resolved»): no es del script. Con `--retries=1` y la demora solo en el primer intento, el reporte dice **1 flaky**.
- **Lo que se aprende.** Ni `test.slow()` (triplica el *timeout* de la prueba, no el del `expect`) ni subir el *timeout* lo arreglan: es un ticket al ambiente, con la hora y la petición.
- **Lo ven:** Sala 1 y Sala 3.
- **Capturas:** [1 · la acción](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/capturas/rojo4-1-accion.png) · [2 · el error](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/capturas/rojo4-2-error.png) · [3 · la red](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/capturas/rojo4-3-red.png) · [el trace](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/triage/traces/rojo4.zip) (zip, para trace.playwright.dev)

## Las salas

Cada rojo lo ven dos salas: si no coinciden en la caja, ese es el debate de la vuelta.

| Sala | Rojos |
|---|---|
| Sala 1 | 1 y 4 |
| Sala 2 | 2 y 3 |
| Sala 3 | 3 y 4 |
| Sala 4 | 1 y 2 |

La línea pegable: `Sala X · rojo N · caja: ___ · evidencia: ___ (la línea del trace, de la consola o la regla)`

Salas **aleatorias**. **Pega en el chat** quien va primero en orden alfabético; **cuida el reloj** el segundo. Si a los 60 segundos nadie pegó, pega el siguiente.

## El mírame

| Qué | El comando | Qué se ve |
|---|---|---|
| Rojo 2 con su trace | `npx.cmd playwright test --project=triage -g "rojo 2"` (tarda unos 30 s) y abrir el trace | El XPath que espera y la captura donde la lista «Operador» está en otro contenedor. |
| Rojo 4 con su trace | `npx.cmd playwright test --project=triage -g "rojo 4"` | La pestaña de red: la petición de saldos sin respuesta cuando vence el `expect`. |
| El flaky | `npx.cmd playwright test --project=triage -g "flaky" --retries=1` | El reporte dice «1 flaky»: falló la primera vez y pasó al reintentar. En el repo, `retries` es 0: aquí se muestra a propósito. |

> Un reintento que pasa no es un verde: es un aviso de *flaky*. Pregunten siempre cuántas pasaron al segundo intento.

## En una línea

| La pieza | En una línea |
|---|---|
| `test.info().attach` | Pega un valor o un archivo a la prueba y el reporte lo muestra: es el **registro de la corrida** (`registrar()` en `src/soporte/registro.ts`). No es un log que se imprime: queda con la prueba. |
| `test.slow()` | Triplica el *timeout* de **la prueba**, no el del `expect`, que sigue en 5 s. Es para una prueba lenta a propósito, no para tapar un rojo. |
| `retries` | En el repo es 0. En un pipeline se usa `process.env.CI ? 2 : 0`, y cada *flaky* es una alerta con ticket, no un verde. |

## Las frases y de dónde salen

- Flaky: falló la primera vez y pasó al reintentar. (playwright.dev/docs/test-retries)
- on-first-retry graba el trace solo en el primer reintento. (playwright.dev/docs/trace-viewer)
- trace.playwright.dev carga el trace en tu navegador y no lo envía a ningún servidor. (playwright.dev/docs/trace-viewer)
- test.slow() triplica el timeout de la prueba, no el del expect. (playwright.dev/docs/test-annotations)
- El expect espera 5 segundos por defecto. (playwright.dev/docs/test-timeouts)
- attach pega un valor o un archivo a la prueba, y el reporte lo muestra. (playwright.dev/docs/api/class-testinfo)
- test.fail(): la prueba tiene que fallar; si un día pasa, avisa. (playwright.dev/docs/test-annotations)

## Tu proyecto

**Una falla provocada en tu CP y clasificada**: cambia una fila de tu tabla de la S8 (un esperado, un dato) o rompe algo a propósito, mira el rojo y di su caja con su evidencia. Arma tu **lámina de la falla** con la plantilla. Pega en el chat principal: «Mi CP · falla: ___ · caja: ___ · evidencia: ___».

Si vas por la vía de especificador, ya tienes tu prueba hecha: cambia una fila de tus Ejemplos y predice el rojo antes de correrlo.

## Fuentes

- Playwright, «Retries» (playwright.dev/docs/test-retries): reintentos y pruebas *flaky*.
- Playwright, «Trace viewer» (playwright.dev/docs/trace-viewer): `on-first-retry` y trace.playwright.dev.
- Playwright, «Annotations» (playwright.dev/docs/test-annotations): `test.fail()` y `test.slow()`.
- Playwright, «TestInfo» (playwright.dev/docs/api/class-testinfo): `attach`.
- Playwright, «Continuous Integration» (playwright.dev/docs/ci): `retries` en CI.
- ISTQB, CTFL v4.0: defecto, falla y error; el informe de defectos.
