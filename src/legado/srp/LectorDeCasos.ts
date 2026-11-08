/**
 * DESPUÉS (SRP) · Una sola tarea: convertir el texto de un CSV en casos de prueba.
 *
 * Recibe el TEXTO, no la ruta del archivo: leer el disco es otra responsabilidad.
 * Así se prueba sin archivos.
 */

/** Un caso: cada columna del encabezado con su valor. Ejemplo: { id: 'T01', monto: '100000' } */
export type Caso = Record<string, string>;

/** Convierte un CSV separado por ";" en una lista de casos. */
export function leerCasos(texto: string): Caso[] {
  // TODO RETO 1 (parte A): mueve aquí la lógica de AyudanteTodo.leerCasosCsv, con dos mejoras:
  //   1. Quita las líneas vacías (por ejemplo, la última línea del archivo).
  //   2. Quita el "\r" que dejan los archivos guardados en Windows.
  // Pista: texto.split(/\r?\n/) parte por líneas con o sin "\r", y
  //        .filter((linea) => linea.trim() !== '') quita las vacías.
  // Cuando termines, borra la línea "throw" de abajo.
  throw new Error('PENDIENTE (S4): completa leerCasos en src/legado/srp/LectorDeCasos.ts — ver retos/S04.md, reto 1');
}
