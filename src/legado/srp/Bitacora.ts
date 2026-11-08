/**
 * DESPUÉS (SRP) · Una sola tarea: registrar lo que pasa durante la prueba.
 *
 * La hora llega por el constructor ("reloj"). En la prueba de unidad le pasamos un reloj
 * fijo y así sabemos exactamente qué línea debe quedar.
 */
export class Bitacora {
  private readonly registro: string[] = [];

  constructor(private readonly reloj: () => Date = () => new Date()) {}

  /** Agrega una línea con el formato: [2026-11-12T23:00:00.000Z] mensaje */
  registrar(mensaje: string): void {
    // TODO RETO 1 (parte B): arma la línea con la hora de this.reloj() y el mensaje,
    // y agrégala a this.registro.
    // Pista: mira AyudanteTodo.escribirLog. Cambia new Date() por this.reloj()
    //        y en lugar de escribir el archivo, usa this.registro.push(linea).
    // Cuando termines, borra la línea "throw" de abajo.
    throw new Error('PENDIENTE (S4): completa Bitacora.registrar en src/legado/srp/Bitacora.ts — ver retos/S04.md, reto 1');
  }

  /** Devuelve una copia de las líneas registradas. */
  lineas(): string[] {
    return [...this.registro];
  }
}
