/**
 * S8 · SOLUCIÓN de la Sala 3 · CP-101 · Una recarga sin código da comprobante y descuenta.
 * Se copia a tests/recargas/ para correrla:  npx.cmd playwright test -g "@CP-101" --project=recargas
 * (también sale el CP-101-gherkin de la S7: es el mismo caso, con un solo dato).
 *
 * La tabla «Ejemplos» es fabricaDeRecargas.sinCodigo(): $1.000 (el mínimo), $10.000 y $50.000 (el borde:
 * el último monto que no pide código). $50.001 pide código: otro camino, otro Esquema (el CP-102).
 * Va por la pantalla: el «Entonces» es el comprobante que ve el cliente.
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
const CELULAR = '3001234567';

for (const fila of fabricaDeRecargas.sinCodigo()) {
  test(`CP-101 · ${pesos(fila.monto)} sin código → saldo ${pesos(fila.saldoFinal)}`, { tag: '@CP-101' }, async ({ page, cliente, paginaRecargas }) => {
    const ana = Actor.llamado('Ana').puede(NavegarLaWeb.con(page));

    await test.step(`Dado que Ana tiene la sesión abierta y ${pesos(SALDO_INICIAL)} en Ahorros`, async () => {
      await abrirConSesion(page, cliente, usuarios.ana);
      await paginaRecargas.abrir();
      await expect(paginaRecargas.saldoDisponible).toHaveText(pesos(SALDO_INICIAL));
    });

    await test.step(`Cuando recarga ${pesos(fila.monto)} a un celular Claro ${CELULAR}`, async () => {
      await ana.intenta(RecargarDesdeLaPantalla.celular(CELULAR).por(fila.monto).con('Claro'));
    });

    await test.step(`Entonces ve el comprobante «Recarga exitosa» con «Valor: ${pesos(fila.monto)}»`, async () => {
      const comprobante = await ana.pregunta(ResultadoDeLaRecarga.queVio());
      expect(comprobante).toContain('Recarga exitosa');
      expect(comprobante).toContain(`Valor: ${pesos(fila.monto)}`);
    });

    await test.step(`Y su saldo de Ahorros queda en ${pesos(fila.saldoFinal)}`, async () => {
      await expect(paginaRecargas.saldoDisponible).toHaveText(pesos(fila.saldoFinal));
    });
  });
}
