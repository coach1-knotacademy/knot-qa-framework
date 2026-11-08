/**
 * CÓDIGO HEREDADO (S4).
 *
 * El equipo anterior envolvió el navegador en esta interfaz para no depender de una
 * herramienta en particular. Eso nos sirve: en las pruebas de unidad de la S4 usamos un
 * navegador FALSO (tests/retos-s04/dobles/NavegadorFalso.ts) y no abrimos ningún navegador.
 */
export interface Navegador {
  ir(ruta: string): Promise<void>;
  escribir(campo: string, valor: string): Promise<void>;
  pulsar(boton: string): Promise<void>;
  leer(elemento: string): Promise<string>;
  capturar(archivo: string): Promise<void>;
}
