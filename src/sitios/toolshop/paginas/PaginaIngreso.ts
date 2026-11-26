import { Locator, Page } from '@playwright/test';
import { PaginaToolshop } from './PaginaToolshop';

/** El ingreso (Sign in). Solo se prueban sus validaciones: no se crean cuentas en un sitio compartido. */
export class PaginaIngreso extends PaginaToolshop {
  readonly ruta = 'auth/login';
  private readonly correo: Locator;
  private readonly clave: Locator;
  private readonly botonIngresar: Locator;

  constructor(page: Page) {
    super(page);
    this.correo = page.getByLabel('Email address');
    // La etiqueta dice «Password *». exact: false (el valor por omisión) la encuentra igual.
    this.clave = page.getByLabel('Password');
    this.botonIngresar = page.getByRole('button', { name: 'Login' });
  }

  error(texto: string): Locator {
    return this.page.getByText(texto, { exact: true });
  }

  /** Intenta ingresar con lo que reciba (vacío, si no recibe nada). */
  async ingresar(correo = '', clave = ''): Promise<void> {
    if (correo) await this.correo.fill(correo);
    if (clave) await this.clave.fill(clave);
    await this.botonIngresar.click();
  }
}
