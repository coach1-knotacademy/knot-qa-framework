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
    const linea = `[${this.reloj().toISOString()}] ${mensaje}`;
    this.registro.push(linea);
  }

  /** Devuelve una copia de las líneas registradas. */
  lineas(): string[] {
    return [...this.registro];
  }
}
