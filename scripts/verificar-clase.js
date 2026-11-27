// Revisa todo el repo con UN comando: corre las pruebas y muestra una tabla con
// las pruebas base, los retos (pendientes o resueltos) y los hallazgos esperados.
//
// Uso:
//   npm run verificar-clase                      detecta el estado por los PENDIENTE
//   npm run verificar-clase -- s06-inicio        exige exactamente el estado de esa etiqueta
//   npm run verificar-clase -- --proyectos=ui,unidad   corre solo esos proyectos
//   npm run verificar-clase -- --proyectos=triage      S9 · los rojos a propósito: se muestran aparte, no son problemas
//
// Termina con código 0 si el estado es el esperado y con 1 si hay algo que revisar.
// S9 · Una prueba FLAKY (falló y pasó al reintentar) no cuenta como verde: cuenta como ALERTA y el resumen lo dice.
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const RAIZ = path.join(__dirname, '..');
const RESULTADOS = path.join(RAIZ, 'resultados.json');

const RETOS = {
  S3: {
    1: 'PaginaLogin.ingresar',
    2: 'PaginaOtp.validar',
    3: 'PaginaTransferir.transferir',
    4: 'ClienteBanco.transferir',
    5: 'iniciarSesionPorUi',
  },
  S4: {
    1: 'SRP · separar AyudanteTodo',
    2: 'OCP · reglas de costo y cuenta Nómina',
    3: 'LSP · corregir la jerarquía de páginas',
    4: 'ISP · interfaces pequeñas',
    5: 'DIP · Cliente y ClienteFalso',
  },
  S5: {
    1: 'Factory · fábrica de transferencias',
    2: 'Screenplay · tarea Recargar (extra)',
  },
  S6: {
    1: 'Ambientes · producción bloqueada',
    2: 'Localizadores · la página heredada',
  },
};

// Bugs sembrados a propósito en el Banco Demo. Las pruebas los esperan: no se corrigen.
const HALLAZGOS = {
  'BUG-01': { texto: 'el monto exacto de $1.000 se rechaza', necesita: 'reto 3 de la S3' },
  'BUG-02': { texto: 'desde Corriente no se descuenta el 4x1000 del saldo', necesita: 'reto 4 de la S3' },
  'BUG-03': { texto: '"BLOQUEADO" en mayúsculas puede entrar', necesita: null },
  'MIG-01': { texto: 'en /api/v2/cuentas la cuenta Corriente dice "Ahorros"', necesita: null },
  'BUG-04': { texto: 'si el operador no responde, igual se descuenta el saldo de la recarga', necesita: null },
  // Kit de voz · sembrado en el guion del agente de voz (voz/guiones.json, CP-305), no en el Banco Demo.
  'VOZ-01': { texto: 'el agente de voz no avisa que la llamada se graba (CP-305)', necesita: null },
};
const TODOS = Object.keys(HALLAZGOS);
// Hasta la S4 no existían las recargas (BUG-04) ni el kit de voz (VOZ-01).
const HASTA_S4 = TODOS.filter((id) => id !== 'BUG-04' && id !== 'VOZ-01');

