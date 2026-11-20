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

  /** Paso 1 · FRÁGIL (clase CSS): la clase es para pintar, no para encontrar. Si cambia el estilo, se cae. */
  readonly campoValor: Locator;
  /** Paso 2 · FRÁGIL (nth-child): "el cuarto hijo del primer formulario". Si mueven un campo, apunta a otro. */
  readonly campoNumero: Locator;
  /** Paso 3 · FRÁGIL (XPath absoluto): la ruta completa desde <html>. Cualquier contenedor nuevo la rompe. */
  readonly listaOperador: Locator;
  /** Paso 4 · FRÁGIL (id): el id lo pone desarrollo y lo puede cambiar sin avisar. */
  readonly saldoDisponible: Locator;
  /** Paso 5 · FRÁGIL (texto parcial con CSS): el texto está bien, pero amarrado a "un botón hijo directo de un form". */
  readonly botonRecargar: Locator;

  /** Lo único que el equipo anterior escribió bien: el comprobante por su rol (role="status"). */
  readonly comprobante: Locator;

  constructor(page: Page) {
    super(page);
    // TODO paso 1: el campo tiene la etiqueta "Valor de la recarga".
    this.campoValor = page.locator('input.campo-valor');
    // TODO paso 2: el campo tiene la etiqueta "Número de celular".
    this.campoNumero = page.locator('main > form:first-of-type > :nth-child(4)');
    // TODO paso 3: la lista tiene la etiqueta "Operador".
    this.listaOperador = page.locator('xpath=/html/body/main/form[1]/select');
    // TODO paso 4: el saldo no tiene etiqueta ni rol propio. Desarrollo pactó con nosotros data-testid="saldo-disponible".
    this.saldoDisponible = page.locator('#saldo');
    // TODO paso 5: es un botón (rol "button") que se llama "Recargar".
    this.botonRecargar = page.locator('form > button:has-text("Recargar")');
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
