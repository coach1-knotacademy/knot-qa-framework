import { $ } from '@wdio/globals';
import { PaginaBase } from './PaginaBase';
import { porAccesibilidad, porId, porTexto } from './localizadores';

/** El carrito: los productos agregados y el total a pagar. */
export class PaginaCarrito extends PaginaBase {
  /** Peldaño 3: el título "My Cart" usa el mismo resource-id que otros títulos de la app. */
  get titulo() {
    return $(porTexto('My Cart'));
  }

  // Peldaño 2: la barra de abajo del carrito.
  get cantidadDeArticulos() {
    return $(porId('itemsTV'));
  }

  get total() {
    return $(porId('totalPriceTV'));
  }

  // Peldaño 1.
  get botonPagar() {
    return $(porAccesibilidad('Confirms products for checkout'));
  }

  async esperarQueCargue(): Promise<void> {
    await this.titulo.waitForDisplayed();
  }
}