// Lo que debe pasar en cada etiqueta del repo.
const ESTADOS = {
  's03-inicio': { pendientes: { S3: [1, 2, 3, 4, 5], S4: [], S5: [], S6: [] }, retosS04: false, retosS05: false, retosS06: false, confirmados: ['BUG-03', 'MIG-01'] },
  's03-solucion': { pendientes: { S3: [], S4: [], S5: [], S6: [] }, retosS04: false, retosS05: false, retosS06: false, confirmados: HASTA_S4 },
  's04-inicio': { pendientes: { S3: [], S4: [1, 2, 3, 4, 5], S5: [], S6: [] }, retosS04: true, retosS05: false, retosS06: false, confirmados: HASTA_S4 },
  's04-solucion': { pendientes: { S3: [], S4: [], S5: [], S6: [] }, retosS04: true, retosS05: false, retosS06: false, confirmados: HASTA_S4 },
  's05-inicio': { pendientes: { S3: [], S4: [], S5: [1, 2], S6: [] }, retosS04: true, retosS05: true, retosS06: false, confirmados: TODOS },
  's05-solucion': { pendientes: { S3: [], S4: [], S5: [], S6: [] }, retosS04: true, retosS05: true, retosS06: false, confirmados: TODOS },
  // S6 · Llega con los retos de la S5 ya resueltos (como la S5 llegó con los de la S4).
  's06-inicio': { pendientes: { S3: [], S4: [], S5: [], S6: [1, 2] }, retosS04: true, retosS05: true, retosS06: true, confirmados: TODOS },
  's06-solucion': { pendientes: { S3: [], S4: [], S5: [], S6: [] }, retosS04: true, retosS05: true, retosS06: true, confirmados: TODOS },
  // S7 · Gherkin no agrega retos de código (la práctica es el escenario y el mapeo): las pruebas quedan como en la S6.
  's07-inicio': { pendientes: { S3: [], S4: [], S5: [], S6: [1, 2] }, retosS04: true, retosS05: true, retosS06: true, confirmados: TODOS },
  's07-solucion': { pendientes: { S3: [], S4: [], S5: [], S6: [1, 2] }, retosS04: true, retosS05: true, retosS06: true, confirmados: TODOS },
  // S8 · Una prueba, muchos datos: tampoco hay retos de código. Entra una prueba BASE, tests/recargas/CP-104-limites.spec.ts
  // (un test() por fila de la tabla). En la solución están además las de las otras 4 salas (CP-101, 103, 105 y 107).
  's08-inicio': { pendientes: { S3: [], S4: [], S5: [], S6: [1, 2] }, retosS04: true, retosS05: true, retosS06: true, ddtS08: 'inicio', confirmados: TODOS },
  's08-solucion': { pendientes: { S3: [], S4: [], S5: [], S6: [1, 2] }, retosS04: true, retosS05: true, retosS06: true, ddtS08: 'solucion', confirmados: TODOS },
  // S9 · Triage de fallas: tampoco hay retos de código (la práctica es clasificar rojos). Entran tests/triage-s09/ (el proyecto
  // «triage», que solo corre si se pide: no está en esta corrida) y src/soporte/registro.ts. Inicio y solución quedan iguales.
  's09-inicio': { pendientes: { S3: [], S4: [], S5: [], S6: [1, 2] }, retosS04: true, retosS05: true, retosS06: true, ddtS08: 'inicio', triageS09: true, confirmados: TODOS },
  's09-solucion': { pendientes: { S3: [], S4: [], S5: [], S6: [1, 2] }, retosS04: true, retosS05: true, retosS06: true, ddtS08: 'inicio', triageS09: true, confirmados: TODOS },
};
// S8 · Las pruebas de datos: la del mírame (siempre desde la S8) y las de las salas (solo en la solución).
const DDT_S08 = path.join(RAIZ, 'tests', 'recargas', 'CP-104-limites.spec.ts');
const DDT_S08_SALAS = ['CP-101-sin-codigo', 'CP-103-celulares', 'CP-105-limite-diario', 'CP-107-operadores']
  .map((nombre) => path.join(RAIZ, 'tests', 'recargas', `${nombre}.spec.ts`));
// S9 · El triage: los rojos a propósito (proyecto «triage») y el registro de la corrida.
const TRIAGE_S09 = [path.join(RAIZ, 'tests', 'triage-s09'), path.join(RAIZ, 'src', 'soporte', 'registro.ts')];

