import { Locator, Page } from '@playwright/test';

/**
 * CLASE PADRE de las pantallas de la Toolshop. La misma idea de src/paginas/PaginaBase.ts
 * y de PaginaParaBank: cada hija dice su ruta y hereda abrir().
 * Las rutas son relativas a la urlBase (sin "/" al inicio).
 */
export abstract class PaginaToolshop {
  /** El número del carrito en el menú (aparece cuando hay algo en el carrito). */
  readonly unidadesEnElCarrito: Locator;
  private readonly enlaceCarrito: Locator;

  constructor(protected readonly page: Page) {
    // Peldaño 4 (test-id pactado): un número que cambia no tiene un texto fijo que buscar.
    this.unidadesEnElCarrito = page.getByTestId('cart-quantity');
    // Peldaño 1 (rol + nombre): el enlace del menú se llama «cart».
    this.enlaceCarrito = page.getByRole('link', { name: 'cart' });
  }

  abstract readonly ruta: string;

  /**
   * Abre la pantalla sin esperar a que carguen TODOS los recursos de terceros (chat, analítica, imágenes).
   * En un sitio real, alguno se demora y el evento "load" puede tardar minutos: nos pasó en la primera corrida.
   * Después, cada prueba espera lo que de verdad necesita (un título, un producto) con una aserción que reintenta.
   */
  async abrir(): Promise<void> {
    await this.page.goto(this.ruta, { waitUntil: 'domcontentloaded' });
  }

  async irAlCarrito(): Promise<void> {
    await this.enlaceCarrito.click();
  }

  /** "$14.15" o "14.15" → 14.15. Los precios se comparan como números, no como texto. */
  protected aNumero(texto: string): number {
    return Number(texto.replace(/[^\d.]/g, ''));
  }
}
