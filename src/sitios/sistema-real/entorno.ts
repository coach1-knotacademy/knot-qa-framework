/**
 * CONFIGURACIÓN del ejemplo con un sistema real (kit «web real», parte B). LO CORRE SOLO EL INSTRUCTOR.
 *
 * Es el formulario público «Recarga tu Nequi» por PSE: PRODUCCIÓN de un tercero, con dinero real.
 * No es un sitio de práctica. Por eso las reglas viven aquí, en un solo lugar, y el proyecto
 * "sistema-real" de playwright.config.ts solo existe si alguien pone SISTEMA_REAL=1 a propósito.
 *
 * Reglas (no se negocian):
 *  1. Solo validaciones del formulario: se mira, no se envía. Nunca se pulsa «Continuar».
 *  2. Nunca se marca «Confirmo que soy una persona real»: es un control antibots. Ahí se detiene
 *     la automatización, a propósito. Saltarlo sería atacar el control, no probarlo.
 *  3. Nunca datos reales: celulares de prueba evidentes (3000000000).
 *  4. Sin carga ni estrés: una prueba a la vez (workers: 1), pocas corridas y una pausa entre pruebas.
 */
export const entornoSistemaReal = {
  /** Dirección del formulario. */
  urlBase: process.env.URL_SISTEMA_REAL ?? 'https://clientes.nequi.com.co/',

  /** Celulares de prueba EVIDENTES: nadie los confunde con el número de una persona. */
  celularDePrueba: '3000000000',
  otroCelularDePrueba: '3000000001',

  /** Pausa de cortesía entre pruebas, en milisegundos: es producción de un tercero. */
  pausaEntrePruebasMs: 3_000,
};
