import { Locator, Page } from '@playwright/test';
import { TipoDeCuenta } from '../ClienteParaBank';
import { PaginaParaBank } from './PaginaParaBank';

/** "Open New Account": abre una cuenta nueva pasándole $100 de otra cuenta. */
export class PaginaAbrirCuenta extends PaginaParaBank {
  readonly ruta = 'openaccount.htm';
  readonly numeroNuevo: Locator;
  private readonly listaTipo: Locator;
  private readonly listaOrigen: Locator;
  private readonly botonAbrir: Locator;

  constructor(page: Page) {
    super(page);
    this.listaTipo = page.locator('#type');
    this.listaOrigen = page.locator('#fromAccountId');
    this.botonAbrir = page.getByRole('button', { name: 'Open New Account' });
    this.numeroNuevo = page.locator('#newAccountId');
  }

  /** Abre la cuenta y devuelve su número. */
  async abrirCuenta(tipo: TipoDeCuenta, desde?: number): Promise<number> {
    await this.listaTipo.selectOption(tipo === 'CHECKING' ? '0' : '1');
    await this.esperarOpciones(this.listaOrigen);
    if (desde) await this.listaOrigen.selectOption(String(desde));
    await this.botonAbrir.click();
    await this.numeroNuevo.filter({ hasText: /\d+/ }).waitFor();
    return Number(await this.numeroNuevo.innerText());
  }
}
