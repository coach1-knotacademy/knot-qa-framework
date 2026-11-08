/**
 * RETO 3 (S4) · LSP: una hija debe poder usarse donde se usa su padre, sin sorpresas.
 */
import { test, expect } from '@playwright/test';
import { PaginaConsulta, PaginaDeCuentas, PaginaTransferencia, transferirDesdeTodas } from '../../src/legado/lsp/paginasDeCuenta';
import { NavegadorFalso } from './dobles/NavegadorFalso';

const PENDIENTE = 'PENDIENTE (S4): corrige la jerarquía en src/legado/lsp/paginasDeCuenta.ts — ver retos/S04.md, reto 3';

test('PaginaConsulta ya no se hace pasar por una PaginaTransferencia', () => {
  const consulta = new PaginaConsulta(new NavegadorFalso());

  expect(consulta instanceof PaginaTransferencia, PENDIENTE).toBe(false);
});

test('las dos páginas comparten lo común a través de PaginaDeCuentas', async () => {
  const navegador = new NavegadorFalso({ 'saldo Ahorros': '$1.500.000' });

  for (const pagina of [new PaginaTransferencia(navegador), new PaginaConsulta(navegador)]) {
    expect(pagina instanceof PaginaDeCuentas, PENDIENTE).toBe(true);
    await pagina.abrir();
    expect(await pagina.saldoDe('Ahorros')).toBe('$1.500.000');
  }
  expect(navegador.acciones).toEqual(['ir /transferir', 'leer saldo Ahorros', 'ir /inicio', 'leer saldo Ahorros']);
});

test('toda PaginaTransferencia puede transferir', async () => {
  const navegador = new NavegadorFalso();

  await transferirDesdeTodas([new PaginaTransferencia(navegador)], '2000000001', 50_000);

  expect(navegador.acciones).toContain('pulsar Transferir');
});
