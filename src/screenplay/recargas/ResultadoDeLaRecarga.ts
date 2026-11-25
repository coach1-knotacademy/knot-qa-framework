import { Actor, Pregunta } from '../Actor';

/**
 * PREGUNTA (S7): ¿qué dijo el banco después de la recarga? (el comprobante o el mensaje de error)
 *   expect(await ana.pregunta(ResultadoDeLaRecarga.queVio())).toContain('Recarga exitosa');
 *
 * La tarea RecargarDesdeLaPantalla ya esperó la respuesta y la anotó en la memoria del actor.
 * Para lo que sigue en pantalla (el saldo), el «Entonces» usa una aserción que reintenta:
 *   await expect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000')
 */
export class ResultadoDeLaRecarga implements Pregunta<string> {
  static queVio(): ResultadoDeLaRecarga {
    return new ResultadoDeLaRecarga();
  }

  async respondidaPor(actor: Actor): Promise<string> {
    return actor.recuerdo<string>('resultadoDeLaRecarga');
  }
}
