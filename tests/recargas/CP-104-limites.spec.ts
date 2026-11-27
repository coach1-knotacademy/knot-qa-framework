/**
 * S8 · CP-104 · Una prueba, muchos datos (Data Driven Testing).
 *
 * El Esquema del escenario está en especificaciones/recargas-datos.feature y su tabla «Ejemplos»
 * vive en la fábrica: fabricaDeRecargas.rechazosPorMonto(). Aquí, un for…of crea UN test() POR FILA.
 *
 *   La fila de la tabla es la fila del reporte.
 *
 * Qué hay que mirar:
 *  1. EL TÍTULO ÚNICO. Cada prueba lleva su dato en el título: «CP-104 · $150.000 → «La recarga máxima es $100.000»».
 *     Eso es lo que da UNA LÍNEA POR FILA en el reporte, con su verde o su rojo.
 *  2. LA ETIQUETA { tag: '@CP-104' }: agrupa las filas del mismo caso del ALM. La etiqueta agrupa; el título distingue.
 *  3. LA CAPA. Las filas van por API (cliente.recargar): la regla se prueba en la capa barata, sin abrir el navegador.
 *     Una sola fila va por la pantalla, para ver lo que ve el cliente.
 *
 * NUNCA un solo test() con un ciclo adentro: sale UNA línea en el reporte, y si falla la primera fila,
 * las demás ni se prueban. Con un test() por fila, cada dato tiene su resultado.
 *
 * ERROR PROVOCADO (para verlo en clase): quita ${pesos(rechazo.monto)} del título de abajo y corre.
 * Las filas de $100.001 y $150.000 tienen el mismo mensaje, así que quedan con el MISMO nombre, y Playwright
 * se niega a correr: no corre NINGUNA prueba, ni las de los otros archivos, y termina en error:
 *   Error: duplicate test title "Por API, una prueba por fila › CP-104 · → «La recarga máxima es $100.000»"
 * Sin el dato en el título, el reporte no podría decir cuál de las dos falló. Deshaz el cambio.
 *
 * Correr solo este caso y abrir el reporte:
 *   npx.cmd playwright test -g "@CP-104" --project=recargas      (salen 4: 3 por API y 1 por la pantalla)
 *   npm.cmd run reporte                                            (escribe @CP-104 en el buscador)
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

test.describe('Por API, una prueba por fila', () => {
  // Una vuelta del for = un test() con su propio título. El for corre al CARGAR el archivo, no dentro de una prueba.
  for (const rechazo of fabricaDeRecargas.rechazosPorMonto()) {
    test(`CP-104 · ${pesos(rechazo.monto)} → «${rechazo.mensaje}»`, { tag: '@CP-104' }, async ({ cliente }) => {
      // Los pasos son los del Esquema, llenados con esta fila: así se leen en el reporte.
      await test.step(`Dado que Ana tiene la sesión abierta y ${pesos(SALDO_INICIAL)} en Ahorros`, async () => {
        await cliente.iniciarSesion(usuarios.ana);
        expect(await cliente.saldoDeAhorros()).toBe(SALDO_INICIAL);
      });

      const respuesta = await test.step(`Cuando recarga ${pesos(rechazo.monto)} a un celular Claro ${CELULAR}`, async () => {
        return cliente.recargar(fabricaDeRecargas.valida({ monto: rechazo.monto, numero: CELULAR, operador: 'Claro' }));
      });

      await test.step(`Entonces ve el mensaje «${rechazo.mensaje}»`, async () => {
        // 400 = el banco rechazó la recarga. El texto de "error" es el mismo que la pantalla le muestra al cliente.
        expect(respuesta.estado).toBe(400);
        expect(respuesta.datos.error).toBe(rechazo.mensaje);
      });

      await test.step(`Y su saldo de Ahorros sigue en ${pesos(SALDO_INICIAL)}`, async () => {
        expect(await cliente.saldoDeAhorros()).toBe(SALDO_INICIAL);
      });
    });
  }
});

// Una fila representativa por la pantalla: $150.000, que es más de $50.000 y aun así el banco NO pide código
// (revisa el máximo antes). Es la fila que más se presta a confusión, por eso es la que ve el cliente.
const porLaPantalla = fabricaDeRecargas.rechazosPorMonto().find((fila) => fila.monto === 150_000);
if (!porLaPantalla) throw new Error('La tabla rechazosPorMonto ya no trae la fila de $150.000');

test(`CP-104 · por la pantalla · ${pesos(porLaPantalla.monto)} → «${porLaPantalla.mensaje}»`, { tag: '@CP-104' }, async ({ page, cliente, paginaRecargas }) => {
  const ana = Actor.llamado('Ana').puede(NavegarLaWeb.con(page));

  await test.step(`Dado que Ana tiene la sesión abierta y ${pesos(SALDO_INICIAL)} en Ahorros`, async () => {
    await abrirConSesion(page, cliente, usuarios.ana);
    await paginaRecargas.abrir();
    await expect(paginaRecargas.saldoDisponible).toHaveText(pesos(SALDO_INICIAL));
  });

  await test.step(`Cuando recarga ${pesos(porLaPantalla.monto)} a un celular Claro ${CELULAR}`, async () => {
    await ana.intenta(RecargarDesdeLaPantalla.celular(CELULAR).por(porLaPantalla.monto).con('Claro'));
  });

  await test.step(`Entonces ve el mensaje «${porLaPantalla.mensaje}»`, async () => {
    expect(await ana.pregunta(ResultadoDeLaRecarga.queVio())).toBe(porLaPantalla.mensaje);
    // Y no le pidió el código: el rechazo llegó antes.
    await expect(paginaRecargas.campoCodigo).toBeHidden();
  });

  await test.step(`Y su saldo de Ahorros sigue en ${pesos(SALDO_INICIAL)}`, async () => {
    // El saldo se vuelve a pedir después de la respuesta: va el «video» (toHaveText reintenta), no la foto.
    await expect(paginaRecargas.saldoDisponible).toHaveText(pesos(SALDO_INICIAL));
  });
});
