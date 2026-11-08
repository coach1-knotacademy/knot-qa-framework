import { Locator, Page } from '@playwright/test';
import { PaginaBase } from './PaginaBase';

/** Lo que se necesita para una transferencia. Los campos con "?" son opcionales. */
export interface DatosTransferencia {
  /** Número de la cuenta de origen. Si no se indica, queda la que viene seleccionada (Ahorros). */
  origen?: string;
  destino: string;
  monto: number;
  /** Marcar la casilla del 4x1000. Si no se indica, se marca. */
  aceptar4x1000?: boolean;
}

/** Pantalla "Transferir". */
export class PaginaTransferir extends PaginaBase {
  readonly ruta = '/transferir';
  readonly comprobante: Locator;
  private readonly listaOrigen: Locator;
  private readonly campoDestino: Locator;
  private readonly campoMonto: Locator;
  private readonly casilla4x1000: Locator;
  private readonly botonTransferir: Locator;

  constructor(page: Page) {
    super(page);
    this.comprobante = page.getByRole('status');
    this.listaOrigen = page.getByLabel('Cuenta de origen');
    this.campoDestino = page.getByLabel('Cuenta destino');
    this.campoMonto = page.getByLabel('Monto');
    this.casilla4x1000 = page.getByLabel('Acepto el cobro del 4x1000');
    this.botonTransferir = page.getByRole('button', { name: 'Transferir' });
  }

  /** Llena el formulario y pulsa Transferir. */
  async transferir({ origen, destino, monto, aceptar4x1000 = true }: DatosTransferencia): Promise<void> {
    if (origen) {
      await this.listaOrigen.selectOption(origen);
    }
    await this.campoDestino.fill(destino);
    await this.campoMonto.fill(String(monto));
    if (aceptar4x1000) {
      await this.casilla4x1000.check();
    }
    await this.botonTransferir.click();
  }

  /** Espera la respuesta del banco y devuelve el texto del comprobante o del error. */
  async esperarResultado(): Promise<string> {
    const resultado = this.comprobante.or(this.mensajeDeError);
    await resultado.waitFor();
    return (await resultado.innerText()).trim();
  }
}
