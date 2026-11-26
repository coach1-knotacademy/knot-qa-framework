/**
 * KIT DE VOZ · EL ORÁCULO: decide si una llamada del agente de voz cumple, mirando el TEXTO.
 *
 * El audio no se compara con el audio. Se transcribe (STT) y se revisa la transcripción:
 *   - frases obligatorias: se identifica, dice el motivo y avisa que la llamada se graba;
 *   - lo prohibido: amenazas o lenguaje ofensivo;
 *   - si ofrece (o no) un acuerdo de pago;
 *   - la INTENCIÓN del cliente (promesa de pago, ya pagó, no reconoce la deuda, pide una persona);
 *   - los DATOS: monto y fecha;
 *   - el WER contra el guion, con un UMBRAL (por ejemplo ≤ 15 %). Nunca coincidencia exacta:
 *     un STT nunca devuelve el texto idéntico, y una prueba que pide igualdad exacta siempre es roja.
 *
 * Este archivo no importa nada (ni fs, ni Playwright): son funciones puras. Por eso el laboratorio del
 * navegador (laboratorio/voz.html) usa EXACTAMENTE este mismo código, convertido a JS por el generador.
 */

// ─────────────────────────── Tipos ───────────────────────────
export type Hablante = 'agente' | 'cliente' | 'desconocido';
export type Intencion = 'promesa_de_pago' | 'ya_pago' | 'no_reconoce_la_deuda' | 'pide_una_persona' | 'sin_intencion_clara';

export interface Turno {
  hablante: Hablante;
  texto: string;
}

/** Lo que devuelve el STT: el texto completo y, si el motor separa voces, quién dijo qué. */
export interface Transcripcion {
  llamada: string;
  motor: string;
  texto: string;
  turnos: Turno[];
}

export interface FraseObligatoria {
  id: string;
  nombre: string;
  /** Formas aceptadas. Se comparan ya normalizadas (sin tildes, números en dígitos). */
  alternativas: string[];
}

export interface Politica {
  umbral_wer: number;
  frases: FraseObligatoria[];
  prohibidas: string[];
}

export interface Esperado {
  intencion: Intencion;
  monto: number | null;
  fecha: string | null;
  frases: string[];
  ofrece_acuerdo: boolean;
}

export interface Guion {
  id: string;
  caso: string;
  cliente: string;
  audio: string;
  turnos: Turno[];
  esperado: Esperado;
}

// ─────────────────────────── 1. Normalizar ───────────────────────────
const NUMEROS: Record<string, number> = {
  cero: 0, uno: 1, dos: 2, tres: 3, cuatro: 4, cinco: 5, seis: 6, siete: 7, ocho: 8, nueve: 9,
  diez: 10, once: 11, doce: 12, trece: 13, catorce: 14, quince: 15, dieciseis: 16, diecisiete: 17, dieciocho: 18, diecinueve: 19,
  veinte: 20, veintiuno: 21, veintiun: 21, veintidos: 22, veintitres: 23, veinticuatro: 24, veinticinco: 25,
  veintiseis: 26, veintisiete: 27, veintiocho: 28, veintinueve: 29,
  treinta: 30, cuarenta: 40, cincuenta: 50, sesenta: 60, setenta: 70, ochenta: 80, noventa: 90,
  cien: 100, ciento: 100, doscientos: 200, doscientas: 200, trescientos: 300, trescientas: 300,
  cuatrocientos: 400, cuatrocientas: 400, quinientos: 500, quinientas: 500, seiscientos: 600, seiscientas: 600,
  setecientos: 700, setecientas: 700, ochocientos: 800, ochocientas: 800, novecientos: 900, novecientas: 900,
  mil: 1000, millon: 1000000, millones: 1000000,
};
const MULTIPLICADORES = ['mil', 'millon', 'millones'];

/** Valor de la palabra i si es parte de un número. "un/una" y los dígitos solo cuentan delante de mil/millón. */
function valorNumerico(palabras: string[], i: number): number | undefined {
  const p = palabras[i];
  const siguienteMultiplica = MULTIPLICADORES.indexOf(palabras[i + 1]) >= 0;
  if (p in NUMEROS) return NUMEROS[p];
  if ((p === 'un' || p === 'una') && siguienteMultiplica) return 1;
  if (/^\d+$/.test(p) && siguienteMultiplica) return Number(p);
  return undefined;
}

/** "ciento ochenta y cinco mil" → "185000". Así el guion y el STT hablan igual de los números. */
function numerosEnDigitos(palabras: string[]): string[] {
  const salida: string[] = [];
  let i = 0;
  while (i < palabras.length) {
    if (valorNumerico(palabras, i) === undefined) {
      salida.push(palabras[i]);
      i += 1;
      continue;
    }
    let total = 0;
    let actual = 0;
    let anterior = -1;
    while (i < palabras.length) {
      // "cuarenta y cinco": la "y" solo une una decena con una unidad.
      if (palabras[i] === 'y' && anterior >= 30 && anterior % 10 === 0 && anterior < 100) {
        const unidad = valorNumerico(palabras, i + 1);
        if (unidad !== undefined && unidad >= 1 && unidad <= 9) {
          i += 1;
          continue;
        }
        break;
      }
      const valor = valorNumerico(palabras, i);
      if (valor === undefined) break;
      if (valor === 1000) {
        total += (actual || 1) * 1000;
        actual = 0;
      } else if (valor === 1000000) {
        total = (total + (actual || 1)) * 1000000;
        actual = 0;
      } else {
        actual += valor;
      }
      anterior = valor;
      i += 1;
    }
    salida.push(String(total + actual));
  }
  return salida;
}

