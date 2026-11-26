/**
 * FIXTURES de la Toolshop (kit «web real»): cada prueba recibe sus páginas ya armadas,
 * igual que con el Banco Demo (src/soporte/fixtures.ts) y con ParaBank.
 */
import { test as base } from '@playwright/test';
import { PaginaCarrito } from './paginas/PaginaCarrito';
import { PaginaCatalogo } from './paginas/PaginaCatalogo';
import { PaginaContacto } from './paginas/PaginaContacto';
import { PaginaIngreso } from './paginas/PaginaIngreso';
import { PaginaProducto } from './paginas/PaginaProducto';

interface PiezasToolshop {
  catalogo: PaginaCatalogo;
  producto: PaginaProducto;
  carrito: PaginaCarrito;
  contacto: PaginaContacto;
  ingreso: PaginaIngreso;
}

export const test = base.extend<PiezasToolshop>({
  catalogo: async ({ page }, usar) => usar(new PaginaCatalogo(page)),
  producto: async ({ page }, usar) => usar(new PaginaProducto(page)),
  carrito: async ({ page }, usar) => usar(new PaginaCarrito(page)),
  contacto: async ({ page }, usar) => usar(new PaginaContacto(page)),
  ingreso: async ({ page }, usar) => usar(new PaginaIngreso(page)),
});

export { expect } from '@playwright/test';
