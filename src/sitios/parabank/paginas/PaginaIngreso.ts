import { Locator, Page } from '@playwright/test';
import { PaginaParaBank } from './PaginaParaBank';

/** Pantalla de inicio de ParaBank, con el ingreso en la columna izquierda. */
export class PaginaIngreso extends PaginaParaBank {
  readonly ruta = 'index.htm';
  /** El saludo que aparece al entrar ("Welcome Ana Prueba"). */
  readonly saludo: Locator;
  private readonly campoUsuario: Locator;
  private readonly campoClave: Locator;
  private readonly botonIngresar: Locator;

  constructor(page: Page) {
    super(page);
    this.saludo = page.locator('#leftPanel .smallText');
    this.campoUsuario = page.locator('input[name="username"]');
    this.campoClave = page.locator('input[name="password"]');
    this.botonIngresar = page.getByRole('button', { name: 'Log In' });
  }

  async ingresar(usuario: string, clave: string): Promise<void> {
    await this.campoUsuario.fill(usuario);
    await this.campoClave.fill(clave);
    await this.botonIngresar.click();
  }
}
