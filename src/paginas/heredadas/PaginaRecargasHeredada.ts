import { Locator, Page } from '@playwright/test';
import { Recarga } from '../../datos/fabricaDeRecargas';
import { PaginaBase } from '../PaginaBase';

/** Las dos versiones de la pantalla de Recargas: la de hoy y la del rediseño (?rediseno=1). */
export type VersionDeRecargas = 'hoy' | 'rediseño';

/**
 * RETO 2 (S6) · LOCALIZADORES ROBUSTOS: el Page Object que nos "heredó" otro equipo.
 *
 * Funciona HOY: todas sus pruebas pasan. Pero el equipo anterior escribió los localizadores mirando
 * el HTML por dentro (clases, posiciones, la ruta completa, los id), no lo que ve el usuario.
 * Desarrollo rediseñó la pantalla (/recargas?rediseno=1) y no cambió nada de lo que ve el cliente…
 * y aun así esta clase se cae. Tu trabajo: cambiar cada localizador frágil por uno robusto.
 *
 * LA ESCALERA (de arriba hacia abajo; se baja solo si el de arriba no se puede):
 *   1. getByRole(rol, { name })   lo que ve y oye el usuario (también un lector de pantalla)
 *   2. getByLabel('...')          la etiqueta del campo
 *   3. getByText('...')           un texto visible que no se repite
 *   4. getByTestId('...')         un data-testid PACTADO con desarrollo, cuando no hay nada visible que sirva
 *   5. CSS o XPath                nunca como primera opción: leen cómo está hecho el HTML, no lo que hace
 *
 * Los localizadores son públicos a propósito (el equipo anterior los dejó así): las pruebas del reto
 * miden cada uno por separado, contra la versión de hoy y contra la del rediseño.
 */
export class PaginaRecargasHeredada extends PaginaBase {
  readonly ruta = '/recargas';

  /** Paso 1 · ROBUSTO: por su etiqueta (antes: la clase CSS input.campo-valor). */
  readonly campoValor: Locator;
  /** Paso 2 · ROBUSTO: por su etiqueta (antes: nth-child, la posición dentro del formulario). */
  readonly campoNumero: Locator;
  /** Paso 3 · ROBUSTO: por su etiqueta (antes: el XPath absoluto desde <html>). */
  readonly listaOperador: Locator;
  /** Paso 4 · ROBUSTO: por el data-testid pactado con desarrollo (antes: el id #saldo). */
  readonly saldoDisponible: Locator;
  /** Paso 5 · ROBUSTO: por su rol y su nombre (antes: texto parcial amarrado a "form > button"). */
  readonly botonRecargar: Locator;

  /** Lo único que el equipo anterior escribió bien: el comprobante por su rol (role="status"). */
  readonly comprobante: Locator;

  constructor(page: Page) {
    super(page);
    this.campoValor = page.getByLabel('Valor de la recarga');
    this.campoNumero = page.getByLabel('Número de celular');
    this.listaOperador = page.getByLabel('Operador');
    this.saldoDisponible = page.getByTestId('saldo-disponible');
    this.botonRecargar = page.getByRole('button', { name: 'Recargar' });
    this.comprobante = page.getByRole('status');
  }

  /** Abre la pantalla de hoy o la del rediseño. */
  async abrir(version: VersionDeRecargas = 'hoy'): Promise<void> {
    await this.page.goto(version === 'rediseño' ? `${this.ruta}?rediseno=1` : this.ruta);
  }

  /** Llena el formulario y pulsa Recargar. */
  async recargar({ operador, numero, monto }: Recarga): Promise<void> {
    await this.listaOperador.selectOption(operador);
    await this.campoNumero.fill(numero);
    await this.campoValor.fill(String(monto));
    await this.botonRecargar.click();
  }

  /** Espera la respuesta y devuelve el texto del comprobante o del error. */
  async esperarResultado(): Promise<string> {
    const resultado = this.comprobante.or(this.mensajeDeError);
    await resultado.waitFor();
    return (await resultado.innerText()).trim();
  }
}
