/**
 * S5 · ASÍ NO. Esta prueba está en ROJO A PROPÓSITO.
 *
 * Usa siempre el mismo usuario, como cuando en el trabajo manual se reutiliza "el usuario
 * de pruebas de siempre". Simula dos corridas, la de ayer y la de hoy: la primera puede
 * funcionar, pero la segunda siempre falla porque el usuario ya existe, aunque el sitio
 * funcione bien. (Lo vimos de verdad: ParaBank reinicia su base de datos, y ese día la
 * prueba pasó una vez y al siguiente volvió a fallar.)
 *
 * La solución está en fabricaDeClientes.ts: un cliente nuevo y único en cada corrida.
 */
import { test, expect } from '../../src/sitios/parabank/fixtures';
import { fabricaDeClientes } from '../../src/sitios/parabank/fabricaDeClientes';

const USUARIO_DE_SIEMPRE = 'knotanafija';

async function registrarSinFallar(registrar: () => Promise<unknown>): Promise<string> {
  try {
    await registrar();
    return 'registrado';
  } catch (error) {
    return (error as Error).message;
  }
}

test('ASÍ NO · registrar siempre el mismo usuario (rojo a propósito)', async ({ parabank }) => {
  test.info().annotations.push({ type: 'antes', description: 'Dato fijo: funciona una sola vez. Ver fabricaDeClientes.ts' });
  const datos = fabricaDeClientes.nuevo({ usuario: USUARIO_DE_SIEMPRE });

  const ayer = await registrarSinFallar(() => parabank.registrar(datos));
  const hoy = await registrarSinFallar(() => parabank.registrar(datos));

  expect(ayer, 'la corrida de ayer').toBe('registrado');
  expect(hoy, 'la corrida de hoy, con el mismo usuario').toBe('registrado');
});
