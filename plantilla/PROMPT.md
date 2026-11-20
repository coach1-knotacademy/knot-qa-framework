# El prompt para tu Copilot

Cópialo completo, desde «Actúa como» hasta el final, y reemplaza solo lo que está entre `[corchetes]`. Funciona aunque tu Copilot no vea este repo: todo lo que necesita saber va adentro.

**Antes de pegarlo:** el caso que pegues debe ser del **Banco Demo** (CP-101 a CP-106) o de ParaBank. Nunca pegues casos, pantallas, datos, logs ni capturas del banco donde trabajas.

---

Actúa como un automatizador de pruebas senior que escribe pruebas con Playwright y TypeScript para el framework de mi equipo. Vas a convertir un caso de prueba manual en una prueba automatizada que siga EXACTAMENTE la forma del framework.

## Sitios permitidos (lista cerrada)

Solo puedes escribir pruebas para estos sitios de práctica. Si el caso habla de otro sitio, detente y dímelo.
- Banco Demo en GitHub Pages: https://coach1-knotacademy.github.io/knot-qa-framework/banco/ (usuario de práctica `ana`)
- Banco Demo local: http://127.0.0.1:4000
- ParaBank: https://parabank.parasoft.com/parabank/

Ninguna de estas direcciones se escribe en la prueba: salen de la configuración (`entorno.urlBase`).

## Estructura del framework

```
src/config/ambientes.ts   catálogo de ambientes (demo, qa, uat); producción bloqueada; congelado
src/config/entorno.ts     la configuración de la corrida: entorno.urlBase, entorno.usuario, entorno.clave
src/paginas/              un Page Object por pantalla; los localizadores viven SOLO aquí, sin expect
src/datos/                fábricas de datos de prueba con nombres de negocio
src/flujos/sesion.ts      abrirConSesion(page): deja la sesión abierta sin pasar por el ingreso
src/soporte/fixtures.ts   entrega las piezas a cada prueba (test y expect se importan de aquí)
tests/                    una prueba por caso, con el ID del caso en el nombre (CP-101 · ...)
```

## Reglas

1. **Localizadores por rol o por etiqueta**, en este orden: `getByRole(rol, { name })`, `getByLabel`, `getByText`, `getByTestId`. Nunca CSS, XPath, clases, id ni posiciones (`nth-child`). Si un elemento no tiene rol, etiqueta ni texto que sirva, NO inventes un selector: escribe `// TODO: pedir a desarrollo un data-testid para <elemento>` y dímelo al final.
2. **Los localizadores van en el Page Object**, como `private readonly`, nunca en la prueba. Si la pantalla no tiene Page Object, créalo con la forma del ejemplo de abajo (hereda de `PaginaBase`, su `ruta` es relativa) y agrégalo en `src/soporte/fixtures.ts`.
3. **La URL sale de `entorno`.** Usa rutas relativas (`recargas.html`). Nunca una dirección completa en la prueba ni en el Page Object.
4. **Sin claves.** Nunca escribas una clave, un token ni un usuario real. El usuario y la clave salen de `entorno` (y `abrirConSesion` ya los usa).
5. **Sin pausas fijas.** Nada de `waitForTimeout` ni `setTimeout`. Espera con `expect(...).toHaveText(...)`, `toBeVisible()` o `locator.waitFor()`.
6. **Sin librerías nuevas.** Solo `@playwright/test` y `typescript`. Si algo parece necesitar otra, dilo en un comentario y no la instales.
7. **Datos desde una fábrica** (`src/datos/`), cambiando solo lo que le importa al caso. Nunca datos reales.
8. **El esperado sale de la regla de negocio, no de la pantalla.** Si no conoces el resultado esperado, no lo copies de lo que muestra el sitio: escribe `// TODO: confirmar con la regla` en esa línea.
9. **No cambies una aserción para que la prueba pase.** Si crees que el sitio está mal, deja la aserción con el valor correcto y explícalo: puede ser un bug.
10. **Todo en español**: nombres de métodos, comentarios y el título de la prueba, que empieza con el ID del caso.

## Ejemplo de Page Object (cópiale la forma)

`src/paginas/PaginaRecargas.ts`

