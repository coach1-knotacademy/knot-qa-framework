import { Intencion, Transcripcion, detectarIntencion, textoDe } from '../../voz/oraculo';
import { Actor, Pregunta } from '../Actor';

/**
 * PREGUNTA: ¿qué quiere el cliente? (promesa de pago, ya pagó, no reconoce la deuda, pide una persona)
 *   expect(await lucia.pregunta(IntencionDelCliente.enLaLlamada())).toBe('promesa_de_pago');
 * Mira solo lo que dijo el CLIENTE: si el agente dice «ya pagó», no cuenta como intención del cliente.
 */
export class IntencionDelCliente implements Pregunta<Intencion> {
  static enLaLlamada(): IntencionDelCliente {
    return new IntencionDelCliente();
  }

  async respondidaPor(actor: Actor): Promise<Intencion> {
    return detectarIntencion(textoDe(actor.recuerdo<Transcripcion>('transcripcion'), 'cliente'));
  }
}
