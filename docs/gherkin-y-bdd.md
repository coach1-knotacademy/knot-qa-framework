# Gherkin y BDD sobre el framework (S7)

Construye sobre las capas de la S3 (ver [arquitectura.md](arquitectura.md)), los patrones de la S5 (ver [patrones.md](patrones.md)) y la configuración de la S6 (ver [configuracion-y-localizadores.md](configuracion-y-localizadores.md)). Este archivo lo genera `laboratorio/generar/generar_actividades_s7.py` desde `fichas_s7.py`, la misma fuente de las actividades y del deck: si cambias algo, cámbialo allí.

**Gherkin es tu CP con otra sintaxis: dice QUÉ pasa en el negocio. Las capas del framework dicen CÓMO.**

Objetivo de la sesión: Tu CP en Gherkin, mapeado a las capas del framework.

| Pieza | Dónde verla |
|---|---|
| Los escenarios (CP-101 resuelto; CP-102 a CP-106 para practicar) | `especificaciones/recargas.feature` |
| La prueba con un `test.step` por paso | `tests/recargas/CP-101-gherkin.spec.ts` |
| La tarea del «Cuando», que usa el Page Object por dentro | `src/screenplay/recargas/RecargarDesdeLaPantalla.ts` |
| El revisor de escenarios | `laboratorio/revisor-escenarios.js` · `npm.cmd run revisar-escenarios` |

## Gherkin y BDD

| | |
|---|---|
| **El problema que ya sufrías a mano** | El CP del Excel lo entiende quien lo escribió; el script, solo quien sabe código. Negocio aprueba uno, QA automatiza otro, y con el tiempo dicen cosas distintas. |
| **La idea, en una frase** | Un escenario de Gherkin es el CP escrito para que lo lean negocio, QA y la máquina: **Dado** (la precondición), **Cuando** (lo que hace el cliente), **Entonces** (el resultado esperado, con el dato). |
| **Sus partes, en el repo** | `especificaciones/recargas.feature` (los escenarios, con la etiqueta `@CP-101`) · `tests/recargas/CP-101-gherkin.spec.ts` (cada paso es un `test.step`) · `src/screenplay/recargas/RecargarDesdeLaPantalla.ts` (la tarea que ejecuta el «Cuando»). |
| **Sí, cuando** | El caso tiene reglas de negocio que alguien tiene que aprobar (montos, límites, bloqueos) y lo van a leer personas que no programan. |
| **No, cuando** | Es una prueba técnica que solo lee QA (un contrato de API, un cálculo): ahí basta un `test()` con buen nombre. Y un Gherkin con clics («hago clic en…») es peor que no tener Gherkin. |
| **La frase para tu líder** | El escenario es el contrato: lo firma negocio, lleva el ID del ALM y corre sobre las mismas capas. Si cambia la pantalla, el escenario no se toca. |
| **Cómo pedírselo a la IA** | «Convierte este CP del Banco Demo en un escenario de Gherkin en español: Dado, Cuando y Entonces, sin clics ni localizadores, máximo 5 pasos, con la etiqueta @CP-xxx y el resultado esperado con el dato exacto. Si falta el esperado, escribe TODO: no lo inventes.» |

## BDD, Gherkin y la herramienta no son lo mismo

| | Qué es | Hoy |
|---|---|---|
| **BDD** | una **práctica de equipo**: descubrir el comportamiento con ejemplos (los «tres amigos»: negocio, desarrollo y QA), formularlo y automatizarlo. | Hoy solo **formulamos**. |
| **Gherkin** | el **lenguaje** de los escenarios: `Característica`, `Escenario`, `Dado`, `Cuando`, `Entonces`, `Y`, `Pero`. En español con `# language: es`. | Es lo que escriben hoy. |
| **Cucumber · playwright-bdd** | las **herramientas** que leen el `.feature` y llaman a un código por cada paso. | Hoy no se instalan: cada paso es un `test.step` y corre igual. |

En el banco, BDD casi siempre es Gherkin escrito por QA, no los tres amigos en una sala. Aun así vale: el valor real es la trazabilidad. `@CP-101` en el escenario es la fila del ALM (o de Xray).

## El CP-101 en tres idiomas

**1 · El caso manual**

- **CP-101 · Recarga normal a celular**
- Precondición: Ana inició sesión. Saldo de Ahorros: $1.500.000.
- 1. Ir a «Recargar celular».
- 2. Elegir Claro, escribir el celular 3001234567 y el valor $10.000.
- 3. Pulsar «Recargar».
- Esperado: comprobante con «Recarga exitosa». Saldo de Ahorros: $1.490.000.

**2 · Gherkin** (`especificaciones/recargas.feature`)

```gherkin
@CP-101
Escenario: Una recarga normal da comprobante y descuenta de Ahorros
  Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
  Cuando recarga $10.000 a un celular Claro 3001234567
  Entonces ve el comprobante «Recarga exitosa»
  Y su saldo de Ahorros queda en $1.490.000
```

**3 · La prueba** (`tests/recargas/CP-101-gherkin.spec.ts`)

```ts
test('CP-101 · Recarga normal a celular (escenario Gherkin)', { tag: '@CP-101' }, async ({ page, cliente, paginaRecargas }) => {
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
});
```

Se corre con `npx.cmd playwright test -g "CP-101" --project=recargas`. El reporte HTML muestra los pasos con el texto del escenario.

## Del escenario a las capas

