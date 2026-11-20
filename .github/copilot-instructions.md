# Instrucciones para Copilot en este repo

Este es un framework de práctica de automatización con Playwright y TypeScript (Bootcamp QA, Knot Academy). Cuando generes o cambies pruebas:

1. **Page Object para cada pantalla.** Los localizadores van solo en `src/paginas/` (Banco Demo) o `src/sitios/parabank/paginas/` (ParaBank), como `private readonly`. Las pruebas en `tests/` no tienen ni un localizador: llaman métodos como `paginaRecargas.recargar(...)`. Usa de modelo `src/paginas/PaginaLogin.ts`.
   **Localizadores por rol o por etiqueta** (S6), en este orden: `getByRole(rol, { name })`, `getByLabel`, `getByText`, `getByTestId`. Nunca CSS, XPath, clases, id ni `nth-child`. Si no hay nada que sirva, escribe `// TODO: pedir a desarrollo un data-testid para <elemento>`. No copies el estilo de `src/paginas/heredadas/`: son los localizadores frágiles del reto 2.
2. **Datos desde una fábrica.** Nada de usuarios, montos o números escritos a mano en la prueba: usa `src/datos/fabricaDeRecargas.ts`, `src/datos/fabricaDeTransferencias.ts` o `src/sitios/parabank/fabricaDeClientes.ts`, y solo cambia lo que le importa a la prueba.
3. **La dirección del sitio sale de la configuración.** Nunca escribas `http://127.0.0.1:4000` ni la URL de ParaBank en una prueba: usa rutas relativas (`/recargas`) y `src/config/entorno.ts`. Los ambientes están en `src/config/ambientes.ts` (`local`, `qa`, `uat`): nunca agregues producción ni escribas una clave; la clave llega por la terminal (`$env:CLAVE_BANCO`).
4. **Las piezas llegan por fixtures.** Importa `test` y `expect` desde `src/soporte/fixtures.ts` (o `src/sitios/parabank/fixtures.ts`). No hagas `new PaginaX(page)` dentro de la prueba.
5. **El resultado esperado sale de la regla de negocio, no de la pantalla.** Si no sabes cuál es el valor correcto, deja un comentario `// TODO: confirmar el valor esperado con la regla` en vez de copiar lo que muestra el sitio. Revisa `banco-demo/reglas.js`.
6. **Esperas sin pausas fijas.** Nada de `waitForTimeout`. Usa `expect(...).toHaveText(...)` o `locator.waitFor()`.
7. **No instales dependencias nuevas.** El repo vive con `@playwright/test`, `typescript` y `@types/node`. Si algo parece necesitar otra librería, dilo en un comentario.
8. **Nunca datos reales.** Ni de clientes, ni del banco, ni contraseñas. Solo los datos de práctica del Banco Demo y los que crean las fábricas.

Escribe en español: nombres de métodos, comentarios y títulos de las pruebas.
