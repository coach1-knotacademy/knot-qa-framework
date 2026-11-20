import { Locator, Page } from '@playwright/test';

/**
 * CLASE PADRE de todas las pantallas: lo que tienen en común.
 * Cada pantalla hija dice su ruta y hereda abrir() y el mensaje de error.
 */
export abstract class PaginaBase {
  /** El mensaje de error. Se busca por su rol (alert), no por su id ni su color. */
  readonly mensajeDeError: Locator;

  constructor(protected readonly page: Page) {
    this.mensajeDeError = page.getByRole('alert');
  }

  /** La ruta de la pantalla, RELATIVA a entorno.urlBase (por ejemplo "recargas.html"). Nunca la dirección completa. */
  abstract readonly ruta: string;

  async abrir(): Promise<void> {
    await this.page.goto(this.ruta);
  }
}
