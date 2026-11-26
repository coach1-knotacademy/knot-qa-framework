import { Actor, Tarea } from '../Actor';
import { UsarElAgenteDeVoz } from './UsarElAgenteDeVoz';

/**
 * TAREA: escuchar una llamada del agente de voz (es decir, transcribirla).
 *   await lucia.intenta(EscucharLaLlamada.numero('CP-301'));
 * Es el «Dado la llamada CP-301 transcrita del audio sintético». La transcripción queda en la memoria
 * del actor para las preguntas. La tarea no sabe si el texto sale de un archivo o de ElevenLabs.
 */
export class EscucharLaLlamada implements Tarea {
  private constructor(private readonly llamada: string) {}

  static numero(llamada: string): EscucharLaLlamada {
    return new EscucharLaLlamada(llamada);
  }

  async realizadaPor(actor: Actor): Promise<void> {
    const transcripcion = await actor.usa(UsarElAgenteDeVoz).transcriptor.transcribir(this.llamada);
    if (!transcripcion.texto.trim()) throw new Error(`${actor.nombre} no pudo escuchar la llamada ${this.llamada}: la transcripción está vacía`);
    actor.recuerda('transcripcion', transcripcion);
  }
}
