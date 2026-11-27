/**
 * S8 · SOLUCIÓN de la Sala 1 · CP-103 · Un celular mal escrito se rechaza.
 * Se copia a tests/recargas/ para correrla:  npx.cmd playwright test -g "@CP-103" --project=recargas
 *
 * La tabla «Ejemplos» es fabricaDeRecargas.celularesInvalidos(): tres datos, el mismo mensaje.
 * Cada fila prueba un pedazo distinto de la regla (corto, largo y prefijo): si se quita una, ese error puede volver.
 * Va por API, como el CP-104: es un rechazo, la regla se prueba en la capa barata.
 */
import { fabricaDeRecargas, mensajes, pesos } from '../../src/datos/fabricaDeRecargas';
import { usuarios } from '../../src/datos/usuarios';
import { test, expect } from '../../src/soporte/fixtures';

const SALDO_INICIAL = 1_500_000;
const MONTO = 10_000;

for (const celular of fabricaDeRecargas.celularesInvalidos()) {
  // El título lleva el dato (el celular y su caso): una línea por fila en el reporte.
  test(`CP-103 · ${celular.numero} (${celular.caso}) → «${mensajes.celular}»`, { tag: '@CP-103' }, async ({ cliente }) => {
    await test.step(`Dado que Ana tiene la sesión abierta y ${pesos(SALDO_INICIAL)} en Ahorros`, async () => {
      await cliente.iniciarSesion(usuarios.ana);
      expect(await cliente.saldoDeAhorros()).toBe(SALDO_INICIAL);
    });

    const respuesta = await test.step(`Cuando recarga ${pesos(MONTO)} al celular ${celular.numero}`, async () => {
      return cliente.recargar(fabricaDeRecargas.valida({ numero: celular.numero, monto: MONTO }));
    });

    await test.step(`Entonces ve el mensaje «${mensajes.celular}»`, async () => {
      expect(respuesta.estado).toBe(400);
      expect(respuesta.datos.error).toBe(mensajes.celular);
    });

    await test.step(`Y su saldo de Ahorros sigue en ${pesos(SALDO_INICIAL)}`, async () => {
      expect(await cliente.saldoDeAhorros()).toBe(SALDO_INICIAL);
    });
  });
}
