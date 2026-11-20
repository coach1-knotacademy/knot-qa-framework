import { Locator, Page } from '@playwright/test';
import { Recarga } from '../datos/fabricaDeRecargas';
import { PaginaBase } from './PaginaBase';

/**
 * PAGE OBJECT · Pantalla "Recargar celular" del Banco Demo.
 *
 * La prueba dice QUÉ ("recarga esto"); esta clase sabe CÓMO. Los localizadores siguen la escalera:
 *   rol + nombre → etiqueta → texto visible → data-testid pactado → (CSS o XPath: nunca)
 * Por eso aguantan el rediseño de la pantalla (recargas.html?rediseno=1): cambian los id, las clases
 * y el orden, pero no lo que ve el usuario.
 */
export class PaginaRecargas extends PaginaBase {
  readonly ruta = 'recargas.html';
  /** El saldo no tiene etiqueta ni rol propio: se usa el data-testid que se pactó con desarrollo. */
  readonly saldoDisponible: Locator;
  readonly comprobante: Locator;
  private readonly listaOperador: Locator;
  private readonly campoNumero: Locator;
  private readonly campoValor: Locator;
  private readonly botonRecargar: Locator;

  constructor(page: Page) {
    super(page);
    this.saldoDisponible = page.getByTestId('saldo-disponible');
    this.comprobante = page.getByRole('status');
    this.listaOperador = page.getByLabel('Operador');
    this.campoNumero = page.getByLabel('Número de celular');
    this.campoValor = page.getByLabel('Valor de la recarga');
    this.botonRecargar = page.getByRole('button', { name: 'Recargar' });
  }

  /** Llena el formulario y pulsa Recargar. */
  async recargar({ operador, numero, monto }: Recarga): Promise<void> {
    await this.listaOperador.selectOption(operador);
    await this.campoNumero.fill(numero);
    await this.campoValor.fill(String(monto));
    await this.botonRecargar.click();
  }

  /** Espera la respuesta (sin pausas fijas) y devuelve el texto del comprobante o del error. */
  async esperarResultado(): Promise<string> {
    const resultado = this.comprobante.or(this.mensajeDeError);
    await resultado.waitFor();
    return (await resultado.innerText()).trim();
  }
}
