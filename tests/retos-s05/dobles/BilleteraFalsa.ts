import { Recarga } from '../../../src/datos/fabricaDeRecargas';
import { Billetera, ResultadoDeBilletera } from '../../../src/screenplay/billetera/UsarLaBilletera';

/**
 * DOBLE DE PRUEBA: una billetera que vive en memoria. No llama a ningún banco.
 * Anota cada recarga que le piden, para que la prueba revise qué le llegó.
 */
export class BilleteraFalsa implements Billetera {
  readonly recargasRecibidas: Recarga[] = [];

  constructor(private saldoActual: number) {}

  async recargar(recarga: Recarga): Promise<ResultadoDeBilletera> {
    this.recargasRecibidas.push(recarga);
    if (recarga.monto > this.saldoActual) return { estado: 400, error: 'Saldo insuficiente' };
    this.saldoActual -= recarga.monto;
    return { estado: 201 };
  }

  async saldo(): Promise<number> {
    return this.saldoActual;
  }
}
