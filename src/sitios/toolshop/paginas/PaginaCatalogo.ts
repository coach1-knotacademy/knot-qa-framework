import { Locator, Page } from '@playwright/test';
import { PaginaToolshop } from './PaginaToolshop';

/**
 * El catálogo (la página de inicio): buscar, filtrar por categoría y abrir un producto.
 * Todos los localizadores salen de lo que ve la persona: rol + nombre o etiqueta.
 */
export class PaginaCatalogo extends PaginaToolshop {
  readonly ruta = '';
  /** El título que confirma la búsqueda: «Searched for: Pliers». */
  readonly tituloDeLaBusqueda: Locator;
  /** Los nombres de los productos que se ven ahora (cada tarjeta tiene su título). */
  readonly nombresDeProductos: Locator;
  private readonly buscador: Locator;
  private readonly botonBuscar: Locator;

  constructor(page: Page) {
    super(page);
    this.buscador = page.getByRole('textbox', { name: 'Search' });
    // exact: también existe el botón «X» para limpiar, y textos que contienen "Search".
    this.botonBuscar = page.getByRole('button', { name: 'Search', exact: true });
    this.tituloDeLaBusqueda = page.getByRole('heading', { name: /^Searched for:/ });
    this.nombresDeProductos = page.getByRole('heading', { level: 5 });
  }

  /** La tarjeta de un producto: el enlace que tiene su título. */
  private tarjeta(nombre: string): Locator {
    return this.page.getByRole('link').filter({ has: this.page.getByRole('heading', { level: 5, name: nombre, exact: true }) });
  }

  async buscar(texto: string): Promise<void> {
    await this.buscador.fill(texto);
    await this.botonBuscar.click();
  }

  /** Marca una categoría del filtro «By category» (por ejemplo «Hammer»). */
  async filtrarPorCategoria(categoria: string): Promise<void> {
    await this.page.getByRole('checkbox', { name: categoria, exact: true }).check();
  }

  /**
   * ¿Todos los productos que se ven tienen ese texto en el nombre? (sin importar mayúsculas)
   * Ojo: la lista se actualiza DESPUÉS de buscar o filtrar. Por eso la prueba usa expect.poll,
   * que vuelve a preguntar hasta que la lista nueva aparece (y falla si nunca aparece).
   */
  async todosLosProductosDicen(texto: string): Promise<boolean> {
    const nombres = (await this.nombresDeProductos.allInnerTexts()).map((n) => n.trim());
    return nombres.length > 0 && nombres.every((n) => n.toLowerCase().includes(texto.toLowerCase()));
  }

  /** El precio que muestra la tarjeta del producto en el catálogo, como número. */
  async precioEnElCatalogo(nombre: string): Promise<number> {
    // Peldaño 4 (test-id pactado): el precio cambia, no hay un texto fijo que buscar.
    return this.aNumero(await this.tarjeta(nombre).getByTestId('product-price').innerText());
  }

  async abrirProducto(nombre: string): Promise<void> {
    await this.tarjeta(nombre).click();
  }
}
