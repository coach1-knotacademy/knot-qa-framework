import { Locator, Page } from '@playwright/test';

/**
 * PAGE OBJECT del formulario público «Recarga tu Nequi» (PSE). Kit «web real», parte B: lo corre solo el instructor.
 * Reglas en ./entorno.ts. Este Page Object, A PROPÓSITO, no tiene métodos para pulsar «Continuar»
 * ni para marcar la casilla antibots: si no existe el método, ninguna prueba lo puede hacer por error.
 *
 * EL HALLAZGO (verificado el 25 nov): los campos salen en el árbol de accesibilidad como
 * spinbutton y textbox SIN NOMBRE. La causa está en el HTML: el id se repite. El componente
 * <nequi-input id="phoneNumber"> y el <input id="phoneNumber"> de adentro tienen el mismo id,
 * y <label for="phoneNumber"> apunta al primero (el envoltorio), que no es un campo.
 * Resultado: getByLabel('Número de celular') no encuentra nada, y un lector de pantalla tampoco.
 *
 * LA ESCALERA (S6) aplicada a este formulario:
 *  - Peldaño 2, lo ideal:  getByLabel('Número de celular')    → 0 elementos (es el hallazgo).
 *  - Lo que usamos:        getByRole('spinbutton').nth(0)    → rol sí, nombre no. Un peldaño más abajo:
 *    depende del ORDEN de los campos, igual que nth-child. Si agregan un campo arriba, escribiríamos
 *    en el equivocado. Por eso abrir() revisa que haya exactamente 2 campos numéricos y 1 de texto,
 *    y si no, para con un mensaje claro en vez de escribir donde no es.
 *  - La recomendación profesional: pedir a desarrollo un <label for> que apunte al <input> (id único)
 *    o un aria-label. Arregla la prueba y, sobre todo, la accesibilidad para las personas.
 */
export class PaginaRecargaPse {
  readonly ruta = 'recargas';
  readonly titulo: Locator;

  /** Lo que DEBERÍA funcionar (peldaño 2). Se deja para demostrar el hallazgo: hoy encuentra 0 elementos. */
  readonly celularPorEtiqueta: Locator;

  /** Lo que sí funciona: rol sin nombre + posición (un peldaño más abajo, protegido por abrir()). */
  readonly celular: Locator;
  readonly confirmacion: Locator;
  readonly valor: Locator;

  /** Solo para verificar que está deshabilitado. NUNCA se pulsa. */
  readonly continuar: Locator;
  /** Solo para verificar que nadie la marcó. NUNCA se marca: es el control antibots. */
  readonly antibots: Locator;

  private readonly camposNumericos: Locator;
  private readonly camposDeTexto: Locator;

  constructor(private readonly page: Page) {
    this.titulo = page.getByRole('heading', { name: 'Recarga tu Nequi' });
    this.celularPorEtiqueta = page.getByLabel('Número de celular', { exact: true });
    this.camposNumericos = page.getByRole('spinbutton');
    this.camposDeTexto = page.getByRole('textbox');
    this.celular = this.camposNumericos.nth(0);
    this.confirmacion = this.camposNumericos.nth(1);
    this.valor = this.camposDeTexto.first();
    this.continuar = page.getByRole('button', { name: 'Continuar' });
    this.antibots = page.getByRole('checkbox', { name: 'Confirmo que soy una persona real.' });
  }

  /** Abre el formulario y revisa que siga teniendo la forma que el Page Object conoce. */
  async abrir(): Promise<void> {
    await this.page.goto(this.ruta);
    await this.titulo.waitFor();
    await this.celular.waitFor();
    const numericos = await this.camposNumericos.count();
    const deTexto = await this.camposDeTexto.count();
    if (numericos !== 2 || deTexto !== 1) {
      throw new Error(
        `El formulario cambió: hay ${numericos} campos numéricos y ${deTexto} de texto, y el Page Object espera 2 y 1 ` +
          '(celular, confirmación y valor). Los localizadores van por posición: revisa el orden antes de seguir.',
      );
    }
  }

  /** El mensaje de validación que se ve debajo de un campo (peldaño 3: texto). */
  error(texto: string): Locator {
    return this.page.getByText(texto, { exact: true });
  }

  /** Escribe el celular y su confirmación, y sale del campo (la validación se dispara al salir). */
  async escribirCelular(numero: string, confirmacion = numero): Promise<void> {
    await this.celular.fill(numero);
    await this.confirmacion.fill(confirmacion);
    await this.confirmacion.blur();
  }

  async escribirValor(valor: string): Promise<void> {
    await this.valor.fill(valor);
    await this.valor.blur();
  }

  /**
   * DIAGNÓSTICO (no es un localizador): ¿por qué las etiquetas no nombran los campos?
   * Cuenta cuántos elementos tienen el id al que apunta cada <label for> y si ese id es el del <input>.
   */
  async diagnosticoDeEtiquetas(): Promise<{ etiqueta: string; elementosConEseId: number; apuntaAUnCampo: boolean }[]> {
    return this.page.evaluate(() =>
      ['phoneNumber', 'confirmPhoneNumber', 'transactionValue'].map((id) => {
        const etiqueta = document.querySelector(`label[for="${id}"]`);
        const primero = document.getElementById(id);
        return {
          etiqueta: etiqueta?.textContent?.trim() ?? '(sin etiqueta)',
          elementosConEseId: document.querySelectorAll(`[id="${id}"]`).length,
          apuntaAUnCampo: primero instanceof HTMLInputElement,
        };
      }),
    );
  }
}
