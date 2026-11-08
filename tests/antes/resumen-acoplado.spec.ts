/**
 * ANTES (S4, DIP) · Para probar una suma hace falta el banco encendido.
 * ResumenAcoplado crea por dentro un ClienteHttp real. Esta prueba pasa, pero es lenta y
 * depende del servidor. Compárala con tests/retos-s04/reto5-dip.spec.ts.
 */
import { test, expect } from '@playwright/test';
import { usuarios } from '../../src/datos/usuarios';
import { ResumenAcoplado } from '../../src/legado/dip/ResumenAcoplado';

test('el saldo total de Ana es la suma de sus dos cuentas', async () => {
  const resumen = new ResumenAcoplado();

  expect(await resumen.saldoTotal(usuarios.ana)).toBe(1_750_000);
});
