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

// S7 · Cada paso del escenario (especificaciones/CP-101.feature) es un test.step con el mismo texto:
// el reporte HTML muestra el escenario paso a paso, como lo leería negocio.
test('CP-101 · una recarga de $10.000 a Claro da comprobante y descuenta de Ahorros', { tag: '@CP-101' }, async ({ paginaRecargas }) => {
  await test.step('Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros', async () => {
    await paginaRecargas.abrir();
    await expect(paginaRecargas.saldoDisponible).toHaveText('$1.500.000');
  });

  await test.step('Cuando recarga $10.000 a un celular Claro 3001234567', async () => {
    await paginaRecargas.recargar(fabricaDeRecargas.valida());
  });

  await test.step('Entonces ve el comprobante «Recarga exitosa»', async () => {
    expect(await paginaRecargas.esperarResultado()).toContain('Recarga exitosa');
  });

  await test.step('Y su saldo de Ahorros queda en $1.490.000', async () => {
    // Esperado de la regla, no de la pantalla: la recarga se descuenta completa de Ahorros (1.500.000 − 10.000).
    await expect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000');
  });
});
