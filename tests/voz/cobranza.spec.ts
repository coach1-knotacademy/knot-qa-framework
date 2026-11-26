/**
 * KIT DE VOZ · Cobranza amable: un agente de voz con IA de una empresa FICTICIA llama por una cuota vencida.
 *
 * Es el Esquema del escenario de especificaciones/cobranza-voz.feature: un test por fila de «Ejemplos»
 * (los datos salen de voz/guiones.json, igual que el DDT de la S8). Cada paso de Gherkin es un test.step().
 * Sin navegador ni servidor: se revisa el TEXTO de la llamada, no la pantalla.
 *
 * El mapeo a las capas:
 *   Dado     → la TAREA EscucharLaLlamada, con la HABILIDAD UsarElAgenteDeVoz (un Transcriptor por dentro)
 *   Cuando   → la PREGUNTA CumplimientoDelGuion, que usa el oráculo (src/voz/oraculo.ts)
 *   Entonces → un expect por cada resultado esperado; la intención, con la PREGUNTA IntencionDelCliente
 *
 * CP-305 tiene un defecto SEMBRADO (VOZ-01): el agente no avisa que la llamada se graba. La prueba se
 * escribe con lo CORRECTO, queda en rojo y se marca como hallazgo esperado (como los BUG-0x del Banco Demo).
 *
 * Correr:  npx.cmd playwright test --project=voz          Solo una:  npx.cmd playwright test -g "CP-301" --project=voz
 * Con el motor real (gasta créditos):  $env:VOZ_MOTOR = 'elevenlabs'  (y la clave en el .env)
 */
import { test, expect } from '@playwright/test';
import { Actor } from '../../src/screenplay/Actor';
import { CumplimientoDelGuion } from '../../src/screenplay/voz/CumplimientoDelGuion';
import { EscucharLaLlamada } from '../../src/screenplay/voz/EscucharLaLlamada';
import { IntencionDelCliente } from '../../src/screenplay/voz/IntencionDelCliente';
import { UsarElAgenteDeVoz } from '../../src/screenplay/voz/UsarElAgenteDeVoz';
import { hallazgoEsperado } from '../../src/soporte/hallazgos';
import { guionesDeVoz, politicaDeCobranza } from '../../src/voz/guiones';
import { InformeDeLlamada, normalizar, wer } from '../../src/voz/oraculo';

const NOMBRES: Record<string, string> = { identificacion: 'identificación', motivo: 'motivo', grabacion: 'grabación', acuerdo: 'acuerdo' };
const porcentaje = (x: number) => `${Math.round(x * 1000) / 10} %`;

test.describe('Cobranza amable por voz · el agente cumple el guion y entiende al cliente', () => {
  for (const g of guionesDeVoz) {
    const frases = [...g.esperado.frases, ...(g.esperado.ofrece_acuerdo ? ['acuerdo'] : [])].map((f) => NOMBRES[f]).join(', ');

    test(`${g.id} · ${g.caso}`, { tag: ['@voz', `@${g.id}`] }, async () => {
      if (g.id === 'CP-305') hallazgoEsperado('VOZ-01', 'el agente de voz no avisa que la llamada se graba');

      const lucia = Actor.llamado('Lucía, QA del canal de voz').puede(UsarElAgenteDeVoz.segunElEntorno());
      let informe!: InformeDeLlamada;

      await test.step(`Dado la llamada «${g.id}» transcrita del audio sintético`, async () => {
        await lucia.intenta(EscucharLaLlamada.numero(g.id));
      });

      await test.step('Cuando el oráculo revisa la transcripción contra el guion', async () => {
        informe = await lucia.pregunta(CumplimientoDelGuion.contra(g));
      });

      await test.step(`Entonces el agente dice «${frases}» y ninguna frase prohibida`, async () => {
        expect(informe.faltantes, `HALLAZGO en ${g.id}: el agente no ${informe.faltantes.join(' ni ')}. Es un defecto del agente, no de la prueba`).toEqual([]);
        expect(informe.prohibidas, `HALLAZGO en ${g.id}: el agente dijo palabras prohibidas`).toEqual([]);
        expect(
          informe.ofreceAcuerdo,
          g.esperado.ofrece_acuerdo
            ? `HALLAZGO en ${g.id}: el agente no ofreció un acuerdo de pago`
            : `HALLAZGO en ${g.id}: el agente ofreció un acuerdo a quien ${g.esperado.intencion === 'ya_pago' ? 'ya pagó' : 'no reconoce la deuda'}`,
        ).toBe(g.esperado.ofrece_acuerdo);
      });

      await test.step(`Y la intención del cliente es «${g.esperado.intencion}» con monto ${g.esperado.monto} y fecha «${g.esperado.fecha ?? 'ninguna'}»`, async () => {
        expect(await lucia.pregunta(IntencionDelCliente.enLaLlamada()), `el agente entendió otra cosa (evidencia: «${informe.intencion.evidencia}»)`).toBe(g.esperado.intencion);
        expect(informe.datos).toEqual({ monto: g.esperado.monto, fecha: g.esperado.fecha });
      });

      await test.step(`Y el WER contra el guion es de máximo ${porcentaje(politicaDeCobranza.umbral_wer)}`, async () => {
        const errores = informe.wer.alineacion.filter((p) => p.tipo !== 'igual').map((p) => `${p.guion ?? '∅'}→${p.transcripcion ?? '∅'}`);
        test.info().annotations.push({ type: 'WER', description: `${g.id}: ${porcentaje(informe.wer.valor)} (${errores.join(', ') || 'sin errores'})` });
        expect(informe.wer.valor, `WER de ${porcentaje(informe.wer.valor)}: ${errores.join(', ')}`).toBeLessThanOrEqual(politicaDeCobranza.umbral_wer);
      });
    });
  }
});

test.describe('El oráculo de voz (pruebas de unidad)', () => {
  test('los números en palabras y en dígitos quedan iguales', () => {
    expect(normalizar('Le debe CIENTO OCHENTA Y CINCO MIL pesos, señora')).toBe('le debe 185000 pesos senora');
    expect(normalizar('Le debe $185.000, señora')).toBe('le debe 185000 pesos senora');
    expect(normalizar('el quince de diciembre')).toBe('el 15 de diciembre');
  });

  test('el WER cuenta palabras cambiadas sobre las palabras del guion, sin importar tildes ni signos', () => {
    expect(wer('Esta llamada es grabada.', 'esta llamada es grabada').valor).toBe(0);
    // 1 palabra cambiada de 4 = 25 %: con un umbral de 15 % esta frase no pasaría.
    expect(wer('esta llamada es grabada', 'esta llamada es robada').valor).toBe(0.25);
  });
});
