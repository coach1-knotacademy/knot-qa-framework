/**
 * CAPA DE CONFIGURACIÓN (S6) · LOS AMBIENTES
 *
 * Es lo mismo que hacen en Postman con los "environments": el mismo pedido, contra QA o contra UAT,
 * cambiando solo el ambiente. Aquí el "pedido" es toda la suite y el ambiente se elige en la terminal:
 *
 *   $env:AMBIENTE = 'qa'
 *   $env:CLAVE_BANCO = '...'      (la clave nunca va escrita en el código)
 *   npm.cmd test
 *
 * configurarAmbiente() es una FUNCIÓN PURA: recibe el nombre y las variables y devuelve la configuración.
 * No lee la terminal por su cuenta (eso lo hace entorno.ts), y por eso se puede probar sin cambiar nada
 * del equipo: la prueba le pasa un objeto con las variables que quiere simular.
 *
 * Tres controles de un banco real, uno por paso del reto 1 (más el paso 1, que es el catálogo):
 *   - el secreto falla DE INMEDIATO si falta (paso 2), en lugar de fallar 40 pruebas después;
 *   - producción está BLOQUEADA (paso 3): este framework solo corre contra ambientes de pruebas;
 *   - la configuración queda CONGELADA (paso 4): nadie la cambia a mitad de la corrida.
 */

/** Los ambientes que este framework conoce. Cualquier otro nombre se bloquea (paso 3). */
export type NombreDeAmbiente = 'local' | 'qa' | 'uat';

/** La configuración que usan las pruebas. Tiene la misma forma que entorno.ts desde la S3, más el nombre. */
export interface Ambiente {
  nombre: NombreDeAmbiente;
  urlBase: string;
  usuario: string;
  clave: string;
}

/** Las variables de la terminal (process.env) o, en una prueba, un objeto que las simula. */
export type Variables = Record<string, string | undefined>;

/**
 * EL CATÁLOGO: dónde vive cada ambiente. Es el "environment" de Postman, pero en el código.
 * Las direcciones de qa y uat son FICTICIAS (.ejemplo no existe en internet): sirven para practicar.
 * Aquí no hay claves: las claves llegan por la terminal (CLAVE_BANCO).
 */
export const catalogoDeAmbientes: Record<NombreDeAmbiente, { urlBase: string; usuario: string }> = {
  local: { urlBase: 'http://127.0.0.1:4000', usuario: 'ana' },
  qa: { urlBase: 'https://qa.banco-demo.ejemplo', usuario: 'ana' },
  uat: { urlBase: 'https://uat.banco-demo.ejemplo', usuario: 'ana' },
};

/**
 * La clave de los usuarios de práctica del Banco Demo local. Es pública (está escrita en la pantalla
 * de ingreso), por eso puede vivir aquí. Solo se usa en "local"; en qa y uat la clave llega por la terminal.
 */
export const CLAVE_DE_PRACTICA = 'Clave123';

/** Lee una variable. Si está vacía (por ejemplo, CLAVE_BANCO= en un archivo .env), cuenta como que no está. */
export function leer(variables: Variables, nombre: string): string | undefined {
  const valor = variables[nombre]?.trim();
  return valor ? valor : undefined;
}

/**
 * Paso 3 · Solo se aceptan los ambientes del catálogo. Producción, o cualquier nombre que no conozcamos,
 * se bloquea con un mensaje claro. Es una LISTA BLANCA: "PRODUCCION", "prod" o "produccion " también
 * quedan bloqueados, sin tener que adivinar cómo lo va a escribir alguien (acuérdate del BUG-03).
 */
export function elegirAmbiente(nombre: string): NombreDeAmbiente {
  if (Object.keys(catalogoDeAmbientes).includes(nombre)) return nombre as NombreDeAmbiente;
  throw new Error(`Ambiente "${nombre}" bloqueado. Este framework no corre contra producción ni contra ambientes que no conoce. Usa local, qa o uat.`);
}

/** Paso 1 · La dirección del ambiente: la del catálogo, salvo que la terminal traiga URL_BANCO. */
export function urlDelAmbiente(nombre: NombreDeAmbiente, variables: Variables): string {
  return leer(variables, 'URL_BANCO') ?? catalogoDeAmbientes[nombre].urlBase;
}

/**
 * Paso 2 · La clave. En local, la de práctica. Fuera de local, la terminal TIENE que traer CLAVE_BANCO:
 * si no la trae, se falla de inmediato y se dice qué hacer. Nunca se "inventa" una clave por defecto.
 */
export function claveDelAmbiente(nombre: NombreDeAmbiente, variables: Variables): string {
  if (nombre === 'local') return leer(variables, 'CLAVE_BANCO') ?? CLAVE_DE_PRACTICA;
  const clave = leer(variables, 'CLAVE_BANCO');
  if (!clave) throw new Error(`Falta CLAVE_BANCO para el ambiente ${nombre}. Defínela en la terminal: $env:CLAVE_BANCO = '...'`);
  return clave;
}

/**
 * Paso 4 · Congelar la configuración. Hoy cualquiera puede escribir entorno.usuario = 'luis' en una prueba:
 * esa prueba pasa sola, pero las que corren después en el mismo proceso usan otro usuario sin saberlo.
 * Object.freeze() lo impide: intentar cambiarla lanza un error en el momento, no un rojo misterioso después.
 */
export function congelar(config: Ambiente): Readonly<Ambiente> {
  return Object.freeze(config);
}

/**
 * Arma la configuración del ambiente pedido. La usa entorno.ts con las variables de la terminal.
 *   configurarAmbiente('local', {})                         → el Banco Demo de tu equipo
 *   configurarAmbiente('qa', { CLAVE_BANCO: 'xyz' })        → QA, con la clave de la terminal
 *   configurarAmbiente('produccion', {})                    → error: bloqueado
 */
export function configurarAmbiente(nombre: string, variables: Variables = {}): Readonly<Ambiente> {
  const ambiente = elegirAmbiente(nombre);
  return congelar({
    nombre: ambiente,
    urlBase: urlDelAmbiente(ambiente, variables),
    usuario: leer(variables, 'USUARIO_BANCO') ?? catalogoDeAmbientes[ambiente].usuario,
    clave: claveDelAmbiente(ambiente, variables),
  });
}