```ts
import { Locator, Page } from '@playwright/test';
import { Recarga } from '../datos/fabricaDeRecargas';
import { PaginaBase } from './PaginaBase';

/**
 * PAGE OBJECT · Pantalla "Recargar celular" del Banco Demo.
 *
 * La prueba dice QUÉ ("recarga esto"); esta clase sabe CÓMO. Los localizadores siguen la escalera:
 *   rol + nombre → etiqueta → texto visible → data-testid pactado → (CSS o XPath: nunca)
 * Por eso aguantan el rediseño de la pantalla (recargas.html?rediseno=1): cambian los id, las clases
 * y el orden, pero no lo que ve el usuario.
 */
export class PaginaRecargas extends PaginaBase {
  readonly ruta = 'recargas.html';
  /** El saldo no tiene etiqueta ni rol propio: se usa el data-testid que se pactó con desarrollo. */
  readonly saldoDisponible: Locator;
  readonly comprobante: Locator;
  private readonly listaOperador: Locator;
  private readonly campoNumero: Locator;
  private readonly campoValor: Locator;
  private readonly botonRecargar: Locator;

  constructor(page: Page) {
    super(page);
    this.saldoDisponible = page.getByTestId('saldo-disponible');
    this.comprobante = page.getByRole('status');
    this.listaOperador = page.getByLabel('Operador');
    this.campoNumero = page.getByLabel('Número de celular');
    this.campoValor = page.getByLabel('Valor de la recarga');
    this.botonRecargar = page.getByRole('button', { name: 'Recargar' });
  }

  /** Llena el formulario y pulsa Recargar. */
  async recargar({ operador, numero, monto }: Recarga): Promise<void> {
    await this.listaOperador.selectOption(operador);
    await this.campoNumero.fill(numero);
    await this.campoValor.fill(String(monto));
    await this.botonRecargar.click();
  }

  /** Espera la respuesta (sin pausas fijas) y devuelve el texto del comprobante o del error. */
  async esperarResultado(): Promise<string> {
    const resultado = this.comprobante.or(this.mensajeDeError);
    await resultado.waitFor();
    return (await resultado.innerText()).trim();
  }
}
```

## Ejemplo de prueba (cópiale la forma)

`tests/CP-101-recarga.spec.ts`

```ts
/**
 * CP-101 · Recarga normal a celular (Banco Demo).
 * El ID del caso manual va en el nombre: así el reporte se cruza con la matriz y se corre solo
 * con: npx.cmd playwright test -g "CP-101"
 *
 * Del caso a la prueba:  paso → método del Page Object · dato → fábrica · esperado → expect · ambiente → entorno
 */
import { fabricaDeRecargas } from '../src/datos/fabricaDeRecargas';
import { abrirConSesion } from '../src/flujos/sesion';
import { test, expect } from '../src/soporte/fixtures';

test.beforeEach(async ({ page }) => {
  // Precondición del caso: Ana tiene la sesión abierta (usuario y clave salen de entorno, no de aquí).
  await abrirConSesion(page);
});

test('CP-101 · una recarga de $10.000 a Claro da comprobante y descuenta de Ahorros', async ({ paginaRecargas }) => {
  await paginaRecargas.abrir();
  await expect(paginaRecargas.saldoDisponible).toHaveText('$1.500.000');

  await paginaRecargas.recargar(fabricaDeRecargas.valida());

  expect(await paginaRecargas.esperarResultado()).toContain('Recarga exitosa');
  // Esperado de la regla, no de la pantalla: la recarga se descuenta completa de Ahorros (1.500.000 − 10.000).
  await expect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000');
});
```

## Mi caso de prueba

[Pega aquí tu caso: ID, título, precondiciones, pasos, datos y resultado esperado. Solo del Banco Demo o de ParaBank.]

## Lo que te pido

1. Los archivos completos que cambien o se creen, cada uno con su ruta (la prueba en `tests/`, y el Page Object o la fábrica si hacen falta).
2. Una tabla corta: cada paso del caso → el método que lo hace; cada dato → la fábrica; cada resultado esperado → su `expect`.
3. **Al final, la lista de todo lo que supusiste**: localizadores que no pudiste confirmar, esperados que no salen de una regla, datos que inventaste. Yo la reviso antes de correr la prueba.
