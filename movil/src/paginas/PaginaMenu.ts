import { $ } from '@wdio/globals';
import { PaginaBase } from './PaginaBase';
import { porAccesibilidad, porId } from './localizadores';

/** El menú lateral (las tres rayas). */
export class PaginaMenu extends PaginaBase {
  /** Peldaño 1: estas dos opciones sí tienen content-desc. */
  get opcionIniciarSesion() {
    return $(porAccesibilidad('Login Menu Item'));
  }

  get opcionCerrarSesion() {
    return $(porAccesibilidad('Logout Menu Item'));
  }

  /** Peldaño 2: la lista del menú. */
  private get lista() {
    return $(porId('menuRV'));
  }

  async esperarQueCargue(): Promise<void> {
    await this.lista.waitForDisplayed();
  }

  async irAIniciarSesion(): Promise<void> {
    await this.abrirMenu();
    await this.esperarQueCargue();
    await this.opcionIniciarSesion.click();
  }
}
