// KIT DE VOZ · Genera los audios SINTÉTICOS de los guiones y sus transcripciones.
//
//   npm run voz:generar                         las 6 llamadas de voz/guiones.json
//   npm run voz:generar -- --solo=CP-301        solo esa (o varias: --solo=CP-301,CP-306)
//   npm run voz:generar -- --frase "Le habla Lía, de Servicios Los Alisos"   una frase nueva (demo en vivo)
//   npm run voz:generar -- --motor=say          fuerza las voces de macOS (sin internet ni clave)
//   npm run voz:generar -- --forzar             vuelve a pedir a ElevenLabs aunque el guion no haya cambiado
//
// Motor:
//   - Con ELEVENLABS_API_KEY en el .env: ElevenLabs (TTS para el audio y Scribe para transcribir).
//     Si una llamada no cambió desde la última vez, no se vuelve a pedir (no gasta créditos).
//   - Sin clave: voces de macOS (`say`) y ffmpeg. Sin STT, la transcripción es el guion
//     (con los errores sembrados de la llamada con ruido). El archivo dice cuál motor se usó.
//
// Deja: voz/audios/*.mp3 y voz/transcripciones.json (con el motor y la fecha).
// La clave NUNCA se imprime ni se escribe en ningún archivo. Sin dependencias nuevas: Node 22 (fetch, FormData).
// Solo audio sintético de guiones ficticios: nunca llamadas reales (Ley 1581; la voz es un dato biométrico).
const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');
const { spawnSync } = require('child_process');

const RAIZ = path.join(__dirname, '..');
const VOZ = path.join(RAIZ, 'voz');
const AUDIOS = path.join(VOZ, 'audios');
const SALIDA = path.join(VOZ, 'transcripciones.json');
const API = 'https://api.elevenlabs.io/v1';

