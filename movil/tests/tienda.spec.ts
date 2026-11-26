/**
 * Kit móvil · La tienda de práctica en un emulador Android, con Appium + WebdriverIO + TypeScript.
 *
 * Cada it() es un escenario de especificaciones/tienda.feature y cada paso() es una línea del Gherkin,
 * con el mismo texto (como test.step en Playwright). La prueba no tiene ni un localizador: están en
 * src/paginas/. Los datos salen de src/datos/. La evidencia (capturas, video, pasos) la deja
 * src/soporte/evidencias.ts sin que la prueba lo pida.
 *
 * Antes de cada prueba la app se abre limpia (sin sesión, carrito vacío): wdio.conf.ts → beforeTest.
 */
import { expect } from '@wdio/globals';
import { PaginaCarrito } from '../src/paginas/PaginaCarrito';
import { PaginaCatalogo } from '../src/paginas/PaginaCatalogo';
import { PaginaDetalle } from '../src/paginas/PaginaDetalle';
import { PaginaLogin } from '../src/paginas/PaginaLogin';
import { PaginaMenu } from '../src/paginas/PaginaMenu';
import { comoLoMuestraLaApp, productos, totalEsperado } from '../src/datos/productos';
import { usuarios } from '../src/datos/usuarios';
import { paso } from '../src/soporte/evidencias';

describe('Tienda móvil · Comprar en la tienda desde el celular', () => {
  const menu = new PaginaMenu();
  const login = new PaginaLogin();
  const catalogo = new PaginaCatalogo();
  const detalle = new PaginaDetalle();
  const carrito = new PaginaCarrito();

  it('@CP-401 Un comprador entra con su usuario y su clave', async () => {
    await paso('Dado que el comprador abre la pantalla de inicio de sesión', async () => {
      await menu.irAIniciarSesion();
      await login.esperarQueCargue();
    });
    await paso('Cuando entra con su correo y su clave', async () => {
      await login.entrarCon(usuarios.comprador);
    });
    await paso('Entonces ve el catálogo «Products»', async () => {
      await catalogo.esperarQueCargue();
      await expect(catalogo.titulo).toHaveText('Products');
    });
    await paso('Y el menú le ofrece «Log Out»', async () => {
      await menu.abrirMenu();
      await expect(menu.opcionCerrarSesion).toHaveText('Log Out');
    });
  });

  it('@CP-402 Un usuario bloqueado no puede entrar', async () => {
    await paso('Dado que el usuario bloqueado abre la pantalla de inicio de sesión', async () => {
      await menu.irAIniciarSesion();
      await login.esperarQueCargue();
    });
    await paso('Cuando entra con su correo y su clave', async () => {
      await login.entrarCon(usuarios.bloqueado);
    });
    await paso('Entonces ve el mensaje «Sorry this user has been locked out.»', async () => {
      await expect(login.errorDeLaClave).toHaveText('Sorry this user has been locked out.');
    });
    await paso('Y sigue en la pantalla «Login»', async () => {
      await expect(login.titulo).toHaveText('Login');
    });
  });

  it('@CP-403 Sin usuario, la app lo pide antes de intentar entrar', async () => {
    await paso('Dado que alguien abre la pantalla de inicio de sesión', async () => {
      await menu.irAIniciarSesion();
      await login.esperarQueCargue();
    });
    await paso('Cuando intenta entrar sin escribir correo ni clave', async () => {
      await login.entrarCon(usuarios.vacio);
    });
    await paso('Entonces ve el mensaje «Username is required»', async () => {
      await expect(login.errorDelUsuario).toHaveText('Username is required');
    });
  });

  it('@CP-404 Dos mochilas en el carrito suman el total correcto', async () => {
    const mochila = productos.mochila;
    const precio = comoLoMuestraLaApp(mochila.precioEnCentavos);
    await paso('Dado que el cliente está en el catálogo con el carrito vacío', async () => {
      await expect(catalogo.titulo).toBeDisplayed();
      await expect(catalogo.contadorDelCarrito).not.toBeExisting();
    });
    await paso(`Cuando agrega 2 «${mochila.nombre}» de ${precio} al carrito`, async () => {
      await catalogo.abrirProducto(mochila.nombre);
      await detalle.esperarQueCargue();
      await expect(detalle.precio).toHaveText(precio);
      await detalle.agregarAlCarrito(2);
      await expect(detalle.contadorDelCarrito).toHaveText('2');
      await detalle.irAlCarrito();
      await carrito.esperarQueCargue();
    });
    await paso('Entonces el carrito muestra 2 artículos', async () => {
      await expect(carrito.cantidadDeArticulos).toHaveText('2 Items');
    });
    await paso(`Y el total es ${totalEsperado(mochila, 2)}`, async () => {
      await expect(carrito.total).toHaveText(totalEsperado(mochila, 2));
    });
  });
});
