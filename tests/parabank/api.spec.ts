/**
 * S5 · ParaBank por API (lo mismo que harías en Postman, pero repetible y con verificación).
 */
import { test, expect } from '../../src/sitios/parabank/fixtures';

test('el login por API devuelve el cliente', async ({ clienteNuevo, parabank }) => {
  const { estado, datos } = await parabank.login(clienteNuevo.usuario, clienteNuevo.clave);

  expect(estado).toBe(200);
  expect(datos).toMatchObject({ id: clienteNuevo.id, firstName: clienteNuevo.nombre });
});

test('con una clave equivocada el servicio no devuelve el cliente', async ({ clienteNuevo, parabank }) => {
  const { estado } = await parabank.login(clienteNuevo.usuario, 'otra-clave');

  expect(estado).toBe(400);
});

test('una transferencia por API mueve exactamente el monto', async ({ clienteNuevo, parabank }) => {
  const ahorros = await parabank.abrirCuenta(clienteNuevo.id, 'SAVINGS', clienteNuevo.cuentaPrincipal);

  const { estado, mensaje } = await parabank.transferir(clienteNuevo.cuentaPrincipal, ahorros.id, 30);

  expect(estado).toBe(200);
  expect(mensaje).toContain('Successfully transferred $30');
  expect(await parabank.saldoDe(ahorros.id)).toBe(130);
});
