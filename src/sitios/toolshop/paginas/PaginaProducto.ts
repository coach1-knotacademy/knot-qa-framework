import { Locator, Page } from '@playwright/test';
import { PaginaToolshop } from './PaginaToolshop';

/** El detalle de un producto: nombre, precio, cantidad y «Add to cart». */
export class PaginaProducto extends PaginaToolshop {
  // El detalle se abre desde el catálogo (cada producto tiene su propio id en la dirección).
  readonly ruta = '';
  readonly nombre: Locator;
  readonly descripcion: Locator;
  /** El aviso que sale al agregar: «Product added to shopping cart.» */
  readonly avisoAgregado: Locator;
  private readonly precio: Locator;
  private readonly masUno: Locator;
  private readonly botonAgregar: Locator;

  constructor(page: Page) {
    super(page);
    this.nombre = page.getByRole('heading', { level: 1 });
    this.descripcion = page.getByTestId('product-description');
    this.avisoAgregado = page.getByText('Product added to shopping cart.').first();
    this.precio = page.getByTestId('unit-price');
    this.masUno = page.getByRole('button', { name: 'Increase quantity' });
    this.botonAgregar = page.getByRole('button', { name: 'Add to cart' });
  }

  async precioUnitario(): Promise<number> {
    return this.aNumero(await this.precio.innerText());
  }

  /** Agrega N unidades: sube la cantidad desde 1 y pulsa «Add to cart» una sola vez. */
  async agregarAlCarrito(cantidad: number): Promise<void> {
    for (let i = 1; i < cantidad; i += 1) await this.masUno.click();
    await this.botonAgregar.click();
  }
}
