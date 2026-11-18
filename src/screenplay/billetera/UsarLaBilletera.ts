/**
 * SCREENPLAY sobre las recargas del Banco Demo (S5 · reto 2).
 *
 * La HABILIDAD guarda una "Billetera": algo que sabe recargar y decir el saldo.
 * En el banco de verdad es el servicio del Banco Demo; en las pruebas de unidad, una BilleteraFalsa.
 * Es la D de SOLID otra vez: la tarea no sabe cuál le pasaron, solo la usa.
 */
import { Recarga } from '../../datos/fabricaDeRecargas';

/** Lo que responde una billetera al recargar: el código HTTP y, si falló, el error. */
export interface ResultadoDeBilletera {
  estado: number;
  error?: string;
}

export interface Billetera {
  recargar(recarga: Recarga): Promise<ResultadoDeBilletera>;
  saldo(): Promise<number>;
}

/** HABILIDAD: usar una billetera. */
export class UsarLaBilletera {
  constructor(readonly billetera: Billetera) {}

  static de(billetera: Billetera): UsarLaBilletera {
    return new UsarLaBilletera(billetera);
  }
}
