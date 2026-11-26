import { $ } from '@wdio/globals';
import { PaginaBase } from './PaginaBase';
import { porAccesibilidad, porId } from './localizadores';

/** El detalle de un producto: precio, cantidad y "Add to cart". */
export class PaginaDetalle extends PaginaBase {
  // Peldaño 2.
  get nombre() {
    return $(porId('productTV'));
  }

  get precio() {
    return $(porId('priceTV'));
  }

  get cantidad() {
    return $(porId('noTV'));
  }

  // Peldaño 1: los botones de la app sí tienen content-desc.
  private get botonMas() {
    return $(porAccesibilidad('Increase item quantity'));
  }

  private get botonAgregar() {
    return $(porAccesibilidad('Tap to add product to cart'));
  }

  async esperarQueCargue(): Promise<void> {
    await this.botonAgregar.waitForDisplayed();
  }

  /** Deja la cantidad pedida (empieza en 1) y agrega al carrito. */
  async agregarAlCarrito(cantidad: number): Promise<void> {
    for (let i = 1; i < cantidad; i++) await this.botonMas.click();
    await this.botonAgregar.click();
  }
}
