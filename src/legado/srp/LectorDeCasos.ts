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
  const lineas = texto.split(/\r?\n/).filter((linea) => linea.trim() !== '');
  const [encabezado, ...filas] = lineas;
  const columnas = encabezado.split(';');
  return filas.map((fila) => {
    const valores = fila.split(';');
    const caso: Caso = {};
    columnas.forEach((columna, i) => (caso[columna] = valores[i]));
    return caso;
  });
}
