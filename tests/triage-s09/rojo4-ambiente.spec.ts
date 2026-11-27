/**
 * S9 · TRIAGE · ROJO 4 · CAJA: AMBIENTE (el servicio no respondió a tiempo)
 *
 * Con page.route se demora el servicio de saldos (/api/cuentas) 7 segundos, como un ambiente de QA lento.
 * El expect espera 5 segundos (el tiempo por defecto de Playwright): vence antes de que llegue el saldo.
 *
 * LA EVIDENCIA ES LA RED DEL TRACE: cuando vence el expect, la petición GET /api/cuentas sigue PENDIENTE
 * (en la pestaña «Network» no tiene respuesta). La pantalla y la prueba están bien: el servicio no respondió
 * a tiempo. El ticket va a infraestructura o al dueño del servicio, con la hora y la petición (están en el
 * registro de la corrida: «Attachments» del reporte).
 *
 * ¿Y test.slow()? Triplica el tiempo de LA PRUEBA (30 s → 90 s), no el del expect, que sigue en 5 s:
 * falla igual. ¿Y subir el timeout del expect a 10 s? Pasa… y esconde que el servicio tarda 7 s.
 * ¿Y retries? Abajo está el flaky: si la demora es solo la primera vez, el reintento pasa y el reporte dice
 * «1 flaky». Eso no es un verde: es una alerta que hay que investigar.
 *
 * Correrlo:
 *   npx.cmd playwright test --project=triage -g "rojo 4"
 *   npx.cmd playwright test --project=triage -g "flaky" --retries=1      (el reporte dice «1 flaky»)
 * En el repo retries es 0: aquí se pide --retries=1 a propósito, solo para mostrar el flaky.
 */
import { Page } from '@playwright/test';
import { usuarios } from '../../src/datos/usuarios';
import { abrirConSesion } from '../../src/flujos/sesion';
import { registrar } from '../../src/soporte/registro';
import { test, expect } from '../../src/soporte/fixtures';

/** El ambiente lento, simulado: cada petición de saldos espera `ms` antes de seguir hacia el Banco Demo. */
async function demorarElServicioDeSaldos(page: Page, ms: number): Promise<void> {
  await page.route('**/api/cuentas', async (ruta) => {
    // El registro de la corrida: la hora y la petición, lo que pide el ticket al ambiente.
    await registrar('petición demorada', { hora: new Date().toISOString(), metodo: ruta.request().method(), url: ruta.request().url(), demoraMs: ms });
    await new Promise((listo) => setTimeout(listo, ms));
    // Si la prueba ya terminó (falló el expect y se cerró la página), la petición ya no tiene a dónde ir.
    await ruta.continue().catch(() => {});
  });
}

test('rojo 4 · el saldo tarda 7 segundos y el expect espera 5', async ({ page, cliente, paginaRecargas }) => {
  await demorarElServicioDeSaldos(page, 7_000);
  await abrirConSesion(page, cliente, usuarios.ana);

  await paginaRecargas.abrir();

  await expect(paginaRecargas.saldoDisponible).toHaveText('$1.500.000');
});

test('flaky · el saldo tarda solo en el primer intento', async ({ page, cliente, paginaRecargas }) => {
  // test.info().retry dice qué reintento es: 0 la primera vez, 1 en el primer reintento.
  const intento = test.info().retry;
  await registrar('intento', { intento: intento + 1, demoraDelServicioMs: intento === 0 ? 7_000 : 0 });
  if (intento === 0) await demorarElServicioDeSaldos(page, 7_000);
  await abrirConSesion(page, cliente, usuarios.ana);

  await paginaRecargas.abrir();

  await expect(paginaRecargas.saldoDisponible).toHaveText('$1.500.000');
});
