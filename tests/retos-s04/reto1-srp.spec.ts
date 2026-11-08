/**
 * RETO 1 (S4) · SRP: cada clase con una sola tarea.
 * Pruebas de unidad: no abren navegador ni necesitan el banco. Tardan milisegundos.
 * Corre solo este reto:  npx playwright test reto1 --project=unidad
 */
import { test, expect } from '@playwright/test';
import { Bitacora } from '../../src/legado/srp/Bitacora';
import { leerCasos } from '../../src/legado/srp/LectorDeCasos';

test.describe('LectorDeCasos', () => {
  test('convierte cada fila en un caso con los nombres del encabezado', () => {
    const texto = 'id;caso;monto\nT01;Transferencia normal;100000\nT02;Monto bajo el mínimo;999';

    expect(leerCasos(texto)).toEqual([
      { id: 'T01', caso: 'Transferencia normal', monto: '100000' },
      { id: 'T02', caso: 'Monto bajo el mínimo', monto: '999' },
    ]);
  });

  test('ignora las líneas vacías y el \\r de los archivos de Windows', () => {
    const texto = 'id;monto\r\nT01;100000\r\n\r\nT02;999\r\n';

    expect(leerCasos(texto)).toEqual([
      { id: 'T01', monto: '100000' },
      { id: 'T02', monto: '999' },
    ]);
  });
});

test.describe('Bitacora', () => {
  test('cada línea lleva la hora y el mensaje', () => {
    const relojFijo = () => new Date('2026-11-12T23:00:00.000Z');
    const bitacora = new Bitacora(relojFijo);

    bitacora.registrar('Inicio de la prueba');
    bitacora.registrar('Transferencia enviada');

    expect(bitacora.lineas()).toEqual([
      '[2026-11-12T23:00:00.000Z] Inicio de la prueba',
      '[2026-11-12T23:00:00.000Z] Transferencia enviada',
    ]);
  });
});
