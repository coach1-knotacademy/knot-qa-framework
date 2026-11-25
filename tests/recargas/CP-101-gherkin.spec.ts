/**
 * S7 · El CP-101 escrito en Gherkin (especificaciones/recargas.feature) y ejecutado con Playwright.
 *
 * No hace falta otra herramienta para empezar: cada paso de Gherkin es un test.step() con el mismo
 * texto, y el reporte HTML muestra el escenario paso a paso, como lo leería el líder o negocio.
 * (En un equipo con Node, playwright-bdd o Cucumber leen el .feature directamente; la idea es la misma.)
 *
 * El mapeo de cada paso a su capa:
 *   Dado     → la precondición: abrirConSesion (src/flujos/), con usuario y clave del entorno (src/config/)
 *   Cuando   → la TAREA RecargarDesdeLaPantalla (src/screenplay/), que usa PaginaRecargas (src/paginas/)
 *              y saca los datos de la fábrica (src/datos/)
 *   Entonces → un expect por cada resultado esperado; el saldo, con una aserción que reintenta
 *
 * Correr solo este caso:  npx.cmd playwright test -g "CP-101" --project=recargas
 */
import { abrirConSesion } from '../../src/flujos/sesion';
import { usuarios } from '../../src/datos/usuarios';
import { Actor } from '../../src/screenplay/Actor';
import { NavegarLaWeb } from '../../src/screenplay/navegador/NavegarLaWeb';
import { RecargarDesdeLaPantalla } from '../../src/screenplay/recargas/RecargarDesdeLaPantalla';
import { ResultadoDeLaRecarga } from '../../src/screenplay/recargas/ResultadoDeLaRecarga';
import { test, expect } from '../../src/soporte/fixtures';

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
