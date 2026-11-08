/**
 * RETO 5 (S4) · DIP: depender de una interfaz y usar un doble en la prueba de unidad.
 * Compara con tests/antes/resumen-acoplado.spec.ts, que necesita el banco encendido.
 */
import { test, expect } from '@playwright/test';
import { usuarios } from '../../src/datos/usuarios';
import { ResumenDeCuentas } from '../../src/legado/dip/ResumenDeCuentas';
import { ClienteFalso } from './dobles/ClienteFalso';

test('suma los saldos con un cliente falso, sin banco', async () => {
  const cliente = new ClienteFalso([
    { numero: '1000000001', tipo: 'Ahorros', saldo: 1_000 },
    { numero: '1000000002', tipo: 'Corriente', saldo: 2_500 },
  ]);
  const resumen = new ResumenDeCuentas(cliente);

  expect(await resumen.saldoTotal(usuarios.ana)).toBe(3_500);
  expect(cliente.sesiones).toEqual([usuarios.ana.usuario]);
});

test('un cliente sin cuentas da saldo total 0', async () => {
  // Con el banco real este caso no se puede probar: siempre arranca con 2 cuentas.
  const resumen = new ResumenDeCuentas(new ClienteFalso([]));

  expect(await resumen.saldoTotal(usuarios.luis)).toBe(0);
});