// ---------- Argumentos ----------
const argumentos = process.argv.slice(2);
const pedido = argumentos.find((a) => !a.startsWith('--'));
const proyectos = (argumentos.find((a) => a.startsWith('--proyectos=')) || '').replace('--proyectos=', '').split(',').filter(Boolean);
const verSalida = argumentos.includes('--ver');
if (pedido && !ESTADOS[pedido]) {
  console.log(`Estado desconocido: ${pedido}. Usa uno de: ${Object.keys(ESTADOS).join(', ')}`);
  process.exit(1);
}

// ---------- Colores (solo en una terminal) ----------
const conColor = process.stdout.isTTY && !process.env.NO_COLOR;
const pintar = (codigo) => (t) => (conColor ? `\u001b[${codigo}m${t}\u001b[0m` : String(t));
const verde = pintar('32');
const rojo = pintar('31');
const amarillo = pintar('33');
const azul = pintar('36');
const negrita = pintar('1');
// Una etiqueta de estado de ancho fijo, para que la tabla quede alineada.
const etiqueta = (texto, color) => color(texto.padEnd(13));

// ---------- 1. Correr las pruebas ----------
console.log(negrita('Verificación de clase'));
console.log(`Corriendo las pruebas${proyectos.length ? ` de: ${proyectos.join(', ')}` : ''}. Tarda menos de un minuto...`);
fs.rmSync(RESULTADOS, { force: true });
const cli = require.resolve('@playwright/test/cli', { paths: [RAIZ] });
const corrida = spawnSync(process.execPath, [cli, 'test', ...proyectos.map((p) => `--project=${p}`)], {
  cwd: RAIZ,
  encoding: 'utf8',
  env: { ...process.env, PLAYWRIGHT_HTML_OPEN: 'never', FORCE_COLOR: '0' },
  maxBuffer: 64 * 1024 * 1024,
});
if (verSalida) console.log(corrida.stdout, corrida.stderr);
if (!fs.existsSync(RESULTADOS)) {
  console.log(rojo('No se generó resultados.json. Esto dijo Playwright:'));
  console.log(corrida.stdout, corrida.stderr);
  process.exit(1);
}

