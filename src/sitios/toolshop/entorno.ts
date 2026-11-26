/**
 * CONFIGURACIÓN de la Toolshop (kit «web real»): Practice Software Testing, una tienda PÚBLICA
 * hecha para practicar automatización (https://practicesoftwaretesting.com).
 *
 * Es un sitio real y compartido: cualquier persona del mundo prueba ahí al mismo tiempo. Por eso:
 *  - cada prueba arranca con un carrito vacío (cada prueba abre su propio navegador limpio);
 *  - no se crean cuentas ni se paga: solo catálogo, carrito y validaciones de formularios;
 *  - va de a una prueba (workers: 1 en playwright.config.ts), por cortesía con el sitio.
 *
 * Un solo lugar dice dónde está el sitio. Si mañana hay otro ambiente, se cambia aquí
 * (o con la variable URL_TOOLSHOP) y ninguna prueba se entera.
 */
export const entornoToolshop = {
  /** Dirección del sitio. Termina en "/" para que las rutas relativas funcionen. */
  urlBase: process.env.URL_TOOLSHOP ?? 'https://practicesoftwaretesting.com/',

  /**
   * El sitio tiene atributos data-test pactados con quien lo construyó (data-test="cart-total").
   * Es el peldaño 4 de la escalera: lo usamos solo para valores que cambian, como precios y totales.
   */
  atributoDePrueba: 'data-test',

  /** El sitio se ve en varios idiomas. Se fija en inglés para que los textos esperados no cambien. */
  idioma: 'en-US',
};
