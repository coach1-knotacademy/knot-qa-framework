/**
 * S5 · ParaBank: lo que un cliente hace con su plata, por la pantalla.
 * Varias pruebas son HÍBRIDAS: actúan en la pantalla y verifican en el servicio (o al revés).
 */
import { test, expect } from '../../src/sitios/parabank/fixtures';

test('abre una cuenta de ahorros y queda con los $100 de apertura', async ({ clienteEnSesion, abrirCuenta, parabank }) => {
  await abrirCuenta.abrir();
  const nueva = await abrirCuenta.abrirCuenta('SAVINGS', clienteEnSesion.cuentaPrincipal);

  // Verificar en el servicio, no en la pantalla: es la fuente de verdad.
  const { datos: cuentas } = await parabank.cuentas(clienteEnSesion.id);
  expect(cuentas.find((c) => c.id === nueva)).toMatchObject({ type: 'SAVINGS', balance: 100 });
});

test('transfiere $25 entre sus cuentas y los dos saldos cambian', async ({ clienteEnSesion, parabank, transferir }) => {
  // Preparar por API: más rápido y no es lo que esta prueba quiere probar.
  const ahorros = await parabank.abrirCuenta(clienteEnSesion.id, 'SAVINGS', clienteEnSesion.cuentaPrincipal);
  const antes = await parabank.saldoDe(clienteEnSesion.cuentaPrincipal);

  await transferir.abrir();
  await transferir.transferir({ monto: 25, desde: clienteEnSesion.cuentaPrincipal, hacia: ahorros.id });

  await expect(transferir.resultado).toContainText('$25.00 has been transferred');
  expect(await parabank.saldoDe(clienteEnSesion.cuentaPrincipal)).toBe(antes - 25);
  expect(await parabank.saldoDe(ahorros.id)).toBe(125);
});

test('la cuenta que se abre por API aparece en la pantalla', async ({ clienteEnSesion, parabank, resumen }) => {
  const corriente = await parabank.abrirCuenta(clienteEnSesion.id, 'CHECKING', clienteEnSesion.cuentaPrincipal);

  await resumen.abrir();

  await expect(resumen.filaDe(corriente.id)).toBeVisible();
  expect(await resumen.saldoDe(corriente.id)).toBe('$100.00');
});

test('paga una factura y el pago queda en los movimientos', async ({ clienteEnSesion, pagarFactura, parabank }) => {
  await pagarFactura.abrir();
  await pagarFactura.pagar({ beneficiario: 'Empresa de Energía', cuentaDelBeneficiario: '54321', monto: 40, desde: clienteEnSesion.cuentaPrincipal });

  await expect(pagarFactura.resultado).toContainText('Bill Payment to Empresa de Energía in the amount of $40.00');
  const movimientos = await parabank.movimientos(clienteEnSesion.cuentaPrincipal);
  expect(movimientos.some((m) => m.type === 'Debit' && m.amount === 40)).toBe(true);
});

test('un préstamo con cuota inicial mayor al saldo se niega', async ({ clienteEnSesion, prestamo }) => {
  await prestamo.abrir();
  await prestamo.solicitar({ monto: 10_000, cuotaInicial: 5_000, desde: clienteEnSesion.cuentaPrincipal });

  await expect(prestamo.estado).toHaveText('Denied');
  await expect(prestamo.motivoDelRechazo).toContainText('You do not have sufficient funds');
});