// ---------- El .env, leído a mano (sin dependencias). La terminal manda sobre el archivo. ----------
function leerEnv() {
  const valores = {};
  const archivo = path.join(RAIZ, '.env');
  if (!fs.existsSync(archivo)) return valores;
  for (const linea of fs.readFileSync(archivo, 'utf8').split(/\r?\n/)) {
    const m = linea.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/);
    if (!m || linea.trim().startsWith('#')) continue;
    valores[m[1]] = m[2].replace(/^(['"])(.*)\1$/, '$2');
  }
  return valores;
}
const env = { ...leerEnv(), ...Object.fromEntries(Object.entries(process.env).filter(([, v]) => v !== '')) };
const CLAVE = env.ELEVENLABS_API_KEY || '';

// ---------- Argumentos ----------
const args = process.argv.slice(2);
const opcion = (nombre) => {
  const i = args.findIndex((a) => a === `--${nombre}` || a.startsWith(`--${nombre}=`));
  if (i < 0) return undefined;
  return args[i].includes('=') ? args[i].split('=').slice(1).join('=') : args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
};
const motorPedido = opcion('motor');
const MOTOR = motorPedido === 'say' ? 'say' : motorPedido === 'elevenlabs' || CLAVE ? 'elevenlabs' : 'say';
if (MOTOR === 'elevenlabs' && !CLAVE) {
  console.error('Pediste --motor=elevenlabs, pero ELEVENLABS_API_KEY está vacía en el .env.');
  process.exit(1);
}
const FORZAR = Boolean(opcion('forzar'));
const SOLO = typeof opcion('solo') === 'string' ? opcion('solo').split(',').map((s) => s.trim().toUpperCase()) : null;
const FRASE = typeof opcion('frase') === 'string' ? opcion('frase') : null;

const VOCES = {
  elevenlabs: {
    // Voces colombianas de la biblioteca de ElevenLabs (acento colombiano, conversacionales). Se cambian en el .env.
    agente: env.ELEVENLABS_VOZ_AGENTE || 'kd5kUGaa17tlaf9G7ZXj', // «Valentina», cálida y clara: la asistente Lía
    cliente_mujer: env.ELEVENLABS_VOZ_CLIENTA || 'HQkNMSvU4RYxL7ghM0Pa', // «Vivi», natural: las señoras
    cliente_hombre: env.ELEVENLABS_VOZ_CLIENTE || 'k1LcwPlB8fqtr2BOqzNo', // «Edinson», calmado: los señores
  },
  say: {
    agente: env.SAY_VOZ_AGENTE || 'Paulina',
    cliente_mujer: env.SAY_VOZ_CLIENTA || 'Paulina',
    cliente_hombre: env.SAY_VOZ_CLIENTE || 'Eddy (Spanish (Mexico))',
  },
};
const MODELO_TTS = env.ELEVENLABS_MODELO_TTS || 'eleven_multilingual_v2';
const MODELO_STT = env.ELEVENLABS_MODELO_STT || 'scribe_v2';

// ---------- El oráculo: el MISMO src/voz/oraculo.ts, compilado aquí con el TypeScript del repo ----------
function cargarOraculo() {
  const ts = require('typescript');
  const fuente = fs.readFileSync(path.join(RAIZ, 'src', 'voz', 'oraculo.ts'), 'utf8');
  const js = ts.transpileModule(fuente, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
  const modulo = { exports: {} };
  new Function('exports', 'module', js)(modulo.exports, modulo);
  return modulo.exports;
}

// ---------- Herramientas ----------
const hayFfmpeg = () => spawnSync('ffmpeg', ['-version'], { stdio: 'ignore' }).status === 0;
const temporal = fs.mkdtempSync(path.join(os.tmpdir(), 'knot-voz-'));
process.on('exit', () => fs.rmSync(temporal, { recursive: true, force: true }));

function correr(comando, argumentos) {
  const r = spawnSync(comando, argumentos, { encoding: 'utf8' });
  if (r.status !== 0) throw new Error(`${comando} falló: ${(r.stderr || r.error || '').toString().slice(0, 300)}`);
}

/** Une los turnos con una pausa corta. La llamada con ruido pasa por un filtro de línea telefónica. */
function unirTurnos(archivos, destino, conRuido) {
  if (!hayFfmpeg()) {
    if (MOTOR === 'say') throw new Error('Sin ffmpeg no se puede convertir el audio de say a mp3. Instálalo o usa ElevenLabs.');
    // Los mp3 de ElevenLabs (mismo formato) se pueden pegar uno tras otro; sin pausa y sin ruido.
    fs.writeFileSync(destino, Buffer.concat(archivos.map((a) => fs.readFileSync(a))));
    return;
  }
  const entradas = archivos.flatMap((a) => ['-i', a]);
  const partes = archivos.map((_, i) => `[${i}:a]aresample=22050,aformat=channel_layouts=mono,apad=pad_dur=0.45[a${i}]`);
  let filtro = `${partes.join(';')};${archivos.map((_, i) => `[a${i}]`).join('')}concat=n=${archivos.length}:v=0:a=1[c]`;
  if (conRuido) {
    filtro += ';[c]highpass=f=300,lowpass=f=3400[v];anoisesrc=color=pink:amplitude=0.05:sample_rate=22050[n];[v][n]amix=inputs=2:duration=first:normalize=0[o]';
  } else {
    filtro += ';[c]anull[o]';
  }
  correr('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...entradas, '-filter_complex', filtro, '-map', '[o]', '-c:a', 'libmp3lame', '-b:a', '64k', destino]);
}

async function errorDeApi(respuesta) {
  // Se muestra el código y el mensaje de la API (nunca la clave, que solo va en la cabecera).
  const cuerpo = (await respuesta.text()).slice(0, 300);
  return new Error(`ElevenLabs respondió ${respuesta.status}: ${cuerpo}`);
}

async function hablarElevenLabs(texto, voz, destino) {
  const respuesta = await fetch(`${API}/text-to-speech/${voz}?output_format=mp3_44100_64`, {
    method: 'POST',
    headers: { 'xi-api-key': CLAVE, 'Content-Type': 'application/json', Accept: 'audio/mpeg' },
    body: JSON.stringify({ text: texto, model_id: MODELO_TTS, voice_settings: { stability: 0.5, similarity_boost: 0.75 } }),
  });
  if (!respuesta.ok) throw await errorDeApi(respuesta);
  fs.writeFileSync(destino, Buffer.from(await respuesta.arrayBuffer()));
}

function hablarSay(texto, voz, destino) {
  correr('say', ['-v', voz, '-r', '175', '-o', destino, texto]);
}

/** Igual que turnosDesdePalabras() de src/screenplay/voz/UsarElAgenteDeVoz.ts: el primero que habla es el agente. */
function turnosDesdePalabras(palabras) {
  const roles = new Map();
  const turnos = [];
  for (const p of palabras) {
    if (p.type === 'audio_event') continue;
    const id = p.speaker_id || 'sin_voz';
    if (!roles.has(id)) roles.set(id, roles.size === 0 ? 'agente' : roles.size === 1 ? 'cliente' : 'desconocido');
    const hablante = roles.get(id);
    const ultimo = turnos[turnos.length - 1];
    if (ultimo && ultimo.hablante === hablante) ultimo.texto += p.text;
    else if (p.type === 'word') turnos.push({ hablante, texto: p.text });
  }
  return turnos.map((t) => ({ hablante: t.hablante, texto: t.texto.trim() }));
}

async function transcribirElevenLabs(archivo, hablantes = 2) {
  const formulario = new FormData();
  formulario.append('file', new Blob([fs.readFileSync(archivo)], { type: 'audio/mpeg' }), path.basename(archivo));
  formulario.append('model_id', MODELO_STT);
  formulario.append('language_code', 'spa');
  formulario.append('diarize', hablantes > 1 ? 'true' : 'false');
  if (hablantes > 1) formulario.append('num_speakers', String(hablantes));
  formulario.append('tag_audio_events', 'false');
  formulario.append('timestamps_granularity', 'word');
  const respuesta = await fetch(`${API}/speech-to-text`, { method: 'POST', headers: { 'xi-api-key': CLAVE }, body: formulario });
  if (!respuesta.ok) throw await errorDeApi(respuesta);
  const datos = await respuesta.json();
  return { texto: datos.text.trim(), turnos: turnosDesdePalabras(datos.words || []) };
}

/** Sin STT: el texto es el guion, con los errores sembrados si la llamada los tiene. */
function transcripcionSimulada(guion) {
  const turnos = guion.turnos.map((t) => ({ hablante: t.hablante, texto: t.texto }));
  for (const e of guion.errores_simulados || []) {
    if (!turnos[e.turno] || !turnos[e.turno].texto.includes(e.de)) throw new Error(`${guion.id}: el error simulado «${e.de}» no está en el turno ${e.turno}`);
    turnos[e.turno].texto = turnos[e.turno].texto.replace(e.de, e.a);
  }
  return { texto: turnos.map((t) => t.texto).join(' '), turnos };
}

const huella = (guion) =>
  crypto.createHash('sha1').update(JSON.stringify({ turnos: guion.turnos, cliente_voz: guion.cliente_voz, ruido: !!guion.ruido, motor: MOTOR, voces: VOCES[MOTOR], MODELO_TTS, MODELO_STT })).digest('hex').slice(0, 12);

async function generarAudio(guion, destino) {
  const piezas = [];
  for (const [i, turno] of guion.turnos.entries()) {
    // El cliente habla con la voz de su género (cliente_voz en guiones.json: «mujer» u «hombre»).
    const voz = VOCES[MOTOR][turno.hablante === 'cliente' ? `cliente_${guion.cliente_voz || 'hombre'}` : turno.hablante];
    const pieza = path.join(temporal, `${guion.id}-${i}.${MOTOR === 'say' ? 'aiff' : 'mp3'}`);
    if (MOTOR === 'say') hablarSay(turno.texto, voz, pieza);
    else await hablarElevenLabs(turno.texto, voz, pieza);
    piezas.push(pieza);
  }
  unirTurnos(piezas, destino, guion.ruido);
}

const pct = (x) => `${(x * 100).toFixed(1)} %`;

// ---------- Una frase nueva (demo en vivo) ----------
async function frase(texto) {
  const oraculo = cargarOraculo();
  const carpeta = path.join(VOZ, 'demo');
  fs.mkdirSync(carpeta, { recursive: true });
  const audio = path.join(carpeta, 'frase.mp3');
  const pieza = path.join(temporal, `frase.${MOTOR === 'say' ? 'aiff' : 'mp3'}`);
  console.log(`Motor: ${MOTOR === 'say' ? 'say (macOS)' : `ElevenLabs (${MODELO_TTS} + ${MODELO_STT})`}`);
  console.log(`Guion:          ${texto}`);
  if (MOTOR === 'say') hablarSay(texto, VOCES.say.agente, pieza);
  else await hablarElevenLabs(texto, VOCES.elevenlabs.agente, pieza);
  unirTurnos([pieza], audio, Boolean(opcion('ruido')));
  console.log(`Audio:          ${path.relative(RAIZ, audio)}`);
  if (MOTOR === 'say') {
    console.log('Sin clave de ElevenLabs no hay STT: el audio quedó hecho, pero no se puede transcribir.');
    return;
  }
  const t = await transcribirElevenLabs(audio, 1);
  const r = oraculo.wer(texto, t.texto);
  console.log(`Transcripción:  ${t.texto}`);
  console.log(`WER:            ${pct(r.valor)} (${r.sustituciones} cambiadas, ${r.borrados} borradas, ${r.inserciones} de más, sobre ${r.palabrasDelGuion} palabras)`);
  for (const p of r.alineacion.filter((x) => x.tipo !== 'igual')) console.log(`  - ${p.tipo}: «${p.guion || ''}» → «${p.transcripcion || ''}»`);
  const leida = oraculo.leerIntencion(t.texto);
  console.log(`Intención:      ${leida.intencion}${leida.evidencia ? ` («${leida.evidencia}»)` : ''}`);
}

// ---------- Las llamadas de los guiones ----------
async function llamadas() {
  const oraculo = cargarOraculo();
  const { politica, llamadas: guiones } = JSON.parse(fs.readFileSync(path.join(VOZ, 'guiones.json'), 'utf8'));
  const anterior = fs.existsSync(SALIDA) ? JSON.parse(fs.readFileSync(SALIDA, 'utf8')) : { llamadas: {} };
  // Si cambia el motor, se rehacen todas para que el archivo no mezcle motores.
  const mismoMotor = anterior.motor_id === MOTOR;
  const solo = mismoMotor ? SOLO : null;
  if (SOLO && !mismoMotor) console.log(`Cambió el motor (antes: ${anterior.motor_id || 'ninguno'}): se rehacen las ${guiones.length} llamadas.`);
  fs.mkdirSync(AUDIOS, { recursive: true });
  let generadas = 0;

  const resultado = {
    _que_es: 'Transcripciones de los audios SINTÉTICOS de voz/guiones.json. Las lee TranscriptorDeArchivo (src/screenplay/voz/UsarElAgenteDeVoz.ts). Las genera: npm run voz:generar',
    motor_id: MOTOR,
    motor: MOTOR === 'say'
      ? 'say (macOS) · sin STT: la transcripción es el guion, con los errores sembrados de la llamada con ruido'
      : `ElevenLabs · TTS ${MODELO_TTS} · STT ${MODELO_STT}`,
    fecha: new Date().toISOString(),
    llamadas: {},
  };

  for (const g of guiones) {
    const previa = mismoMotor ? anterior.llamadas[g.id] : undefined;
    const destino = path.join(AUDIOS, g.audio);
    const h = huella(g);
    const pedida = !solo || solo.includes(g.id);
    const reutilizable = previa && fs.existsSync(destino) && (previa.huella === h || !pedida);
    if (reutilizable && !(FORZAR && pedida) && !(MOTOR === 'say' && pedida)) {
      resultado.llamadas[g.id] = previa;
      console.log(`= ${g.id}  sin cambios (no se vuelve a pedir)`);
      continue;
    }
    if (!pedida) {
      if (previa) resultado.llamadas[g.id] = previa;
      continue;
    }
    process.stdout.write(`+ ${g.id}  ${g.caso}... `);
    await generarAudio(g, destino);
    const t = MOTOR === 'say' ? transcripcionSimulada(g) : await transcribirElevenLabs(destino);
    resultado.llamadas[g.id] = { audio: `voz/audios/${g.audio}`, huella: h, texto: t.texto, turnos: t.turnos };
    generadas += 1;
    console.log('listo');
  }
  if (!generadas && anterior.fecha) resultado.fecha = anterior.fecha;
  fs.writeFileSync(SALIDA, JSON.stringify(resultado, null, 2) + '\n');

  // Resumen con el mismo oráculo de las pruebas.
  console.log(`\nMotor: ${resultado.motor}`);
  console.log('Llamada  WER      Intención               Monto    Fecha            Faltan');
  for (const g of guiones) {
    const t = resultado.llamadas[g.id];
    if (!t) continue;
    const inf = oraculo.revisarLlamada(g, { llamada: g.id, motor: MOTOR, texto: t.texto, turnos: t.turnos }, politica);
    console.log(`${g.id.padEnd(9)}${pct(inf.wer.valor).padEnd(9)}${inf.intencion.intencion.padEnd(24)}${String(inf.datos.monto).padEnd(9)}${String(inf.datos.fecha).padEnd(17)}${inf.faltantes.join(', ') || '-'}`);
  }
  console.log(`\nListo: ${path.relative(RAIZ, SALIDA)} y ${path.relative(RAIZ, AUDIOS)}/. Ahora: npx playwright test --project=voz`);
}

(FRASE ? frase(FRASE) : llamadas()).catch((error) => {
  console.error(`\nNo se pudo generar: ${error.message}`);
  if (/fetch failed|ENOTFOUND|ECONNREFUSED|ETIMEDOUT/.test(String(error.message) + String(error.cause))) {
    console.error('Parece que no hay internet. Plan B: las transcripciones que ya están en voz/ siguen sirviendo (npx playwright test --project=voz).');
  }
  process.exit(1);
});
