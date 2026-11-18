/**
 * S5 · La misma prueba de "transferir entre mis cuentas", escrita con SCREENPLAY.
 * Léela en voz alta: suena como un caso de prueba manual.
 * Compárala con 'transfiere $25 entre sus cuentas' en cuentas.spec.ts (Page Object).
 */
import { Actor } from '../../src/screenplay/Actor';
import { AbrirCuenta, EntrarComo, SaldoDe, Transferir, UsarLaApiDeParaBank } from '../../src/sitios/parabank/screenplay/tareas';
import { test, expect } from '../../src/sitios/parabank/fixtures';

test('Ana abre una cuenta de ahorros y se pasa $50', async ({ parabank, clienteNuevo }) => {
  const ana = Actor.llamado('Ana').puede(UsarLaApiDeParaBank.con(parabank));

  await ana.intenta(
    EntrarComo.cliente(clienteNuevo),
    AbrirCuenta.deAhorros().llamada('ahorros'),
    Transferir.desde('principal').hacia('ahorros').por(50),
  );

  expect(await ana.pregunta(SaldoDe.cuenta('ahorros'))).toBe(150);
});
