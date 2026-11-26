import { Locator, Page } from '@playwright/test';
import { Contacto } from '../fabricaDeLaTienda';
import { PaginaToolshop } from './PaginaToolshop';

/**
 * El formulario de contacto. Cada campo tiene su <label>: por eso se encuentra con getByLabel
 * (peldaño 2). Compáralo con el formulario del sistema real, donde eso no funciona.
 */
export class PaginaContacto extends PaginaToolshop {
  readonly ruta = 'contact';
  private readonly nombre: Locator;
  private readonly apellido: Locator;
  private readonly correo: Locator;
  private readonly asunto: Locator;
  private readonly mensaje: Locator;
  private readonly botonEnviar: Locator;

  constructor(page: Page) {
    super(page);
    this.nombre = page.getByLabel('First name');
    this.apellido = page.getByLabel('Last name');
    this.correo = page.getByLabel('Email address');
    this.asunto = page.getByLabel('Subject');
    this.mensaje = page.getByLabel('Message');
    this.botonEnviar = page.getByRole('button', { name: 'Send' });
  }

  /** El mensaje de validación que se ve debajo de un campo (peldaño 3: texto). */
  error(texto: string): Locator {
    return this.page.getByText(texto, { exact: true });
  }

  async enviarVacio(): Promise<void> {
    await this.botonEnviar.click();
  }

  /** Llena solo lo que trae el contacto y envía. El sitio valida antes de mandar nada. */
  async enviar(contacto: Partial<Contacto>): Promise<void> {
    if (contacto.nombre) await this.nombre.fill(contacto.nombre);
    if (contacto.apellido) await this.apellido.fill(contacto.apellido);
    if (contacto.correo) await this.correo.fill(contacto.correo);
    if (contacto.asunto) await this.asunto.selectOption({ label: contacto.asunto });
    if (contacto.mensaje) await this.mensaje.fill(contacto.mensaje);
    await this.botonEnviar.click();
  }
}
