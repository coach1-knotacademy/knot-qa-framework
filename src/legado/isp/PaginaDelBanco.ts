/**
 * CÓDIGO HEREDADO · I de SOLID: segregación de interfaces (ISP).
 *
 * Una interfaz "para todo": cada página del framework anterior debía implementar los 8
 * métodos, aunque no los tuviera. El resultado: métodos que solo lanzan "No aplica".
 *
 * No la modifiques: es el "antes". El reto 4 de la S4 crea interfaces pequeñas en capacidades.ts.
 */
export interface PaginaDelBanco {
  abrir(): Promise<void>;
  ingresar(usuario: string, clave: string): Promise<void>;
  validarOtp(codigo: string): Promise<void>;
  saldoDe(cuenta: string): Promise<string>;
  transferir(destino: string, monto: number): Promise<void>;
  descargarExtracto(mes: string): Promise<void>;
  cambiarClave(actual: string, nueva: string): Promise<void>;
  cerrarSesion(): Promise<void>;
}
