/**
 * SCREENPLAY sobre el canal de voz (kit de voz).
 *
 * La HABILIDAD guarda un "Transcriptor": algo que convierte el audio de una llamada en texto (STT).
 *   - TranscriptorDeArchivo: lee voz/transcripciones.json. Es el de clase: sin red, sin clave, siempre igual.
 *   - TranscriptorElevenLabs: manda el audio a ElevenLabs (Scribe). Solo si hay clave y lo pides.
 * Es la D de SOLID, como la Billetera de la S5: la tarea no sabe cuál le pasaron, solo lo usa.
 * En tu trabajo, con la herramienta de STT de tu equipo, solo escribes otro Transcriptor.
 */
import * as fs from 'fs';
import * as path from 'path';
import { Hablante, Transcripcion, Turno } from '../../voz/oraculo';
import { CARPETA_VOZ, guion } from '../../voz/guiones';

export interface Transcriptor {
  /** El nombre que va al reporte: con qué motor se transcribió. */
  readonly motor: string;
  transcribir(llamada: string): Promise<Transcripcion>;
}

/** Lee las transcripciones ya hechas (las deja `npm run voz:generar`). Para clase: sin red. */
export class TranscriptorDeArchivo implements Transcriptor {
  readonly motor: string;
  private readonly llamadas: Record<string, { texto: string; turnos: Turno[] }>;

  constructor(archivo = path.join(CARPETA_VOZ, 'transcripciones.json')) {
    if (!fs.existsSync(archivo)) throw new Error(`No existe ${archivo}. Genéralo con: npm run voz:generar`);
    const datos = JSON.parse(fs.readFileSync(archivo, 'utf8'));
    this.motor = `archivo (${datos.motor}, ${datos.fecha})`;
    this.llamadas = datos.llamadas;
  }

  async transcribir(llamada: string): Promise<Transcripcion> {
    const t = this.llamadas[llamada];
    if (!t) throw new Error(`La llamada ${llamada} no está en transcripciones.json. Corre: npm run voz:generar`);
    return { llamada, motor: this.motor, texto: t.texto, turnos: t.turnos };
  }
}

interface PalabraDeScribe {
  text: string;
  type: 'word' | 'spacing' | 'audio_event';
  speaker_id?: string;
}

/**
 * Agrupa las palabras de Scribe en turnos. Scribe dice "speaker_0", "speaker_1"...:
 * quien habla primero es el agente (él hace la llamada); el segundo, el cliente.
 * Es la misma regla de scripts/voz-generar.js.
 */
export function turnosDesdePalabras(palabras: PalabraDeScribe[]): Turno[] {
  const roles = new Map<string, Hablante>();
  const turnos: Turno[] = [];
  for (const p of palabras) {
    if (p.type === 'audio_event') continue;
    const id = p.speaker_id ?? 'sin_voz';
    if (!roles.has(id)) roles.set(id, roles.size === 0 ? 'agente' : roles.size === 1 ? 'cliente' : 'desconocido');
    const hablante = roles.get(id)!;
    const ultimo = turnos[turnos.length - 1];
    if (ultimo && ultimo.hablante === hablante) ultimo.texto += p.text;
    else if (p.type === 'word') turnos.push({ hablante, texto: p.text });
  }
  return turnos.map((t) => ({ hablante: t.hablante, texto: t.texto.trim() }));
}

/** Transcribe el audio de verdad con ElevenLabs Scribe. La clave sale del entorno, nunca del código. */
export class TranscriptorElevenLabs implements Transcriptor {
  readonly motor: string;

  constructor(
    private readonly clave: string,
    private readonly modelo = 'scribe_v2',
  ) {
    if (!clave) throw new Error('Falta ELEVENLABS_API_KEY en el .env: sin clave se usa TranscriptorDeArchivo.');
    this.motor = `ElevenLabs ${modelo}`;
  }

  async transcribir(llamada: string): Promise<Transcripcion> {
    const audio = path.join(CARPETA_VOZ, 'audios', guion(llamada).audio);
    const formulario = new FormData();
    formulario.append('file', new Blob([fs.readFileSync(audio)], { type: 'audio/mpeg' }), path.basename(audio));
    formulario.append('model_id', this.modelo);
    formulario.append('language_code', 'spa');
    formulario.append('diarize', 'true');
    formulario.append('num_speakers', '2');
    formulario.append('tag_audio_events', 'false');
    formulario.append('timestamps_granularity', 'word');
    const respuesta = await fetch('https://api.elevenlabs.io/v1/speech-to-text', {
      method: 'POST',
      headers: { 'xi-api-key': this.clave },
      body: formulario,
    });
    if (!respuesta.ok) throw new Error(`ElevenLabs respondió ${respuesta.status} al transcribir ${llamada}`);
    const datos = (await respuesta.json()) as { text: string; words?: PalabraDeScribe[] };
    return { llamada, motor: this.motor, texto: datos.text, turnos: turnosDesdePalabras(datos.words ?? []) };
  }
}

/** HABILIDAD: usar el agente de voz (escuchar sus llamadas a través de un Transcriptor). */
export class UsarElAgenteDeVoz {
  constructor(readonly transcriptor: Transcriptor) {}

  static con(transcriptor: Transcriptor): UsarElAgenteDeVoz {
    return new UsarElAgenteDeVoz(transcriptor);
  }

  /**
   * Lo normal (y en clase): el archivo. Con VOZ_MOTOR=elevenlabs y la clave en el .env, el motor real.
   * Se pide a propósito: así una corrida normal no gasta créditos ni depende de internet.
   */
  static segunElEntorno(entorno: NodeJS.ProcessEnv = process.env): UsarElAgenteDeVoz {
    const clave = entorno.ELEVENLABS_API_KEY ?? '';
    if (entorno.VOZ_MOTOR === 'elevenlabs' && clave) return new UsarElAgenteDeVoz(new TranscriptorElevenLabs(clave));
    return new UsarElAgenteDeVoz(new TranscriptorDeArchivo());
  }
}
