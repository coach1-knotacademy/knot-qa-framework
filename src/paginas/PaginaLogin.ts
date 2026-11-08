import { Locator, Page } from '@playwright/test';
import { PaginaBase } from './PaginaBase';

/**
 * Pantalla de ingreso.
 *
 * ENCAPSULAMIENTO: los localizadores son "private". Las pruebas no los ven: solo llaman
 * a ingresar(). Si mañana el botón cambia de nombre, se corrige aquí y en ningún otro lado.
 */
export class PaginaLogin extends PaginaBase {
  readonly ruta = '/';
  private readonly campoUsuario: Locator;
  private readonly campoClave: Locator;
  private readonly botonIngresar: Locator;

  constructor(page: Page) {
    super(page);
    this.campoUsuario = page.getByLabel('Usuario');
    this.campoClave = page.getByLabel('Clave');
    this.botonIngresar = page.getByRole('button', { name: 'Ingresar' });
  }

  /** Escribe usuario y clave y pulsa Ingresar. */
  async ingresar(usuario: string, clave: string): Promise<void> {
    await this.campoUsuario.fill(usuario);
    await this.campoClave.fill(clave);
    await this.botonIngresar.click();
  }
}
