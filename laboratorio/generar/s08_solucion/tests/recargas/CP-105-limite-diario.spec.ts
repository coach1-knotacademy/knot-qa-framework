/**
 * S8 · SOLUCIÓN de la Sala 4 · CP-105 · Pasado el límite diario no se puede recargar.
 * Se copia a tests/recargas/ para correrla:  npx.cmd playwright test -g "@CP-105" --project=recargas
 *
 * La tabla «Ejemplos» es fabricaDeRecargas.pasadoElLimiteDiario(): el dato del «Dado» (lo que ya recargó hoy)
 * también va en la tabla. $180.000 + $20.000 NO va: da justo $200.000 y pasa (otro resultado, otro Esquema).
 *
 * Prueba HÍBRIDA, como la de límite diario de recargas.spec.ts: el «Dado» se prepara por API (rápido)
 * y el «Cuando» y el «Entonces» van por la pantalla (lo que ve el cliente).
 */
import { abrirConSesion } from '../../src/flujos/sesion';
import { fabricaDeRecargas, mensajes, pesos } from '../../src/datos/fabricaDeRecargas';
import { usuarios } from '../../src/datos/usuarios';
import { Actor } from '../../src/screenplay/Actor';
import { NavegarLaWeb } from '../../src/screenplay/navegador/NavegarLaWeb';
import { RecargarDesdeLaPantalla } from '../../src/screenplay/recargas/RecargarDesdeLaPantalla';
import { ResultadoDeLaRecarga } from '../../src/screenplay/recargas/ResultadoDeLaRecarga';
import { test, expect } from '../../src/soporte/fixtures';

const CELULAR = '3001234567';

for (const fila of fabricaDeRecargas.pasadoElLimiteDiario()) {
  test(`CP-105 · ya recargó ${pesos(fila.yaRecargo)} + ${pesos(fila.monto)} → «${mensajes.limiteDiario}»`, { tag: '@CP-105' }, async ({ page, cliente }) => {
    const ana = Actor.llamado('Ana').puede(NavegarLaWeb.con(page));

    await test.step(`Dado que Ana tiene la sesión abierta y hoy ya recargó ${pesos(fila.yaRecargo)}`, async () => {
      await abrirConSesion(page, cliente, usuarios.ana);
      // De a $50.000 como máximo, para que ninguna recarga de preparación pida código.
      for (const recarga of fabricaDeRecargas.hastaHaberRecargado(fila.yaRecargo)) {
        expect((await cliente.recargar(recarga)).estado).toBe(201);
      }
    });

    await test.step(`Cuando recarga ${pesos(fila.monto)} a un celular Claro ${CELULAR}`, async () => {
      await ana.intenta(RecargarDesdeLaPantalla.celular(CELULAR).por(fila.monto).con('Claro'));
    });

    await test.step(`Entonces ve el mensaje «${mensajes.limiteDiario}»`, async () => {
      expect(await ana.pregunta(ResultadoDeLaRecarga.queVio())).toBe(mensajes.limiteDiario);
    });
  });
}
