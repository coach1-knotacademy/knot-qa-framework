/**
 * CAPA DE DATOS: los productos del catálogo que usan las pruebas.
 * El precio va en CENTAVOS (enteros): así 29,99 × 2 da 59,98 exacto, sin errores de decimales.
 */
export interface Producto {
  nombre: string;
  precioEnCentavos: number;
}

export const productos = {
  mochila: { nombre: 'Sauce Labs Backpack', precioEnCentavos: 2999 },
} satisfies Record<string, Producto>;

/** Como lo muestra la app: "$ 59.98" (con espacio después del signo y punto decimal). */
export function comoLoMuestraLaApp(centavos: number): string {
  return `$ ${(centavos / 100).toFixed(2)}`;
}

export function totalEsperado(producto: Producto, cantidad: number): string {
  return comoLoMuestraLaApp(producto.precioEnCentavos * cantidad);
}
