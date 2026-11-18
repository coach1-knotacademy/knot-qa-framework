/**
 * RETO 1 (S5) · FACTORY: completar la fábrica de transferencias.
 * Modelo: src/datos/fabricaDeRecargas.ts. Cada paso tiene su propia prueba:
 * si uno queda pendiente, los demás se pueden revisar igual.
 */
import { test, expect } from '@playwright/test';
import { fabricaDeTransferencias } from '../../src/datos/fabricaDeTransferencias';

const AHORROS = '1000000001';
const CORRIENTE = '1000000002';
const DESTINO = '2000000001';

test('modelo · valida() arma una transferencia por defecto y deja cambiar solo un dato', () => {
  expect(fabricaDeTransferencias.valida()).toEqual({ origen: AHORROS, destino: DESTINO, monto: 100_000 });
  expect(fabricaDeTransferencias.valida({ monto: 5_000 })).toEqual({ origen: AHORROS, destino: DESTINO, monto: 5_000 });
});

test('paso 1 · desdeCorriente() sale de la cuenta Corriente', () => {
  expect(fabricaDeTransferencias.desdeCorriente()).toEqual({ origen: CORRIENTE, destino: DESTINO, monto: 100_000 });
  expect(fabricaDeTransferencias.desdeCorriente({ monto: 7_000 }).monto).toBe(7_000);
});

test('paso 2 · alMontoMinimo() es de exactamente $1.000', () => {
  expect(fabricaDeTransferencias.alMontoMinimo()).toEqual({ origen: AHORROS, destino: DESTINO, monto: 1_000 });
  expect(fabricaDeTransferencias.alMontoMinimo({ origen: CORRIENTE }).origen).toBe(CORRIENTE);
});

test('paso 3 · aLaMismaCuenta() pone como destino la misma cuenta de origen', () => {
  expect(fabricaDeTransferencias.aLaMismaCuenta()).toEqual({ origen: AHORROS, destino: AHORROS, monto: 100_000 });
  expect(fabricaDeTransferencias.aLaMismaCuenta({ origen: CORRIENTE }).destino).toBe(CORRIENTE);
});

test('cada llamada entrega un objeto nuevo: si una prueba lo cambia, no daña a las demás', () => {
  const primera = fabricaDeTransferencias.valida();
  primera.monto = 1;

  expect(fabricaDeTransferencias.valida().monto).toBe(100_000);
});