| En el escenario | Capa | Pieza | En el código (CP-101) |
|---|---|---|---|
| `@CP-101` (la etiqueta) | Trazabilidad | El título y la etiqueta de la prueba | `{ tag: '@CP-101' }` · se corre con `-g "CP-101"` |
| **Dado** · la precondición | `src/flujos/` + `src/config/` | Un flujo o una tarea; usuario y clave del entorno | `await abrirConSesion(page, cliente, usuarios.ana)` |
| **Cuando** · lo que hace el cliente | `src/screenplay/` → `src/paginas/` | Una **tarea** que usa el Page Object por dentro | `await ana.intenta(RecargarDesdeLaPantalla.celular('3001234567').por(10_000))` |
| El dato ($10.000, Claro) | `src/datos/` | La fábrica: solo se escribe lo que cambia | `fabricaDeRecargas.valida({ monto: 10_000 })` |
| **Entonces** · el esperado | `tests/` | Un `expect` por resultado; lo que está en pantalla, con una aserción que reintenta | `await expect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000')` |
| El ambiente (no aparece en el escenario) | `src/config/` | La configuración de la S6 | `$env:AMBIENTE = 'qa'` |

**Un paso, una línea de código: si un paso necesita 10 líneas en la prueba, falta una tarea.**

### Tres precisiones

- **El `name` de `getByRole`.** `name` es el **nombre accesible**. En un botón es su texto visible, salvo que tenga `aria-label`, que lo reemplaza. No es el atributo `name` del HTML. Y busca un pedazo, sin importar mayúsculas: «Recargar ahora» también pasa; `exact: true` exige el nombre completo.
- **Page Object y Screenplay.** Page Object organiza **pantallas**; Screenplay organiza **tareas**. No compiten: la tarea `RecargarDesdeLaPantalla` usa `PaginaRecargas` por dentro. Page Object es la base; Screenplay se suma cuando hay varios actores (el cliente y el aprobador) o el mismo paso corre por varios canales.
- **El `await` en cada paso.** Todo lo que le pide algo al navegador lleva `await`: las acciones y los `expect` sobre localizadores. El localizador **no** lleva `await`: no hace nada hasta que se usa. Sin `await`, el resultado depende de la suerte: a veces pasa (la acción alcanzó a terminar) y a veces falla con un mensaje que no dice la causa (`Test ended`, `session closed`). Una prueba que pasa por suerte no es evidencia.

## Rosetta: lo de hoy en Java + Selenium + Cucumber o Serenity

| La pieza | Hoy (Playwright) | En el banco |
|---|---|---|
| El escenario | `especificaciones/recargas.feature` | El mismo `.feature`: Gherkin es igual en los dos |
| Un paso | `test.step('Cuando recarga…')` (o `When(...)` con playwright-bdd) | `@Cuando("recarga {int} a un celular {word} {string}")` en Cucumber-JVM |
| La tarea | `ana.intenta(RecargarDesdeLaPantalla.celular(...))` | `actor.attemptsTo(Recargar.celular(...))` en Serenity Screenplay |
| La memoria del actor | `actor.recuerda('clave', valor)` / `actor.recuerdo('clave')` | `actor.remember("clave", valor)` / `actor.recall("clave")` |
| El Page Object | `PaginaRecargas` con `getByRole('button', { name: 'Recargar' })` | `Target.the("botón Recargar").located(By...)` o un `PageObject` con `@FindBy` |
| La espera | Automática, y `await expect(...)` reintenta | `WebDriverWait` con `ExpectedConditions`. Nunca mezclar la espera implícita con la explícita |
| Las piezas de cada prueba | Los fixtures (`test.extend`) | Hooks `@Before` e inyección (PicoContainer o Spring) |
| El reporte | El reporte HTML de Playwright: pasos, trace, video | El reporte de Serenity o Allure |

Lo que se transfiere no es la sintaxis, es la idea: escenario de negocio, tarea con nombre, página que esconde el cómo, esperar un estado y nunca un tiempo.

## El revisor de escenarios

Señala lo típico: clics y pantalla (aviso), localizadores o código (error), esperas fijas y claves escritas (error), falta de ID `@CP-xxx` (error), falta de Dado, Cuando o Entonces (error), más de 5 pasos (aviso) y un «Entonces» sin dato (aviso). Es una ayuda, no un juez: si el esperado es el correcto lo decide la persona.

- En el navegador: actividades de la S7, sección «Tu CP en Gherkin».
- Con el repo: `npm.cmd run revisar-escenarios` (o `-- archivo.feature`).
- La solución de la práctica (CP-102 a CP-106) está en `laboratorio/generar/s07_solucion/especificaciones/recargas.feature`.

## La plantilla de un escenario

```gherkin
# language: es
Característica: <lo que el cliente puede hacer>
  Como <rol>
  quiero <acción>
  para <beneficio>

  @CP-<ID del caso>
  Escenario: <el resultado, en una frase>
    Dado que <el estado del negocio antes: quién, con qué>
    Cuando <lo que hace el cliente, con el dato>
    Entonces <lo que ve o lo que pasa, con el dato exacto>
```

## Fuentes

- Cucumber, «Gherkin Reference» (cucumber.io/docs/gherkin/reference): las palabras clave, también en español (`# language: es`).
- Seb Rose y Gáspár Nagy, *The BDD Books: Discovery* y *Formulation*: BDD es descubrir, formular y automatizar.
- Playwright, «test.step» (playwright.dev/docs/api/class-test#test-step) y «Annotations · Tag tests» (playwright.dev/docs/test-annotations): los pasos en el reporte y la etiqueta `@CP-101`.
- ISTQB, CTAL-TAE v2.0: la capa de definición de pruebas del gTAA.
