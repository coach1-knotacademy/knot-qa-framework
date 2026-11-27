// S9 · La evidencia del triage, para quien no puede instalar (y para el instructor, antes de la clase).
//
// Uso:
//   npm run triage:generar     corre los rojos del triage, el flaky con --retries=1 y el rojo 3 (sin la clave), y deja:
//                                reportes/triage/index.html          el reporte HTML con los traces adentro (va a Pages)
//                                reportes/triage/traces/rojo1.zip…   cada trace con nombre (para trace.playwright.dev)
//                                reportes/triage/capturas/*.png      capturas numeradas: la acción, el error y la red
//                                reportes/triage/rojo3-consola.txt   lo que dice la consola del rojo 3 (no hay trace)
//   npm run triage:sin-clave   solo el rojo 3: el proyecto triage contra el ambiente qa, sin CLAVE_BANCO
//
// Las corridas se hacen en una COPIA del repo en la carpeta temporal del equipo: así el reporte publicado
// no lleva la ruta de tu computador, y tu repo no cambia. Si el reto 1 de la S6 está pendiente, el rojo 3 se
// corre con la solución de la S6 (si la tienes) para mostrar el mensaje real: «Falta CLAVE_BANCO…».
// Nunca corre en CI ni contra internet: solo el Banco Demo local.
const fs = require('fs');
const os = require('os');
const path = require('path');
const http = require('http');
const { spawnSync } = require('child_process');

const RAIZ = path.join(__dirname, '..');
const SALIDA = path.join(RAIZ, 'reportes', 'triage');
// La copia vive en una ruta neutra: los mensajes de error del reporte publicado muestran la ruta del archivo,
// y no debe verse la carpeta de nadie. En macOS y Linux, /tmp/knot-triage; en Windows, la carpeta temporal.
const COPIA = process.platform === 'win32'
  ? path.join(os.tmpdir(), 'knot-triage', 'knot-qa-framework')
  : path.join('/tmp', 'knot-triage', 'knot-qa-framework');
const A_COPIAR = ['playwright.config.ts', 'package.json', 'tsconfig.json', 'src', 'banco-demo', path.join('tests', 'triage-s09')];
const AMBIENTES = path.join('src', 'config', 'ambientes.ts');
const SOLUCION_S6 = path.join(RAIZ, 'laboratorio', 'generar', 's06_solucion', AMBIENTES);
// Playwright se copia también (unos 18 MB): si se enlazara, el trace guardaría la ruta del repo en tu equipo.
const PAQUETES = [path.join('@playwright', 'test'), 'playwright', 'playwright-core'];
const CLI = path.join(COPIA, 'node_modules', '@playwright', 'test', 'cli.js');

// Los rojos con nombre: el título empieza así (para -g) y así se llaman sus archivos de evidencia.
const ROJOS = [
  { id: 'rojo1', titulo: 'rojo 1 ·' },
  { id: 'rojo2', titulo: 'rojo 2 ·' },
  { id: 'rojo4', titulo: 'rojo 4 ·' },
  { id: 'flaky', titulo: 'flaky ·' },
];

const soloSinClave = process.argv.includes('--sin-clave');

// ---------- La copia aislada ----------
function borrarCopia() {
  fs.rmSync(path.dirname(COPIA), { recursive: true, force: true });
}

function armarCopia() {
  borrarCopia();
  fs.mkdirSync(COPIA, { recursive: true });
  for (const parte of A_COPIAR) fs.cpSync(path.join(RAIZ, parte), path.join(COPIA, parte), { recursive: true });
  for (const paquete of PAQUETES) {
    fs.cpSync(path.join(RAIZ, 'node_modules', paquete), path.join(COPIA, 'node_modules', paquete), { recursive: true, dereference: true });
  }
}

/** Corre la CLI de Playwright en la copia y devuelve lo que dijo la consola. */
function playwright(args, env = {}) {
  console.log(`\n> npx playwright ${args.join(' ')}`);
  const corrida = spawnSync(process.execPath, [CLI, ...args], {
    cwd: COPIA,
    encoding: 'utf8',
    env: { ...process.env, PLAYWRIGHT_HTML_OPEN: 'never', FORCE_COLOR: '0', ...env },
    maxBuffer: 64 * 1024 * 1024,
  });
  const salida = `${corrida.stdout || ''}${corrida.stderr || ''}`;
  return { codigo: corrida.status, salida };
}

