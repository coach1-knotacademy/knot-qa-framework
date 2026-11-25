import { Page } from '@playwright/test';

/**
 * HABILIDAD (S7): usar el navegador. Es la habilidad que tiene un cliente que entra a la página.
 *   const ana = Actor.llamado('Ana').puede(NavegarLaWeb.con(page));
 *
 * Compárala con UsarLaBilletera (S5) y UsarLaApiDeParaBank: el ACTOR y las TAREAS no cambian
 * de forma; lo que cambia es el CANAL. Por eso el mismo escenario de Gherkin puede correr por
 * la pantalla, por la API o, en un proyecto de agentes de voz, por la transcripción de la llamada.
 */
export class NavegarLaWeb {
  constructor(readonly page: Page) {}

  static con(page: Page): NavegarLaWeb {
    return new NavegarLaWeb(page);
  }
}
