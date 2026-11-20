/**
 * FIXTURES: le entregan a cada prueba sus piezas ya armadas. La prueba las pide por nombre
 *   test('...', async ({ paginaRecargas }) => { ... })
 * y nunca hace "new PaginaRecargas(page)". Cuando agregues una pantalla, agrégala aquí.
 */
import { test as base } from '@playwright/test';
import { PaginaRecargas } from '../paginas/PaginaRecargas';

interface Piezas {
  paginaRecargas: PaginaRecargas;
}

export const test = base.extend<Piezas>({
  paginaRecargas: async ({ page }, usar) => {
    await usar(new PaginaRecargas(page));
  },
});

export { expect } from '@playwright/test';
