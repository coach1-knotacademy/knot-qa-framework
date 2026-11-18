import { Locator, Page } from '@playwright/test';
import { PaginaParaBank } from './PaginaParaBank';

/** "Accounts Overview": la tabla con las cuentas del cliente y sus saldos. */
export class PaginaResumen extends PaginaParaBank {
  readonly ruta = 'overview.htm';
  readonly tabla: Locator;

  constructor(page: Page) {
    super(page);
    this.tabla = page.locator('#accountTable');
  }

  /** La fila de una cuenta (la primera columna es el número). */
  filaDe(idCuenta: number): Locator {
    return this.tabla.locator('tbody tr').filter({ has: this.page.getByRole('link', { name: String(idCuenta), exact: true }) });
  }

  /** El saldo que muestra la tabla para una cuenta, por ejemplo "$515.50". */
  async saldoDe(idCuenta: number): Promise<string> {
    return (await this.filaDe(idCuenta).locator('td').nth(1).innerText()).trim();
  }
}