// ---------- 2. Clasificar cada prueba ----------
const sinColores = (t) => String(t || '').replace(/\u001b\[[0-9;]*m/g, '');
const reporte = JSON.parse(fs.readFileSync(RESULTADOS, 'utf8'));
const pruebas = [];

function recorrer(suite, archivo) {
  const nombre = suite.file || archivo;
  for (const spec of suite.specs || []) {
    for (const prueba of spec.tests) {
      const resultado = prueba.results[prueba.results.length - 1] || {};
      const error = sinColores([resultado.error?.message, ...(resultado.errors || []).map((e) => e.message)].join('\n'));
      const anotaciones = [...(prueba.annotations || []), ...(resultado.annotations || [])];
      const hallazgo = anotaciones.find((a) => a.type === 'hallazgo');
      const pendiente = error.match(/PENDIENTE \((S\d)\)[^\n]*?reto (\d)/);
      const carpeta = nombre.split('/')[1] || '';
      const retoDelArchivo = path.basename(nombre).match(/^reto(\d)/);

      let tipo;
      if (prueba.status === 'skipped') tipo = 'omitida';
      else if (pendiente) tipo = 'pendiente';
      else if (hallazgo) tipo = prueba.status === 'expected' ? 'hallazgo' : 'alerta';
      // S9 · flaky = falló y pasó al reintentar. NO es un verde: es una alerta que hay que investigar.
      else if (prueba.status === 'flaky') tipo = 'flaky';
      else tipo = prueba.status === 'expected' ? 'verde' : 'rojo';

      pruebas.push({
        archivo: nombre.replace(/^tests\//, '').replace(/\.spec\.ts$/, ''),
        carpeta,
        titulo: spec.title,
        tipo,
        error: error.split('\n').find((l) => l.trim()) || '',
        hallazgo: hallazgo ? hallazgo.description.split(':')[0] : null,
        intentos: prueba.results.length,
        sesion: { 'retos-s03': 'S3', 'retos-s04': 'S4', 'retos-s05': 'S5', 'retos-s06': 'S6' }[carpeta] || null,
        reto: retoDelArchivo ? Number(retoDelArchivo[1]) : null,
        pendienteDe: pendiente ? { sesion: pendiente[1], reto: Number(pendiente[2]) } : null,
      });
    }
  }
  for (const hija of suite.suites || []) recorrer(hija, nombre);
}
reporte.suites.forEach((suite) => recorrer(suite));

const problemas = [];
for (const e of reporte.errors || []) problemas.push(`Error al cargar las pruebas: ${sinColores(e.message).split('\n')[0]}`);
if (!pruebas.length) problemas.push('No se ejecutó ninguna prueba.');

// ---------- 3. Pruebas base: todo lo que no es reto ni hallazgo ----------
const linea = () => console.log('-'.repeat(78));
const columna = (t, n) => String(t).padEnd(n);
console.log('');
console.log(negrita('PRUEBAS BASE') + ' (deben estar en verde)');
linea();
// S9 · Los rojos del triage (tests/triage-s09) fallan a propósito: van en su propia tabla, más abajo.
const esTriage = (p) => p.carpeta === 'triage-s09';
const base = pruebas.filter((p) => !p.sesion && !esTriage(p) && p.tipo !== 'hallazgo' && p.tipo !== 'alerta');
const porArchivo = new Map();
for (const p of base) porArchivo.set(p.archivo, [...(porArchivo.get(p.archivo) || []), p]);
for (const [archivo, lista] of porArchivo) {
  const bien = lista.filter((p) => p.tipo === 'verde').length;
  const hayRojo = lista.some((p) => p.tipo !== 'verde' && p.tipo !== 'flaky');
  const estado = bien === lista.length ? etiqueta('OK', verde) : hayRojo ? etiqueta('FALLA', rojo) : etiqueta('ALERTA', amarillo);
  console.log(`${estado}${columna(archivo, 40)}${bien}/${lista.length} en verde`);
  for (const p of lista.filter((x) => x.tipo === 'flaky')) {
    console.log(amarillo(`        - ${p.titulo}: FLAKY, pasó en el intento ${p.intentos}. No es un verde: abre un ticket.`));
  }
  for (const p of lista.filter((x) => x.tipo !== 'verde' && x.tipo !== 'flaky')) {
    console.log(rojo(`        - ${p.titulo}: ${p.error.slice(0, 120)}`));
    problemas.push(`Prueba base en rojo: ${p.archivo} › ${p.titulo}`);
  }
}

// ---------- 4. Retos ----------
const pendientesPorSesion = { S3: new Set(), S4: new Set(), S5: new Set(), S6: new Set() };
for (const p of pruebas) if (p.pendienteDe) pendientesPorSesion[p.pendienteDe.sesion].add(p.pendienteDe.reto);
const hayRetosS04 = fs.existsSync(path.join(RAIZ, 'tests', 'retos-s04'));
const hayRetosS05 = fs.existsSync(path.join(RAIZ, 'tests', 'retos-s05'));
const hayRetosS06 = fs.existsSync(path.join(RAIZ, 'tests', 'retos-s06'));
const corrioSesion = (sesion) => pruebas.some((p) => p.sesion === sesion);
const resueltosPorSesion = { S3: 0, S4: 0, S5: 0, S6: 0 };

for (const sesion of ['S3', 'S4', 'S5', 'S6']) {
  console.log('');
  console.log(negrita(`RETOS ${sesion}`));
  linea();
  if ((sesion === 'S4' && !hayRetosS04) || (sesion === 'S5' && !hayRetosS05) || (sesion === 'S6' && !hayRetosS06)) {
    console.log(azul(`Todavía no se han publicado (llegan con la etiqueta ${sesion.toLowerCase().replace('s', 's0')}-inicio).`));
    continue;
  }
  if (!corrioSesion(sesion)) {
    console.log(azul('No se corrieron en esta verificación.'));
    continue;
  }
  for (const [numero, nombre] of Object.entries(RETOS[sesion])) {
    const lista = pruebas.filter((p) => p.sesion === sesion && p.reto === Number(numero));
    if (!lista.length) continue;
    const enRojo = lista.filter((p) => p.tipo === 'rojo' || p.tipo === 'alerta');
    const flakyDelReto = lista.filter((p) => p.tipo === 'flaky');
    let estado;
    if (enRojo.length) estado = etiqueta('CON ERRORES', rojo);
    else if (flakyDelReto.length) estado = etiqueta('ALERTA', amarillo);
    else if (pendientesPorSesion[sesion].has(Number(numero))) estado = etiqueta('PENDIENTE', amarillo);
    else {
      estado = etiqueta('RESUELTO', verde);
      resueltosPorSesion[sesion] += 1;
    }
    console.log(`${estado}Reto ${numero} · ${columna(nombre, 42)}${lista.length} pruebas`);
    for (const p of flakyDelReto) console.log(amarillo(`            - ${p.titulo}: FLAKY, pasó en el intento ${p.intentos}. No es un verde.`));
    for (const p of enRojo) {
      console.log(rojo(`            - ${p.titulo}: ${p.error.slice(0, 120)}`));
      problemas.push(`Reto ${numero} de la ${sesion} con una prueba en rojo: ${p.titulo}`);
    }
  }
}

// ---------- 4b. S9 · Los rojos del triage (solo si se pidió --proyectos=triage) ----------
const delTriage = pruebas.filter(esTriage);
if (delTriage.length) {
  console.log('');
  console.log(negrita('TRIAGE S9') + ' (rojos a propósito: fallan para clasificarlos; no son problemas del repo)');
  linea();
  for (const p of delTriage) {
    const estado = p.tipo === 'omitida' ? etiqueta('APARTE', azul) : p.tipo === 'flaky' ? etiqueta('FLAKY', amarillo)
      : p.tipo === 'rojo' ? etiqueta('ROJO', rojo) : etiqueta('PASÓ', verde);
    const detalle = p.tipo === 'omitida' ? 'se corre con npm.cmd run triage:sin-clave'
      : p.tipo === 'flaky' ? `pasó en el intento ${p.intentos}: alerta, no verde` : p.tipo === 'rojo' ? p.error.slice(0, 90) : 'este rojo ya no falla: ¿lo arreglaste en tu repo (por ejemplo, el reto 2 de la S6)?';
    console.log(`${estado}${p.titulo.slice(0, 40).padEnd(42)}${detalle}`);
  }
}

// ---------- 5. Hallazgos esperados ----------
console.log('');
console.log(negrita('HALLAZGOS ESPERADOS') + ' (bugs sembrados a propósito: no se corrigen)');
linea();
const corridaCompleta = proyectos.length === 0;
const confirmados = new Set();
for (const [id, { texto, necesita }] of Object.entries(HALLAZGOS)) {
  const lista = pruebas.filter((p) => p.hallazgo === id);
  const confirmada = lista.find((p) => p.tipo === 'hallazgo');
  const alerta = lista.find((p) => p.tipo === 'alerta');
  const pendiente = lista.find((p) => p.tipo === 'pendiente');
  let estado;
  if (alerta) {
    estado = etiqueta('YA NO FALLA', rojo);
    problemas.push(`${id}: la prueba pasó. ¿Corrigieron el bug del Banco Demo? Los bugs sembrados no se corrigen.`);
  } else if (confirmada) {
    estado = etiqueta('CONFIRMADO', verde);
    confirmados.add(id);
  } else if (pendiente) {
    estado = etiqueta('ESPERA', amarillo);
  } else if (!corridaCompleta) {
    estado = etiqueta('NO SE CORRIÓ', azul);
  } else {
    estado = etiqueta('NO APARECE', rojo);
    problemas.push(`${id}: no hay ninguna prueba que lo detecte.`);
  }
  const donde = confirmada ? ` (${confirmada.archivo})` : pendiente && necesita ? ` (aparece al resolver el ${necesita})` : '';
  console.log(`${estado}${id}  ${texto}${donde}`);
}

// ---------- 6. Estado del repo ----------
const hayDdtS08 = fs.existsSync(DDT_S08);
const hayDdtS08Salas = DDT_S08_SALAS.every((archivo) => fs.existsSync(archivo));
const hayTriageS09 = TRIAGE_S09.every((archivo) => fs.existsSync(archivo));
let detectado;
// S9 no tiene retos de código: con el triage en el repo, inicio y solución se ven iguales (se detecta s09-inicio).
if (hayTriageS09) detectado = 's09-inicio';
else if (hayDdtS08) detectado = hayDdtS08Salas ? 's08-solucion' : 's08-inicio';
else if (hayRetosS06) detectado = pendientesPorSesion.S6.size ? 's06-inicio' : 's06-solucion';
else if (hayRetosS05) detectado = pendientesPorSesion.S5.size ? 's05-inicio' : 's05-solucion';
else if (hayRetosS04) detectado = pendientesPorSesion.S4.size ? 's04-inicio' : 's04-solucion';
else detectado = pendientesPorSesion.S3.size ? 's03-inicio' : 's03-solucion';
const esperado = pedido || detectado;

if (pedido && corridaCompleta) {
  const regla = ESTADOS[pedido];
  const lista = (s) => [...s].sort().join(', ') || 'ninguno';
  if (regla.retosS04 !== hayRetosS04) {
    problemas.push(regla.retosS04 ? 'Faltan los retos de la S4 (tests/retos-s04).' : 'Los retos de la S4 no deberían estar todavía.');
  }
  if (regla.retosS05 !== hayRetosS05) {
    problemas.push(regla.retosS05 ? 'Faltan los retos de la S5 (tests/retos-s05).' : 'Los retos de la S5 no deberían estar todavía.');
  }
  if (regla.retosS06 !== hayRetosS06) {
    problemas.push(regla.retosS06 ? 'Faltan los retos de la S6 (tests/retos-s06).' : 'Los retos de la S6 no deberían estar todavía.');
  }
  if (Boolean(regla.triageS09) !== hayTriageS09) {
    problemas.push(regla.triageS09 ? 'Falta el triage de la S9 (tests/triage-s09 y src/soporte/registro.ts).' : 'El triage de la S9 (tests/triage-s09) no debería estar todavía.');
  }
  if (regla.ddtS08 && !hayDdtS08) problemas.push('Falta la prueba de datos de la S8 (tests/recargas/CP-104-limites.spec.ts).');
  if (regla.ddtS08 === 'solucion' && !hayDdtS08Salas) problemas.push('Faltan las pruebas de datos de las salas de la S8 (CP-101, 103, 105 y 107 en tests/recargas/).');
  for (const sesion of ['S3', 'S4', 'S5', 'S6']) {
    const tiene = lista(pendientesPorSesion[sesion]);
    const debe = lista(regla.pendientes[sesion]);
    if (tiene !== debe) problemas.push(`Retos pendientes de la ${sesion}: hay [${tiene}] y en ${pedido} deben ser [${debe}].`);
  }
  const tiene = lista(confirmados);
  const debe = lista(regla.confirmados);
  if (tiene !== debe) problemas.push(`Hallazgos confirmados: hay [${tiene}] y en ${pedido} deben ser [${debe}].`);
}

// ---------- 7. Resumen ----------
const cuenta = (tipo) => pruebas.filter((p) => p.tipo === tipo).length;
const resueltos = (sesion) => resueltosPorSesion[sesion];
console.log('');
console.log(negrita('RESUMEN'));
linea();
if (corridaCompleta) {
  console.log(`Estado ${pedido ? 'pedido' : 'detectado'}: ${negrita(esperado)}${pedido && pedido !== detectado ? ` (el código parece ${detectado})` : ''}`);
} else {
  console.log(`Corrida parcial (${proyectos.join(', ')}): solo se revisa que no haya pruebas en rojo.`);
}
const enRojo = pruebas.filter((p) => !esTriage(p) && (p.tipo === 'rojo' || p.tipo === 'alerta')).length;
const flaky = pruebas.filter((p) => !esTriage(p) && p.tipo === 'flaky');
console.log(`Pruebas: ${pruebas.length} en total · ${cuenta('verde')} en verde · ${flaky.length} flaky (alerta) · ${cuenta('pendiente')} pendientes · ${cuenta('hallazgo')} hallazgos · ${enRojo} en rojo`);
if (flaky.length) console.log(amarillo(`Flaky: ${flaky.length} prueba(s) fallaron y pasaron al reintentar. No cuentan como verde: cada una es una alerta con ticket.`));
if (delTriage.length) console.log(`Triage S9: ${delTriage.filter((p) => p.tipo === 'rojo').length} rojos a propósito (no cuentan como problemas del repo).`);
if (corrioSesion('S3')) console.log(`Retos S3: ${resueltos('S3')} de 5 resueltos`);
if (hayRetosS04 && corrioSesion('S4')) console.log(`Retos S4: ${resueltos('S4')} de 5 resueltos`);
if (hayRetosS05 && corrioSesion('S5')) console.log(`Retos S5: ${resueltos('S5')} de 2 resueltos`);
if (hayRetosS06 && corrioSesion('S6')) console.log(`Retos S6: ${resueltos('S6')} de 2 resueltos`);
console.log(`Hallazgos confirmados: ${confirmados.size} de ${TODOS.length}`);
console.log('Detalle con pantallazos: npm run evidencias  ·  Reporte completo: npm run reporte');
console.log('');

if (process.env.GITHUB_STEP_SUMMARY) {
  fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, `## Verificación de clase: ${corridaCompleta ? esperado : 'corrida parcial'} ${problemas.length ? '🔴' : '🟢'}\n\n` +
    `| Base en verde | Flaky (alerta) | Pendientes | Hallazgos | En rojo |\n|---|---|---|---|---|\n` +
    `| ${cuenta('verde')} | ${flaky.length} | ${cuenta('pendiente')} | ${cuenta('hallazgo')} | ${enRojo} |\n\n` +
    (flaky.length ? flaky.map((p) => `- ⚠️ Flaky (pasó en el intento ${p.intentos}): ${p.archivo} › ${p.titulo}`).join('\n') + '\n\n' : '') +
    (problemas.length ? problemas.map((p) => `- ${p}`).join('\n') + '\n\n' : ''));
}

if (problemas.length) {
  console.log(rojo(negrita(`HAY ${problemas.length} COSA(S) QUE REVISAR:`)));
  for (const p of problemas) console.log(rojo(`  - ${p}`));
  process.exit(1);
}
if (flaky.length) {
  // Una alerta no rompe el pipeline, pero tampoco se llama «todo en orden»: se dice y se abre un ticket.
  console.log(amarillo(negrita(`EN ORDEN, CON ${flaky.length} ALERTA(S) FLAKY: no son un verde. Abre un ticket por cada una:`)));
  for (const p of flaky) console.log(amarillo(`  - ${p.archivo} › ${p.titulo} (pasó en el intento ${p.intentos})`));
  process.exit(0);
}
const fueraDelTriage = delTriage.length ? ' fuera de los rojos a propósito del triage' : '';
console.log(verde(negrita(corridaCompleta ? `TODO EN ORDEN: el repo está como se espera para ${esperado}.` : `TODO EN ORDEN: ninguna prueba en rojo${fueraDelTriage}.`)));
