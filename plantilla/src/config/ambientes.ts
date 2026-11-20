/**
 * CAPA DE CONFIGURACIÓN · LOS AMBIENTES (S6)
 *
 * Como los "environments" de Postman: la misma suite, contra otro ambiente, sin tocar las pruebas.
 * Tres controles de un banco real:
 *   1. Solo se aceptan los ambientes del catálogo: producción queda BLOQUEADA (lista blanca).
 *   2. Fuera del ambiente de práctica, la clave llega por la terminal y, si falta, se falla DE INMEDIATO.
 *   3. La configuración queda CONGELADA (Object.freeze): nadie la cambia a mitad de la corrida.
 *
 * Para tu proyecto: cambia las direcciones de qa y uat por las de tu sistema (nunca la de producción).
 */

export type NombreDeAmbiente = 'demo' | 'qa' | 'uat';

export interface Ambiente {
  nombre: NombreDeAmbiente;
  urlBase: string;
  usuario: string;
  clave: string;
}

/** Las variables de la terminal (process.env) o, en una prueba, un objeto que las simula. */
export type Variables = Record<string, string | undefined>;

/**
 * EL CATÁLOGO. "demo" es el Banco Demo publicado en GitHub Pages: corre sin instalar un servidor.
 * La dirección termina en "/" para que las rutas relativas (recargas.html) funcionen.
 * Las de qa y uat son FICTICIAS (.ejemplo no existe): reemplázalas por las de tu proyecto.
 */
export const catalogoDeAmbientes: Record<NombreDeAmbiente, { urlBase: string; usuario: string }> = {
  demo: { urlBase: 'https://coach1-knotacademy.github.io/knot-qa-framework/banco/', usuario: 'ana' },
  qa: { urlBase: 'https://qa.mi-proyecto.ejemplo/', usuario: 'usuario-de-pruebas' },
  uat: { urlBase: 'https://uat.mi-proyecto.ejemplo/', usuario: 'usuario-de-pruebas' },
};

/** La clave del Banco Demo es pública (está escrita en su pantalla de ingreso). Solo vale para "demo". */
const CLAVE_DE_PRACTICA = 'Clave123';

/** Lee una variable. Vacía cuenta como que no está. */
export function leer(variables: Variables, nombre: string): string | undefined {
  const valor = variables[nombre]?.trim();
  return valor ? valor : undefined;
}

export function configurarAmbiente(nombre: string, variables: Variables = {}): Readonly<Ambiente> {
  if (!Object.keys(catalogoDeAmbientes).includes(nombre)) {
    throw new Error(`Ambiente "${nombre}" bloqueado. Este framework no corre contra producción ni contra ambientes que no conoce. Usa demo, qa o uat.`);
  }
  const ambiente = nombre as NombreDeAmbiente;

  const clave = ambiente === 'demo' ? leer(variables, 'CLAVE_BANCO') ?? CLAVE_DE_PRACTICA : leer(variables, 'CLAVE_BANCO');
  if (!clave) throw new Error(`Falta CLAVE_BANCO para el ambiente ${ambiente}. Defínela en la terminal: $env:CLAVE_BANCO = '...'`);

  return Object.freeze({
    nombre: ambiente,
    urlBase: leer(variables, 'URL_BANCO') ?? catalogoDeAmbientes[ambiente].urlBase,
    usuario: leer(variables, 'USUARIO_BANCO') ?? catalogoDeAmbientes[ambiente].usuario,
    clave,
  });
}