/** La salida sin la ruta de la copia (rutas relativas al repo, como las verías en tu terminal). */
function sinRutas(texto) {
  // La carpeta temporal tiene dos nombres en macOS (/var/… y /private/var/…): se quitan los dos, y también la del repo.
  const rutas = [fs.existsSync(COPIA) ? fs.realpathSync(COPIA) : COPIA, COPIA, RAIZ];
  return rutas.reduce((t, ruta) => t.split(ruta + path.sep).join('').split(ruta).join('.'), texto);
}

// ---------- Rojo 3: sin la clave ----------
function rojo3() {
  const pendiente = fs.readFileSync(path.join(RAIZ, AMBIENTES), 'utf8').includes('PENDIENTE (S6)');
  if (pendiente && fs.existsSync(SOLUCION_S6)) {
    fs.copyFileSync(SOLUCION_S6, path.join(COPIA, AMBIENTES));
    console.log('\nTu reto 1 de la S6 está pendiente: el rojo 3 se corre con la solución de la S6, en una copia aparte (tu repo no cambia).');
  } else if (pendiente) {
    console.log('\nTu reto 1 de la S6 está pendiente: vas a ver «PENDIENTE (S6)…» en lugar del mensaje de la clave. Es el mismo freno, sin terminar.');
    console.log('Con el reto resuelto, la consola dice: Falta CLAVE_BANCO para el ambiente qa. Defínela en la terminal: $env:CLAVE_BANCO = \'...\'');
  }
  // AMBIENTE=qa y la clave VACÍA (no borrada): así tampoco la trae un .env. Vacía cuenta como que no está.
  const { codigo, salida } = playwright(['test', '--project=triage', '--reporter=list'], { AMBIENTE: 'qa', CLAVE_BANCO: '' });
  const limpia = sinRutas(salida);
  console.log(limpia);
  console.log(`(La corrida terminó con código ${codigo}: no corrió ninguna prueba, no hay trace ni reporte. La evidencia es esta consola.)`);
  return limpia;
}

if (soloSinClave) {
  try {
    armarCopia();
    rojo3();
  } finally {
    borrarCopia();
  }
  process.exit(0);
}

// ---------- 1. Los rojos y el flaky ----------
const BLOBS = path.join(COPIA, 'blobs');
const RESULTADOS = path.join(COPIA, 'resultados');

function correrTriage() {
  // Corrida 1: los rojos, con retries 0 (como todo el repo). El flaky va aparte.
  const r1 = playwright(['test', '--project=triage', '--grep-invert', 'flaky', '--reporter=list,blob,json', `--output=${path.join(RESULTADOS, 'rojos')}`], {
    PLAYWRIGHT_BLOB_OUTPUT_FILE: path.join(BLOBS, 'rojos.zip'),
    PLAYWRIGHT_JSON_OUTPUT_FILE: path.join(RESULTADOS, 'rojos.json'),
  });
  console.log(sinRutas(r1.salida).split('\n').filter((l) => /^\s+[✘✓-]\s+\d|^\s+\d+ (failed|passed|skipped|flaky)/.test(l)).join('\n'));
  // Corrida 2: el flaky, con --retries=1 a propósito: falla la primera vez y pasa al reintentar.
  const r2 = playwright(['test', '--project=triage', '-g', 'flaky', '--retries=1', '--reporter=list,blob,json', `--output=${path.join(RESULTADOS, 'flaky')}`], {
    PLAYWRIGHT_BLOB_OUTPUT_FILE: path.join(BLOBS, 'flaky.zip'),
    PLAYWRIGHT_JSON_OUTPUT_FILE: path.join(RESULTADOS, 'flaky.json'),
  });
  console.log(sinRutas(r2.salida).split('\n').filter((l) => /^\s+[✘✓-]\s+\d|^\s+\d+ (failed|passed|skipped|flaky)/.test(l)).join('\n'));
  if (!fs.existsSync(path.join(BLOBS, 'rojos.zip')) || !fs.existsSync(path.join(BLOBS, 'flaky.zip'))) {
    console.log(sinRutas(r1.salida + r2.salida));
    throw new Error('No se generaron los reportes de las corridas: mira la salida de arriba.');
  }
  // Un solo reporte HTML con las dos corridas.
  fs.rmSync(SALIDA, { recursive: true, force: true });
  const m = playwright(['merge-reports', '--reporter=html', BLOBS], { PLAYWRIGHT_HTML_OUTPUT_DIR: SALIDA });
  if (!fs.existsSync(path.join(SALIDA, 'index.html'))) {
    console.log(m.salida);
    throw new Error('No se generó el reporte HTML.');
  }
}

