/**
 * RETO 4 (S4) · ISP: ninguna clase debe tener métodos que no sabe hacer.
 */
import { test, expect } from '@playwright/test';
import { PaginaSaldos } from '../../src/legado/isp/PaginaSaldos';
import { NavegadorFalso } from './dobles/NavegadorFalso';

test('PaginaSaldos solo ofrece lo que sabe hacer', async () => {
  const pagina = new PaginaSaldos(new NavegadorFalso());
  // Recorre todos los métodos de la clase y anota los que responden "No aplica".
  const metodos = Object.getOwnPropertyNames(PaginaSaldos.prototype).filter((nombre) => nombre !== 'constructor');
  const queNoAplican: string[] = [];
  for (const nombre of metodos) {
    const metodo = Reflect.get(pagina, nombre) as (...valores: string[]) => Promise<unknown>;
    await metodo.call(pagina, 'x', 'y').catch((error: Error) => {
      if (error.message.includes('No aplica')) queNoAplican.push(nombre);
    });
  }

  expect(queNoAplican, 'PENDIENTE (S4): PaginaSaldos todavía tiene métodos que lanzan "No aplica" — ver retos/S04.md, reto 4').toEqual([]);
});

test('abre, lee un saldo y cierra sesión', async () => {
  const navegador = new NavegadorFalso({ 'saldo Corriente': '$250.000' });
  const pagina = new PaginaSaldos(navegador);

  await pagina.abrir();
  const saldo = await pagina.saldoDe('Corriente');
  await pagina.cerrarSesion();

  expect(saldo).toBe('$250.000');
  expect(navegador.acciones).toEqual(['ir /inicio', 'leer saldo Corriente', 'pulsar Salir']);
});
