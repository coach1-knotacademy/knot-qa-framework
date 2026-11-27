/**
 * S9 · TRIAGE · ROJO 1 · CAJA: SISTEMA
 *
 * Es el CP-106 (el operador no responde) SIN la marca hallazgoEsperado. El operador simulado no responde
 * con el número de pruebas 3000000504; la regla del negocio dice que el cliente NO pierde la plata.
 * El Banco Demo la descuenta igual: es el BUG-04, sembrado a propósito. No se corrige.
 *
 * LA EVIDENCIA ES LA REGLA, no el trace: «Expected: 1500000 · Received: 1480000». El esperado sale de la
 * regla del negocio (no de lo que pinta la pantalla) y el saldo se lee por API: el saldo real, el del servicio.
 * La prueba hizo bien su trabajo: encontró un bug. El ticket va a desarrollo, con la regla y el ID del caso.
 *
 * En la suite (tests/recargas/recargas.spec.ts) este mismo caso lleva hallazgoEsperado('BUG-04', ...):
 * sale como FALLA ESPERADA, el cuarto estado. Un bug conocido, registrado con su ID, que no ensucia la
 * corrida y avisa el día que lo arreglen. Aquí se le quita la marca para ver el rojo tal como llega al daily.
 *
 * ¿test.slow() o retries? No. El sistema responde rápido y siempre igual: reintentar da el mismo rojo
 * y darle más tiempo no cambia la regla. Un rojo del sistema no se tapa: se reporta.
 *
 * Correrlo: npx.cmd playwright test --project=triage -g "rojo 1"
 */
import { fabricaDeRecargas } from '../../src/datos/fabricaDeRecargas';
import { usuarios } from '../../src/datos/usuarios';
import { abrirConSesion } from '../../src/flujos/sesion';
import { registrar } from '../../src/soporte/registro';
import { test, expect } from '../../src/soporte/fixtures';

test('rojo 1 · CP-106 · si el operador no responde, el cliente no pierde la plata', async ({ page, cliente, paginaRecargas }) => {
  await abrirConSesion(page, cliente, usuarios.ana);
  await paginaRecargas.abrir();

  await paginaRecargas.recargar(fabricaDeRecargas.aOperadorCaido({ monto: 20_000 }));
  expect(await paginaRecargas.esperarResultado()).toBe('El operador no responde. Intenta más tarde.');

  // Se actúa en la pantalla y se verifica en el servicio: el saldo real, no el que pinta la página.
  const saldo = await cliente.saldoDeAhorros();
  // El registro de la corrida: queda con la prueba en el reporte (Attachments), aunque el expect de abajo falle.
  await registrar('CP-106 · saldo de Ahorros por API', {
    regla: 'Si el operador no responde, el cliente no pierde la plata',
    esperado: 1_500_000,
    obtenido: saldo,
    hallazgo: 'BUG-04',
  });

  expect(saldo).toBe(1_500_000);
});