/** Los traces de cada prueba, sacados del resultado JSON de cada corrida. */
function traces() {
  const porPrueba = {};
  const recorrer = (suite) => {
    for (const spec of suite.specs || []) {
      for (const prueba of spec.tests) {
        porPrueba[spec.title] = prueba.results.map((r) => (r.attachments || []).find((a) => a.name === 'trace')?.path).filter(Boolean);
      }
    }
    for (const hija of suite.suites || []) recorrer(hija);
  };
  for (const archivo of ['rojos.json', 'flaky.json']) JSON.parse(fs.readFileSync(path.join(RESULTADOS, archivo), 'utf8')).suites.forEach(recorrer);

  const destino = path.join(SALIDA, 'traces');
  fs.mkdirSync(destino, { recursive: true });
  const copiados = {};
  for (const { id, titulo } of ROJOS) {
    const titulos = Object.keys(porPrueba).filter((t) => t.startsWith(titulo));
    if (titulos.length !== 1) throw new Error(`No encontré una sola prueba que empiece con «${titulo}» (encontré ${titulos.length}).`);
    const lista = porPrueba[titulos[0]];
    if (!lista.length) throw new Error(`La prueba «${titulos[0]}» no dejó trace.`);
    if (id === 'flaky') {
      // El flaky deja dos: el intento que falló y el reintento que pasó.
      lista.forEach((origen, i) => fs.copyFileSync(origen, path.join(destino, `flaky-intento${i + 1}.zip`)));
      copiados[id] = lista.map((_, i) => `flaky-intento${i + 1}.zip`);
    } else {
      fs.copyFileSync(lista[lista.length - 1], path.join(destino, `${id}.zip`));
      copiados[id] = [`${id}.zip`];
    }
  }
  return copiados;
}

