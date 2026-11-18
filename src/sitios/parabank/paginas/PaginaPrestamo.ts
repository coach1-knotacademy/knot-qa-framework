import { Locator, Page } from '@playwright/test';
import { PaginaParaBank } from './PaginaParaBank';

/** "Request Loan": pide un préstamo con una cuota inicial. El banco lo aprueba o lo niega. */
export class PaginaPrestamo extends PaginaParaBank {
  readonly ruta = 'requestloan.htm';
  /** "Approved" o "Denied". */
  readonly estado: Locator;
  readonly motivoDelRechazo: Locator;
  private readonly campoMonto: Locator;
  private readonly campoCuotaInicial: Locator;
  private readonly listaOrigen: Locator;
  private readonly botonSolicitar: Locator;

  constructor(page: Page) {
    super(page);
    this.estado = page.locator('#loanStatus');
    this.motivoDelRechazo = page.locator('#loanRequestDenied');
    this.campoMonto = page.locator('#amount');
    this.campoCuotaInicial = page.locator('#downPayment');
    this.listaOrigen = page.locator('#fromAccountId');
    this.botonSolicitar = page.getByRole('button', { name: 'Apply Now' });
  }

  async solicitar({ monto, cuotaInicial, desde }: { monto: number; cuotaInicial: number; desde: number }): Promise<void> {
    await this.esperarOpciones(this.listaOrigen);
    await this.campoMonto.fill(String(monto));
    await this.campoCuotaInicial.fill(String(cuotaInicial));
    await this.listaOrigen.selectOption(String(desde));
    await this.botonSolicitar.click();
    await this.estado.filter({ hasText: /\w/ }).waitFor();
  }
}
