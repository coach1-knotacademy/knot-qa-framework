import { Locator, Page } from '@playwright/test';
import { Recarga } from '../datos/fabricaDeRecargas';
import { PaginaBase } from './PaginaBase';

/**
 * Pantalla "Recargar celular" (S5) · PAGE OBJECT
 *
 * La prueba dice QUÉ quiere ("recarga esto") y esta clase sabe CÓMO se hace en la pantalla.
 * Si el botón cambia de nombre o el campo se mueve, se corrige aquí y en ningún otro lado.
 */
export class PaginaRecargas extends PaginaBase {
  readonly ruta = '/recargas';
  readonly comprobante: Locator;
  readonly saldoDisponible: Locator;
  readonly campoCodigo: Locator;
  /** S6 · Público: la prueba del servicio de saldos caído revisa que siga habilitado (antes lo buscaba ella misma). */
  readonly botonRecargar: Locator;
  private readonly listaOperador: Locator;
  private readonly campoNumero: Locator;
  private readonly campoValor: Locator;
  private readonly botonConfirmar: Locator;

  constructor(page: Page) {
    super(page);
    this.comprobante = page.getByRole('status');
    // S6 · Antes era page.locator('#saldo') y se caía con el rediseño. El data-testid lo pactamos con desarrollo.
    this.saldoDisponible = page.getByTestId('saldo-disponible');
    this.listaOperador = page.getByLabel('Operador');
    this.campoNumero = page.getByLabel('Número de celular');
    this.campoValor = page.getByLabel('Valor de la recarga');
    this.botonRecargar = page.getByRole('button', { name: 'Recargar' });
    this.campoCodigo = page.getByLabel('Código de seguridad');
    this.botonConfirmar = page.getByRole('button', { name: 'Confirmar recarga' });
  }

  /** Llena el formulario y pulsa Recargar. */
  async recargar({ operador, numero, monto }: Recarga): Promise<void> {
    await this.listaOperador.selectOption(operador);
    await this.campoNumero.fill(numero);
    await this.campoValor.fill(String(monto));
    await this.botonRecargar.click();
  }

  /** Escribe el código de seguridad (recargas de más de $50.000) y confirma. */
  async confirmar(codigo: string): Promise<void> {
    await this.campoCodigo.fill(codigo);
    await this.botonConfirmar.click();
  }

  /** Espera la respuesta y devuelve el texto del comprobante o del error. */
  async esperarResultado(): Promise<string> {
    const resultado = this.comprobante.or(this.mensajeDeError);
    await resultado.waitFor();
    return (await resultado.innerText()).trim();
  }

  /** El saldo de Ahorros que muestra la pantalla, ya cargado (por ejemplo "$1.500.000"). */
  async saldo(): Promise<string> {
    await this.saldoDisponible.filter({ hasText: '$' }).waitFor();
    return (await this.saldoDisponible.innerText()).trim();
  }
}
