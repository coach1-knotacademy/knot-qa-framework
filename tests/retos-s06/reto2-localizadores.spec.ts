/**
 * RETO 2 (S6) · LOCALIZADORES ROBUSTOS: que la página heredada aguante el rediseño.
 *
 * Cada prueba mide UN localizador de src/paginas/heredadas/PaginaRecargasHeredada.ts contra las dos
 * versiones de la pantalla: la de hoy (/recargas) y la del rediseño (/recargas?rediseno=1).
 * Un localizador robusto encuentra exactamente 1 elemento en las dos, y es el elemento correcto.
 * Corre con navegador y con el Banco Demo (se inicia solo): npx.cmd playwright test reto2 --project=retos-s06-ui
 */
import { Locator } from '@playwright/test';
import { fabricaDeRecargas } from '../../src/datos/fabricaDeRecargas';
import { usuarios } from '../../src/datos/usuarios';
import { abrirConSesion } from '../../src/flujos/sesion';
import { VersionDeRecargas } from '../../src/paginas/heredadas/PaginaRecargasHeredada';
import { test, expect } from '../../src/soporte/fixtures';

const VERSIONES: VersionDeRecargas[] = ['hoy', 'rediseño'];

/**
 * ¿Cuántos elementos encuentra el localizador en la pantalla? Tiene que ser exactamente 1:
 *  - 0 con el rediseño: es el localizador frágil de siempre → el reto sigue pendiente.
 *  - 0 hoy, o más de 1 (el "modo estricto" de Playwright): hay que revisar lo que escribiste.
 */
async function encuentraUnoSolo(localizador: Locator, nombre: string, version: VersionDeRecargas, paso: number): Promise<void> {
  const cuantos = await localizador.count();
  if (cuantos === 1) return;
  if (cuantos === 0 && version === 'rediseño') {
    throw new Error(`PENDIENTE (S6): con el rediseño, ${nombre} no encuentra nada (${localizador}). Cámbialo por uno que lea lo que ve el usuario — ver retos/S06.md, reto 2, paso ${paso}`);
  }
  throw new Error(`${nombre} encontró ${cuantos} elementos en la versión "${version}" (${localizador}). Debe encontrar exactamente 1.`);
}

test.beforeEach(async ({ page, cliente }) => {
  await abrirConSesion(page, cliente, usuarios.ana);
});

test('paso 1 · campoValor (clase CSS) encuentra el campo hoy y con el rediseño', async ({ paginaRecargasHeredada: heredada }) => {
  for (const version of VERSIONES) {
    await heredada.abrir(version);
    await encuentraUnoSolo(heredada.campoValor, 'campoValor', version, 1);

    // Es el campo que el usuario conoce como "Valor de la recarga", y se puede escribir en él.
    await expect(heredada.campoValor).toHaveAccessibleName('Valor de la recarga');
    await heredada.campoValor.fill('10000');
    await expect(heredada.campoValor).toHaveValue('10000');
  }
});

test('paso 2 · campoNumero (nth-child) encuentra el celular hoy y con el rediseño', async ({ paginaRecargasHeredada: heredada }) => {
  for (const version of VERSIONES) {
    await heredada.abrir(version);
    await encuentraUnoSolo(heredada.campoNumero, 'campoNumero', version, 2);

    await expect(heredada.campoNumero).toHaveAccessibleName('Número de celular');
    await heredada.campoNumero.fill('3001234567');
    await expect(heredada.campoNumero).toHaveValue('3001234567');
  }
});

test('paso 3 · listaOperador (XPath absoluto) encuentra la lista hoy y con el rediseño', async ({ paginaRecargasHeredada: heredada }) => {
  for (const version of VERSIONES) {
    await heredada.abrir(version);
    await encuentraUnoSolo(heredada.listaOperador, 'listaOperador', version, 3);

    await expect(heredada.listaOperador).toHaveAccessibleName('Operador');
    await heredada.listaOperador.selectOption('Tigo');
    await expect(heredada.listaOperador).toHaveValue('Tigo');
  }
});

test('paso 4 · saldoDisponible (#saldo) muestra el saldo de Ahorros hoy y con el rediseño', async ({ paginaRecargasHeredada: heredada }) => {
  for (const version of VERSIONES) {
    await heredada.abrir(version);
    await encuentraUnoSolo(heredada.saldoDisponible, 'saldoDisponible', version, 4);

    // El saldo llega del servicio con una demora: toHaveText espera solo, sin pausas fijas.
    await expect(heredada.saldoDisponible).toHaveText('$1.500.000');
  }
});

test('paso 5 · botonRecargar (texto parcial con CSS) es el botón Recargar hoy y con el rediseño', async ({ paginaRecargasHeredada: heredada }) => {
  for (const version of VERSIONES) {
    await heredada.abrir(version);
    await encuentraUnoSolo(heredada.botonRecargar, 'botonRecargar', version, 5);

    // Con el formulario vacío, el botón correcto responde con la primera regla del banco.
    await heredada.botonRecargar.click();
    await expect(heredada.mensajeDeError).toHaveText('Elige un operador');
  }
});

test('al final · una recarga completa con la página heredada funciona hoy y con el rediseño', async ({ paginaRecargasHeredada: heredada }) => {
  // Las dos recargas son de la misma sesión: el saldo baja $10.000 cada vez (regla: se descuenta de Ahorros).
  const saldoEsperado = { hoy: '$1.490.000', rediseño: '$1.480.000' };
  for (const version of VERSIONES) {
    await heredada.abrir(version);
    await encuentraUnoSolo(heredada.campoValor, 'campoValor', version, 1);
    await encuentraUnoSolo(heredada.campoNumero, 'campoNumero', version, 2);
    await encuentraUnoSolo(heredada.listaOperador, 'listaOperador', version, 3);
    await encuentraUnoSolo(heredada.saldoDisponible, 'saldoDisponible', version, 4);
    await encuentraUnoSolo(heredada.botonRecargar, 'botonRecargar', version, 5);

    await heredada.recargar(fabricaDeRecargas.valida());

    expect(await heredada.esperarResultado()).toContain('Recarga exitosa');
    await expect(heredada.saldoDisponible).toHaveText(saldoEsperado[version]);
  }
});
