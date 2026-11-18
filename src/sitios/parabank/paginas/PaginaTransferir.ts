import { Locator, Page } from '@playwright/test';
import { PaginaParaBank } from './PaginaParaBank';

/** "Transfer Funds": mueve plata entre dos cuentas del mismo cliente. */
export class PaginaTransferirParaBank extends PaginaParaBank {
  readonly ruta = 'transfer.htm';
  /** El recuadro "Transfer Complete!" con el detalle. */
  readonly resultado: Locator;
  private readonly campoMonto: Locator;
  private readonly listaDesde: Locator;
  private readonly listaHacia: Locator;
  private readonly botonTransferir: Locator;

  constructor(page: Page) {
    super(page);
    this.resultado = page.locator('#showResult');
    this.campoMonto = page.locator('#amount');
    this.listaDesde = page.locator('#fromAccountId');
    this.listaHacia = page.locator('#toAccountId');
    this.botonTransferir = page.getByRole('button', { name: 'Transfer' });
  }

  async transferir({ monto, desde, hacia }: { monto: number; desde: number; hacia: number }): Promise<void> {
    await this.esperarOpciones(this.listaHacia);
    await this.campoMonto.fill(String(monto));
    await this.listaDesde.selectOption(String(desde));
    await this.listaHacia.selectOption(String(hacia));
    await this.botonTransferir.click();
    await this.resultado.or(this.page.locator('#showError')).first().waitFor();
  }
}
