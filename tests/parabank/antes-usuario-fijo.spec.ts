/**
 * S5 · ASÍ NO. Esta prueba está en ROJO A PROPÓSITO.
 *
 * Registra siempre al mismo usuario, como cuando en el trabajo manual se reutiliza "el usuario
 * de pruebas de siempre". Pasa la primera vez. Desde la segunda, ParaBank responde que el
 * usuario ya existe y la prueba falla, aunque el sitio funcione bien.
 *
 * La solución está en fabricaDeClientes.ts: un cliente nuevo y único en cada prueba.
 */
import { test, expect } from '../../src/sitios/parabank/fixtures';
import { fabricaDeClientes } from '../../src/sitios/parabank/fabricaDeClientes';

test('ASÍ NO · registrar siempre el mismo usuario (rojo a propósito)', async ({ parabank }) => {
  test.info().annotations.push({ type: 'antes', description: 'Dato fijo: funciona una sola vez. Ver fabricaDeClientes.ts' });

  const cliente = await parabank.registrar(fabricaDeClientes.nuevo({ usuario: 'knotanafija' }));

  expect(cliente.id).toBeGreaterThan(0);
});
