import { Locator, Page } from '@playwright/test';
import { revisarLimite } from '../ClienteParaBank';

/**
 * CLASE PADRE de las pantallas de ParaBank. Igual idea que src/paginas/PaginaBase.ts:
 * cada hija dice su ruta y hereda abrir(). Las rutas son relativas a la urlBase (sin "/" al inicio).
 */
export abstract class PaginaParaBank {
  /** El título grande de la pantalla (por ejemplo "Transfer Funds"). */
  readonly titulo: Locator;
  /** La caja de error que muestran todas las pantallas cuando algo falla. */
  readonly error: Locator;

  constructor(protected readonly page: Page) {
    this.titulo = page.locator('#rightPanel h1.title').first();
    this.error = page.locator('#rightPanel .error').first();
  }

  abstract readonly ruta: string;

  async abrir(): Promise<void> {
    const respuesta = await this.page.goto(this.ruta);
    if (respuesta) revisarLimite(respuesta);
  }

  /** Espera a que una lista de cuentas termine de cargar (ParaBank la llena después de abrir la pantalla). */
  protected async esperarOpciones(lista: Locator): Promise<void> {
    await lista.locator('option').first().waitFor({ state: 'attached' });
  }
}