// ---------- 2. Las capturas (la acción, el error y la red), con el visor del propio reporte ----------
function servir(carpeta) {
  const tipos = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.zip': 'application/zip', '.png': 'image/png', '.svg': 'image/svg+xml', '.json': 'application/json', '.ttf': 'font/ttf', '.webmanifest': 'application/manifest+json' };
  const servidor = http.createServer((req, res) => {
    const ruta = path.join(carpeta, decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!ruta.startsWith(carpeta) || !fs.existsSync(ruta) || fs.statSync(ruta).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': tipos[path.extname(ruta)] || 'application/octet-stream' });
    fs.createReadStream(ruta).pipe(res);
  });
  return new Promise((listo) => servidor.listen(0, '127.0.0.1', () => listo(servidor)));
}

async function capturas(textoRojo3) {
  const { chromium } = require(require.resolve('@playwright/test', { paths: [RAIZ] }));
  const destino = path.join(SALIDA, 'capturas');
  fs.mkdirSync(destino, { recursive: true });
  const servidor = await servir(SALIDA);
  const base = `http://127.0.0.1:${servidor.address().port}`;
  const navegador = await chromium.launch({ channel: process.env.PW_CHANNEL });
  const pagina = await navegador.newPage({ viewport: { width: 1400, height: 900 }, locale: 'es-CO' });
  const hechas = [];
  const foto = async (nombre) => {
    await pagina.waitForTimeout(400);
    await pagina.screenshot({ path: path.join(destino, nombre) });
    hechas.push(nombre);
  };
  try {
    // Cada rojo: 1 · la acción que falló (con la pantalla), 2 · el error, 3 · la red.
    // En la red se filtra lo que cuenta para cada rojo: las llamadas al servicio (rojo 1), todo (rojo 2: la página
    // cargó bien, el sistema respondió) y la petición de saldos que sigue pendiente (rojo 4).
    const filtroDeRed = { rojo1: '/api/', rojo2: '', rojo4: 'cuentas' };
    for (const id of ['rojo1', 'rojo2', 'rojo4']) {
      await abrirTrace(pagina, `${base}/trace/index.html?trace=${base}/traces/${id}.zip`);
      await pestana(pagina, 'Call');
      await foto(`${id}-1-accion.png`);
      await pestana(pagina, 'Errors');
      await foto(`${id}-2-error.png`);
      await pestana(pagina, 'Network');
      if (filtroDeRed[id]) await pagina.getByPlaceholder('Filter network').fill(filtroDeRed[id]);
      await foto(`${id}-3-red.png`);
    }
    // El rojo 3 no tiene trace: su captura es la consola.
    await pagina.setContent(consolaHtml(textoRojo3));
    await pagina.setViewportSize({ width: 1100, height: 200 });
    await pagina.screenshot({ path: path.join(destino, 'rojo3-1-consola.png'), fullPage: true });
    hechas.push('rojo3-1-consola.png');
    // El reporte: el resumen y el flaky con sus dos intentos.
    await pagina.setViewportSize({ width: 1400, height: 900 });
    await pagina.goto(`${base}/index.html`);
    await pagina.getByText('rojo 1 ·').first().waitFor();
    await foto('reporte-1-resumen.png');
    await pagina.getByRole('link', { name: /flaky ·/ }).first().click();
    await pagina.getByText(/Retry #1/).first().waitFor();
    await foto('flaky-1-reporte.png');
  } finally {
    await navegador.close();
    servidor.close();
  }
  return hechas;
}

/** Abre un trace en el visor y deja seleccionada la acción que falló. */
async function abrirTrace(pagina, url) {
  await pagina.goto(url);
  const conError = pagina.locator('.action-title.action-error, .tree-view-entry .action-error, [class*="action-error"]').first();
  await pagina.locator('.action-title, .tree-view-entry').first().waitFor({ timeout: 30_000 });
  if (await conError.count()) await conError.click();
}

async function pestana(pagina, nombre) {
  const tab = pagina.getByRole('tab', { name: new RegExp(`^${nombre}`) }).first();
  if (await tab.count()) await tab.click();
  else await pagina.locator('.tabbed-pane-tab-label', { hasText: nombre }).first().click();
}

function consolaHtml(texto) {
  const escapar = (t) => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const lineas = texto.split('\n');
  // Solo lo que cuenta: el error y las líneas de la pila que son del repo (lo demás es Node por dentro).
  const utiles = lineas.filter((l) => l.startsWith('Error') || (/^\s+at /.test(l) && !/node:internal|node_modules|\(node:/.test(l)));
  const cuerpo = utiles.map((l) => (l.startsWith('Error') ? `<b class="e">${escapar(l)}</b>` : escapar(l))).join('\n');
  return `<!doctype html><meta charset="utf-8"><style>
body{margin:0;background:#0f1424;font:15px/1.55 Consolas,Menlo,monospace;color:#d7dcef}
.barra{background:#1c2236;color:#9aa3c2;padding:8px 16px;font:13px system-ui,sans-serif}
pre{margin:0;padding:16px 20px 20px;white-space:pre-wrap}.p{color:#7fd1ae}.e{color:#ff8f8f}.n{color:#9aa3c2}
</style><div class="barra">Terminal · rojo 3 · ambiente: qa · sin CLAVE_BANCO</div><pre><span class="p">PS&gt; $env:AMBIENTE = 'qa'</span>          <span class="n"># y $env:CLAVE_BANCO sin definir</span>
<span class="p">PS&gt; npx.cmd playwright test --project=triage</span>
${cuerpo}
    <span class="n">… (y el resto de la pila de Node)</span>

<span class="n">No corrió ninguna prueba: no hay trace, ni captura, ni reporte. La evidencia es esta consola.</span></pre>`;
}

// ---------- Todo junto ----------
(async () => {
  console.log('Triage S9 · generando la evidencia (tarda alrededor de un minuto)...');
  try {
    armarCopia();
    correrTriage();
    const zips = traces();
    const textoRojo3 = rojo3();
    fs.writeFileSync(path.join(SALIDA, 'rojo3-consola.txt'), textoRojo3);
    const fotos = await capturas(textoRojo3);
    console.log('\nListo. Quedó en reportes/triage/:');
    console.log('  index.html                 el reporte (se publica en sitio/reportes/triage/)');
    console.log(`  traces/                    ${Object.values(zips).flat().join(', ')}`);
    console.log(`  capturas/                  ${fotos.join(', ')}`);
    console.log('  rojo3-consola.txt          la consola del rojo 3');
  } finally {
    borrarCopia();
  }
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
