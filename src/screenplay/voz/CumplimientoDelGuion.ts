import { politicaDeCobranza } from '../../voz/guiones';
import { Guion, InformeDeLlamada, Transcripcion, revisarLlamada } from '../../voz/oraculo';
import { Actor, Pregunta } from '../Actor';

/**
 * PREGUNTA: ¿la llamada cumple el guion y la política de cobranza?
 *   const informe = await lucia.pregunta(CumplimientoDelGuion.contra(guion('CP-301')));
 *   expect(informe.faltantes).toEqual([]);
 *
 * Devuelve el informe completo (frases, prohibidas, acuerdo, intención, datos y WER) para que cada
 * «Entonces» revise lo suyo. El umbral del WER sale de la política; se puede cambiar: .conUmbral(0.10).
 */
export class CumplimientoDelGuion implements Pregunta<InformeDeLlamada> {
  private umbral = politicaDeCobranza.umbral_wer;

  private constructor(private readonly guion: Guion) {}

  static contra(guion: Guion): CumplimientoDelGuion {
    return new CumplimientoDelGuion(guion);
  }

  conUmbral(umbral: number): CumplimientoDelGuion {
    this.umbral = umbral;
    return this;
  }

  async respondidaPor(actor: Actor): Promise<InformeDeLlamada> {
    return revisarLlamada(this.guion, actor.recuerdo<Transcripcion>('transcripcion'), politicaDeCobranza, this.umbral);
  }
}
