/**
 * S5 · Bugs REALES de ParaBank, encontrados con estas pruebas (no los sembramos nosotros).
 *
 * Cada prueba dice lo que DEBERÍA pasar. Como el sitio tiene el bug, falla, y la marcamos
 * como "falla esperada" (hallazgoEsperado): la suite queda en verde y el hallazgo documentado.
 * Si un día Parasoft lo corrige, la prueba pasa y Playwright avisa.
 */
import { hallazgoEsperado } from '../../src/soporte/hallazgos';
import { test, expect } from '../../src/sitios/parabank/fixtures';

test('no deja transferir más de lo que hay en la cuenta', async ({ clienteNuevo, parabank }) => {
  hallazgoEsperado('PB-01', 'ParaBank deja transferir más del saldo y la cuenta queda en negativo');
  // Dos cuentas propias de esta prueba, con $100 cada una: no tocamos la cuenta principal.
  const origen = await parabank.abrirCuenta(clienteNuevo.id, 'CHECKING', clienteNuevo.cuentaPrincipal);
  const destino = await parabank.abrirCuenta(clienteNuevo.id, 'SAVINGS', clienteNuevo.cuentaPrincipal);

  const { estado } = await parabank.transferir(origen.id, destino.id, 10_000);

  expect(estado, 'el banco debería rechazar la transferencia').toBe(400);
  expect(await parabank.saldoDe(origen.id), 'la cuenta no debería quedar en negativo').toBe(100);
});

test('no acepta transferencias con monto negativo', async ({ clienteNuevo, parabank }) => {
  hallazgoEsperado('PB-02', 'ParaBank acepta montos negativos: la plata se mueve al revés');
  const origen = await parabank.abrirCuenta(clienteNuevo.id, 'CHECKING', clienteNuevo.cuentaPrincipal);
  const destino = await parabank.abrirCuenta(clienteNuevo.id, 'SAVINGS', clienteNuevo.cuentaPrincipal);

  const { estado } = await parabank.transferir(origen.id, destino.id, -50);

  expect(estado, 'el banco debería rechazar un monto negativo').toBe(400);
  expect(await parabank.saldoDe(destino.id)).toBe(100);
});
