import { Locator, Page } from '@playwright/test';
import { PaginaToolshop } from './PaginaToolshop';

/** El carrito (primer paso del checkout): una fila por producto y el total. Aquí se detiene la prueba: no se paga. */
export class PaginaCarrito extends PaginaToolshop {
  readonly ruta = 'checkout';
  /** El total del carrito, abajo de la tabla. */
  readonly total: Locator;

  constructor(page: Page) {
    super(page);
    this.total = page.getByTestId('cart-total');
  }

  /** La cantidad de un producto: el campo se llama «Quantity for Pliers» (tiene nombre accesible). */
  cantidadDe(producto: string): Locator {
    return this.page.getByRole('spinbutton', { name: `Quantity for ${producto}` });
  }

  /** El total de la fila de un producto. */
  totalDeLaFila(producto: string): Locator {
    return this.page.getByRole('row').filter({ has: this.page.getByRole('cell', { name: producto, exact: true }) }).getByTestId('line-price');
  }
}
