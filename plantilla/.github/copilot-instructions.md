# Instrucciones para Copilot en este framework

Framework de automatización con Playwright y TypeScript, por capas (Bootcamp QA, Knot Academy). Cuando generes o cambies pruebas:

1. **Solo sitios de práctica:** el Banco Demo (GitHub Pages o `http://127.0.0.1:4000`) y ParaBank. Nunca sistemas, datos, pantallas ni logs de un banco real.
2. **Localizadores por rol o por etiqueta**, en este orden: `getByRole(rol, { name })`, `getByLabel`, `getByText`, `getByTestId`. Nunca CSS, XPath, clases, id ni `nth-child`. Si no hay nada que sirva, escribe `// TODO: pedir a desarrollo un data-testid para <elemento>`.
3. **Page Object para cada pantalla** en `src/paginas/`, con los localizadores `private readonly` y sin `expect`. Modelo: `src/paginas/PaginaRecargas.ts`. Las pruebas en `tests/` no tienen localizadores.
4. **La URL sale de `src/config/entorno.ts`.** Rutas relativas (`recargas.html`); nunca una dirección completa.
5. **Sin claves en el código.** El usuario y la clave salen de `entorno`; fuera del ambiente `demo`, la clave llega por la terminal (`$env:CLAVE_BANCO`).
6. **Las piezas llegan por fixtures:** importa `test` y `expect` desde `src/soporte/fixtures.ts`. No hagas `new PaginaX(page)` en la prueba.
7. **Datos desde una fábrica** (`src/datos/`), cambiando solo lo que le importa a la prueba.
8. **El esperado sale de la regla de negocio, no de la pantalla.** Si no lo conoces: `// TODO: confirmar con la regla`. Nunca cambies una aserción para que la prueba pase.
9. **Sin `waitForTimeout`** ni librerías nuevas (solo `@playwright/test` y `typescript`).
10. **El ID del caso manual va en el título** de la prueba: `CP-101 · ...`.

Escribe en español: nombres de métodos, comentarios y títulos. Al final de tu respuesta, lista lo que supusiste.
