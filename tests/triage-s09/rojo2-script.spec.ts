/**
 * S9 · TRIAGE · ROJO 2 · CAJA: SCRIPT
 *
 * Desarrollo publicó el rediseño de Recargas (REDISENO=1): cambiaron los id, las clases, el orden de los campos
 * y los contenedores. Lo que ve el cliente NO cambió: las etiquetas, los roles y los textos de los botones.
 * La prueba usa PaginaRecargasHeredada (S6), con los localizadores que leen el HTML por dentro.
 *
 * LA EVIDENCIA ES EL TRACE: la primera acción espera un localizador que nunca aparece
 * («waiting for locator('xpath=/html/body/main/form[1]/select')») y en la captura la lista «Operador»
 * está ahí, en otro contenedor. El sistema funciona: la prueba está mal. Lo arregla QA, es su código.
 * La salida es la escalera de la S6: getByRole / getByLabel sobreviven al rediseño; el XPath absoluto, no.
 *
 * ¿test.slow() o retries? No. El elemento no tarda: no existe con ese localizador. Con el triple de tiempo
 * espera el triple y falla igual; al reintentar, falla igual. Un rojo que se repite idéntico no es flaky.
 *
 * El rediseño, SOLO para esta prueba: el servidor con REDISENO=1 lo único que hace es poner
 * window.REDISENO_POR_DEFECTO = true en la página de Recargas (banco-demo/server.js). Aquí se pone lo mismo
 * con addInitScript, así el Banco Demo de las demás pruebas no cambia. En tu equipo, a mano, es lo mismo que:
 *   $env:REDISENO = '1'
 *   npm.cmd run demo        (y abre http://127.0.0.1:4000/recargas)
 *
 * Correrlo: npx.cmd playwright test --project=triage -g "rojo 2"
 * Tarda unos 30 segundos: la acción espera hasta que se acaba el tiempo de la prueba (30 s, como en todo el repo).
 */
import { fabricaDeRecargas } from '../../src/datos/fabricaDeRecargas';
import { usuarios } from '../../src/datos/usuarios';
import { abrirConSesion } from '../../src/flujos/sesion';
import { registrar } from '../../src/soporte/registro';
import { test, expect } from '../../src/soporte/fixtures';

test('rojo 2 · con el rediseño, la página heredada no encuentra el formulario de Recargas', async ({ page, cliente, paginaRecargasHeredada: heredada }) => {
  // «Desarrollo publicó el rediseño»: lo mismo que hace el servidor con REDISENO=1, pero solo en esta prueba.
  await page.addInitScript(() => {
    (window as unknown as { REDISENO_POR_DEFECTO: boolean }).REDISENO_POR_DEFECTO = true;
  });
  await abrirConSesion(page, cliente, usuarios.ana);
  // La dirección de siempre (/recargas): la prueba no sabe que hubo un rediseño, como en la vida real.
  await heredada.abrir();

  await registrar('pantalla y page object', {
    pantalla: page.url(),
    rediseno: 'REDISENO=1 (desarrollo publicó el rediseño)',
    pageObject: 'PaginaRecargasHeredada (src/paginas/heredadas/)',
    localizadores: {
      listaOperador: String(heredada.listaOperador),
      campoNumero: String(heredada.campoNumero),
      campoValor: String(heredada.campoValor),
      botonRecargar: String(heredada.botonRecargar),
    },
  });

  await heredada.recargar(fabricaDeRecargas.valida());

  expect(await heredada.esperarResultado()).toContain('Recarga exitosa');
});
