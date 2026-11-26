import { $ } from '@wdio/globals';
import { porAccesibilidad, porId } from './localizadores';

/**
 * CLASE PADRE (abstracta): lo que todas las pantallas de la app tienen en común.
 * Es la misma PaginaBase del framework de Playwright: cambia el "page" por el celular, nada más.
 *
 * - La barra de arriba (menú y carrito) está en todas las pantallas: se escribe UNA vez aquí y
 *   las hijas (PaginaLogin, PaginaCatalogo...) la HEREDAN.
 * - Los localizadores son "getters": se buscan en el momento de usarlos, no al crear la página.
 *   (En móvil la pantalla cambia todo el tiempo; un elemento guardado de antes queda "viejo").
 */
export abstract class PaginaBase {
  /** Peldaño 1 (accessibility id): el botón de las tres rayas. */
  protected get botonMenu() {
    return $(porAccesibilidad('View menu'));
  }

  /** Peldaño 1: el carrito de la barra de arriba. */
  protected get botonCarrito() {
    return $(porAccesibilidad('View cart'));
  }

  /** Peldaño 2 (resource-id): el numerito rojo del carrito. No tiene content-desc propio. */
  get contadorDelCarrito() {
    return $(porId('cartTV'));
  }

  /** Cada pantalla dice cómo saber que ya cargó. La hija está obligada a escribirlo (POLIMORFISMO). */
  abstract esperarQueCargue(): Promise<void>;

  async abrirMenu(): Promise<void> {
    await this.botonMenu.click();
  }

  async irAlCarrito(): Promise<void> {
    await this.botonCarrito.click();
  }
}
