/**
 * Kit «web real» · Toolshop: agregar al carrito y verificar la cantidad y el total (CP-504).
 * Escenario en especificaciones/toolshop.feature. La prueba se detiene en el carrito: no se compra.
 *
 * El esperado sale de la REGLA (total = precio unitario × cantidad), no de copiar lo que mostró la pantalla.
 *
 * Correr:  npx.cmd playwright test --project=toolshop -g "CP-504"
 */
import { fabricaDeCompras } from '../../src/sitios/toolshop/fabricaDeLaTienda';
import { test, expect } from '../../src/sitios/toolshop/fixtures';

test('CP-504 · Dos unidades en el carrito suman el doble del precio', { tag: '@CP-504' }, async ({ catalogo, producto, carrito }) => {
  const compra = fabricaDeCompras.dosUnidades();
  let precio = 0;

  await test.step('Dado que Ana tiene el carrito vacío', async () => {
    await catalogo.abrir();
    await expect(catalogo.nombresDeProductos.first()).toBeVisible();
    await expect(catalogo.unidadesEnElCarrito).toHaveCount(0);
  });

  await test.step(`Cuando lleva ${compra.cantidad} unidades de «${compra.producto}» al carrito`, async () => {
    await catalogo.abrirProducto(compra.producto);
    await expect(producto.nombre).toHaveText(compra.producto);
    precio = await producto.precioUnitario();
    await producto.agregarAlCarrito(compra.cantidad);
    await expect(producto.avisoAgregado).toBeVisible();
    await expect(producto.unidadesEnElCarrito).toHaveText(String(compra.cantidad));
    await producto.irAlCarrito();
  });

  await test.step(`Entonces el carrito muestra ${compra.cantidad} unidades de «${compra.producto}»`, async () => {
    await expect(carrito.cantidadDe(compra.producto)).toHaveValue(String(compra.cantidad));
  });

  await test.step(`Y el total es ${compra.cantidad} veces el precio unitario`, async () => {
    const esperado = `$${(precio * compra.cantidad).toFixed(2)}`;
    await expect(carrito.totalDeLaFila(compra.producto)).toHaveText(esperado);
    await expect(carrito.total).toHaveText(esperado);
  });
});
