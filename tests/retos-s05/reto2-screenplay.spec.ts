/**
 * RETO 2 (S5, extra) · SCREENPLAY: la tarea Recargar.
 * Sin navegador ni banco: la habilidad usa una BilleteraFalsa que vive en memoria.
 */
import { test, expect } from '@playwright/test';
import { Actor } from '../../src/screenplay/Actor';
import { Recargar } from '../../src/screenplay/billetera/Recargar';
import { SaldoDisponible } from '../../src/screenplay/billetera/SaldoDisponible';
import { UsarLaBilletera } from '../../src/screenplay/billetera/UsarLaBilletera';
import { BilleteraFalsa } from './dobles/BilleteraFalsa';

test('Ana recarga $20.000 y su saldo baja exactamente eso', async () => {
  const billetera = new BilleteraFalsa(100_000);
  const ana = Actor.llamado('Ana').puede(UsarLaBilletera.de(billetera));

  await ana.intenta(Recargar.celular('3109876543').por(20_000));

  expect(await ana.pregunta(SaldoDisponible.enLaBilletera())).toBe(80_000);
  expect(billetera.recargasRecibidas).toEqual([{ operador: 'Claro', numero: '3109876543', monto: 20_000 }]);
});

test('si la billetera dice que no, la tarea falla con el mismo mensaje', async () => {
  const ana = Actor.llamado('Ana').puede(UsarLaBilletera.de(new BilleteraFalsa(5_000)));

  let mensaje = '';
  try {
    await ana.intenta(Recargar.celular('3109876543').por(20_000));
  } catch (error) {
    mensaje = (error as Error).message;
  }

  expect(mensaje).toBe('Ana no pudo recargar: Saldo insuficiente');
});
