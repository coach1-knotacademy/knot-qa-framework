import { fabricaDeRecargas } from '../../datos/fabricaDeRecargas';
import { Actor, Tarea } from '../Actor';
import { UsarLaBilletera } from './UsarLaBilletera';

/**
 * TAREA: recargar un celular.
 *   await ana.intenta(Recargar.celular('3001234567').por(20_000));
 * Si la billetera responde con error, la tarea falla con ese mensaje (como en un caso manual:
 * si el paso no se puede hacer, el caso se detiene ahí).
 */
export class Recargar implements Tarea {
  private monto = 10_000;

  private constructor(private readonly numero: string) {}

  static celular(numero: string): Recargar {
    return new Recargar(numero);
  }

  por(monto: number): Recargar {
    this.monto = monto;
    return this;
  }

  async realizadaPor(actor: Actor): Promise<void> {
    // TODO reto 2 (extra), en tres líneas. Modelo: SaldoDisponible.ts y la tarea Transferir de ParaBank.
    //   1. Arma la recarga: fabricaDeRecargas.valida({ numero: this.numero, monto: this.monto })
    //   2. Pídesela a la billetera del actor: await actor.usa(UsarLaBilletera).billetera.recargar(recarga)
    //   3. Si el estado no es 201, lanza el error: `${actor.nombre} no pudo recargar: ${resultado.error}`
    // Cuando termines, borra la línea "throw" de abajo.
    throw new Error(`PENDIENTE (S5): completa Recargar.realizadaPor en src/screenplay/billetera/Recargar.ts — ver retos/S05.md, reto 2 (${actor.nombre})`);
  }
}
