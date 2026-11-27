/**
 * S8 · SOLUCIÓN de la Sala 5 · CP-107 · Cada operador recibe la recarga.
 * Se copia a tests/recargas/ para correrla:  npx.cmd playwright test -g "@CP-107" --project=recargas
 *
 * La tabla «Ejemplos» ya existía: fabricaDeRecargas.paraCadaOperador() (recargas.spec.ts la usa por API).
 * Escribirla en Gherkin la vuelve la especificación que firma negocio: el día que llegue un operador nuevo,
 * se agrega una fila en la fábrica y aparece una línea nueva en el reporte, sin escribir otra prueba.
 * Va por la pantalla: el «Entonces» es el comprobante con el operador que eligió el cliente.
 */
import { abrirConSesion } from '../../src/flujos/sesion';
import { fabricaDeRecargas, pesos } from '../../src/datos/fabricaDeRecargas';
import { usuarios } from '../../src/datos/usuarios';
import { Actor } from '../../src/screenplay/Actor';
import { NavegarLaWeb } from '../../src/screenplay/navegador/NavegarLaWeb';
import { RecargarDesdeLaPantalla } from '../../src/screenplay/recargas/RecargarDesdeLaPantalla';
import { ResultadoDeLaRecarga } from '../../src/screenplay/recargas/ResultadoDeLaRecarga';
import { test, expect } from '../../src/soporte/fixtures';

const SALDO_INICIAL = 1_500_000;
const MONTO = 10_000;

for (const recarga of fabricaDeRecargas.paraCadaOperador({ monto: MONTO })) {
  test(`CP-107 · ${recarga.operador} recibe la recarga de ${pesos(recarga.monto)}`, { tag: '@CP-107' }, async ({ page, cliente, paginaRecargas }) => {
    const ana = Actor.llamado('Ana').puede(NavegarLaWeb.con(page));

    await test.step(`Dado que Ana tiene la sesión abierta y ${pesos(SALDO_INICIAL)} en Ahorros`, async () => {
      await abrirConSesion(page, cliente, usuarios.ana);
      await paginaRecargas.abrir();
      await expect(paginaRecargas.saldoDisponible).toHaveText(pesos(SALDO_INICIAL));
    });

    await test.step(`Cuando recarga ${pesos(recarga.monto)} a un celular ${recarga.operador} ${recarga.numero}`, async () => {
      await ana.intenta(RecargarDesdeLaPantalla.celular(recarga.numero).por(recarga.monto).con(recarga.operador));
    });

    await test.step(`Entonces ve el comprobante «Recarga exitosa» con «${recarga.operador} · ${recarga.numero}»`, async () => {
      const comprobante = await ana.pregunta(ResultadoDeLaRecarga.queVio());
      expect(comprobante).toContain('Recarga exitosa');
      expect(comprobante).toContain(`${recarga.operador} · ${recarga.numero}`);
    });

    await test.step(`Y su saldo de Ahorros queda en ${pesos(SALDO_INICIAL - recarga.monto)}`, async () => {
      await expect(paginaRecargas.saldoDisponible).toHaveText(pesos(SALDO_INICIAL - recarga.monto));
    });
  });
}