/**
 * Deja el texto listo para comparar: minúsculas, sin tildes ni signos, los números en dígitos
 * ("$185.000", "185 mil" y "ciento ochenta y cinco mil pesos" quedan todos "185000 pesos").
 */
export function normalizar(texto: string): string {
  let t = String(texto || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  t = t.replace(/\$\s*([\d.,]+)/g, ' $1 pesos ');
  t = t.replace(/(\d)[.,](?=\d{3}\b)/g, '$1');
  t = t.replace(/%/g, ' por ciento ');
  t = t.replace(/[^a-z0-9\s]/g, ' ');
  const palabras = numerosEnDigitos(t.split(/\s+/).filter(Boolean));
  return palabras.filter((p, i) => !(p === 'pesos' && palabras[i - 1] === 'pesos')).join(' ');
}

/** ¿Está la frase (como palabras completas) dentro del texto? Los dos ya normalizados. */
function contiene(textoNormalizado: string, frase: string): boolean {
  const buscada = normalizar(frase);
  return buscada.length > 0 && ` ${textoNormalizado} `.indexOf(` ${buscada} `) >= 0;
}

// ─────────────────────────── 2. WER ───────────────────────────
export type TipoDePaso = 'igual' | 'sustitucion' | 'borrado' | 'insercion';
export interface PasoDeAlineacion {
  tipo: TipoDePaso;
  guion?: string;
  transcripcion?: string;
}
export interface ResultadoWer {
  /** Errores / palabras del guion. 0 = idéntico. 0,15 = 15 %. */
  valor: number;
  sustituciones: number;
  borrados: number;
  inserciones: number;
  palabrasDelGuion: number;
  alineacion: PasoDeAlineacion[];
}

/**
 * WER (Word Error Rate): cuántas palabras hay que cambiar, borrar o insertar para pasar del guion
 * a la transcripción (distancia de Levenshtein en palabras), dividido por las palabras del guion.
 */
export function wer(guion: string, transcripcion: string): ResultadoWer {
  const ref = normalizar(guion).split(' ').filter(Boolean);
  const hip = normalizar(transcripcion).split(' ').filter(Boolean);
  const n = ref.length;
  const m = hip.length;
  const d: number[][] = [];
  for (let i = 0; i <= n; i++) {
    d.push([]);
    for (let j = 0; j <= m; j++) d[i].push(i === 0 ? j : j === 0 ? i : 0);
  }
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      const costo = ref[i - 1] === hip[j - 1] ? 0 : 1;
      d[i][j] = Math.min(d[i - 1][j - 1] + costo, d[i - 1][j] + 1, d[i][j - 1] + 1);
    }
  }
  // Recorrer el camino de vuelta para mostrar QUÉ palabras fallaron (eso es lo que se reporta).
  const alineacion: PasoDeAlineacion[] = [];
  let i = n;
  let j = m;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && d[i][j] === d[i - 1][j - 1] + (ref[i - 1] === hip[j - 1] ? 0 : 1)) {
      alineacion.unshift({ tipo: ref[i - 1] === hip[j - 1] ? 'igual' : 'sustitucion', guion: ref[i - 1], transcripcion: hip[j - 1] });
      i -= 1;
      j -= 1;
    } else if (i > 0 && d[i][j] === d[i - 1][j] + 1) {
      alineacion.unshift({ tipo: 'borrado', guion: ref[i - 1] });
      i -= 1;
    } else {
      alineacion.unshift({ tipo: 'insercion', transcripcion: hip[j - 1] });
      j -= 1;
    }
  }
  const cuenta = (tipo: TipoDePaso) => alineacion.filter((p) => p.tipo === tipo).length;
  const errores = n === 0 ? m : d[n][m];
  return {
    valor: n === 0 ? (m === 0 ? 0 : 1) : errores / n,
    sustituciones: cuenta('sustitucion'),
    borrados: cuenta('borrado'),
    inserciones: cuenta('insercion'),
    palabrasDelGuion: n,
    alineacion,
  };
}

// ─────────────────────────── 3. Frases obligatorias y prohibidas ───────────────────────────
export function frasesDichas(textoDelAgente: string, frases: FraseObligatoria[]): string[] {
  const t = normalizar(textoDelAgente);
  return frases.filter((f) => f.alternativas.some((alt) => contiene(t, alt))).map((f) => f.id);
}

