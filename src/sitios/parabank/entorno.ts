/**
 * CONFIGURACIÓN de ParaBank (S5): un banco de práctica PÚBLICO en internet (Parasoft).
 *
 * Es un sitio real y compartido: cualquier persona del mundo puede crear clientes y mover
 * plata ahí. Por eso cada prueba crea su propio cliente con la fábrica (fabricaDeClientes.ts)
 * y nunca usa los usuarios de ejemplo que todo el mundo toca.
 *
 * Un solo lugar dice dónde está el sitio. Si mañana hay otro ambiente, se cambia aquí
 * (o con la variable URL_PARABANK) y ninguna prueba se entera.
 */
export const entornoParaBank = {
  /** Dirección del sitio. Termina en "/" para que las rutas relativas funcionen. */
  urlBase: process.env.URL_PARABANK ?? 'https://parabank.parasoft.com/parabank/',

  /** Clave de los clientes que crean las pruebas. Es un sitio público: nunca uses una clave real. */
  clave: 'Clave123',

  /**
   * Pausa de cortesía al terminar cada prueba, en milisegundos. ParaBank responde HTTP 429 si recibe
   * demasiadas peticiones seguidas. Es una regla de convivencia con el sitio: vive aquí, una sola vez.
   */
  pausaEntrePruebasMs: Number(process.env.PAUSA_PARABANK_MS ?? 5_000),
};
