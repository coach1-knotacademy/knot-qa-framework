import { Actor, Pregunta } from '../Actor';
import { UsarLaBilletera } from './UsarLaBilletera';

/**
 * PREGUNTA: ¿cuánta plata le queda al actor en la billetera?
 * Esta clase está COMPLETA: úsala de modelo para la tarea Recargar.
 */
export class SaldoDisponible implements Pregunta<number> {
  static enLaBilletera(): SaldoDisponible {
    return new SaldoDisponible();
  }

  respondidaPor(actor: Actor): Promise<number> {
    return actor.usa(UsarLaBilletera).billetera.saldo();
  }
}