export function prohibidasDichas(textoDelAgente: string, prohibidas: string[]): string[] {
  const t = normalizar(textoDelAgente);
  return prohibidas.filter((p) => contiene(t, p));
}

// ─────────────────────────── 4. Intención y datos ───────────────────────────
const MESES = 'enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre';
const FECHA = new RegExp(`\\b(\\d{1,2}) de (${MESES})\\b`, 'g');

/**
 * Reglas simples, en orden: la primera que encaja gana. Se aplican al texto DEL CLIENTE.
 * En un equipo real esto lo hace un clasificador (o el mismo agente); la prueba revisa que acierte.
 */
const REGLAS: { intencion: Intencion; patron: RegExp }[] = [
  { intencion: 'pide_una_persona', patron: /\b(hablar|comunicar\w*|pasar\w*|atender\w*) con (una persona|un asesor|una asesora|un humano|alguien)\b|\bno (quiero|voy a) (hablar|negociar) con una maquina\b/ },
  { intencion: 'no_reconoce_la_deuda', patron: /\bno reconozco\b|\bno es mia\b|\byo no debo\b|\bno debo nada\b|\bnunca he tenido\b|\bno tengo (ninguna )?deuda\b/ },
  { intencion: 'ya_pago', patron: /\bya (lo |la )?(pague|cancele|hice el pago|realice el pago|esta pagad[ao])\b/ },
  { intencion: 'promesa_de_pago', patron: new RegExp(`\\b(pago|pagare|pagar|le pago|abono|cancelo)\\b.*\\b\\d{1,2} de (${MESES})\\b`) },
];

export interface LecturaDeIntencion {
  intencion: Intencion;
  /** La frase que hizo encajar la regla: es la evidencia que se pone en el reporte. */
  evidencia: string | null;
}

export function leerIntencion(textoDelCliente: string): LecturaDeIntencion {
  const t = normalizar(textoDelCliente);
  for (const regla of REGLAS) {
    const encontrado = t.match(regla.patron);
    if (encontrado) return { intencion: regla.intencion, evidencia: encontrado[0] };
  }
  return { intencion: 'sin_intencion_clara', evidencia: null };
}

export function detectarIntencion(textoDelCliente: string): Intencion {
  return leerIntencion(textoDelCliente).intencion;
}

export interface DatosDeLaLlamada {
  monto: number | null;
  fecha: string | null;
}

/** El monto es el primero que se dice en pesos (lo dice el agente); la fecha, la última que dice el cliente. */
export function extraerDatos(textoCompleto: string, textoDelCliente: string): DatosDeLaLlamada {
  const monto = normalizar(textoCompleto).match(/\b(\d+) pesos\b/);
  const fechas = normalizar(textoDelCliente).match(FECHA) || normalizar(textoCompleto).match(FECHA) || [];
  return { monto: monto ? Number(monto[1]) : null, fecha: fechas.length ? fechas[fechas.length - 1] : null };
}

// ─────────────────────────── 5. Quién dijo qué ───────────────────────────
/** El texto de un hablante. Si el motor no separó las voces, se usa el texto completo. */
export function textoDe(transcripcion: Transcripcion, hablante: Hablante): string {
  const suyos = transcripcion.turnos.filter((t) => t.hablante === hablante);
  return suyos.length ? suyos.map((t) => t.texto).join(' ') : transcripcion.texto;
}

export function textoDelGuion(guion: Guion): string {
  return guion.turnos.map((t) => t.texto).join(' ');
}

// ─────────────────────────── 6. El informe completo de una llamada ───────────────────────────
export interface RevisionDeFrase {
  id: string;
  nombre: string;
  dicha: boolean;
}
export interface InformeDeLlamada {
  llamada: string;
  frases: RevisionDeFrase[];
  /** Los nombres de las frases obligatorias que el agente NO dijo. Vacío = cumple. */
  faltantes: string[];
  prohibidas: string[];
  ofreceAcuerdo: boolean;
  intencion: LecturaDeIntencion;
  datos: DatosDeLaLlamada;
  wer: ResultadoWer;
  umbralWer: number;
}

export function revisarLlamada(guion: Guion, transcripcion: Transcripcion, politica: Politica, umbralWer = politica.umbral_wer): InformeDeLlamada {
  const agente = textoDe(transcripcion, 'agente');
  const cliente = textoDe(transcripcion, 'cliente');
  const dichas = frasesDichas(agente, politica.frases);
  const frases = politica.frases.map((f) => ({ id: f.id, nombre: f.nombre, dicha: dichas.indexOf(f.id) >= 0 }));
  return {
    llamada: guion.id,
    frases,
    faltantes: frases.filter((f) => guion.esperado.frases.indexOf(f.id) >= 0 && !f.dicha).map((f) => f.nombre),
    prohibidas: prohibidasDichas(agente, politica.prohibidas),
    ofreceAcuerdo: dichas.indexOf('acuerdo') >= 0,
    intencion: leerIntencion(cliente),
    datos: extraerDatos(transcripcion.texto, cliente),
    wer: wer(textoDelGuion(guion), transcripcion.texto),
    umbralWer,
  };
}
