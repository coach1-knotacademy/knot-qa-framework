/**
 * Kit «web real», parte B · Un sistema REAL: el formulario público «Recarga tu Nequi» (PSE).
 * LO CORRE SOLO EL INSTRUCTOR, en demo. Es producción de un tercero: reglas en src/sitios/sistema-real/entorno.ts.
 *
 *   Solo validaciones del formulario · nunca «Continuar» · nunca la casilla antibots
 *   · celulares de prueba evidentes · una prueba a la vez, con pausa · pocas corridas.
 *
 * El proyecto "sistema-real" no existe si no se pide a propósito (nunca en CI):
 *   PowerShell:  $env:SISTEMA_REAL="1"; npx.cmd playwright test --project=sistema-real
 *   cmd:         set SISTEMA_REAL=1&& npx.cmd playwright test --project=sistema-real
 *   Mac/Linux:   SISTEMA_REAL=1 npx playwright test --project=sistema-real
 *
 * Para VER en rojo el error de getByLabel (demo, una sola prueba): agrega VER_ERROR=1 y -g "rojo a propósito".
 */
import { test, expect } from '@playwright/test';
import { entornoSistemaReal } from '../../src/sitios/sistema-real/entorno';
import { PaginaRecargaPse } from '../../src/sitios/sistema-real/PaginaRecargaPse';

const { celularDePrueba, otroCelularDePrueba, pausaEntrePruebasMs } = entornoSistemaReal;

// Cortesía con producción: una pausa al terminar cada prueba.
test.afterEach(async () => {
  await new Promise((listo) => setTimeout(listo, pausaEntrePruebasMs));
});

test(
  'A11Y-01 · getByLabel no encuentra el celular: los campos no tienen nombre accesible',
  { annotation: { type: 'hallazgo', description: 'A11Y-01: el <label for> apunta a un id repetido y los campos quedan sin nombre accesible' } },
  async ({ page }, testInfo) => {
    const recarga = new PaginaRecargaPse(page);
    await recarga.abrir();

    await test.step('El peldaño 2 (getByLabel) no encuentra nada', async () => {
      await expect(recarga.celularPorEtiqueta).toHaveCount(0);
      // Se intenta escribir como lo haría una prueba normal, con un tiempo corto, y se guarda el error.
      const error = await recarga.celularPorEtiqueta.fill(celularDePrueba, { timeout: 3_000 }).then(
        () => null,
        (e: Error) => e,
      );
      expect(error, 'getByLabel no debía encontrar el campo').not.toBeNull();
      await testInfo.attach('error de getByLabel', { body: error!.message, contentType: 'text/plain' });
      expect(error!.message).toContain("getByLabel('Número de celular', { exact: true })");
    });

    await test.step('Los campos existen, pero sin nombre accesible', async () => {
      await expect(recarga.celular).toHaveAccessibleName('');
      await expect(recarga.confirmacion).toHaveAccessibleName('');
      await expect(recarga.valor).toHaveAccessibleName('');
    });

    await test.step('La causa: el id se repite y el <label for> apunta al envoltorio, no al campo', async () => {
      const diagnostico = await recarga.diagnosticoDeEtiquetas();
      await testInfo.attach('diagnóstico de las etiquetas', { body: JSON.stringify(diagnostico, null, 2), contentType: 'application/json' });
      for (const campo of diagnostico) {
        expect(campo.elementosConEseId, `«${campo.etiqueta}»: elementos con el mismo id`).toBeGreaterThan(1);
        expect(campo.apuntaAUnCampo, `«${campo.etiqueta}»: ¿la etiqueta apunta a un <input>?`).toBe(false);
      }
    });
  },
);

test('Continuar está deshabilitado con el formulario vacío', async ({ page }) => {
  const recarga = new PaginaRecargaPse(page);
  await recarga.abrir();

  await expect(recarga.continuar).toBeDisabled();
  await expect(recarga.antibots).not.toBeChecked();
});

test(
  'si la confirmación no coincide, avisa y Continuar sigue deshabilitado',
  { annotation: { type: 'hallazgo', description: 'A11Y-02: el mensaje de error no está asociado al campo (sin descripción accesible)' } },
  async ({ page }) => {
    const recarga = new PaginaRecargaPse(page);
    await recarga.abrir();

    await recarga.escribirCelular(celularDePrueba, otroCelularDePrueba);

    await expect(recarga.error('¡Ups! Esos dos números no coinciden, porfa revísalos.')).toBeVisible();
    await expect(recarga.continuar).toBeDisabled();
    // El mensaje se ve, pero un lector de pantalla no lo anuncia con el campo: no hay aria-describedby.
    await expect(recarga.confirmacion).toHaveAccessibleDescription('');
  },
);

test('un celular de 3 dígitos se rechaza', async ({ page }) => {
  const recarga = new PaginaRecargaPse(page);
  await recarga.abrir();

  await recarga.escribirCelular('300');

  await expect(recarga.error('Este no parece un número de celular válido')).toBeVisible();
  await expect(recarga.continuar).toBeDisabled();
});

test('el valor mínimo es $1: con $0 avisa y con $1 ya no', async ({ page }) => {
  const recarga = new PaginaRecargaPse(page);
  await recarga.abrir();
  // Así lo muestra la página, con corchetes incluidos.
  const avisoDelMinimo = recarga.error('Debes ingresar mín. [$1]');

  await recarga.escribirValor('0');
  await expect(recarga.valor).toHaveValue('$0');
  await expect(avisoDelMinimo).toBeVisible();

  // Valor límite: justo en el mínimo, el aviso desaparece.
  await recarga.escribirValor('1');
  await expect(recarga.valor).toHaveValue('$1');
  await expect(avisoDelMinimo).toBeHidden();
});

test('con datos válidos, Continuar sigue deshabilitado: aquí se detiene la automatización', async ({ page }, testInfo) => {
  const recarga = new PaginaRecargaPse(page);
  await recarga.abrir();

  await recarga.escribirCelular(celularDePrueba);
  await recarga.escribirValor('10000');

  await expect(recarga.error('¡Ups! Esos dos números no coinciden, porfa revísalos.')).toBeHidden();
  await expect(recarga.valor).toHaveValue('$10.000');
  // Falta elegir el banco y confirmar el antibots. El antibots NO se toca: es una persona la que confirma.
  await expect(recarga.antibots).not.toBeChecked();
  await expect(recarga.continuar).toBeDisabled();
  await testInfo.attach('hasta aquí llega la automatización', { body: await page.screenshot({ fullPage: true }), contentType: 'image/png' });
});

test('rojo a propósito · así falla getByLabel (solo para la demo)', async ({ page }) => {
  test.skip(process.env.VER_ERROR !== '1', 'Solo en la demo: VER_ERROR=1');
  const recarga = new PaginaRecargaPse(page);
  await recarga.abrir();

  // Esto es lo que escribiría cualquiera (y lo que propone la IA). Se queda esperando y falla.
  await recarga.celularPorEtiqueta.fill(celularDePrueba, { timeout: 5_000 });
});
