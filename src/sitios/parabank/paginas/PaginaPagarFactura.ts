import { Locator, Page } from '@playwright/test';
import { PaginaParaBank } from './PaginaParaBank';

/** Lo que pide el formulario de pago de facturas. */
export interface Factura {
  beneficiario: string;
  cuentaDelBeneficiario: string;
  monto: number;
  desde: number;
}

/** "Bill Pay": paga una factura a un tercero (servicios, celular, tarjeta...). */
export class PaginaPagarFactura extends PaginaParaBank {
  readonly ruta = 'billpay.htm';
  readonly resultado: Locator;
  private readonly botonPagar: Locator;

  constructor(page: Page) {
    super(page);
    this.resultado = page.locator('#billpayResult');
    this.botonPagar = page.getByRole('button', { name: 'Send Payment' });
  }

  private campo(nombre: string): Locator {
    return this.page.locator(`input[name="${nombre}"]`);
  }

  async pagar({ beneficiario, cuentaDelBeneficiario, monto, desde }: Factura): Promise<void> {
    await this.campo('payee.name').fill(beneficiario);
    await this.campo('payee.address.street').fill('Calle 1');
    await this.campo('payee.address.city').fill('Bogota');
    await this.campo('payee.address.state').fill('DC');
    await this.campo('payee.address.zipCode').fill('110111');
    await this.campo('payee.phoneNumber').fill('6011234567');
    await this.campo('payee.accountNumber').fill(cuentaDelBeneficiario);
    await this.campo('verifyAccount').fill(cuentaDelBeneficiario);
    await this.campo('amount').fill(String(monto));
    const origen = this.page.locator('select[name="fromAccountId"]');
    await this.esperarOpciones(origen);
    await origen.selectOption(String(desde));
    await this.botonPagar.click();
    await this.resultado.or(this.page.locator('#billpayError')).first().waitFor();
  }
}
