// Generado por una IA (Claude Sonnet, actuando como asistente tipo Copilot) el 24 nov 2026,
// con el CP-102 COMPLETO, como lo pegaría un tester (URL, usuario y clave, cómo se lee el código
// en el buzón, pasos y resultado esperado), pero SIN ver el repo ni la aplicación.
// Se guarda tal cual, sin corregir.
import { test, expect, Page } from '@playwright/test';

const BASE_URL = 'http://127.0.0.1:4000';
const USUARIO = 'ana';
const CLAVE = 'Clave123';

// Lee el último código de seguridad (6 dígitos) del buzón de SMS de pruebas.
async function leerCodigoDelBuzon(page: Page, usuario: string): Promise<string> {
  const buzon = await page.context().newPage();
  await buzon.goto(`${BASE_URL}/buzon`);
  await buzon.getByRole('textbox').fill(usuario);
  await buzon.getByRole('button', { name: 'Buscar' }).click();
  const texto = await buzon.locator('body').innerText();
  const codigos = texto.match(/\b\d{4,8}\b/g);
  await buzon.close();
  if (!codigos || codigos.length === 0) {
    throw new Error('No se encontró un código de seguridad en el buzón');
  }
  return codigos[codigos.length - 1];
}

async function iniciarSesion(page: Page) {
  await page.goto(BASE_URL);
  await page.getByLabel(/usuario/i).fill(USUARIO);
  await page.getByLabel(/clave/i).fill(CLAVE);
  await page.getByRole('button', { name: /ingresar|iniciar sesión/i }).click();

  await expect(page.getByLabel('Código de seguridad')).toBeVisible();
  const codigo = await leerCodigoDelBuzon(page, USUARIO);
  await page.getByLabel('Código de seguridad').fill(codigo);
  await page.getByRole('button', { name: 'Validar' }).click();
}

test.describe('Recargas', () => {
  test('CP-102 · Recarga de más de $50.000 con código', async ({ page }) => {
    // Precondición: Ana inició sesión
    await iniciarSesion(page);

    // Paso 1
    await page.goto(`${BASE_URL}/recargas`);

    // Paso 2
    await page.getByLabel(/operador/i).selectOption({ label: 'Claro' });
    await page.getByLabel(/celular/i).fill('3001234567');
    await page.getByLabel(/valor/i).fill('60000');

    // Paso 3
    await page.getByRole('button', { name: 'Recargar' }).click();

    // Esperado 1: antes de recargar, pide el código de seguridad
    const campoCodigo = page.getByLabel('Código de seguridad');
    await expect(campoCodigo).toBeVisible();

    // Paso 4: nuevo código desde el buzón
    const codigo = await leerCodigoDelBuzon(page, USUARIO);
    await campoCodigo.fill(codigo);
    await page.getByRole('button', { name: 'Confirmar recarga' }).click();

    // Esperado 2: comprobante
    await expect(page.getByText('Recarga exitosa')).toBeVisible();
    await expect(page.getByText('Valor: $60.000')).toBeVisible();

    // Esperado 3: saldo de Ahorros = $1.440.000
    await page.goto(BASE_URL + '/');
    await expect(page.getByText('$1.440.000')).toBeVisible();
  });
});

// Supuestos que declaró la IA (resumen fiel): los selectores salen del texto del pedido y "es probable
// que haya que ajustarlos"; el código es el último número del buzón; el saldo se ve en la página de
// inicio después del login; el saldo inicial es $1.500.000 y nada más lo modifica en paralelo.
