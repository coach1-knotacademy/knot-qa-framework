import { test } from '@playwright/test';

/**
 * S9 · EL REGISTRO DE LA CORRIDA (el "logging" del framework).
 *
 * registrar() pega un dato a la prueba que está corriendo, y el reporte lo muestra en «Attachments»,
 * junto a sus pasos, su captura y su trace. No es un console.log que se pierde en la terminal:
 * queda con la prueba, en el reporte que se comparte, y se lee igual en tu equipo y en el pipeline.
 *
 *   await registrar('saldo por API', { esperado: 1_500_000, obtenido: saldo });
 *
 * Por dentro es test.info().attach (https://playwright.dev/docs/api/class-testinfo), con el dato en JSON
 * legible. Se registra ANTES del expect que puede fallar: si el expect falla, la prueba se detiene ahí
 * y lo que venía después no se ejecuta.
 *
 * Lo que NUNCA se registra: claves, tokens ni datos reales de clientes. El reporte se comparte.
 */
export async function registrar(nombre: string, datos: unknown): Promise<void> {
  await test.info().attach(nombre, {
    body: JSON.stringify(datos, null, 2),
    contentType: 'application/json',
  });
}
