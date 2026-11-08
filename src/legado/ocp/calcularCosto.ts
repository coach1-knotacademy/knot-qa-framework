/**
 * CÓDIGO HEREDADO · O de SOLID: abierto a extensión, cerrado a modificación (OCP).
 *
 * Cada tipo de cuenta nuevo obliga a ABRIR esta función y agregar otro "case".
 * Cada cambio puede romper los tipos que ya funcionaban, y todos se vuelven a probar.
 *
 * No la modifiques: es el "antes". El reto 2 de la S4 crea reglas por tipo en reglasDeCosto.ts.
 */

/** 4x1000: 4 pesos por cada 1.000 transferidos, redondeado a pesos. */
export function cuatroPorMil(monto: number): number {
  return Math.round((monto * 4) / 1000);
}

/** Costo de una transferencia según el tipo de cuenta de origen. */
export function calcularCosto(tipoCuenta: string, monto: number): number {
  switch (tipoCuenta) {
    case 'Ahorros':
      return cuatroPorMil(monto);
    case 'Corriente':
      return cuatroPorMil(monto) + 2_000; // comisión fija por transferencia
    default:
      throw new Error(`Tipo de cuenta desconocido: ${tipoCuenta}`);
  }
}
