// Generado por una IA (Claude Sonnet, actuando como asistente tipo Copilot) el 17 nov 2026,
// SOLO con el pedido del tester, sin ver el repo. Se guarda tal cual, sin corregir.
import { test, expect } from '@playwright/test';

const BASE = 'http://127.0.0.1:4000';

test('recarga exitosa descuenta el saldo', async ({ page, context }) => {
  // Login
  await page.goto(`${BASE}/login`);
  await page.getByLabel('Usuario').fill('ana');
  await page.getByLabel('Clave').fill('Clave123');
  await page.getByRole('button', { name: 'Ingresar' }).click();

  // OTP: se lee del buzón de pruebas en otra pestaña
  const buzon = await context.newPage();
  await buzon.goto(`${BASE}/buzon`);
  const textoBuzon = await buzon.locator('body').innerText();
  const otp = textoBuzon.match(/\b\d{6}\b/)?.[0];   // supuesto: código de 6 dígitos
  expect(otp, 'No se encontró el OTP en el buzón').toBeTruthy();
  await buzon.close();

  await page.getByLabel(/código|otp/i).fill(otp!);
  await page.getByRole('button', { name: /verificar|continuar|ingresar/i }).click();

  // Recargas
  await page.goto(`${BASE}/recargas`);
  const saldoLocator = page.getByTestId('saldo');   // supuesto
  const saldoAntes = Number((await saldoLocator.innerText()).replace(/\D/g, ''));

  await page.getByLabel('Operador').selectOption({ label: 'Claro' });
  await page.getByLabel('Celular').fill('3001234567');
  await page.getByLabel('Valor').fill('60000');
  await page.getByRole('button', { name: 'Recargar' }).click();

  // Validaciones
  await expect(page.getByText(/recarga exitosa/i)).toBeVisible();
  await expect(async () => {
    const saldoDespues = Number((await saldoLocator.innerText()).replace(/\D/g, ''));
    expect(saldoDespues).toBe(saldoAntes - 60000);
  }).toPass();
});

// Nota de la IA: "al no ver la aplicación, asumí varias cosas que pueden no coincidir: la ruta /login,
// las etiquetas Operador, Celular, Valor y código/otp, el data-testid="saldo", el texto Recarga exitosa,
// el OTP de 6 dígitos y que el operador es un <select>. Ajusta los localizadores a la pantalla real."
