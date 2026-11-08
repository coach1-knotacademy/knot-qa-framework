/**
 * DESPUÉS (ISP) · Interfaces pequeñas: cada una es UNA capacidad.
 * Una página implementa solo las capacidades que de verdad tiene.
 */

/** Ejemplo ya resuelto: las páginas que se pueden abrir. */
export interface SeAbre {
  abrir(): Promise<void>;
}

/** Las páginas que muestran saldos. */
export interface ConsultaSaldos {
  saldoDe(cuenta: string): Promise<string>;
}

/** Las páginas que tienen el botón Salir. */
export interface CierraSesion {
  cerrarSesion(): Promise<void>;
}
