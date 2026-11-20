import { fabricaDeRecargas } from '../../datos/fabricaDeRecargas';
import { Actor, Tarea } from '../Actor';
import { ResultadoDeBilletera, UsarLaBilletera } from './UsarLaBilletera';

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
    const recarga = fabricaDeRecargas.valida({ numero: this.numero, monto: this.monto });
    const resultado: ResultadoDeBilletera = await actor.usa(UsarLaBilletera).billetera.recargar(recarga);
    actor.recuerda('ultimaRecarga', resultado);
    if (resultado.estado !== 201) throw new Error(`${actor.nombre} no pudo recargar: ${resultado.error}`);
  }
}
