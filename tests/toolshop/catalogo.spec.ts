/**
 * Kit «web real» · Toolshop: buscar, filtrar y ver el detalle (CP-501 a CP-503).
 * Los escenarios están en especificaciones/toolshop.feature. Cada paso de Gherkin es un test.step con el mismo texto.
 *
 * El mapeo de cada paso a su capa:
 *   Dado     → abrir la página (la dirección sale de entornoToolshop, vía baseURL)
 *   Cuando   → un método del Page Object (src/sitios/toolshop/paginas/), con el dato de la fábrica
 *   Entonces → un expect que reintenta. La lista de productos se actualiza DESPUÉS de buscar:
 *              expect.poll vuelve a preguntar hasta que la lista nueva aparece.
 *
 * Correr:  npx.cmd playwright test --project=toolshop
 */
import { catalogoDePrueba } from '../../src/sitios/toolshop/fabricaDeLaTienda';
import { test, expect } from '../../src/sitios/toolshop/fixtures';

test('CP-501 · La búsqueda muestra solo los productos que coinciden', { tag: '@CP-501' }, async ({ catalogo }) => {
  const { busqueda } = catalogoDePrueba;

  await test.step('Dado que Ana está en el catálogo de la tienda', async () => {
    await catalogo.abrir();
    await expect(catalogo.nombresDeProductos.first()).toBeVisible();
  });

  await test.step(`Cuando busca «${busqueda}»`, async () => {
    await catalogo.buscar(busqueda);
  });

  await test.step(`Entonces ve el título «Searched for: ${busqueda}»`, async () => {
    await expect(catalogo.tituloDeLaBusqueda).toHaveText(`Searched for: ${busqueda}`);
  });

  await test.step(`Y todos los productos que ve tienen «${busqueda}» en el nombre`, async () => {
    await expect.poll(() => catalogo.todosLosProductosDicen(busqueda), { message: `Hay productos que no dicen «${busqueda}»` }).toBe(true);
  });
});

test('CP-502 · El filtro por categoría deja solo esa categoría', { tag: '@CP-502' }, async ({ catalogo }) => {
  const { categoria } = catalogoDePrueba;

  await test.step('Dado que Ana está en el catálogo de la tienda', async () => {
    await catalogo.abrir();
    await expect(catalogo.nombresDeProductos.first()).toBeVisible();
  });

  await test.step(`Cuando filtra por la categoría «${categoria}»`, async () => {
    await catalogo.filtrarPorCategoria(categoria);
  });

  await test.step(`Entonces todos los productos que ve tienen «${categoria}» en el nombre`, async () => {
    await expect.poll(() => catalogo.todosLosProductosDicen(categoria), { message: `Hay productos fuera de «${categoria}»` }).toBe(true);
  });
});

test('CP-503 · El detalle de un producto muestra el mismo precio del catálogo', { tag: '@CP-503' }, async ({ catalogo, producto }) => {
  const nombre = catalogoDePrueba.productoConDetalle;
  let precioDelCatalogo = 0;

  await test.step('Dado que Ana está en el catálogo de la tienda', async () => {
    await catalogo.abrir();
    await expect(catalogo.nombresDeProductos.first()).toBeVisible();
    precioDelCatalogo = await catalogo.precioEnElCatalogo(nombre);
  });

  await test.step(`Cuando abre el detalle de «${nombre}»`, async () => {
    await catalogo.abrirProducto(nombre);
  });

  await test.step(`Entonces ve el nombre «${nombre}» y su descripción`, async () => {
    await expect(producto.nombre).toHaveText(nombre);
    await expect(producto.descripcion).not.toBeEmpty();
  });

  await test.step('Y el precio es el mismo que mostraba el catálogo', async () => {
    // El oráculo no es un número escrito a mano: es la consistencia entre dos pantallas del mismo sistema.
    expect(await producto.precioUnitario()).toBe(precioDelCatalogo);
  });
});
