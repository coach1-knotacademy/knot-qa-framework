/**
 * DESPUÉS (ISP) · Interfaces pequeñas: cada una es UNA capacidad.
 * Una página implementa solo las capacidades que de verdad tiene.
 */

/** Ejemplo ya resuelto: las páginas que se pueden abrir. */
export interface SeAbre {
  abrir(): Promise<void>;
}

// TODO RETO 4 (paso 1): crea dos interfaces más, con el mismo estilo de SeAbre:
//   - ConsultaSaldos, con:  saldoDe(cuenta: string): Promise<string>;
//   - CierraSesion, con:    cerrarSesion(): Promise<void>;
