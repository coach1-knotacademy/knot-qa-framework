import { $ } from '@wdio/globals';
import { PaginaBase } from './PaginaBase';
import { porId, porIdJuntoAlTexto, porTexto } from './localizadores';

/** La pantalla de inicio de la app: la lista de productos. */
export class PaginaCatalogo extends PaginaBase {
  /** Peldaño 3 (UiAutomator por texto): el título "Products" no tiene un id único en la app. */
  get titulo() {
    return $(porTexto('Products'));
  }

  /** Peldaño 2: la lista. */
  private get lista() {
    return $(porId('productRV'));
  }

  async esperarQueCargue(): Promise<void> {
    await this.lista.waitForDisplayed();
  }

  /**
   * Peldaño 3: en una lista, lo único que distingue a un producto es su nombre.
   * Se toca la IMAGEN que está junto a ese nombre (el nombre solo no es "tocable" en esta app).
   */
  async abrirProducto(nombre: string): Promise<void> {
    await $(porIdJuntoAlTexto('productIV', nombre)).click();
  }
}
